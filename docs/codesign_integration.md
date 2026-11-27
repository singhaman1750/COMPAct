# Using COMPAct in a co-design optimisation

This guide is for a project that optimises a robot's design and control together (for example a
quadruped with CMA-ES and convex MPC) and wants each actuator to be a COMPAct actuator instead of
an off-the-shelf one. The design variables per actuator become a **motor** and a **gear ratio**;
COMPAct supplies the best gearbox type for them, the actuator's mass, size, efficiency, torque,
speed and inertia, and at the end the gearbox itself (teeth, modules, planets, face widths) with
its CAD files.

Two calls do the work:

| When | Call | Time | Gives |
|---|---|---|---|
| every evaluation of the optimiser | `ActuatorMap().actuator(motor, ratio)` | milliseconds | best gearbox type, mass, sizes, efficiency, output torque and speed, reflected inertia |
| once per chosen actuator, at the end | `final_design(motor, ratio, material, gb_type, cad_dir)` | 0.1 s to ~75 s | the real design: gearbox type, teeth counts, modules, planets, face widths, exact ratio, CAD equation files |

The map is a set of smooth fits to the optimiser's best designs over a grid of motors and ratios
(map v3: 32 motors, ratios 4–30, 3D-printed and metal; RO60 has no design, ISSUES.md bug 16), so it is fast enough for the loop. Teeth
counts are whole numbers and can't come from a fit, so the final design runs the optimiser once.

## Setup

In the co-design repo, with its Python environment active:

```bash
git submodule add https://github.com/singhaman1750/COMPAct external/COMPAct
git -C external/COMPAct checkout map-v3      # pin the COMPAct version that built the map
pip install -e external/COMPAct
python -c "import compact_api; print(compact_api.ActuatorMap().path)"
```

Use the editable install (`-e`): COMPAct reads its config files, CAD templates and maps from its
own folder. Pinning to a tag means `final_design` runs the same code that built the map. To move
to a newer COMPAct, check out a newer tag in the submodule and commit the submodule change.

Import only `compact_api`. If the co-design repo has a top-level package called `tools`, it still
works (COMPAct puts its own folder last on `sys.path`), but avoid importing COMPAct's internals
directly.

## In the optimisation loop

```python
from compact_api import ActuatorMap

amap = ActuatorMap()                         # the latest released map in the installed COMPAct
a = amap.actuator("U8_Lite", 9.3, "3dp")     # motor, ratio, material
```

`a` is an `Actuator` (all SI units):

