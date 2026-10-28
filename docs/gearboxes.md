# Gearbox types

Every type is one entry in `GEARBOXES` in [`gearbox_runner.py`](../gearbox_runner.py); this page
describes them. Bug and issue numbers refer to [`ISSUES.md`](../ISSUES.md).

All types share: MIT stress analysis, a brute-force search over teeth, module and planets near the
requested ratio, a cost that combines mass, efficiency, width and a penalty for missing the ratio
(gains `K_Mass`, `K_Eff`, `K_Width` in the config file), and materials from
`config_files/config.json` (see the README's material modes).

## Framed outrunner motors

The gearbox sits on the motor's mounting face; any framed motor from `motors.json` can be used.
Motors smaller than 80 mm may have a gearbox up to 1.25× the motor diameter
(`SMALL_MOTOR_DIA_MM` / `MAX_GB_DIA_MULT_FACTOR_SMALL_MOTOR` in the params file).

| Type | Gearbox | Module · params file | Max gearbox diameter | Known issues |
|---|---|---|---|---|
| `sspg` | Single-stage planetary | `ActuatorAndGearbox` · `sspg_params.json` | factor × motor Ø − 2 × `ringRadialWidthMM` | CAD 1 (sun countersink radius fixed in the model) |
| `cpg` | Compound planetary | `ActuatorAndGearbox` · `cpg_params.json` | factor × motor Ø | — |
| `wpg` | Wolfrom planetary (3K) | `ActuatorAndGearbox` · `wpg_params.json` | factor × motor Ø − 2 × `ringRadialWidthMMBig` | — |
| `dspg` | Double-stage planetary | `ActuatorAndGearbox` · `dspg_params.json` | factor × motor Ø − 2 × `ring_radial_thickness` | CAD 3 (stage-1 ring split with small motors) |

The smallest motors (MN5008, MAD 5008, MAD 5010, 55–56 mm) find no SSPG or WPG design at the
golden ratios.

## Frameless outrunner motors (RO100, RO80, RO60)

The gearbox sits inside the rotor/stator of a frameless motor.

| Type | Gearbox | Module · params file | Max gearbox diameter | Known issues |
|---|---|---|---|---|
| `isspg_inside` | Internal single-stage, InBearing | `ActuatorAndGearbox_ISSPG_inside` · `isspg_params.json` | not limited | RO60 finds no design |
| `isspg_compact` | Internal single-stage, OutBearing | `ActuatorAndGearbox_ISSPG_compact` · `isspg_params.json` | not limited | bug 5; RO60 finds no design |
| `icpg` | Internal compound | `ActuatorandGearbox_ICPG` · `icpg_params.json` | factor × stator ID (inside the stator) | RO60 finds no design |
| `idspg` | Internal double-stage | `ActuatorandGearbox_IDSPG` · `idspg_params.json` | factor × (motor OD + 2 × 1.5); stage 1: stator ID − 2 × ring-1 width | bug 7 (bearings counted twice); RO60 finds no design |

RO100's rotor screws are M4 for now (bug 8, M4 vs M5 to be decided). ICPG's config file is
`motor_config.json`, IDSPG's `idspg_motor_config.json`; the others use `config.json`.

## Frameless inrunner motors (RI100, RI80)

| Type | Gearbox | Module · params file | Max gearbox diameter | Known issues |
|---|---|---|---|---|
| `insspg_type_1` | Inrunner single-stage, type 1 (independent) | `ActuatorandGearbox_INSSPG` · `insspg_params.json` | stator OD − 5.5 − 2 × 1.5 − 0.8 / 2 | bug 5 |
| `insspg_type_2` | Inrunner single-stage, type 2 (dependent) | same module and params | same | bugs 4 and 6 |
| `incpg_dependent` | Inrunner compound, dependent | `ActuatorAndGearbox_INCPG_dependent` · `incpg_dependent_params.json` | factor × motor Ø | minimum rotor top bearing bore set per motor in the params file |
| `incpg_independent` | Inrunner compound, independent | `ActuatorAndGearbox_INCPG_independent` · `incpg_independent_params.json` | factor × motor Ø | rotor bearings set per motor in the params file |
| `inwpg_dependent` | Inrunner Wolfrom, dependent | `ActuatorAndGearbox_INWPG_dependent` · `inwpg_params_dependent.json` | factor × motor Ø | as INCPG dependent |
| `inwpg_independent` | Inrunner Wolfrom, independent | `ActuatorAndGearbox_INWPG_independent` · `inwpg_params_independent.json` | factor × motor Ø | as INCPG independent |
| `indspg` | Inrunner double-stage | `ActuatorandGearbox_INDSPG` · `indspg_params.json` | factor × (stator wire OD − 2 × ring-2 width); stage 1: rotor ID − 4 × 1.5 | — |

INSSPG reads `insspg_motor_config.json`, INDSPG `indspg_motor_config.json`; the others `config.json`.

## Differences still to unify

Configuration files, safety factors, the motor driver and the diameter rules above differ between
types for historical reasons. They are kept as they are (so results don't change) and listed in
ISSUES.md, "Unify per-gearbox settings"; when one is unified, update this page in the same commit.

## Files each type writes

| Output | Where |
|---|---|
| Results CSV | `results/results_BruteForce_<motor>/<TYPE>_BRUTEFORCE_MIT_<motor>[_metal].csv` (INSSPG adds `_<gb_type>`) |
| CAD equations | `CADs/<FAMILY>/<gb_type>_equations*.txt` — variants write their own files in their family's folder (e.g. `CADs/ISSPG/isspg_inside_equations_onshape.txt` and `isspg_compact_…`) |
