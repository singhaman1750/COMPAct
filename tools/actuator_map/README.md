# Actuator map

Builds a map from **(motor, gear ratio, material)** to the COMPAct actuator for co-design: it runs
the normal optimiser for every gearbox type that fits each motor, over a grid of gear ratios, and
records each best design's cost, mass, efficiency, torque share, width, diameter and CAD variables.
It only calls the optimiser (`gearbox_runner`), so the normal workflow (`actOpt.py`) is unchanged.

## Run a sweep

```bash
python tools/actuator_map/sweep.py --name pilot \
    --motors U8_Lite MN8014 MAD_M6C12_KV170 RO100 RI100 --ratios 4:30:1
```

| Option | Meaning |
|---|---|
| `--name` | run folder: `tools/actuator_map/runs/<name>/` (gitignored) |
| `--motors` | motor names from `config_files/motors.json` |
| `--ratios` | `start:stop:step` (stop included), or a list such as `"6.5 10 20"` |
| `--materials` | `3dp`, `metal` (default both) |
| `--types` | only these gearbox types (default: every type that takes the motor's type) |
| `--workers` | parallel processes (default: CPU count − 1) |

Each case runs in its own temporary folder, so the repo's `CADs/` and `results/` are not touched.
Results go to `runs/<name>/cases/<material>/<motor>/<gb_type>__<ratio>.json`; `run.json` records
the request and the git commit. A case whose file exists is skipped, so an interrupted sweep
continues where it stopped (use a new `--name` to start again).

## One case's file

| Field | Meaning |
|---|---|
| `feasible`, `error` | a design was found; `error` is set if the optimiser raised (e.g. ISSUES.md bug 13) |
| `gear_ratio`, `cost`, `mass_kg`, `efficiency` | of the best design, as COMPAct computes them |
| `torque_carried_fraction` | share of the motor's peak torque the gears carry (< 1 when the face width was capped: ISSPG, ICPG, INWPG with 3D-printed gears) |
| `width_body_mm`, `width_with_driver_mm` | along the axis, motor casing to output retainer; with the driver mount |
| `dia_body_mm`, `dia_widest_mm` | largest round part; smallest circle holding everything (casing ears) |
| `geometry_notes` | set when a width or diameter is approximate |
| `same_cad_file` | the captured best design rewrites the optimiser's CAD file byte for byte (always true) |
| `opt_parameters`, `cad_vars` | the optimiser's design parameters and every Onshape CAD variable |
| `commit` | git commit the case ran on (`-dirty` if the optimiser code or config had local changes) |

Width and diameter come from `geometry.py`: formulas over the CAD variables, matched to the
Onshape models. The optimiser's own `actuator_width` is not used for the frameless and inrunner
types (ISSUES.md, bug 15).

## Build the table

```bash
python tools/actuator_map/table.py --name pilot
```

Reads the run's case files, `config_files/motors.json` and `config_files/cost.json`, and writes
into the run folder `table_3dp.csv`, `table_metal.csv` (one row per motor, requested ratio and
gearbox type with a design) and `summary.md` (best type per ratio, where it changes, ratio ranges,
cases without a design). Units are SI; speeds are also in rpm.

| Columns | Meaning |
|---|---|
| `ratio_requested`, `ratio` | asked for; the design's real ratio |
| `ns, np, np_small, nr, nr_small, module, n_planets` | teeth, module and planets (stage 1); `np_small`/`nr_small` for compound and Wolfrom |
| `ns_2 … n_planets_2` | stage 2 of DSPG, IDSPG, INDSPG |
| `mass_kg`, `width_body_m`, `width_with_driver_m`, `dia_body_m`, `dia_widest_m` | whole actuator |
| `peak_torque_out_Nm` | motor peak × ratio × efficiency × `torque_carried_fraction` |
| `rated_torque_out_Nm` | min(motor rated, fraction × motor peak) × ratio × efficiency |
| `no_load_speed_out_*`, `rated_speed_out_*` | motor speed ÷ ratio (rad/s and rpm) |
| `reflected_inertia_kgm2` | ratio² × motor rotor inertia (the gears' own inertia not yet included); `rotor_inertia_basis` says datasheet or estimate |
| `real_width_score` | **the map's rule:** K_Mass·mass + K_Eff·efficiency + K_Width_real·(width with driver, mm) + ratio error + K_torque_shortfall·(1 − fraction), gains from `cost.json` (K_Width_real 0.05) |
| `compact_cost` | the optimiser's own cost (width = planet face widths), kept as a second rule |
| `best_by_real_width`, `best_by_compact_cost` | the lowest-score type of that motor, ratio and material, by each rule |
| `near_best_real_width`, `near_best_compact` | every type within 2 % of the best score (near-ties: the winner may flip between neighbouring ratios) |
| `no_full_torque_design` | no type at this motor, ratio and material carries 80 % of the peak torque |
| `torque_capped`, `geometry_approx`, `cad_issues` | gears carry < 100 % of peak torque; width approximate; open CAD issues of the type (ISSUES.md) |

**Rules for "best"** (pilot review, 2026-10-29): a capped design can be best only if its gears carry
at least 80 % of the peak torque (`MIN_CARRIED_FRACTION_FOR_BEST`); if no design does, the best of
all is still given and the group is marked `no_full_torque_design`.

## Fit over the gear ratio

```bash
python tools/actuator_map/fit.py --name pilot          # --no-plots to skip the figures
```

For every motor, material and gearbox type, fits mass, widths, diameters, efficiency,
torque-carried fraction and the optimiser's cost against the design's real gear ratio, and writes
into the run folder:

| File | Content |
|---|---|
| `fits.json` | per type and quantity: the pieces (each from its first ratio, polynomial coefficients in the plain ratio, low → high, and degree), the break ratios between pieces, errors and the data points (for exact piecewise-linear interpolation); valid ratio intervals; per motor and material the best type over the ratio range and the switch ratios, by both rules |
| `fits.md` | per type and quantity: typical (RMS) / largest error and the pieces' degrees (`d1+d1` = two straight pieces); the best-type intervals; ratios where the fitted best differs from the table's |
| `plots/<motor>_<material>.png` | mass, width with driver, body diameter and real-width score vs ratio: points, fits, switch ratios |

**Model:** a quantity is split into pieces where its designs really jump: a step more than 3× the
usual step between neighbouring designs that changes the level by more than 10 % for at least 3
designs (a lone odd design or a smooth steep rise is not a jump; e.g. RI100 3dp INDSPG length,
86 → 108 mm between ratio 25.5 and 26.8). Each piece gets the lowest polynomial degree (0–3) whose
RMS error is within 1 % of the value above the best degree's, at most (points − 1) ÷ 2 (4 points: a
straight line). So a quantity is smooth in pieces with a step where the designs step. The designs
are discrete (teeth, modules, bearings), so neighbouring ratios still scatter around the trend
(pilot: typically 1–4 %; capped INWPG's torque fraction ~10–14 %); the data points stay for exact
interpolation.

**Best type between swept ratios:** each type valid at that ratio gets the real-width score from
its fitted values, the 80 % torque rule is applied, and the lowest wins; the type switches where
the score curves cross (e.g. U8_Lite 3dp: CPG → WPG at 13.7). Where two types are near-tied the
winner can flip over very short ranges (e.g. CPG for 4–4.04, then SSPG), so a best-type interval
shorter than 0.5 is merged into a neighbour that is valid over it, scores within 2 % and doesn't
break the 80 % rule; `fits.json` keeps the unmerged intervals as `best_<rule>_raw`. Output torque,
speed and reflected inertia are not fitted: they follow exactly from the ratio, efficiency,
fraction and the motor.

## Use the map

`map.py` is standalone (numpy and one `fits.json`, which also holds the motors' values, the gains
and the rules), so it can be copied into a co-design project together with a map folder.

```python
from tools.actuator_map.map import ActuatorMap

amap = ActuatorMap("tools/actuator_map/runs/pilot")    # a run folder or a released map folder
a = amap.actuator("U8_Lite", 14.6, "3dp")
a.gb_type                        # 'wpg'  (best type at this ratio)
a.mass, a.width, a.dia           # 0.837 kg, 0.101 m (with driver mount), 0.115 m
a.peak_torque, a.rated_torque    # 34.0 N m, 9.0 N m at the output
a.no_load_speed                  # rad/s at the output (a.no_load_speed_rpm in rpm)
a.reflected_inertia              # ratio^2 x rotor inertia, kg m^2
a.flags                          # torque_capped, no_full_torque_design, near_best, cad_issues, ...
```

| Argument | Meaning |
|---|---|
| `gb_type="dspg"` | that type at this ratio instead of the best |
| `types=["cpg", "dspg"]` | only these types may be best |
| `rule="compact_cost"` | best by the optimiser's own cost instead of the real-width score |
| `method="interp"` | linear between the swept designs of the type (exact at the designs) instead of the smooth fits |
| `derivative=True` | `a.derivatives`: d(value)/d(ratio) of every value (exact within a fit piece) |

**Fit or interp?** The fits are smooth trends, which a gradient-based co-design optimiser needs.
Where neighbouring designs scatter (e.g. small-motor WPG masses: 595 g at 19:1, 837 g at 20:1) a
fit can be several % off a single design, while interp follows every design but its slope jumps
at each one. `a.flags["fit_error_high"]` lists the quantities whose fit is more than 5 % off at
some design. Optimise with the fits, then read the final design with `method="interp"`.

A ratio where no (allowed) type has designs raises `ValueError` (no extrapolation). Helpers:
`motors()`, `materials(motor)`, `types(motor, material)`, `covered(motor, material)`,
`best_types(motor, material)` (intervals and switch ratios), `ranking(motor, ratio, material)`.
All values are SI; speeds also in rpm. The gears' own inertia is not included yet.

## Choose a motor and gearbox for a torque and speed

Give the output peak torque and output no-load speed you need; every motor and gearbox type is
ranked, and the best designs come with their gear ratio, gearbox parameters and CAD files.

```bash
python tools/actuator_map/choose.py --torque 30 --speed 25            # N m, rad/s (or --speed_rpm)
python tools/actuator_map/choose.py --torque 30 --speed 25 --no-map   # optimise everything, no map
```

1. **Screening** (default): `ActuatorMap.select()` takes, for every motor and type, the ratios
   where output peak torque (motor peak × ratio × efficiency × torque fraction, from the fits)
   and output no-load speed (motor no-load speed ÷ ratio) both reach the ask, and the lowest score
   among them. The swept designs themselves are judged too, with their exact values: the smooth
   fit can average a good design away (e.g. a torque fraction that falls steeply between designs).
   It asks for 2 % more (`--margin`), since the values are approximate. Milliseconds for all motors.
2. **Confirmation**: the first 8 (`--shortlist`) are run through the normal optimiser (as in a
   sweep); torque and speed are recomputed from each real design. A design that misses by a
   little is re-run at a corrected ratio (at most 2 rounds, `--rounds`). About 20 s to a few
   minutes, mostly DSPG.
3. **Ranking**: designs that meet the ask, by score (real-width score, or `--rule compact_cost`;
   both without the ratio-error term, since the ratio is chosen here, not asked); then the closest
   misses (smallest shortfall: 1 − torque/ask plus 1 − speed/ask, short parts only).

`--no-map` runs the optimiser for every motor and type at every whole ratio from torque ÷ motor
peak (`--min_ratio` 4 at least) to motor no-load speed ÷ speed (`--max_ratio` 40 at most): 5 to 40
minutes per ask. Use it for asks outside the map's ratios (the screening prints which motors) or
to check the screening. Other options: `--material`, `--motors`, `--types`, `--map`, `--top`,
`--name`, `--workers`.

Output in `runs/select_<name>/` (gitignored): `result.json` (the ask, options, commits, every
confirmed design ranked, with its table columns, gears and `opt_parameters`) and the CAD equation
files of every confirmed design in `cads/<motor>__<type>__<ratio>/`. A warning is printed when
optimiser code or config changed since the map's sweep (screening may then be off; confirmation
always uses the current code).

In another project (map only, no optimiser):

```python
cands = amap.select(torque=30.0, speed=25.0, material="3dp")   # [Candidate], meeting the ask first
c = cands[0]
c.motor, c.gb_type, c.ratio, c.meets, c.window      # window: [[low, high], ...] ratios that meet it
c.torque_margin, c.speed_margin, c.actuator.mass     # c.actuator: as amap.actuator() gives it
```

**Checked against `--no-map`** (map v2, all 33 motors, 3dp, 2026-11-05): 10 N m / 60 rad/s →
MAD_7005_KV115 SSPG 6:1; 30 N m / 25 rad/s → RO100 ISSPG compact 4:1; 100 N m / 10 rad/s → RI100
INDSPG 23.1:1. The same design both ways, in about 20 s instead of 10–37 minutes.

**Limits:** peak torque and no-load speed are two corner points; meeting both doesn't mean the
motor gives the peak torque at speed. No-load speeds are `motors.json`'s (KV × 48 V for the framed
motors). The 80 % torque rule of the map isn't used: the torque check already counts the torque
fraction, and capped types still pay `K_torque_shortfall` in their score.

