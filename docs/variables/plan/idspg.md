# IDSPG: variable classification plan

Part of [the plan for all actuators](../PLAN.md). Survey only: nothing in the code, config or CAD output changes on this branch.

## Inventory

- **CAD interface:** `idspg_equations_onshape.txt`, **198 variables**; other files: `idspg_equations.txt` (198)
- **Code:** `internaldoubleStagePlanetaryActuator` in `ActuatorandGearbox_IDSPG.py` (lines 166-2170)
- **Config:** `idspg_params.json`, block(s) read: `idspg_design_parameters_3DP`; search bounds `idspg_optimization_parameters`; gear standard / MIT factors from `idspg_motor_config.json`; driver: `OdrivePro`
- **Survey draft:** dependent 88, fixed 78, input 24, optimisation 8; 1 names also in SSPG / CPG; 35 alias names (same value written under a second name); 2 flagged by the survey

## Special cases (frameless outrunner, double stage)

| Variable(s) | What the code does | Proposed classification |
|---|---|---|
| `a1_*` / `a2_*` | two stages, as DSPG; plus un-prefixed motor names (`Rotor_*`, `Stator_*`, `rotor_*`, `bearing_retainer_thickness`, …) | one entry per Onshape name |
| **35 alias pairs** | same attribute under both prefixes (e.g. `a1_Ns2` = `a2_Ns`, `a2_Nr1` = `a1_Nr`) | identical classification, `alias_of` (as DSPG) |
| stage-2 `Ns`, `Np`, `module`, `num_planet` | assigned twice (L236-239 and L636-639, same source) | Optimisation (the survey's "formula" is due to the double assignment) |
| `a1_Nr`, `a2_Nr` | `Ns + 2·Np` per stage | Dependent / implicit constraint |
| `a1_ring_OD` | **= `Stator_ID`** (the stage-1 ring fits the stator bore) | Dependent / formula (copy of an input) |
| `a2_ring_OD` | `Nr2·module2 + 2·ring_radial_thickness` | Dependent / formula |
| `a1_fw_s_used` | a floor rule (`a1_fw_s_used_min`) | Dependent / formula (two-case) |
| `a2_fw_s_used`, `shortfall`, `a1_/a2_ring_gear_relation` | axial-fill rules that make the two stages fill the rotor height | Dependent / formula; read in detail during the work (L540-560, L750-765) |
| stage-1 widths | MIT stress rule; **ISSUES bug 14** (IDSPG stage-1 wide 3D-printed gears, still open) | Dependent / stress rule |
| `a2_sun_coupler_hub_thickness` | writer `getattr(self, "sun_coupler_hub_thickness1", "N/A")` (stage-1 value) | alias (as DSPG) |

## Hard-coded numbers (medium)

| Where | Number | Note |
|---|---|---|
| `a1_/a2_sun_hub_dia` (CAD L564) | **5** (`1.5 × 5`) | **the mass code uses `1.5 × 4`** (L1839): CAD / mass mismatch (new bug); shared `sun_hub_dia` margin item |
| planet-bearing minimum per stage (L1620-1625) | 2/3 | `planet_bearing_gap` (one key or per stage) |
| mass code: casing margins (`1.5 × 4`, `× 2.5`), bolt structure (8, 3 mm), retainer (`× 1.5`, `× 3`), extra bearing masses (2 × 6 g) | various | mass-only list |

## Config (`idspg_params.json`)
- `idspg_design_parameters` (29 keys): **not read** → unused block.
- Code-only keys of `idspg_design_parameters_3DP` (91 keys): `sCarrierExtrusion*_Stg1/2`, `planetMinDistanceMM`, `Motor_case_thickness`, `clearance_case_mount_holes_shell_thickness`, `output_mounti…` (full list in the table below).
- Config file for the gear standard: `idspg_motor_config.json`.

## Test plan
- Tooling: alias pairs (as DSPG); one Onshape and one plain file with the same 198 names.
- Setter for both stages; RO100 / RO80; 2 golden designs.
- Extra gear sets for the axial-fill rules (both branches), RO80 (CAD 6: stage-2 parts don't move).

## Risks / notes
- The axial-fill rules are the least clear part of any type; expect medium confidence there.
- Effort: ~2 h.

## Survey draft: every variable

Automatic first pass from the code (the special cases above take precedence). Category guesses come from the source of each value; *flags* mark hard-coded numbers, several assignments or a writer expression. The final category, sub-type, `depends_on`, confidence and reason are set during the classification itself.

| # | Variable | Draft category / sub-type | Conf. | Line | Code | Flags | SSPG / CPG |
|---|---|---|---|---|---|---|---|
| 1 | `a1_Ns` | optimisation / teeth | high | 231 | `self.internaldoubleStagePlanetaryGearbox.Stage1.Ns` |  |  |
| 2 | `a1_Np` | optimisation / teeth | high | 232 | `self.internaldoubleStagePlanetaryGearbox.Stage1.Np` |  |  |
| 3 | `a1_Nr` | dependent / formula | high | 347 | `self.Ns1 + 2 * self.Np1` |  |  |
| 4 | `a1_num_planet` | optimisation / planets | high | 233 | `self.internaldoubleStagePlanetaryGearbox.Stage1.numPlanet` |  |  |
| 5 | `a1_module` | optimisation / module | high | 234 | `self.internaldoubleStagePlanetaryGearbox.Stage1.module` |  |  |
| 6 | `a1_pressure_angle` | fixed / gear standard | high | 245 | `self.internaldoubleStagePlanetaryGearbox.Stage1.getPressureAngleRad() * 180 / np.pi` |  |  |
| 7 | `a1_motor_OD` | input / motor | high | 290 | `self.motorDiaMM` |  |  |
| 8 | `a1_motor_height` | input / motor | high | 291 | `self.motorLengthMM` |  |  |
| 9 | `a1_h_a` | dependent / formula | high | 348 | `1 * self.module1` |  |  |
| 10 | `a1_h_b` | dependent / formula | high | 350 | `1.25 * self.module1` |  |  |
| 11 | `a1_h_f` | dependent / formula | high | 349 | `1.25 * self.module1` |  |  |
| 12 | `a1_clr_tip_root` | dependent / formula | high | 352 | `self.h_f1 - self.h_a1` |  |  |
| 13 | `a1_dp_s` | dependent / formula | high | 355 | `self.module1 * self.Ns1` |  |  |
| 14 | `a1_db_s` | dependent / formula | high | 356 | `self.dp_s1 * np.cos(np.deg2rad(self.pressure_angle))` |  |  |
| 15 | `a1_fw_s_calc` | dependent / stress rule (face width) | high | 241 | `self.internaldoubleStagePlanetaryGearbox.Stage1.fwSunMM` |  |  |
| 16 | `a1_alpha_s` | dependent / formula | high | 357 | `np.sqrt(self.dp_s1 ** 2 - self.db_s1 ** 2) / self.db_s1 * 180 / np.pi - self.pressure_angle` |  |  |
| 17 | `a1_beta_s` | dependent / formula | high | 358 | `(360 / (4 * self.Ns1) - self.alpha_s1) * 2` |  |  |
| 18 | `a1_dp_p` | dependent / formula | high | 361 | `self.module1 * self.Np1` |  |  |
| 19 | `a1_db_p` | dependent / formula | high | 362 | `self.dp_p1 * np.cos(np.deg2rad(self.pressure_angle))` |  |  |
| 20 | `a1_fw_p` | dependent / formula | high | 351 | `self.fw_r1` |  |  |
| 21 | `a1_alpha_p` | dependent / formula | high | 363 | `np.sqrt(self.dp_p1 ** 2 - self.db_p1 ** 2) / self.db_p1 * 180 / np.pi - self.pressure_angle` |  |  |
| 22 | `a1_beta_p` | dependent / formula | high | 364 | `(360 / (4 * self.Np1) - self.alpha_p1) * 2` |  |  |
| 23 | `a1_dp_r` | dependent / formula | high | 367 | `self.module1 * self.Nr1` |  |  |
| 24 | `a1_db_r` | dependent / formula | high | 368 | `self.dp_r1 * np.cos(np.deg2rad(self.pressure_angle))` |  |  |
| 25 | `a1_fw_r` | dependent / stress rule (face width) | high | 242 | `self.internaldoubleStagePlanetaryGearbox.Stage1.fwRingMM` |  |  |
| 26 | `a1_alpha_r` | dependent / formula | high | 369 | `np.sqrt(self.dp_r1 ** 2 - self.db_r1 ** 2) / self.db_r1 * 180 / np.pi - self.pressure_angle` |  |  |
| 27 | `a1_beta_r` | dependent / formula | high | 370 | `(360 / (4 * self.Nr1) + self.alpha_r1) * 2` |  |  |
| 28 | `a1_bearing_ID` | dependent / lookup (bearing) | high | 379 | `Bearing1.getBearingIDMM()` |  |  |
| 29 | `a1_bearing_OD` | dependent / lookup (bearing) | high | 380 | `Bearing1.getBearingODMM()` |  |  |
| 30 | `a1_bearing_height` | dependent / lookup (bearing) | high | 381 | `Bearing1.getBearingWidthMM()` |  |  |
| 31 | `a1_clearance_planet` | fixed / config | high | 247, 646 | `self.design_params["clearance_planet"] ‖ self.design_params["clearance_planet"]` | 2 assignments (two-case rule or reassigned) |  |
| 32 | `a1_sec_carrier_thickness` | fixed / config | high | 254 | `self.design_params["sec_carrier_thickness1"]` |  |  |
| 33 | `a1_sun_coupler_hub_thickness` | fixed / config | high | 255 | `self.design_params["sun_coupler_hub_thickness1"]` |  |  |
| 34 | `a1_clearance_sun_coupler_sec_carrier` | fixed / config | high | 256, 648 | `self.design_params["clearance_sun_coupler_sec_carrier"] ‖ self.design_params["clearance_sun_coupler_sec_carrie…` | 2 assignments (two-case rule or reassigned) |  |
| 35 | `a1_ring_radial_thickness` | fixed / config | high | 253, 651 | `self.design_params["ring_radial_thickness"] ‖ self.design_params["ring_radial_thickness"]` | 2 assignments (two-case rule or reassigned) |  |
| 36 | `a1_ring_OD` | dependent / formula | high | 391 | `self.Stator_ID` |  |  |
| 37 | `a1_pattern_offset_from_motor_case_OD_base` | fixed / config | high | 572 | `self.design_params["pattern_offset_from_motor_case_OD_base"]` |  |  |
| 38 | `a1_pattern_bulge_dia` | fixed / config | high | 573 | `self.design_params["pattern_bulge_dia"]` |  |  |
| 39 | `a1_pattern_num_bulge` | fixed / config | high | 574 | `self.design_params["pattern_num_bulge"]` |  |  |
| 40 | `a1_pattern_depth` | fixed / config | high | 575 | `self.design_params["pattern_depth"]` |  |  |
| 41 | `a1_planet_pin_bolt_dia` | fixed / config | high | 586 | `self.design_params["planet_pin_bolt_dia1"]` |  |  |
| 42 | `a1_planet_pin_socket_head_dia` | dependent / lookup (bolt/nut) | high | 597 | `planet_pin_bolt1.bolt_head_dia` |  |  |
| 43 | `a1_carrier_PCD` | dependent / formula | high | 561 | `(self.Np1 + self.Ns1) * self.module1` |  |  |
| 44 | `a1_planet_shaft_dia` | fixed / config | high | 577 | `self.design_params["planet_shaft_dia1"]` |  |  |
| 45 | `a1_planet_shaft_step_offset` | fixed / config | high | 264 | `self.design_params["planet_shaft_step_offset"]` |  |  |
| 46 | `a1_carrier_trapezoidal_support_sun_offset` | fixed / config | high | 578 | `self.design_params["carrier_trapezoidal_support_sun_offset1"]` |  |  |
| 47 | `a1_carrier_trapezoidal_support_hole_PCD_offset_bearing_ID` | fixed / config | high | 579 | `self.design_params["carrier_trapezoidal_support_hole_PCD_offset_bearing_ID1"]` |  |  |
| 48 | `a1_carrier_trapezoidal_support_hole_dia` | fixed / config | high | 587 | `self.design_params["carrier_trapezoidal_support_hole_dia1"]` |  |  |
| 49 | `a1_carrier_trapezoidal_support_hole_socket_head_dia` | dependent / lookup (bolt/nut) | high | 602 | `carrier_trapezoidal_support_hole_bolt1.bolt_head_dia` |  |  |
| 50 | `a1_carrier_bearing_step_width` | fixed / config | high | 263 | `self.design_params["carrier_bearing_step_width"]` |  |  |
| 51 | `a1_standard_clearance_1_5mm` | fixed / config | high | 250, 649 | `self.design_params["standard_clearance_1_5mm"] ‖ self.design_params["standard_clearance_1_5mm"]` | 2 assignments (two-case rule or reassigned) |  |
| 52 | `a1_standard_fillet_1_5mm` | fixed / config | high | 251, 650 | `self.design_params["standard_fillet_1_5mm"] ‖ self.design_params["standard_fillet_1_5mm"]` | 2 assignments (two-case rule or reassigned) |  |
| 53 | `a1_sun_shaft_bearing_OD` | fixed / config | high | 580 | `self.design_params["sun_shaft_bearing_OD1"]` |  |  |
| 54 | `a1_sun_shaft_bearing_width` | fixed / config | high | 581 | `self.design_params["sun_shaft_bearing_width1"]` |  |  |
| 55 | `a1_standard_bearing_insertion_chamfer` | fixed / config | high | 252 | `self.design_params["standard_bearing_insertion_chamfer"]` |  |  |
| 56 | `a1_carrier_trapezoidal_support_hole_wrench_size` | dependent / lookup (bolt/nut) | high | 603 | `carrier_trapezoidal_support_hole_bolt1.nut_width_across_flats` |  |  |
| 57 | `a1_planet_pin_bolt_wrench_size` | dependent / lookup (bolt/nut) | high | 598 | `planet_pin_bolt1.nut_width_across_flats` |  |  |
| 58 | `a1_planet_bearing_OD` | fixed / config | high | 582 | `self.design_params["planet_bearing_OD1"]` |  |  |
| 59 | `a1_planet_bearing_width` | fixed / config | high | 583 | `self.design_params["planet_bearing_width1"]` |  |  |
| 60 | `a1_planet_bore` | fixed / config | high | 584 | `self.design_params["planet_bore1"]` |  |  |
| 61 | `a1_sun_shaft_bearing_ID` | fixed / config | high | 585 | `self.design_params["sun_shaft_bearing_ID1"]` |  |  |
| 62 | `a1_sun_hub_dia` | dependent / formula | medium | 564 | `self.rotor_mount_hole_PCD + self.rotor_mount_hole_dia + self.standard_clearance_1_5mm * 5` | numbers 5 |  |
| 63 | `a1_sun_central_bolt_dia` | fixed / config | high | 588 | `self.design_params["sun_central_bolt_dia1"]` |  |  |
| 64 | `a1_sun_central_bolt_socket_head_dia` | dependent / lookup (bolt/nut) | high | 607 | `sun_central_bolt1.bolt_head_dia` |  |  |
| 65 | `a1_fw_s_used` | dependent / formula | high | 552 | `a1_fw_s_used_min` |  |  |
| 66 | `a1_Ns2` | dependent / formula | high | 236, 636 | `self.internaldoubleStagePlanetaryGearbox.Stage2.Ns ‖ self.internaldoubleStagePlanetaryGearbox.Stage2.Ns` | 2 assignments (two-case rule or reassigned) |  |
| 67 | `a1_Np2` | dependent / formula | high | 237, 637 | `self.internaldoubleStagePlanetaryGearbox.Stage2.Np ‖ self.internaldoubleStagePlanetaryGearbox.Stage2.Np` | 2 assignments (two-case rule or reassigned) |  |
| 68 | `a1_Nr2` | dependent / formula | high | 686 | `self.Ns2 + 2 * self.Np2` |  |  |
| 69 | `a1_module2` | dependent / formula | high | 238, 638 | `self.internaldoubleStagePlanetaryGearbox.Stage2.module ‖ self.internaldoubleStagePlanetaryGearbox.Stage2.modul…` | 2 assignments (two-case rule or reassigned) |  |
| 70 | `a1_dp_s2` | dependent / formula | high | 696 | `self.module2 * self.Ns2` |  |  |
| 71 | `a1_db_s2` | dependent / formula | high | 700 | `self.dp_s2 * np.cos(np.deg2rad(self.pressure_angle))` |  |  |
| 72 | `a1_fw_s_calc2` | dependent / stress rule (face width) | high | 642 | `self.internaldoubleStagePlanetaryGearbox.Stage2.fwSunMM` |  |  |
| 73 | `a1_alpha_s2` | dependent / formula | high | 705 | `np.sqrt(self.dp_s2**2 - self.db_s2**2) / self.db_s2 * 180 / np.pi - self.pressure_angle` |  |  |
| 74 | `a1_beta_s2` | dependent / formula | high | 708 | `(360 / (4 * self.Ns2) - self.alpha_s2) * 2` |  |  |
| 75 | `a1_fw_s_used2` | dependent / formula | high | 754 | `(self.bearing_retainer_thickness + self.standard_clearance_1_5mm + self.sec_carrier_thickness2 + self.clearanc…` |  |  |
| 76 | `a1_fw_p2` | dependent / formula | high | 687 | `self.fw_r2` |  |  |
| 77 | `a1_tight_clearance_3DP` | fixed / config | high | 248 | `self.design_params["tight_clearance_3DP"]` |  |  |
| 78 | `a1_loose_clearance_3DP` | fixed / config | high | 249 | `self.design_params["loose_clearance_3DP"]` |  |  |
| 79 | `a2_Ns` | dependent / formula | high | 236, 636 | `self.internaldoubleStagePlanetaryGearbox.Stage2.Ns ‖ self.internaldoubleStagePlanetaryGearbox.Stage2.Ns` | 2 assignments (two-case rule or reassigned) |  |
| 80 | `a2_Np` | dependent / formula | high | 237, 637 | `self.internaldoubleStagePlanetaryGearbox.Stage2.Np ‖ self.internaldoubleStagePlanetaryGearbox.Stage2.Np` | 2 assignments (two-case rule or reassigned) |  |
| 81 | `a2_Nr` | dependent / formula | high | 686 | `self.Ns2 + 2 * self.Np2` |  |  |
| 82 | `a2_module` | dependent / formula | high | 238, 638 | `self.internaldoubleStagePlanetaryGearbox.Stage2.module ‖ self.internaldoubleStagePlanetaryGearbox.Stage2.modul…` | 2 assignments (two-case rule or reassigned) |  |
| 83 | `a2_pressure_angle` | fixed / gear standard | high | 245 | `self.internaldoubleStagePlanetaryGearbox.Stage1.getPressureAngleRad() * 180 / np.pi` |  |  |
| 84 | `a2_h_a` | dependent / formula | high | 688 | `1 * self.module2` |  |  |
| 85 | `a2_h_f` | dependent / formula | high | 689 | `1.25 * self.module2` |  |  |
| 86 | `a2_clr_tip_root` | dependent / formula | high | 691 | `self.h_f2 - self.h_a2` |  |  |
| 87 | `a2_dp_r` | dependent / formula | high | 695 | `self.module2 * self.Nr2` |  |  |
| 88 | `a2_db_r` | dependent / formula | high | 702 | `self.dp_r2 * np.cos(np.deg2rad(self.pressure_angle))` |  |  |
| 89 | `a2_fw_r` | dependent / stress rule (face width) | high | 643 | `self.internaldoubleStagePlanetaryGearbox.Stage2.fwRingMM` |  |  |
| 90 | `a2_alpha_r` | dependent / formula | high | 707 | `np.sqrt(self.dp_r2**2 - self.db_r2**2) / self.db_r2 * 180 / np.pi - self.pressure_angle` |  |  |
| 91 | `a2_beta_r` | dependent / formula | high | 710 | `(360 / (4 * self.Nr2) + self.alpha_r2) * 2` |  |  |
| 92 | `a2_bearing_ID` | dependent / lookup (bearing) | high | 435, 719 | `Bearing2.getBearingIDMM() ‖ Bearing2.getBearingIDMM()` | 2 assignments (two-case rule or reassigned) |  |
| 93 | `a2_bearing_OD` | dependent / lookup (bearing) | high | 436, 720 | `Bearing2.getBearingODMM() ‖ Bearing2.getBearingODMM()` | 2 assignments (two-case rule or reassigned) |  |
| 94 | `a2_bearing_height` | dependent / lookup (bearing) | high | 437, 721 | `Bearing2.getBearingWidthMM() ‖ Bearing2.getBearingWidthMM()` | 2 assignments (two-case rule or reassigned) |  |
| 95 | `a2_clearance_planet` | fixed / config | high | 247, 646 | `self.design_params["clearance_planet"] ‖ self.design_params["clearance_planet"]` | 2 assignments (two-case rule or reassigned) |  |
| 96 | `a2_output_mounting_hole_dia` | fixed / config | high | 667 | `self.design_params["output_mounting_hole_dia2"]` |  |  |
| 97 | `a2_sec_carrier_thickness` | fixed / config | high | 652 | `self.design_params["sec_carrier_thickness2"]` |  |  |
| 98 | `a2_sun_coupler_hub_thickness` | dependent / formula | high | 963 | `writer: getattr(self, "sun_coupler_hub_thickness1", "N/A")` | writer writes an expression, not one attribute |  |
| 99 | `a2_clearance_sun_coupler_sec_carrier` | fixed / config | high | 256, 648 | `self.design_params["clearance_sun_coupler_sec_carrier"] ‖ self.design_params["clearance_sun_coupler_sec_carrie…` | 2 assignments (two-case rule or reassigned) |  |
| 100 | `a2_motor_OD` | input / motor | high | 290 | `self.motorDiaMM` |  |  |
| 101 | `a2_output_mounting_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 725 | `output_mounting_hole2.nut_width_across_flats` |  |  |
| 102 | `a2_output_mounting_nut_thickness` | dependent / lookup (bolt/nut) | high | 726 | `output_mounting_hole2.nut_thickness` |  |  |
| 103 | `a2_output_mounting_nut_depth` | fixed / config | high | 673 | `self.design_params["output_mounting_nut_depth2"]` |  |  |
| 104 | `a2_ring_radial_thickness` | fixed / config | high | 253, 651 | `self.design_params["ring_radial_thickness"] ‖ self.design_params["ring_radial_thickness"]` | 2 assignments (two-case rule or reassigned) |  |
| 105 | `a2_ring_OD` | dependent / formula | high | 773 | `self.Nr2 * self.module2 + self.ring_radial_thickness * 2` |  |  |
| 106 | `a2_pattern_offset_from_motor_case_OD_base` | fixed / config | high | 572 | `self.design_params["pattern_offset_from_motor_case_OD_base"]` |  |  |
| 107 | `a2_pattern_bulge_dia` | fixed / config | high | 573 | `self.design_params["pattern_bulge_dia"]` |  |  |
| 108 | `a2_pattern_num_bulge` | fixed / config | high | 574 | `self.design_params["pattern_num_bulge"]` |  |  |
| 109 | `a2_pattern_depth` | fixed / config | high | 575 | `self.design_params["pattern_depth"]` |  |  |
| 110 | `a2_motor_height` | input / motor | high | 291 | `self.motorLengthMM` |  |  |
| 111 | `a2_num_planet` | dependent / formula | high | 239, 639 | `self.internaldoubleStagePlanetaryGearbox.Stage2.numPlanet ‖ self.internaldoubleStagePlanetaryGearbox.Stage2.nu…` | 2 assignments (two-case rule or reassigned) |  |
| 112 | `a2_planet_pin_bolt_dia` | fixed / config | high | 668 | `self.design_params["planet_pin_bolt_dia2"]` |  |  |
| 113 | `a2_planet_pin_socket_head_dia` | dependent / lookup (bolt/nut) | high | 730 | `planet_bolt2.bolt_head_dia` |  |  |
| 114 | `a2_carrier_PCD` | dependent / formula | high | 697 | `(self.Np2 + self.Ns2) * self.module2` |  |  |
| 115 | `a2_planet_shaft_dia` | fixed / config | high | 654 | `self.design_params["planet_shaft_dia2"]` |  |  |
| 116 | `a2_fw_p` | dependent / formula | high | 687 | `self.fw_r2` |  |  |
| 117 | `a2_planet_shaft_step_offset` | fixed / config | high | 655 | `self.design_params["planet_shaft_step_offset2"]` |  |  |
| 118 | `a2_carrier_trapezoidal_support_sun_offset` | fixed / config | high | 656 | `self.design_params["carrier_trapezoidal_support_sun_offset2"]` |  |  |
| 119 | `a2_carrier_trapezoidal_support_hole_PCD_offset_bearing_ID` | fixed / config | high | 657 | `self.design_params["carrier_trapezoidal_support_hole_PCD_offset_bearing_ID2"]` |  |  |
| 120 | `a2_carrier_trapezoidal_support_hole_dia` | fixed / config | high | 669 | `self.design_params["carrier_trapezoidal_support_hole_dia2"]` |  |  |
| 121 | `a2_carrier_trapezoidal_support_hole_socket_head_dia` | dependent / lookup (bolt/nut) | high | 735 | `carrier_trapezoidal_support_hole2.bolt_head_dia` |  |  |
| 122 | `a2_carrier_bearing_step_width` | fixed / config | high | 658 | `self.design_params["carrier_bearing_step_width2"]` |  |  |
| 123 | `a2_standard_clearance_1_5mm` | fixed / config | high | 250, 649 | `self.design_params["standard_clearance_1_5mm"] ‖ self.design_params["standard_clearance_1_5mm"]` | 2 assignments (two-case rule or reassigned) |  |
| 124 | `a2_standard_fillet_1_5mm` | fixed / config | high | 251, 650 | `self.design_params["standard_fillet_1_5mm"] ‖ self.design_params["standard_fillet_1_5mm"]` | 2 assignments (two-case rule or reassigned) |  |
| 125 | `a2_sun_shaft_bearing_OD` | fixed / config | high | 659 | `self.design_params["sun_shaft_bearing_OD2"]` |  |  |
| 126 | `a2_sun_shaft_bearing_width` | fixed / config | high | 660 | `self.design_params["sun_shaft_bearing_width2"]` |  |  |
| 127 | `a2_standard_bearing_insertion_chamfer` | fixed / config | high | 252 | `self.design_params["standard_bearing_insertion_chamfer"]` |  |  |
| 128 | `a2_carrier_trapezoidal_support_hole_wrench_size` | dependent / lookup (bolt/nut) | high | 736 | `carrier_trapezoidal_support_hole2.nut_width_across_flats` |  |  |
| 129 | `a2_planet_pin_bolt_wrench_size` | dependent / lookup (bolt/nut) | high | 731 | `planet_bolt2.nut_width_across_flats` |  |  |
| 130 | `a2_h_b` | dependent / formula | high | 690 | `1.25 * self.module2` |  |  |
| 131 | `a2_dp_s` | dependent / formula | high | 696 | `self.module2 * self.Ns2` |  |  |
| 132 | `a2_db_s` | dependent / formula | high | 700 | `self.dp_s2 * np.cos(np.deg2rad(self.pressure_angle))` |  |  |
| 133 | `a2_fw_s_calc` | dependent / stress rule (face width) | high | 642 | `self.internaldoubleStagePlanetaryGearbox.Stage2.fwSunMM` |  |  |
| 134 | `a2_alpha_s` | dependent / formula | high | 705 | `np.sqrt(self.dp_s2**2 - self.db_s2**2) / self.db_s2 * 180 / np.pi - self.pressure_angle` |  |  |
| 135 | `a2_beta_s` | dependent / formula | high | 708 | `(360 / (4 * self.Ns2) - self.alpha_s2) * 2` |  |  |
| 136 | `a2_dp_p` | dependent / formula | high | 694 | `self.module2 * self.Np2` |  |  |
| 137 | `a2_db_p` | dependent / formula | high | 701 | `self.dp_p2 * np.cos(np.deg2rad(self.pressure_angle))` |  |  |
| 138 | `a2_alpha_p` | dependent / formula | high | 706 | `np.sqrt(self.dp_p2**2 - self.db_p2**2) / self.db_p2 * 180 / np.pi - self.pressure_angle` |  |  |
| 139 | `a2_beta_p` | dependent / formula | high | 709 | `(360 / (4 * self.Np2) - self.alpha_p2) * 2` |  |  |
| 140 | `a2_planet_bearing_OD` | fixed / config | high | 661 | `self.design_params["planet_bearing_OD2"]` |  |  |
| 141 | `a2_planet_bearing_width` | fixed / config | high | 662 | `self.design_params["planet_bearing_width2"]` |  |  |
| 142 | `a2_planet_bore` | fixed / config | high | 663 | `self.design_params["planet_bore2"]` |  |  |
| 143 | `a2_sun_shaft_bearing_ID` | fixed / config | high | 664 | `self.design_params["sun_shaft_bearing_ID2"]` |  |  |
| 144 | `a2_sun_hub_dia` | dependent / formula | medium | 564 | `self.rotor_mount_hole_PCD + self.rotor_mount_hole_dia + self.standard_clearance_1_5mm * 5` | numbers 5 |  |
| 145 | `a2_sun_central_bolt_dia` | fixed / config | high | 670 | `self.design_params["sun_central_bolt_dia2"]` |  |  |
| 146 | `a2_sun_central_bolt_socket_head_dia` | dependent / lookup (bolt/nut) | high | 740 | `sun_central_bolt2.bolt_head_dia` |  |  |
| 147 | `a2_fw_s_used` | dependent / formula | high | 754 | `(self.bearing_retainer_thickness + self.standard_clearance_1_5mm + self.sec_carrier_thickness2 + self.clearanc…` |  |  |
| 148 | `a2_Ns1` | optimisation / teeth | high | 231 | `self.internaldoubleStagePlanetaryGearbox.Stage1.Ns` |  |  |
| 149 | `a2_Np1` | optimisation / teeth | high | 232 | `self.internaldoubleStagePlanetaryGearbox.Stage1.Np` |  |  |
| 150 | `a2_Nr1` | dependent / formula | high | 347 | `self.Ns1 + 2 * self.Np1` |  |  |
| 151 | `a2_module1` | optimisation / module | high | 234 | `self.internaldoubleStagePlanetaryGearbox.Stage1.module` |  |  |
| 152 | `a2_bearing1_ID` | dependent / lookup (bearing) | high | 379 | `Bearing1.getBearingIDMM()` |  |  |
| 153 | `a2_bearing1_OD` | dependent / lookup (bearing) | high | 380 | `Bearing1.getBearingODMM()` |  |  |
| 154 | `a2_bearing1_height1` | dependent / lookup (bearing) | high | 381 | `Bearing1.getBearingWidthMM()` |  |  |
| 155 | `a2_num_planet1` | optimisation / planets | high | 233 | `self.internaldoubleStagePlanetaryGearbox.Stage1.numPlanet` |  |  |
| 156 | `a2_tight_clearance_3DP` | fixed / config | high | 248 | `self.design_params["tight_clearance_3DP"]` |  |  |
| 157 | `a2_loose_clearance_3DP` | fixed / config | high | 249 | `self.design_params["loose_clearance_3DP"]` |  |  |
| 158 | `Rotor_ID` | input / motor | high | 304 | `self.motor.rotor_ID` |  |  |
| 159 | `Rotor_OD` | input / motor | high | 305 | `self.motor.motor_OD` |  |  |
| 160 | `Rotor_bottom_ID` | input / motor | high | 306 | `self.motor.motor_rotor_base_ID` |  |  |
| 161 | `Rotor_csk_head_height` | input / motor | high | 307 | `self.motor.rotorCSKHeadHeightMM` |  |  |
| 162 | `Rotor_csk_head_upper_dia` | input / motor | high | 308 | `self.motor.rotorCSKHeadUpperDiaMM` |  |  |
| 163 | `Rotor_height` | input / motor | high | 309 | `self.motor.rotor_height` |  |  |
| 164 | `Stator_ID` | input / motor | high | 310 | `self.motor.stator_ID` |  |  |
| 165 | `Stator_OD` | input / motor | high | 311 | `self.motor.stator_OD` |  |  |
| 166 | `Stator_height` | input / motor | high | 312 | `self.motor.stator_height` |  |  |
| 167 | `Stator_mounting_holes_PCD` | input / motor | high | 313 | `self.motor.stator_hole_PCD` |  |  |
| 168 | `rotor_mount_hole_PCD` | input / motor | high | 314 | `self.motor.motor_rotor_hole_PCD` |  |  |
| 169 | `rotor_mount_hole_dia` | input / motor | high | 315 | `self.motor.motor_rotor_hole_dia` |  |  |
| 170 | `rotor_mount_hole_num` | input / motor | high | 316 | `self.motor.motor_rotor_hole_num` |  |  |
| 171 | `rotor_bottom_thickness` | input / motor | high | 317 | `self.motor.motor_rotor_base_thickness` |  |  |
| 172 | `stator_mounitng_holes_head_socket_dia` | input / motor | high | 318 | `self.motor.stator_mounitng_holes_head_socket_dia` |  |  |
| 173 | `stator_mounting_hole_num` | input / motor | high | 319 | `self.motor.stator_hole_num` |  |  |
| 174 | `stator_mounting_holes_dia` | input / motor | high | 320 | `self.motor.stator_hole_dia` |  |  |
| 175 | `stator_mounting_plate_OD` | input / motor | high | 321 | `self.motor.motor_stator_extrusion_dia` |  |  |
| 176 | `stator_rotor_top_offset` | input / motor | high | 322 | `self.motor.stator_top_rotor_top_offset` |  |  |
| 177 | `motor_stator_extrusion_depth` | input / motor | high | 323 | `self.motor.motor_stator_extrusion_depth` |  |  |
| 178 | `a1_sun_bottom_casing_bearing_ID` | fixed / config | high | 270 | `self.design_params["a1_sun_bottom_casing_bearing_ID"]` |  |  |
| 179 | `a1_sun_bottom_casing_bearing_OD` | fixed / config | high | 271 | `self.design_params["a1_sun_bottom_casing_bearing_OD"]` |  |  |
| 180 | `a1_sun_bottom_casing_bearing_height` | fixed / config | high | 272 | `self.design_params["a1_sun_bottom_casing_bearing_height"]` |  |  |
| 181 | `a1_sun_carrier_bearing_ID` | fixed / config | high | 273 | `self.design_params["a1_sun_carrier_bearing_ID"]` |  |  |
| 182 | `a1_sun_carrier_bearing_OD` | fixed / config | high | 274 | `self.design_params["a1_sun_carrier_bearing_OD"]` |  |  |
| 183 | `a1_sun_carrier_bearing_height` | fixed / config | high | 275 | `self.design_params["a1_sun_carrier_bearing_height"]` |  |  |
| 184 | `bearing_retainer_hole_dia` | fixed / config | high | 276 | `self.design_params["bearing_retainer_hole_dia"]` |  |  |
| 185 | `bearing_retainer_hole_num` | fixed / config | high | 277 | `self.design_params["bearing_retainer_hole_num"]` |  |  |
| 186 | `bearing_retainer_hole_wrench_nut_size` | fixed / config | high | 278 | `self.design_params["bearing_retainer_hole_wrench_nut_size"]` |  |  |
| 187 | `a2_bearing_retainer_hole_dia` | fixed / config | high | 678 | `self.design_params["a2_bearing_retainer_hole_dia"]` |  |  |
| 188 | `a2_bearing_retainer_hole_num` | fixed / config | high | 679 | `self.design_params["a2_bearing_retainer_hole_num"]` |  |  |
| 189 | `a2_bearing_retainer_nut_wrench_size` | fixed / config | high | 680 | `self.design_params["a2_bearing_retainer_nut_wrench_size"]` |  |  |
| 190 | `a2_bearing_retainer_wrench_height` | fixed / config | high | 681 | `self.design_params["a2_bearing_retainer_wrench_height"]` |  |  |
| 191 | `bearing_retainer_thickness` | fixed / config | high | 279, 665 | `self.design_params["bearing_retainer_thickness"] ‖ self.design_params["bearing_retainer_thickness"]` | 2 assignments (two-case rule or reassigned) | sspg: fixed, cpg: fixed |
| 192 | `motor_casing_thickness` | fixed / config | high | 265 | `self.design_params["motor_casing_thickness"]` |  |  |
| 193 | `a1_ring_gear_relation` | dependent / formula | high | 553 | `a1_ring_gear_relation` |  |  |
| 194 | `a2_ring_gear_relation` | dependent / formula | high | 761 | `( self.fw_s1_used + self.standard_clearance_1_5mm + self.carrier_bearing_step_width + self.bearing1_height + s…` |  |  |
| 195 | `a1_ring_gear_thickness_mounting_casing` | fixed / config | high | 280 | `self.design_params["a1_ring_gear_thickness_mounting_casing"]` |  |  |
| 196 | `a2_ring_gear_thickness_mounting_casing` | fixed / config | high | 676 | `self.design_params["a2_ring_gear_thickness_mounting_casing"]` |  |  |
| 197 | `a1_sun_gear_rotor_nut_depth` | fixed / config | high | 281 | `self.design_params["a1_sun_gear_rotor_nut_depth"]` |  |  |
| 198 | `a1_sun_gear_rotor_nut_wrench_size` | fixed / config | high | 282 | `self.design_params["a1_sun_gear_rotor_nut_wrench_size"]` |  |  |

## Config accounting

| Block | Keys | Read by this type | Read but not written to the CAD | Never used |
|---|---|---|---|---|
| `idspg_design_parameters` | 29 | **no** | sCarrierExtrusionDiaMM_Stg1, sCarrierExtrusionClearanceMM_Stg1, sCarrierExtrusionDiaMM_Stg2, sCarrierExtrusionClearanceMM_Stg2, planetMinDistanceMM | Ring1RadialWidthMM, Ring2RadialWidthMM, carrier1ShaftHeightMM, mainCase2AttachmentHeightMM, baseThicknessMM, sCarrierThicknessMM, mainCoverThicknessMM, planetBoreMM, sunBoreMM, couplerRadiusMM, couplerThicknessMM, couplerShaftHeightMM, CarrierRadialThicknessClearance1, CarrierRadialThicknessClearance2, carrierInnerDiaClearanceMM1, sCarrierInnerDiaClearanceMM1, carrierInnerDiaClearanceMM2, sCarrier… |
| `idspg_optimization_parameters` | 14 | yes | GEAR_RATIO_MIN, GEAR_RATIO_MAX, GEAR_RATIO_STEP, MODULE_STAGE1_MIN, MODULE_STAGE1_MAX, MODULE_STAGE2_MIN, MODULE_STAGE2_MAX, NUM_PLANET_STAGE1_MIN, NUM_PLANET_STAGE1_MAX, NUM_PLANET_STAGE2_MIN, NUM_PLANET_STAGE2_MAX, NUM_TEETH_SUN_MIN, NUM_TEETH_PLANET_MIN, MAX_GB_DIA_MULT_FACTOR | — |
| `idspg_design_parameters_3DP` | 91 | yes | sCarrierExtrusionDiaMM_Stg1, sCarrierExtrusionClearanceMM_Stg1, sCarrierExtrusionDiaMM_Stg2, sCarrierExtrusionClearanceMM_Stg2, planetMinDistanceMM, Motor_case_thickness, clearance_case_mount_holes_shell_thickness, output_mounting_hole_dia1, case_mounting_hole_dia, case_mounting_bolt_depth, case_mounting_surface_height, central_hole_offset_from_motor_mount_PCD, base_plate_thickness, air_flow_hole_… | bearing_retainer_thickness1, bearing_retainer_thickness2 |


## Result (classification done)

Spec: [`config_files/variables/idspg_variables.json`](../../../config_files/variables/idspg_variables.json), page [`docs/variables/idspg.md`](../idspg.md) (generated). Tests: the generic `tests/test_variable_categories.py` (IDSPG registered in `tests/variable_helpers.py`, with the two-stage setter of DSPG) and `tests/test_variable_categories_idspg.py`.

**Counts (CAD variables, 198):** input 20, optimisation 15, fixed 79, dependent 84 (54 formula, 21 lookup, 5 stress rule, 4 implicit constraint). 36 names are aliases of another name (the plan said 35: the extra one is `a2_sun_coupler_hub_thickness`, written with `getattr(self, "sun_coupler_hub_thickness1", "N/A")`, the stage-1 value). The plain `idspg_equations.txt` carries the same 198 names, so no stage-file tooling is needed. **Code-only values: 51** (fixed 45, input 4, dependent 2: the two `maxGearboxDiameter` values), including every 3DP config key the CAD does not use. Confidence: 240 high, 9 medium, 0 low.

**Medium-confidence entries**
- `a1_sun_hub_dia`, `a2_sun_hub_dia` (Dependent / formula): the rotor's mount-hole circle plus hole diameter plus a hard-coded `5 x standard_clearance_1_5mm`; the mass code uses `4` (CAD and mass disagree, to be logged); the shared sun-hub margin item the plan still has to decide.
- `a1_fw_s_used`, `a2_fw_s_used` (and its alias `a1_fw_s_used2`), `a1_ring_gear_relation`, `a2_ring_gear_relation` (Dependent / formula): the axial-fill rules that make the two stages fill the rotor height; the two `ring_gear_relation` values are written for the CAD and not used by the code.
- `shortfall` (code-only, Fixed): always 0; the code sets it only in a disabled axial-fill case and the stage-2 sun length adds it. Its source is a constant in the code.
- `planet_bearing_gap` (code-only, Fixed): one key for both stages; the plan leaves open whether it should be one per stage.

**Config key added** to `idspg_design_parameters_3DP` in `idspg_params.json` (shared name, value that keeps every output bit-identical): `planet_bearing_gap` = 1.0 (was `standard_clearance_1_5mm * 2 / 3` in both stages; 1.5 * 2 / 3 is exactly 1.0), in `mitStressAnalysisMinFacewidth`. The other shared keys have no counterpart (no motor-case clearance rule, no `bearing_mount_thickness`). A test shows `planet_bearing_gap` drives exactly its CAD variables in both stages.

**Shared tooling changed:** `tests/variable_helpers.py` (IDSPG entry), `tools/variables/render.py` (a source can be a constant in the code).

**Results:** `python tests/golden/golden.py check`: All 58 cases match the baseline. `python -m pytest -q`: 1107 passed. No `CADs/` file, no golden baseline touched.

**Open questions**
1. One `planet_bearing_gap` for both stages, or one per stage (plan decision 1).
2. The sun-hub margin: 5 in the CAD, 4 in the mass code; and the shared key (plan decision 2). **Done (2026-10-31):** the margin is now the config key `sun_hub_clearance_multiple` (4 in every type with this rule, SSPG and CPG included; 5 in IDSPG, its CAD value), read by the CAD code and the mass code; value-identical; `tests/test_sun_hub_clearance.py`. The mass code now weighs the CAD's hub too (ISSUES bug 23: 1.825 -> 1.826 kg 3dp, 2.429 -> 2.431 kg metal on the golden design).
3. The axial-fill rules (`fw_s_used`, `ring_gear_relation`) are the least clear part; they are plain formulas on the code's locals and are kept medium. ISSUES bug 14 (IDSPG stage-1 wide 3D-printed gears) is still open and affects the stage-1 stress widths, not their classification.
4. `a1_ring_OD` is a copy of `Stator_ID` (an input): the stage-1 ring fits the stator bore.
5. `idspg_design_parameters` (29 keys) is never read; listed as an unused block. The RO80 case where stage-2 parts do not move (CAD 6) concerns the Onshape model.
