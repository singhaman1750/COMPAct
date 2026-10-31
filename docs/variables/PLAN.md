# Variable classification: plan for all actuators

Plan for sorting every gearbox type's CAD variables into **input / optimisation / fixed / dependent**,
as done for SSPG (PR #104) and CPG (PR #110). This page is the overview; each type has its own plan
in [`plan/`](plan/). Made on 2026-10-30 on the branch `variable-classification-plan`, **survey only**:
nothing in the code, config or CAD output changes on this branch.

## Rules (the same as SSPG and CPG)

1. **The Onshape interface stays byte-identical**: the same variable names, in the same order, with
   the same values and the same number formatting (e.g. `5` stays `5`, not `5.0`). No variable is added
   to or removed from any CAD file. The golden check (58 cases) must stay unchanged after every step.
2. **Every variable gets** a category (input / optimisation / fixed / dependent), a sub-type, its source
   (config key, motor, driver) or formula / catalogue lookup / rule, `depends_on`, a **confidence**
   (high / medium / low) and a reason, in `config_files/variables/<type>_variables.json`, with a generated
   page `docs/variables/<type>.md`.
3. **Medium confidence** marks a judgement call or a hard-coded tuning number. Each medium item is
   reviewed with the user one by one (line, code snippet, suggested fix) before anything changes.
4. **Hard-coded tuning numbers** move to the type's config with the **shared key names** (below), in
   every copy of the rule (the CAD code and the mass code), with values that keep every output
   bit-identical. Each moved key gets a test that it drives exactly its CAD variables (and the mass where
   it should).
5. **Categories are consistent across types**: shared rules in `config_files/variables/rules.json`,
   checked by the tests.
6. **Bugs found on the way are logged, not fixed** in the classification PRs (fixes that change results
   get their own PRs).

## Status and size

| Type | Plan | CAD variables | Draft: input / optimisation / fixed / dependent | Alias names | Effort |
|---|---|---|---|---|---|
| SSPG | done (#104), [spec](sspg.md) | 113 | 18 / 4 / 43 / 48 | — | — |
| CPG | done (#110), [spec](cpg.md) | 119 | 18 / 5 / 42 / 54 | — | — |
| WPG | [plan](plan/wpg.md) | 143 | 18 / 5 / 53 / 67 | 0 | ~1.5 h |
| DSPG | [plan](plan/dspg.md) | 255 | 36 / 15 / 89 / 115 | 78 | ~2.5 h |
| ISSPG compact | [plan](plan/isspg_compact.md) | 145 | 22 / 4 / 57 / 62 | 0 | ~1.5 h |
| ISSPG inside | [plan](plan/isspg_inside.md) | 147 | 24 / 4 / 54 / 65 | 0 | ~1 h |
| ICPG | [plan](plan/icpg.md) | 117 | 19 / 5 / 54 / 39 | 0 | ~1.5 h |
| IDSPG | [plan](plan/idspg.md) | 198 | 24 / 8 / 78 / 88 | 35 | ~2 h |
| INSSPG type 1 | [plan](plan/insspg_type_1.md) | 107 | 13 / 4 / 56 / 34 | 0 | ~1.5 h |
| INSSPG type 2 | [plan](plan/insspg_type_2.md) | 107 | 13 / 4 / 56 / 34 | 0 | ~0.5 h |
| INCPG dependent | [plan](plan/incpg_dependent.md) | 134 | 22 / 5 / 55 / 52 | 0 | ~1 h |
| INCPG independent | [plan](plan/incpg_independent.md) | 138 | 22 / 5 / 52 / 59 | 0 | ~0.5 h |
| INDSPG | [plan](plan/indspg.md) | 210 | 12 / 15 / 111 / 72 | 42 | ~2 h |
| INWPG dependent | [plan](plan/inwpg_dependent.md) | 146 | 22 / 5 / 60 / 59 | 0 | ~1.5 h |
| INWPG independent | [plan](plan/inwpg_independent.md) | 150 | 22 / 5 / 57 / 66 | 0 | ~0.5 h |
| **13 remaining** | | **1,997** | | **155** | **~17.5 h** + ~1.5 h tooling + the reviews |

The draft counts come from the survey (below) and change during the classification (e.g. the
implicit ring teeth move from optimisation to dependent, some "formula" guesses become inputs).

## How the plan was made

A read-only survey script (kept outside the repo) reads, for each type: the variable names in the
golden Onshape file, the writer expression of each, every assignment of that attribute in the
actuator class (line and code), and proposes a category from the source (config key → fixed,
motor / driver → input, bolt / bearing table → dependent lookup, gearbox teeth / module → optimisation,
face width → stress rule, otherwise formula), flags hard-coded numbers, several assignments and writer
expressions, and compares with SSPG / CPG. Calibrated on the finished specs: it agrees with CPG on
119 / 119 categories and with SSPG on 112 / 113. A second scan lists hard-coded numbers in each type's
face-width (MIT) and mass functions. Every flagged item was then read by hand; the result is the
"special cases" and "hard-coded numbers" sections of each type's plan.

## Cross-cutting findings

### 1. Shared config keys: where each would go

| Shared key (from SSPG / CPG) | Types with the same hard-coded rule |
|---|---|
| `clearance_motor_and_case_min` (5) | WPG (a **constant** 5 in the CAD, but a growing rule in the mass code), DSPG (stage 1, CAD + mass) |
| `case_mounting_hole_wall_overlap` (0.5) | WPG, DSPG; the inrunner types use `dia / 2` (overlap 0: no hard-coded number) |
| `bearing_mount_wall_bolt_dia_multiple` (2, × 4) | WPG (CAD + mass), DSPG (both stages, CAD + mass); INSSPG reads `bearing_mount_thickness` from the config instead |
| `planet_bearing_gap` (`1.5 × 2/3`, and `× 1/3` per gear in compound / Wolfrom types) | **every** type: WPG, DSPG (per stage), ISSPG ×2, ICPG, IDSPG (per stage), INSSPG ×2, INCPG ×2, INDSPG (per stage), INWPG ×2 |
| `ringRadialWidthMM` | INCPG writes it as `ring_radial_width`; others use `ring_radial_thickness` from the config |

Two-stage types (DSPG, IDSPG, INDSPG) use the suffixes `1` / `2` for stage-specific keys: decide per key
whether one shared value or one per stage (review).

### 2. A new shared item: the sun-hub margin

`sun_hub_dia = … + standard_clearance_1_5mm × 4` is hard-coded in **SSPG and CPG** (already classified,
high confidence as a formula) and in DSPG and ISSPG compact; IDSPG uses **× 5 in the CAD but × 4 in the
mass code**. Proposal: a shared key (e.g. `sun_hub_clearance_multiple`), applied to SSPG and CPG too
(value-identical). To review.

### 3. The CPG "bug 18" pattern (one module in the CAD for two modules)

WPG, ICPG, INCPG (both), INWPG (both) write a single `module` (the big one) although the optimiser
searches separate big / small module ranges; ring-side values use the big module. As in CPG: the code
fix (`module_b` / `module_s`, ring side on `module_s`) is value-identical today (all designs have equal
modules); a second module in the CAD (option B) stays open.

### 4. Shared rules (`rules.json`) need two changes

- **Ring teeth:** extend the implicit-constraint pattern to `Nr_b`, `Nr_s` (Wolfrom), `a1_Nr`, `a2_Nr`
  and the alias names `a1_Nr2`, `a2_Nr1` (double stage).
- **Face widths can't be matched by name**: in WPG `fw_p_b` is the stress width and `fw_r_b` a copy, in
  INWPG it is the other way round. Proposal: keep `fw_s_calc` (and `a1_` / `a2_` variants) by name, and
  for the other widths check that every entry whose value comes from the face-width function is a
  "stress rule" and every copy is a "formula" (a tooling change).

### 5. Mismatches between the CAD code and the mass code (new bugs to log)

| Type | Mismatch |
|---|---|
| WPG | `clearance_motor_and_case`: a constant 5 in the CAD, a growing rule in the mass code |
| WPG | `bearing_mount_thickness`: the CAD and the mass code use different ring terms |
| IDSPG | `sun_hub_dia`: `1.5 × 5` in the CAD, `1.5 × 4` in the mass code |
| CPG | bug 17 (already logged): ring thickness, mass model never grows the ring to the bearing |

### 6. Dead code and unused config (to log, low priority)

- **Lookups overwritten by config values**: INSSPG (9 fastener sizes), INDSPG (`a1_sun_bottom_casing_bearing_*`):
  the CAD gets the config value; the lookup is dead.
- **Config values the CAD ignores** because the code computes them: ISSPG (`sun_hub_dia`,
  `sun_coupler_hub_thickness`, `ring_hub_thickness`, `case_mounting_hole_shift`, `stator_hole_*`, …), INSSPG
  (`bearing_ID/OD/height`, `sun_hub_dia`, …).
- **Unused config blocks** (the runner reads only the 3DP block): `wpg_design_parameters`,
  `dspg_design_parameters`, `cpg_design_parameters` (in `icpg_params.json`), `idspg_design_parameters`,
  `indspg_design_parameters`; unused keys: `sun_sec_carrier_bearing_massKG` (ICPG),
  `output_mounting_hole_num` (CPG, already in its spec).

### 7. Other type-specific points needing a decision

- **ICPG's driver dimensions** come from its own config, not `Motor_drivers` (the runner passes no
  driver): classify as Input / driver (consistent with the others) or Fixed?
- **New hard-coded constants without a shared key**: ISSPG `carrier_thickness_mid` 6 / `ring_hub_thickness` 3 /
  `sun_coupler_hub_thickness` 3; INSSPG `sun_support_OD` cap 21 mm and `fw_s_used` offsets; INDSPG stage-1
  output bearing (38.1 / 47.625 / 4.763 mm, 22.7 g), `sun_hub_dia` and `rotor_mount_hole_PCD` offsets (2).
- **Width caps**: ISSPG, ICPG, INWPG face widths depend on the stator height and margin keys
  (`gear_axial_margin_mm`, `planet_step_gap_mm`, `planet_stack_stator_heights`).

### 8. Mass-only hard-coded numbers (for the metal-mass phase, not this one)

Each type's plan lists the numbers found in its mass code (bearing masses, boss sizes, margins such as
`1.5 × 4`, fillet factors). They don't reach the CAD, so they are out of scope for the classification and
are kept as input for the metal-mass correction.

## Tooling changes needed (before or with the first types that need them)

1. **Alias names** (DSPG 78, IDSPG 35, INDSPG 42): the spec marks the second name `alias_of` the first; the
   tests check equal values and identical classification.
2. **Stage files** (DSPG writes `_stg1` / `_stg2` plain files besides the Onshape file): check them as
   aliases of the Onshape names.
3. **Two types sharing one class** (INSSPG type 1 / 2, chosen by `insspg_type`): the registry passes the
   type to the runner.
4. **Per-type config file names**: `icpg_params.json` reads a block named `cpg_3DP_design_parameters`;
   the gear standard comes from `motor_config.json`, `idspg_motor_config.json`, … instead of `config.json`.
5. **Face-width rule check by source, not name** (finding 4).
6. **Writer expressions** that aren't a single attribute (`getattr(self, "sun_coupler_hub_thickness1", "N/A")`).

## Recommended order

1. **WPG** (framed, closest to CPG) → 2. **DSPG** (needs the alias / stage-file tooling) →
3. **ISSPG compact, inside** → 4. **ICPG** → 5. **IDSPG** → 6. **INSSPG type 1, 2** →
7. **INCPG dependent, independent** → 8. **INDSPG** → 9. **INWPG dependent, independent**.

One branch and PR per type (or per pair for the two-variant types), each following the SSPG / CPG
steps: classify → number check → review the medium items → move the agreed numbers → PR.

## Decisions for the user (before or during the work)

1. One shared key per stage, or one per stage with suffix `1` / `2`, for the double-stage types.
2. The shared `sun_hub_dia` margin key, and whether to apply it to SSPG / CPG too. **Done (2026-10-31):** the margin is now the config key `sun_hub_clearance_multiple` (4 in every type with this rule, SSPG and CPG included; 5 in IDSPG, its CAD value), read by the CAD code and the mass code; value-identical; `tests/test_sun_hub_clearance.py`.
3. ICPG driver dimensions: Input or Fixed.
4. Names for the new type-specific keys (ISSPG, INSSPG, INDSPG constants).
5. Whether to fix the bug-18 pattern (`module_b` / `module_s`) in each type during its classification
   (recommended, value-identical, as CPG).