## Plot fit quality

```bash
python tools/actuator_map/plot_fit.py overview tools/actuator_map/maps/v1 3dp out.png            # mass
python tools/actuator_map/plot_fit.py overview tools/actuator_map/maps/v1 metal out.png efficiency
python tools/actuator_map/plot_fit.py type tools/actuator_map/maps/v1 U8_Lite 3dp dspg out.png    # mass, width, efficiency
```

Each panel: the designs (dots), the smooth fit (blue), the interp line (grey), a ±5 % band around
the fit, designs more than 5 % off in red and piece breaks dashed; below it, the error at each
design (fit − design, %). `overview` shows every gearbox type with one motor (U8_Lite, RO100,
RI100); `type` shows one type with any quantities (`mass_kg`, `width_with_driver_m`,
`width_body_m`, `dia_body_m`, `dia_widest_m`, `efficiency`, `torque_carried_fraction`). A
release includes the overviews in `maps/<version>/plots/`.

## Release a map

```bash
python tools/actuator_map/table.py --name full
python tools/actuator_map/fit.py --name full
python tools/actuator_map/release.py --run full --version v1
```

Copies `fits.json`, `fits.md`, `summary.md` and the tables into `tools/actuator_map/maps/<version>/`
(committed; the case files and plots stay in the gitignored run folder) and writes `map.json`
(the sweep's commit, the grid, case counts, settings, known issues, and warnings such as motors or
ratios without designs) and a README. Released maps: `maps/v1/` (33 motors, ratios 4–30, 3dp and
metal; metal masses are overestimated, see its README) and `maps/v2/` (the same grid, after the steel-ring
metal fixes for every type, the WPG motor case and the IDSPG sun hub; metal masses are still high, see its README).
