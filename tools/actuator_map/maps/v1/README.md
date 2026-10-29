# Actuator map v1

Released COMPAct actuator map: the best gearbox type and the whole actuator's mass, size, torque, speed and reflected inertia for each motor, gear ratio and material. Read it with `tools/actuator_map/map.py` (standalone: copy `map.py` and this folder into another project).

```python
from tools.actuator_map.map import ActuatorMap
amap = ActuatorMap("tools/actuator_map/maps/v1")
a = amap.actuator("U8_Lite", 9.3, "3dp")      # best type at 9.3:1
a.gb_type, a.mass, a.width, a.peak_torque, a.flags
```

Optimise with the smooth fits (the default, with derivatives); read the final design with `method="interp"`. `flags["fit_error_high"]` lists quantities whose fit is more than 5% off at some design.

## Contents

| File | |
|---|---|
| `fits.json` | everything `map.py` needs: fits, best types, motor values, gains, rules |
| `fits.md` | fit quality and best types per motor and material |
| `summary.md` | best type at each swept ratio |
| `table_<material>.csv` | every optimised design (one row per type and ratio) |
| `map.json` | where this map came from, its settings and warnings |
| `plots/fit_overview_<material>_<quantity>.png` | how well the fits follow the designs: every gearbox type with one motor (`tools/actuator_map/plot_fit.py` draws these and single types) |

## Source

- sweep run `full`, COMPAct commit `a89b170e4f95c3814dc556f2419e6bd091bdfd6d`
- 33 motors, ratios 4-30 (step 1), materials 3dp, metal
- 7452 cases: 3930 with a design, 3494 without, 28 raised (counted as no design)

## Known issues

- **metal-overestimate**: Metal masses are overestimated: the metal mode reuses the 3D-printed shapes, the whole gearbox casing is weighed as steel, and planets are as wide as two planet bearings need. This favours compound types (CPG) in the metal map. See docs/metal_sspg_mass.md and ISSUES.md 'Material modes'.
- **bug13**: INDSPG raises instead of reporting 'no design' where it has none (ISSUES.md bug 13); those cases count as no design.
- **CAD6**: IDSPG stage-2 parts don't move in the CAD with smaller motors (RO80).
- **CAD7**: INWPG dependent output ring gear and bearing don't move in the CAD (RI80).
- **reflected-inertia**: Reflected inertia is ratio^2 x rotor inertia only; the gears' inertia is not included. Framed motors' rotor inertias are estimates (+-30 %).

## Warnings

- RO60 (3dp): no design in any gearbox type at any swept ratio; not in the map
- RO60 (metal): no design in any gearbox type at any swept ratio; not in the map
- RI80 (3dp): no design at ratios 12
- RI80 (metal): no design at ratios 12
- RO80 (3dp): no design at ratios 9, 10, 26, 27, 28, 29, 30
- RO80 (metal): no design at ratios 9, 10, 26, 27, 28, 29, 30
- RO100 (3dp): the best type is torque-capped (< 80 % of peak) somewhere in the range; check flags['torque_capped'] / ['no_full_torque_design']
- RO80 (3dp): the best type is torque-capped (< 80 % of peak) somewhere in the range; check flags['torque_capped'] / ['no_full_torque_design']
