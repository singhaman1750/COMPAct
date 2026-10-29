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