| Field | Meaning |
|---|---|
| `gb_type` | the best gearbox type at this ratio (keep it: `final_design` needs it) |
| `mass` | kg, the whole actuator, motor included |
| `width`, `width_body` | m, along the axis, with and without the motor-driver mount |
| `dia`, `dia_widest` | m, the largest round part, and the widest including casing ears |
| `efficiency` | gearbox efficiency |
| `torque_fraction` | share of the motor's peak torque the gears carry; below 1 when the face width was capped |
| `peak_torque`, `rated_torque` | N m at the output (`rated_torque` is None if the motor has no rated value) |
| `no_load_speed`, `rated_speed` | rad/s at the output (`no_load_speed_rpm`, `rated_speed_rpm` also exist) |
| `reflected_inertia` | kg m², ratio² × motor rotor inertia (the gears' own inertia is not included) |
| `heat_coefficient` | W/(N m)²: the winding's copper loss = `heat_coefficient` × output torque² (see below) |
| `motor_constant` | N m/√W, the motor's Km (torque² ÷ copper loss = Km²) |
| `motor_mass`, `gearbox_mass` | kg, the motor alone and everything else (`mass` is the sum) |
| `motor_dia`, `motor_length` | m, the motor alone |
| `score` | COMPAct's score for the design (lower is better) |
| `flags` | notes: `torque_capped`, `cad_issues`, `fit_error_high`, `near_best`, `rotor_inertia_basis`, ... |

Map these onto whatever actuator description the co-design code already uses (mass and inertia
for the links or trunk, size for packaging and collisions, torque and speed limits for the MPC,
efficiency for an energy cost).

Other useful calls:

- `amap.motors()`: the 32 motor names in the map; `amap.motor(name)` gives the motor's own values:
  torques, speeds, rotor inertia, KV, peak and rated current, `resistance_ohm` (line-to-line), the
  torque constants `kt_kv_Nm_per_A` (8.27 ÷ KV), `kt_peak_Nm_per_A` (peak torque ÷ peak current) and
  `kt_datasheet_Nm_per_A` (CubeMars only), mass, `diameter_m`, `length_m`, and a `*_basis` for
  each value that is an estimate or has an unclear convention (`rated_current_basis` tells a
  datasheet value from the 0.31 × peak default).
- `amap.fit_error(motor, material, gb_type, "mass_kg")`: how far that type's fit is from its swept
  designs over its whole ratio range (`rms`, `max_abs` in the quantity's units; `rms_rel`,
  `max_rel` as fractions). It is not the error at one ratio, and it doesn't apply to
  `method="interp"`, which is exact at the designs.
- `amap.covered(motor, "3dp")`: the ratio intervals the map covers for that motor.
- `amap.ranking(motor, ratio, "3dp")`: every gearbox type at that ratio, best first.
- `amap.actuator(motor, ratio, "3dp", gb_type="cpg")`: a specific type instead of the best one.
- `amap.select(torque=30.0, speed=25.0)`: every motor and type ranked for an output peak torque (N m)
  and no-load speed (rad/s) — useful to narrow the motor list before optimising.

`actuator()` raises `ValueError` when the motor has no design at that ratio. In the loop, catch it
and give that candidate a penalty cost instead of stopping.

### Design variables for CMA-ES

- **Ratio:** continuous. Optimise a value in [0, 1] and map it into the motor's covered range,
  `lo + x * (hi - lo)` from `amap.covered(motor, "3dp")`.
- **Motor:** categorical. Either one continuous variable rounded to an index into a motor list
  sorted by peak torque (so neighbouring indices are similar motors), or a separate CMA-ES run per
  motor (better when the list has been narrowed to a few motors, e.g. with `select()`).
- **Gearbox type:** not a variable: the map gives the best type for the motor and ratio.
- **Material:** fix `"3dp"`. Metal masses are known to be too high for now.
- **Per joint:** either one (motor, ratio) shared by every joint, or one per joint group (e.g. hip
  abduction, hip, knee).

The best type can change between neighbouring ratios, which makes small steps in mass or size.
CMA-ES handles this. `derivative=True` gives d(value)/d(ratio) for gradient-based optimisers.

### Winding heat and the two-body mass model

`heat_coefficient` gives the copper loss in the motor's windings for an output torque τ:
`P = heat_coefficient × τ²` (W). It is 0.75 × R ÷ (Kt × ratio × efficiency)², from:

- R: the line-to-line resistance at about 25 °C. For a hot winding multiply by
  1 + 0.00393 × (T − 25 °C) (`amap.meta["resistance_alpha_per_K"]`).
- Kt = 8.27 ÷ KV, per amp of phase-current amplitude; copper loss = 0.75 × R × I_amp².
  Datasheet Kt values (and peak torque ÷ peak current) are 1.0–1.35 × higher for most motors, but no
  maker says which current they mean, so the map uses the KV value. To use another Kt, scale:
  `heat_coefficient × (kt_kv / kt_other)²`.
- The motor driving the load. When the load drives the motor (negative work) the motor torque is
  τ × efficiency ÷ ratio, so the loss is `heat_coefficient × efficiency⁴ × τ²`.
- Copper loss only: iron and friction losses are not included. `efficiency` is the map's fixed
  gearbox efficiency (no load dependence).

For inertia, the motor and the gearbox can be two bodies: `motor_mass` over `motor_length` at the
motor end, `gearbox_mass` over the rest of `width_body`. This fits framed motors, which sit behind the
gearbox; a frameless motor sits around or beside the gears inside the housing, so there the
lengths overlap and one body (`mass` over `width_body`) is closer.

## At the end: the real gearbox

```python
from compact_api import final_design

d = final_design("U8_Lite", 9.3, "3dp", gb_type=a.gb_type, cad_dir="results/knee_actuator")
d["gb_type"], d["ratio"]          # e.g. "cpg", 9.257 (the real ratio from the teeth counts)
d["gears"]                        # {"ns": 21, "np": 51, "np_small": 30, "nr": 102, "module": 0.7, "n_planets": 3}
d["face_widths_mm"]               # {"fw_s_calc": ..., "fw_p_b": ..., ...}
d["mass_kg"], d["efficiency"], d["peak_torque_out_Nm"], d["width_with_driver_m"], d["dia_body_m"]
d["heat_coefficient_W_per_Nm2"]   # as Actuator.heat_coefficient, for the real ratio and efficiency
d["cad_files"]                    # the CAD equation files written under cad_dir
```

`gears` names: `ns` sun, `np` planet (the big planet for compound and Wolfrom types), `np_small`
small planet, `nr` ring (`nr_small`: Wolfrom's second ring), `module`, `n_planets`; double-stage
types also have `ns_2`, `np_2`, `nr_2`, `module_2`, `n_planets_2` for the second stage.
`cad_vars` holds every CAD variable and `commit` the COMPAct commit that made the design.

The CAD equation files drive the SolidWorks or Onshape models of that gearbox type (see
[onshape.md](onshape.md)). They exist for `"3dp"` only: metal has no CAD model, so for `"metal"`
`cad_files` is `[]` and `cad_note` says why (`cad_vars` is still filled). `final_design` raises
`ValueError` if the optimiser finds no design.

`nearest_design(motor, ratio, "3dp")` is an instant alternative: the nearest design that was
actually swept for the map (grid ratios only, no face widths or CAD files).

**Check step:** the real ratio, mass and efficiency differ slightly from the map's smooth values.
Put the real values back into the robot model and evaluate the final design once more.

## Limits

- **Torque and speed** are two corner points: output peak torque and output no-load speed. Meeting
  both doesn't mean the motor gives its peak torque at speed; model the MPC limit as the line
  between them (or a proper motor curve), not a box.
- **Inertia:** `reflected_inertia` leaves out the gears' own inertia. Rotor inertias of the framed
  motors are estimates (±30 %; `flags["rotor_inertia_basis"]`).
- **Fixed settings:** 48 V supply; gears sized for the motor's peak torque; ratios 4–30 only.
- **Heat:** copper loss only, cold resistance; T-Motor and MAD resistances are taken as
  line-to-line (the makers don't say); see [motors.md](motors.md).
- **Metal** masses are too high (the metal mode reuses the 3D-printed shapes;
  [metal_sspg_mass.md](metal_sspg_mass.md)).
- **Open issues:** some types have open CAD issues (`flags["cad_issues"]`), and some 3D-printed
  face widths are capped to fit the motor (`flags["torque_capped"]`, `torque_fraction` < 1). See
  [ISSUES.md](../ISSUES.md).
