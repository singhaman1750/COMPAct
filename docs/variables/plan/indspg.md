# INDSPG: variable classification plan

Part of [the plan for all actuators](../PLAN.md). Survey only: nothing in the code, config or CAD output changes on this branch.

## Inventory

- **CAD interface:** `indspg_equations_onshape.txt`, **210 variables**; other files: `indspg_equations.txt` (210)
- **Code:** `inrunnerdoubleStageActuator` in `ActuatorandGearbox_INDSPG.py` (lines 183-2097)
- **Config:** `indspg_params.json`, block(s) read: `indspg_design_parameters_3DP`; search bounds `indspg_optimization_parameters`; gear standard / MIT factors from `indspg_motor_config.json`; driver: `omit`
- **Survey draft:** dependent 72, fixed 111, input 12, optimisation 15; 1 names also in SSPG / CPG; 42 alias names (same value written under a second name); 7 flagged by the survey

## Special cases (frameless inrunner, double stage)

| Variable(s) | What the code does | Proposed classification |
|---|---|---|
| `a1_*` / `a2_*` | two stages, as DSPG / IDSPG; un-prefixed motor and casing names (`stator_*`, `Stator_*`, `Rotor_*`, `needle_*`, …) | one entry per Onshape name |
| **42 alias pairs** | same attribute under both prefixes | identical classification, `alias_of` |
| `a1_bearing_ID/OD/height` (+ `a2_bearing1_*` aliases) | **hard-coded 38.1 / 47.625 / 4.763 mm** (an inch thin-section bearing); the mass code repeats it with its mass 22.7 g (L1593-1596) | Fixed / hard-coded, **medium**; propose config keys (e.g. `a1_bearing_ID/OD/height/massKG`) |
| `a1_sun_bottom_casing_bearing_*` | **looked up, then overwritten by config** (L413-421) | Fixed / config (dead lookup noted) |
| `a1_fw_p` | **config `fw_p_1_fix`** (a fixed stage-1 planet width, not the stress rule) | Fixed / config |
| `a1_fw_r`, `a1_fw_s_calc`, `a2_fw_r`, `a2_fw_s_calc` | MIT stress rule per stage, SSPG-style bearing minimum | Dependent / stress rule |
| `a1_fw_s_used` | two-case (L451 / L454) with `1.5 × 2 + 1.5 × 0.5` | Dependent / formula, **medium** (× 0.5, × 2) |
| `a2_fw_s_used` | carrier + clearances + loose clearance − 1.5 (two assignments L657 / L659) | Dependent / formula |
| `sun_hub_dia` (`a1_` / `a2_`) | `rotor_ID − 2 × (1.5 + 2)` | Dependent / formula, **medium** (hard-coded 2) |
| `rotor_mount_hole_PCD` | `rotor_ID − CSK head − 2 × 2 − 1.5` | Dependent / formula, **medium** (hard-coded 2 × 2) |
| `a2_sun_coupler_hub_thickness` | writer `getattr(… "sun_coupler_hub_thickness1" …)` | alias (as DSPG) |
| per-stage keys | `a2_bearing_retainer_*`, `stator_casing_thickness`, … from the config | Fixed / config |

## Hard-coded numbers (medium)

| Where | Number | Proposed key |
|---|---|---|
| stage-1 output bearing (CAD L424-426; mass L1593-1596) | 38.1, 47.625, 4.763, 0.0227 kg | new keys for the stage-1 bearing |
| `sun_hub_dia` (L457) | 2 | review (new key or geometry) |
| `rotor_mount_hole_PCD` (L356) | 2 × 2 | review |
| `a1_fw_s_used` (L451) | × 2, × 0.5 | review |
| planet-bearing minimum per stage (L1498-1503) | 2/3 | `planet_bearing_gap` |
| mass code: casing features (`× 2.5`, `× 3`, 9 / 5.5 mm bosses), `fw_carrier = fw_p1 − clearance_planet × 4`, rotor coupler (5), needle-bearing masses (3 g) | various | mass-only list; ISSUES bug 11 (rotor coupler ID) is INDSPG |

## Config (`indspg_params.json`)
- `indspg_design_parameters` (29 keys): **not read** → unused block.
- Code-only keys of `indspg_design_parameters_3DP` (105 keys): `sCarrierExtrusion*_Stg1/2`, `planetMinDistanceMM`, `central_hol…` (full list in the table).
- Config file: `indspg_motor_config.json`.

## Test plan
- Tooling: alias pairs; one Onshape and one plain file (210 names each).
- Setter for both stages; RI100 / RI80; 3 golden designs; note ISSUES bug 13 (crashes where it has no design: build the test designs from golden opt parameters only).

## Risks / notes
- Most hard-coded constants of any type (the stage-1 bearing). Effort: ~2 h.

## Survey draft: every variable

Automatic first pass from the code (the special cases above take precedence). Category guesses come from the source of each value; *flags* mark hard-coded numbers, several assignments or a writer expression. The final category, sub-type, `depends_on`, confidence and reason are set during the classification itself.

| # | Variable | Draft category / sub-type | Conf. | Line | Code | Flags | SSPG / CPG |
|---|---|---|---|---|---|---|---|
| 1 | `a1_Ns` | optimisation / teeth | high | 250 | `self.inrunnerdoubleStagePlanetaryGearbox.Stage1.Ns` |  |  |
| 2 | `a1_Np` | optimisation / teeth | high | 251 | `self.inrunnerdoubleStagePlanetaryGearbox.Stage1.Np` |  |  |
| 3 | `a1_Nr` | dependent / formula | high | 380 | `self.Ns1 + 2 * self.Np1` |  |  |
| 4 | `a1_num_planet` | optimisation / planets | high | 252 | `self.inrunnerdoubleStagePlanetaryGearbox.Stage1.numPlanet` |  |  |
| 5 | `a1_module` | optimisation / module | high | 253 | `self.inrunnerdoubleStagePlanetaryGearbox.Stage1.module` |  |  |
| 6 | `a1_pressure_angle` | fixed / gear standard | high | 259 | `self.inrunnerdoubleStagePlanetaryGearbox.Stage1.getPressureAngleRad() * 180 / np.pi` |  |  |
| 7 | `a1_h_a` | dependent / formula | high | 381 | `1 * self.module1` |  |  |
| 8 | `a1_h_b` | dependent / formula | high | 383 | `1.25 * self.module1` |  |  |
| 9 | `a1_h_f` | dependent / formula | high | 382 | `1.25 * self.module1` |  |  |
| 10 | `a1_clr_tip_root` | dependent / formula | high | 385 | `self.h_f1 - self.h_a1` |  |  |
| 11 | `a1_dp_s` | dependent / formula | high | 388 | `self.module1 * self.Ns1` |  |  |
| 12 | `a1_db_s` | dependent / formula | high | 389 | `self.dp_s1 * np.cos(np.deg2rad(self.pressure_angle))` |  |  |
| 13 | `a1_fw_s_calc` | dependent / stress rule (face width) | high | 255 | `self.inrunnerdoubleStagePlanetaryGearbox.Stage1.fwSunMM` |  |  |
| 14 | `a1_alpha_s` | dependent / formula | high | 390 | `np.sqrt(self.dp_s1 ** 2 - self.db_s1 ** 2) / self.db_s1 * 180 / np.pi - self.pressure_angle` |  |  |
| 15 | `a1_beta_s` | dependent / formula | high | 391 | `(360 / (4 * self.Ns1) - self.alpha_s1) * 2` |  |  |
| 16 | `a1_dp_p` | dependent / formula | high | 394 | `self.module1 * self.Np1` |  |  |
| 17 | `a1_db_p` | dependent / formula | high | 395 | `self.dp_p1 * np.cos(np.deg2rad(self.pressure_angle))` |  |  |
| 18 | `a1_fw_p` | fixed / config | high | 308 | `self.design_params["fw_p_1_fix"]` |  |  |
| 19 | `a1_alpha_p` | dependent / formula | high | 396 | `np.sqrt(self.dp_p1 ** 2 - self.db_p1 ** 2) / self.db_p1 * 180 / np.pi - self.pressure_angle` |  |  |
| 20 | `a1_beta_p` | dependent / formula | high | 397 | `(360 / (4 * self.Np1) - self.alpha_p1) * 2` |  |  |
| 21 | `a1_dp_r` | dependent / formula | high | 400 | `self.module1 * self.Nr1` |  |  |
| 22 | `a1_db_r` | dependent / formula | high | 401 | `self.dp_r1 * np.cos(np.deg2rad(self.pressure_angle))` |  |  |
| 23 | `a1_fw_r` | dependent / stress rule (face width) | high | 256, 1532 | `self.inrunnerdoubleStagePlanetaryGearbox.Stage1.fwRingMM ‖ self.inrunnerdoubleStagePlanetaryGearbox.Stage1.fwR…` | 2 assignments (two-case rule or reassigned) |  |
| 24 | `a1_alpha_r` | dependent / formula | high | 402 | `np.sqrt(self.dp_r1 ** 2 - self.db_r1 ** 2) / self.db_r1 * 180 / np.pi - self.pressure_angle` |  |  |
| 25 | `a1_beta_r` | dependent / formula | high | 403 | `(360 / (4 * self.Nr1) + self.alpha_r1) * 2` |  |  |
| 26 | `a1_bearing_ID` | fixed / hard-coded constant | medium | 424 | `38.1` | value hard-coded in the code; numbers 38.1 |  |
| 27 | `a1_bearing_OD` | fixed / hard-coded constant | medium | 425 | `47.625` | value hard-coded in the code; numbers 47.625 |  |
| 28 | `a1_bearing_height` | fixed / hard-coded constant | medium | 426 | `4.763` | value hard-coded in the code; numbers 4.763 |  |
| 29 | `a1_clearance_planet` | fixed / config | high | 261, 537 | `self.design_params["clearance_planet"] ‖ self.design_params["clearance_planet"]` | 2 assignments (two-case rule or reassigned) |  |
| 30 | `a1_case_mounting_hole_dia` | fixed / config | high | 274 | `self.design_params["case_mounting_hole_dia"]` |  |  |
| 31 | `a1_output_mounting_hole_dia` | fixed / config | high | 273 | `self.design_params["output_mounting_hole_dia1"]` |  |  |
| 32 | `a1_clearance_case_mount_holes_shell_thickness` | fixed / config | high | 272 | `self.design_params["clearance_case_mount_holes_shell_thickness"]` |  |  |
| 33 | `a1_sec_carrier_thickness` | fixed / config | high | 268 | `self.design_params["sec_carrier_thickness1"]` |  |  |
| 34 | `a1_sun_coupler_hub_thickness` | fixed / config | high | 269 | `self.design_params["sun_coupler_hub_thickness1"]` |  |  |
| 35 | `a1_clearance_sun_coupler_sec_carrier` | fixed / config | high | 270, 539 | `self.design_params["clearance_sun_coupler_sec_carrier"] ‖ self.design_params["clearance_sun_coupler_sec_carrie…` | 2 assignments (two-case rule or reassigned) |  |
| 36 | `a1_output_mounting_nut_depth` | fixed / config | high | 462 | `self.design_params["output_mounting_nut_depth1"]` |  |  |
| 37 | `a1_case_mounting_bolt_depth` | fixed / config | high | 275 | `self.design_params["case_mounting_bolt_depth"]` |  |  |
| 38 | `a1_ring_radial_thickness` | fixed / config | high | 267, 542 | `self.design_params["ring_radial_thickness"] ‖ self.design_params["ring_radial_thickness"]` | 2 assignments (two-case rule or reassigned) |  |
| 39 | `a1_ring_to_chamfer_clearance` | fixed / config | high | 463 | `self.design_params["ring_to_chamfer_clearance1"]` |  |  |
| 40 | `a1_Motor_case_OD_base_to_chamfer` | fixed / config | high | 464 | `self.design_params["Motor_case_OD_base_to_chamfer"]` |  |  |
| 41 | `a1_pattern_offset_from_motor_case_OD_base` | fixed / config | high | 465 | `self.design_params["pattern_offset_from_motor_case_OD_base"]` |  |  |
| 42 | `a1_pattern_bulge_dia` | fixed / config | high | 466 | `self.design_params["pattern_bulge_dia"]` |  |  |
| 43 | `a1_pattern_num_bulge` | fixed / config | high | 467 | `self.design_params["pattern_num_bulge"]` |  |  |
| 44 | `a1_pattern_depth` | fixed / config | high | 468 | `self.design_params["pattern_depth"]` |  |  |
| 45 | `a1_case_mounting_nut_clearance` | fixed / config | high | 469 | `self.design_params["case_mounting_nut_clearance"]` |  |  |
| 46 | `a1_case_mounting_surface_height` | fixed / config | high | 276 | `self.design_params["case_mounting_surface_height"]` |  |  |
| 47 | `a1_planet_pin_bolt_dia` | fixed / config | high | 479 | `self.design_params["planet_pin_bolt_dia1"]` |  |  |
| 48 | `a1_planet_pin_socket_head_dia` | dependent / lookup (bolt/nut) | high | 490 | `planet_pin_bolt1.bolt_head_dia` |  |  |
| 49 | `a1_carrier_PCD` | dependent / formula | high | 449 | `(self.Np1 + self.Ns1) * self.module1` |  |  |
| 50 | `a1_planet_shaft_dia` | fixed / config | high | 470 | `self.design_params["planet_shaft_dia1"]` |  |  |
| 51 | `a1_planet_shaft_step_offset` | fixed / config | high | 278 | `self.design_params["planet_shaft_step_offset"]` |  |  |
| 52 | `a1_carrier_trapezoidal_support_sun_offset` | fixed / config | high | 471 | `self.design_params["carrier_trapezoidal_support_sun_offset1"]` |  |  |
| 53 | `a1_carrier_trapezoidal_support_hole_PCD_offset_bearing_ID` | fixed / config | high | 472 | `self.design_params["carrier_trapezoidal_support_hole_PCD_offset_bearing_ID1"]` |  |  |
| 54 | `a1_carrier_trapezoidal_support_hole_dia` | fixed / config | high | 480 | `self.design_params["carrier_trapezoidal_support_hole_dia1"]` |  |  |
| 55 | `a1_carrier_trapezoidal_support_hole_socket_head_dia` | dependent / lookup (bolt/nut) | high | 495 | `carrier_trapezoidal_support_hole_bolt1.bolt_head_dia` |  |  |
| 56 | `a1_carrier_bearing_step_width` | fixed / config | high | 277 | `self.design_params["carrier_bearing_step_width"]` |  |  |
| 57 | `a1_standard_clearance_1_5mm` | fixed / config | high | 264, 540 | `self.design_params["standard_clearance_1_5mm"] ‖ self.design_params["standard_clearance_1_5mm"]` | 2 assignments (two-case rule or reassigned) |  |
| 58 | `a1_standard_fillet_1_5mm` | fixed / config | high | 265, 541 | `self.design_params["standard_fillet_1_5mm"] ‖ self.design_params["standard_fillet_1_5mm"]` | 2 assignments (two-case rule or reassigned) |  |
| 59 | `a1_sun_shaft_bearing_OD` | fixed / config | high | 473 | `self.design_params["sun_shaft_bearing_OD1"]` |  |  |
| 60 | `a1_sun_shaft_bearing_width` | fixed / config | high | 474 | `self.design_params["sun_shaft_bearing_width1"]` |  |  |
| 61 | `a1_standard_bearing_insertion_chamfer` | fixed / config | high | 266 | `self.design_params["standard_bearing_insertion_chamfer"]` |  |  |
| 62 | `a1_carrier_trapezoidal_support_hole_wrench_size` | dependent / lookup (bolt/nut) | high | 496 | `carrier_trapezoidal_support_hole_bolt1.nut_width_across_flats` |  |  |
| 63 | `a1_planet_pin_bolt_wrench_size` | dependent / lookup (bolt/nut) | high | 491 | `planet_pin_bolt1.nut_width_across_flats` |  |  |
| 64 | `a1_planet_bearing_OD` | fixed / config | high | 475 | `self.design_params["planet_bearing_OD1"]` |  |  |
| 65 | `a1_planet_bearing_width` | fixed / config | high | 476 | `self.design_params["planet_bearing_width1"]` |  |  |
| 66 | `a1_planet_bore` | fixed / config | high | 477 | `self.design_params["planet_bore1"]` |  |  |
| 67 | `a1_sun_shaft_bearing_ID` | fixed / config | high | 478 | `self.design_params["sun_shaft_bearing_ID1"]` |  |  |
| 68 | `a1_sun_hub_dia` | dependent / formula | high | 457 | `self.rotor_ID - 2 * (self.standard_clearance_1_5mm + 2)` |  |  |
| 69 | `a1_sun_central_bolt_dia` | fixed / config | high | 481 | `self.design_params["sun_central_bolt_dia1"]` |  |  |
| 70 | `a1_sun_central_bolt_socket_head_dia` | dependent / lookup (bolt/nut) | high | 500 | `sun_central_bolt1.bolt_head_dia` |  |  |
| 71 | `a1_fw_s_used` | dependent / formula | medium | 451, 454 | `self.fw_p_1_fix + self.clearance_planet + self.sec_carrier_thickness1 + self.standard_clearance_1_5mm*2 + self…` | 2 assignments (two-case rule or reassigned); numbers 0.5 |  |
| 72 | `a1_bearing_retainer_thickness` | fixed / config | high | 279 | `self.design_params["bearing_retainer_thickness1"]` |  |  |
| 73 | `a1_stg1_stg2_mounting_pattern_width` | fixed / config | high | 564 | `self.design_params["stg1_stg2_mounting_pattern_width"]` |  |  |
| 74 | `a1_stg1_stg2_allen_socket_head_dia` | dependent / lookup (bolt/nut) | high | 649 | `stg1_stg2_mounting_hole.bolt_head_dia` |  |  |
| 75 | `a1_stg1_stg2_mounting_hole_dia` | fixed / config | high | 563 | `self.design_params["stg1_stg2_mounting_hole_dia"]` |  |  |
| 76 | `a1_Ns2` | optimisation / teeth | high | 527 | `self.inrunnerdoubleStagePlanetaryGearbox.Stage2.Ns` |  |  |
| 77 | `a1_Np2` | optimisation / teeth | high | 528 | `self.inrunnerdoubleStagePlanetaryGearbox.Stage2.Np` |  |  |
| 78 | `a1_Nr2` | dependent / formula | high | 590 | `self.Ns2 + 2 * self.Np2` |  |  |
| 79 | `a1_module2` | optimisation / module | high | 529 | `self.inrunnerdoubleStagePlanetaryGearbox.Stage2.module` |  |  |
| 80 | `a1_dp_s2` | dependent / formula | high | 600 | `self.module2 * self.Ns2` |  |  |
| 81 | `a1_db_s2` | dependent / formula | high | 604 | `self.dp_s2 * np.cos(np.deg2rad(self.pressure_angle))` |  |  |
| 82 | `a1_fw_s_calc2` | dependent / stress rule (face width) | high | 533 | `self.inrunnerdoubleStagePlanetaryGearbox.Stage2.fwSunMM` |  |  |
| 83 | `a1_alpha_s2` | dependent / formula | high | 609 | `np.sqrt(self.dp_s2**2 - self.db_s2**2) / self.db_s2 * 180 / np.pi - self.pressure_angle` |  |  |
| 84 | `a1_beta_s2` | dependent / formula | high | 612 | `(360 / (4 * self.Ns2) - self.alpha_s2) * 2` |  |  |
| 85 | `a1_fw_s_used2` | dependent / formula | high | 657, 659 | `self.fw_p2 + self.clearance_planet + self.sec_carrier_thickness2 + self.standard_clearance_1_5mm + self.loose_…` | 2 assignments (two-case rule or reassigned) |  |
| 86 | `a1_fw_p2` | dependent / formula | high | 591 | `self.fw_r2` |  |  |
| 87 | `a1_tight_clearance_3DP` | fixed / config | high | 262 | `self.design_params["tight_clearance_3DP"]` |  |  |
| 88 | `a1_loose_clearance_3DP` | fixed / config | high | 263 | `self.design_params["loose_clearance_3DP"]` |  |  |
| 89 | `a2_Ns` | optimisation / teeth | high | 527 | `self.inrunnerdoubleStagePlanetaryGearbox.Stage2.Ns` |  |  |
| 90 | `a2_Np` | optimisation / teeth | high | 528 | `self.inrunnerdoubleStagePlanetaryGearbox.Stage2.Np` |  |  |
| 91 | `a2_Nr` | dependent / formula | high | 590 | `self.Ns2 + 2 * self.Np2` |  |  |
| 92 | `a2_module` | optimisation / module | high | 529 | `self.inrunnerdoubleStagePlanetaryGearbox.Stage2.module` |  |  |
| 93 | `a2_pressure_angle` | fixed / gear standard | high | 259 | `self.inrunnerdoubleStagePlanetaryGearbox.Stage1.getPressureAngleRad() * 180 / np.pi` |  |  |
| 94 | `a2_h_a` | dependent / formula | high | 592 | `1 * self.module2` |  |  |
| 95 | `a2_h_f` | dependent / formula | high | 593 | `1.25 * self.module2` |  |  |
| 96 | `a2_clr_tip_root` | dependent / formula | high | 595 | `self.h_f2 - self.h_a2` |  |  |
| 97 | `a2_dp_r` | dependent / formula | high | 599 | `self.module2 * self.Nr2` |  |  |
| 98 | `a2_db_r` | dependent / formula | high | 606 | `self.dp_r2 * np.cos(np.deg2rad(self.pressure_angle))` |  |  |
| 99 | `a2_fw_r` | dependent / stress rule (face width) | high | 534, 1533 | `self.inrunnerdoubleStagePlanetaryGearbox.Stage2.fwRingMM ‖ self.inrunnerdoubleStagePlanetaryGearbox.Stage2.fwR…` | 2 assignments (two-case rule or reassigned) |  |
| 100 | `a2_alpha_r` | dependent / formula | high | 611 | `np.sqrt(self.dp_r2**2 - self.db_r2**2) / self.db_r2 * 180 / np.pi - self.pressure_angle` |  |  |
| 101 | `a2_beta_r` | dependent / formula | high | 614 | `(360 / (4 * self.Nr2) + self.alpha_r2) * 2` |  |  |
| 102 | `a2_bearing_ID` | dependent / lookup (bearing) | high | 628 | `Bearing2.getBearingIDMM()` |  |  |
| 103 | `a2_bearing_OD` | dependent / lookup (bearing) | high | 629 | `Bearing2.getBearingODMM()` |  |  |
| 104 | `a2_bearing_height` | dependent / lookup (bearing) | high | 630 | `Bearing2.getBearingWidthMM()` |  |  |
| 105 | `a2_clearance_planet` | fixed / config | high | 261, 537 | `self.design_params["clearance_planet"] ‖ self.design_params["clearance_planet"]` | 2 assignments (two-case rule or reassigned) |  |
| 106 | `a2_case_mounting_hole_dia` | fixed / config | high | 274 | `self.design_params["case_mounting_hole_dia"]` |  |  |
| 107 | `a2_output_mounting_hole_dia` | fixed / config | high | 559 | `self.design_params["output_mounting_hole_dia2"]` |  |  |
| 108 | `a2_clearance_case_mount_holes_shell_thickness` | fixed / config | high | 272 | `self.design_params["clearance_case_mount_holes_shell_thickness"]` |  |  |
| 109 | `a2_sec_carrier_thickness` | fixed / config | high | 543 | `self.design_params["sec_carrier_thickness2"]` |  |  |
| 110 | `a2_sun_coupler_hub_thickness` | dependent / formula | high | 846 | `writer: getattr(self, "sun_coupler_hub_thickness1", "N/A")` | writer writes an expression, not one attribute |  |
| 111 | `a2_clearance_sun_coupler_sec_carrier` | fixed / config | high | 270, 539 | `self.design_params["clearance_sun_coupler_sec_carrier"] ‖ self.design_params["clearance_sun_coupler_sec_carrie…` | 2 assignments (two-case rule or reassigned) |  |
| 112 | `a2_output_mounting_nut_wrench_size` | fixed / config | high | 557 | `self.design_params["a2_output_mounting_nut_wrench_size"]` |  |  |
| 113 | `a2_output_mounting_nut_depth` | fixed / config | high | 565 | `self.design_params["output_mounting_nut_depth2"]` |  |  |
| 114 | `a2_case_mounting_bolt_depth` | fixed / config | high | 275 | `self.design_params["case_mounting_bolt_depth"]` |  |  |
| 115 | `a2_ring_radial_thickness` | fixed / config | high | 267, 542 | `self.design_params["ring_radial_thickness"] ‖ self.design_params["ring_radial_thickness"]` | 2 assignments (two-case rule or reassigned) |  |
| 116 | `a2_ring_OD` | dependent / formula | high | 655 | `self.Nr2 * self.module2 + self.ring_radial_thickness * 2` |  |  |
| 117 | `a2_ring_to_chamfer_clearance` | fixed / config | high | 544 | `self.design_params["ring_to_chamfer_clearance2"]` |  |  |
| 118 | `a2_Motor_case_OD_base_to_chamfer` | fixed / config | high | 464 | `self.design_params["Motor_case_OD_base_to_chamfer"]` |  |  |
| 119 | `a2_pattern_offset_from_motor_case_OD_base` | fixed / config | high | 465 | `self.design_params["pattern_offset_from_motor_case_OD_base"]` |  |  |
| 120 | `a2_pattern_bulge_dia` | fixed / config | high | 466 | `self.design_params["pattern_bulge_dia"]` |  |  |
| 121 | `a2_pattern_num_bulge` | fixed / config | high | 467 | `self.design_params["pattern_num_bulge"]` |  |  |
| 122 | `a2_pattern_depth` | fixed / config | high | 468 | `self.design_params["pattern_depth"]` |  |  |
| 123 | `a2_case_mounting_nut_clearance` | fixed / config | high | 469 | `self.design_params["case_mounting_nut_clearance"]` |  |  |
| 124 | `a2_case_mounting_surface_height` | fixed / config | high | 276 | `self.design_params["case_mounting_surface_height"]` |  |  |
| 125 | `a2_num_planet` | optimisation / planets | high | 530 | `self.inrunnerdoubleStagePlanetaryGearbox.Stage2.numPlanet` |  |  |
| 126 | `a2_planet_pin_bolt_dia` | fixed / config | high | 560 | `self.design_params["planet_pin_bolt_dia2"]` |  |  |
| 127 | `a2_planet_pin_socket_head_dia` | dependent / lookup (bolt/nut) | high | 622 | `planet_bolt2.bolt_head_dia` |  |  |
| 128 | `a2_carrier_PCD` | dependent / formula | high | 601 | `(self.Np2 + self.Ns2) * self.module2` |  |  |
| 129 | `a2_planet_shaft_dia` | fixed / config | high | 545 | `self.design_params["planet_shaft_dia2"]` |  |  |
| 130 | `a2_fw_p` | dependent / formula | high | 591 | `self.fw_r2` |  |  |
| 131 | `a2_planet_shaft_step_offset` | fixed / config | high | 546 | `self.design_params["planet_shaft_step_offset2"]` |  |  |
| 132 | `a2_carrier_trapezoidal_support_sun_offset` | fixed / config | high | 547 | `self.design_params["carrier_trapezoidal_support_sun_offset2"]` |  |  |
| 133 | `a2_carrier_trapezoidal_support_hole_PCD_offset_bearing_ID` | fixed / config | high | 548 | `self.design_params["carrier_trapezoidal_support_hole_PCD_offset_bearing_ID2"]` |  |  |
| 134 | `a2_carrier_trapezoidal_support_hole_dia` | fixed / config | high | 561 | `self.design_params["carrier_trapezoidal_support_hole_dia2"]` |  |  |
| 135 | `a2_carrier_trapezoidal_support_hole_socket_head_dia` | dependent / lookup (bolt/nut) | high | 640 | `carrier_trapezoidal_support_hole2.bolt_head_dia` |  |  |
| 136 | `a2_carrier_bearing_step_width` | fixed / config | high | 549 | `self.design_params["carrier_bearing_step_width2"]` |  |  |
| 137 | `a2_standard_clearance_1_5mm` | fixed / config | high | 264, 540 | `self.design_params["standard_clearance_1_5mm"] ‖ self.design_params["standard_clearance_1_5mm"]` | 2 assignments (two-case rule or reassigned) |  |
| 138 | `a2_standard_fillet_1_5mm` | fixed / config | high | 265, 541 | `self.design_params["standard_fillet_1_5mm"] ‖ self.design_params["standard_fillet_1_5mm"]` | 2 assignments (two-case rule or reassigned) |  |
| 139 | `a2_sun_shaft_bearing_OD` | fixed / config | high | 550 | `self.design_params["sun_shaft_bearing_OD2"]` |  |  |
| 140 | `a2_sun_shaft_bearing_width` | fixed / config | high | 551 | `self.design_params["sun_shaft_bearing_width2"]` |  |  |
| 141 | `a2_standard_bearing_insertion_chamfer` | fixed / config | high | 266 | `self.design_params["standard_bearing_insertion_chamfer"]` |  |  |
| 142 | `a2_carrier_trapezoidal_support_hole_wrench_size` | dependent / lookup (bolt/nut) | high | 641 | `carrier_trapezoidal_support_hole2.nut_width_across_flats` |  |  |
| 143 | `a2_planet_pin_bolt_wrench_size` | dependent / lookup (bolt/nut) | high | 623 | `planet_bolt2.nut_width_across_flats` |  |  |
| 144 | `a2_h_b` | dependent / formula | high | 594 | `1.25 * self.module2` |  |  |
| 145 | `a2_dp_s` | dependent / formula | high | 600 | `self.module2 * self.Ns2` |  |  |
| 146 | `a2_db_s` | dependent / formula | high | 604 | `self.dp_s2 * np.cos(np.deg2rad(self.pressure_angle))` |  |  |
| 147 | `a2_fw_s_calc` | dependent / stress rule (face width) | high | 533 | `self.inrunnerdoubleStagePlanetaryGearbox.Stage2.fwSunMM` |  |  |
| 148 | `a2_alpha_s` | dependent / formula | high | 609 | `np.sqrt(self.dp_s2**2 - self.db_s2**2) / self.db_s2 * 180 / np.pi - self.pressure_angle` |  |  |
| 149 | `a2_beta_s` | dependent / formula | high | 612 | `(360 / (4 * self.Ns2) - self.alpha_s2) * 2` |  |  |
| 150 | `a2_dp_p` | dependent / formula | high | 598 | `self.module2 * self.Np2` |  |  |
| 151 | `a2_db_p` | dependent / formula | high | 605 | `self.dp_p2 * np.cos(np.deg2rad(self.pressure_angle))` |  |  |
| 152 | `a2_alpha_p` | dependent / formula | high | 610 | `np.sqrt(self.dp_p2**2 - self.db_p2**2) / self.db_p2 * 180 / np.pi - self.pressure_angle` |  |  |
| 153 | `a2_beta_p` | dependent / formula | high | 613 | `(360 / (4 * self.Np2) - self.alpha_p2) * 2` |  |  |
| 154 | `a2_planet_bearing_OD` | fixed / config | high | 552 | `self.design_params["planet_bearing_OD2"]` |  |  |
| 155 | `a2_planet_bearing_width` | fixed / config | high | 553 | `self.design_params["planet_bearing_width2"]` |  |  |
| 156 | `a2_planet_bore` | fixed / config | high | 554 | `self.design_params["planet_bore2"]` |  |  |
| 157 | `a2_sun_shaft_bearing_ID` | fixed / config | high | 555 | `self.design_params["sun_shaft_bearing_ID2"]` |  |  |
| 158 | `a2_sun_hub_dia` | dependent / formula | high | 457 | `self.rotor_ID - 2 * (self.standard_clearance_1_5mm + 2)` |  |  |
| 159 | `a2_sun_central_bolt_dia` | fixed / config | high | 562 | `self.design_params["sun_central_bolt_dia2"]` |  |  |
| 160 | `a2_sun_central_bolt_socket_head_dia` | dependent / lookup (bolt/nut) | high | 645 | `sun_central_bolt2.bolt_head_dia` |  |  |
| 161 | `a2_fw_s_used` | dependent / formula | high | 657, 659 | `self.fw_p2 + self.clearance_planet + self.sec_carrier_thickness2 + self.standard_clearance_1_5mm + self.loose_…` | 2 assignments (two-case rule or reassigned) |  |
| 162 | `a2_bearing_retainer_thickness` | fixed / config | high | 556 | `self.design_params["bearing_retainer_thickness2"]` |  |  |
| 163 | `a2_Ns1` | optimisation / teeth | high | 250 | `self.inrunnerdoubleStagePlanetaryGearbox.Stage1.Ns` |  |  |
| 164 | `a2_Np1` | optimisation / teeth | high | 251 | `self.inrunnerdoubleStagePlanetaryGearbox.Stage1.Np` |  |  |
| 165 | `a2_Nr1` | dependent / formula | high | 380 | `self.Ns1 + 2 * self.Np1` |  |  |
| 166 | `a2_module1` | optimisation / module | high | 253 | `self.inrunnerdoubleStagePlanetaryGearbox.Stage1.module` |  |  |
| 167 | `a2_bearing1_ID` | fixed / hard-coded constant | medium | 424 | `38.1` | value hard-coded in the code; numbers 38.1 |  |
| 168 | `a2_bearing1_OD` | fixed / hard-coded constant | medium | 425 | `47.625` | value hard-coded in the code; numbers 47.625 |  |
| 169 | `a2_bearing1_height1` | fixed / hard-coded constant | medium | 426 | `4.763` | value hard-coded in the code; numbers 4.763 |  |
| 170 | `a2_num_planet1` | optimisation / planets | high | 252 | `self.inrunnerdoubleStagePlanetaryGearbox.Stage1.numPlanet` |  |  |
| 171 | `a2_stg1_stg2_mounting_pattern_width` | fixed / config | high | 564 | `self.design_params["stg1_stg2_mounting_pattern_width"]` |  |  |
| 172 | `a2_stg1_stg2_allen_socket_head_dia` | dependent / lookup (bolt/nut) | high | 649 | `stg1_stg2_mounting_hole.bolt_head_dia` |  |  |
| 173 | `a2_stg1_stg2_mounting_hole_dia` | fixed / config | high | 563 | `self.design_params["stg1_stg2_mounting_hole_dia"]` |  |  |
| 174 | `a2_tight_clearance_3DP` | fixed / config | high | 262 | `self.design_params["tight_clearance_3DP"]` |  |  |
| 175 | `a2_loose_clearance_3DP` | fixed / config | high | 263 | `self.design_params["loose_clearance_3DP"]` |  |  |
| 176 | `Stator_wire_OD` | input / motor | high | 341 | `self.motor.stator_wire_OD` |  |  |
| 177 | `Stator_wire_ID` | input / motor | high | 340 | `self.motor.stator_wire_ID` |  |  |
| 178 | `stator_bottom_step_height_` | input / motor | high | 339 | `self.motor.stator_wire_bottom_height` |  |  |
| 179 | `stator_upper_step_height` | input / motor | high | 338 | `self.motor.stator_wire_top_height` |  |  |
| 180 | `stator_casing_hole_dia` | fixed / config | high | 346 | `self.design_params["stator_casing_hole_dia"]` |  |  |
| 181 | `stator_casing_thickness` | fixed / config | high | 271, 365 | `self.design_params["stator_casing_thickness"] ‖ self.design_params["stator_casing_thickness"]` | 2 assignments (two-case rule or reassigned) |  |
| 182 | `stator_casing_hole_allen_socket_head_dia` | fixed / config | high | 347 | `self.design_params["stator_casing_hole_allen_socket_head_dia"]` |  |  |
| 183 | `stator_mounting_hole_num` | input / motor | high | 343 | `self.motor.stator_hole_num` |  |  |
| 184 | `stator_mounting_holes_dia` | input / motor | high | 337 | `self.motor.stator_hole_dia` |  |  |
| 185 | `stator_mounitng_holes_head_socket_dia` | fixed / config | high | 348 | `self.design_params["stator_mounitng_holes_head_socket_dia"]` |  |  |
| 186 | `Stator_ID` | input / motor | high | 330 | `self.motor.stator_ID` |  |  |
| 187 | `Stator_OD` | input / motor | high | 334 | `self.motor.stator_OD` |  |  |
| 188 | `Stator_height` | input / motor | high | 333 | `self.motor.stator_height` |  |  |
| 189 | `Rotor_ID` | input / motor | high | 332 | `self.motor.rotor_ID` |  |  |
| 190 | `Rotor_OD` | input / motor | high | 329 | `self.motor.rotor_OD` |  |  |
| 191 | `Rotor_height` | input / motor | high | 331 | `self.motor.rotor_height` |  |  |
| 192 | `a2_bearing_retainer_hole_dia` | fixed / config | high | 287, 571 | `self.design_params["a2_bearing_retainer_hole_dia"] ‖ self.design_params["a2_bearing_retainer_hole_dia"]` | 2 assignments (two-case rule or reassigned) |  |
| 193 | `a2_bearing_retainer_hole_num` | fixed / config | high | 288, 572 | `self.design_params["a2_bearing_retainer_hole_num"] ‖ self.design_params["a2_bearing_retainer_hole_num"]` | 2 assignments (two-case rule or reassigned) |  |
| 194 | `a2_bearing_retainer_nut_wrench_size` | fixed / config | high | 289, 573 | `self.design_params["a2_bearing_retainer_nut_wrench_size"] ‖ self.design_params["a2_bearing_retainer_nut_wrench…` | 2 assignments (two-case rule or reassigned) |  |
| 195 | `a2_bearing_retainer_wrench_height` | fixed / config | high | 290, 574 | `self.design_params["a2_bearing_retainer_wrench_height"] ‖ self.design_params["a2_bearing_retainer_wrench_heigh…` | 2 assignments (two-case rule or reassigned) |  |
| 196 | `bearing_retainer_thickness` | fixed / config | high | 291, 575 | `self.design_params["bearing_retainer_thickness"] ‖ self.design_params["bearing_retainer_thickness"]` | 2 assignments (two-case rule or reassigned) | sspg: fixed, cpg: fixed |
| 197 | `a1_sun_bottom_casing_bearing_ID` | fixed / config | high | 413, 419 | `Bearing_bottom_casing.getBearingIDMM() ‖ self.design_params["a1_sun_bottom_casing_bearing_ID"]` | 2 assignments (two-case rule or reassigned) |  |
| 198 | `a1_sun_bottom_casing_bearing_OD` | fixed / config | high | 414, 420 | `Bearing_bottom_casing.getBearingODMM() ‖ self.design_params["a1_sun_bottom_casing_bearing_OD"]` | 2 assignments (two-case rule or reassigned) |  |
| 199 | `a1_sun_bottom_casing_bearing_height` | fixed / config | high | 415, 421 | `Bearing_bottom_casing.getBearingWidthMM() ‖ self.design_params["a1_sun_bottom_casing_bearing_height"]` | 2 assignments (two-case rule or reassigned) |  |
| 200 | `rotor_mount_hole_PCD` | dependent / formula | high | 356 | `self.rotor_ID - self.rotor_csk_head_upper_dia - 2*2 - self.standard_clearance_1_5mm` |  |  |
| 201 | `rotor_mount_hole_dia` | fixed / config | high | 352 | `self.design_params["rotor_mount_hole_dia"]` |  |  |
| 202 | `rotor_mount_hole_num` | fixed / config | high | 353 | `self.design_params["rotor_mount_hole_num"]` |  |  |
| 203 | `Rotor_csk_head_upper_dia` | fixed / config | high | 354 | `self.design_params["Rotor_csk_head_upper_dia"]` |  |  |
| 204 | `Rotor_csk_head_height` | fixed / config | high | 355 | `self.design_params["Rotor_csk_head_height"]` |  |  |
| 205 | `stator_mounting_hole_wrench_dia` | fixed / config | high | 582 | `self.design_params["stator_mounting_hole_wrench_dia"]` |  |  |
| 206 | `stator_mounting_hole_wrench_thickness` | fixed / config | high | 583 | `self.design_params["stator_mounting_hole_wrench_thickness"]` |  |  |
| 207 | `needle_bearing_planet_stg1_ID` | fixed / config | high | 293 | `self.design_params["needle_bearing_planet_stg1_ID"]` |  |  |
| 208 | `needle_bearing_planet_stg1_OD` | fixed / config | high | 294 | `self.design_params["needle_bearing_planet_stg1_OD"]` |  |  |
| 209 | `needle_bearing_planet_stg1_height` | fixed / config | high | 295 | `self.design_params["needle_bearing_planet_stg1_height"]` |  |  |
| 210 | `rotor_metal_part_thickness` | fixed / config | high | 297 | `self.design_params["rotor_metal_part_thickness"]` |  |  |

## Config accounting

| Block | Keys | Read by this type | Read but not written to the CAD | Never used |
|---|---|---|---|---|
| `indspg_design_parameters` | 29 | **no** | sCarrierExtrusionDiaMM_Stg1, sCarrierExtrusionClearanceMM_Stg1, sCarrierExtrusionDiaMM_Stg2, sCarrierExtrusionClearanceMM_Stg2, planetMinDistanceMM | Ring1RadialWidthMM, Ring2RadialWidthMM, carrier1ShaftHeightMM, mainCase2AttachmentHeightMM, baseThicknessMM, sCarrierThicknessMM, mainCoverThicknessMM, planetBoreMM, sunBoreMM, couplerRadiusMM, couplerThicknessMM, couplerShaftHeightMM, CarrierRadialThicknessClearance1, CarrierRadialThicknessClearance2, carrierInnerDiaClearanceMM1, sCarrierInnerDiaClearanceMM1, carrierInnerDiaClearanceMM2, sCarrier… |
| `indspg_optimization_parameters` | 14 | yes | GEAR_RATIO_MIN, GEAR_RATIO_MAX, GEAR_RATIO_STEP, MODULE_STAGE1_MIN, MODULE_STAGE1_MAX, MODULE_STAGE2_MIN, MODULE_STAGE2_MAX, NUM_PLANET_STAGE1_MIN, NUM_PLANET_STAGE1_MAX, NUM_PLANET_STAGE2_MIN, NUM_PLANET_STAGE2_MAX, NUM_TEETH_SUN_MIN, NUM_TEETH_PLANET_MIN, MAX_GB_DIA_MULT_FACTOR | — |
| `indspg_design_parameters_3DP` | 105 | yes | sCarrierExtrusionDiaMM_Stg1, sCarrierExtrusionClearanceMM_Stg1, sCarrierExtrusionDiaMM_Stg2, sCarrierExtrusionClearanceMM_Stg2, planetMinDistanceMM, central_hole_offset_from_motor_mount_PCD, base_plate_thickness, air_flow_hole_offset, bearingIDClearanceMM, clearance_case_mount_holes_shell_thickness2, a1_sun_bottom_casing_bearing_massKg, rotor_mount_hole_PCD, ring2RadialWidthMM | a1_sun_carrier_bearing_ID, a1_sun_carrier_bearing_OD, a1_sun_carrier_bearing_height, bearing_retainer_hole_dia, bearing_retainer_hole_num, bearing_retainer_hole_wrench_nut_size, needle_bearing_planet_OD, needle_bearing_planet_ID, needle_bearing_planet_height |


## Result (classification done)

Spec: [`config_files/variables/indspg_variables.json`](../../../config_files/variables/indspg_variables.json), page [`docs/variables/indspg.md`](../indspg.md) (generated). Tests: the generic `tests/test_variable_categories.py` (INDSPG registered in `tests/variable_helpers.py`, with the two-stage setter of DSPG) and `tests/test_variable_categories_indspg.py`.

**Counts (CAD variables, 210):** input 12, optimisation 15, fixed 109, dependent 74 (47 formula, 18 lookup, 5 stress rule, 4 implicit constraint). 43 names are aliases of another name (the plan said 42: the extra one is `a2_sun_coupler_hub_thickness`, written with `getattr(self, "sun_coupler_hub_thickness1", "N/A")`, the stage-1 value). The plain `indspg_equations.txt` carries the same 210 names. **Code-only values: 43** (fixed 38, dependent 3: the two `maxGearboxDiameter` values and the bottom casing bearing's mass `a1_sun_bottom_casing_bearing_massKg`; input 2), including 11 config keys that are never read and `rotor_mount_hole_PCD_config`. Confidence: 237 high, 16 medium, 0 low.

**Medium-confidence entries** (hard-coded numbers with no config key, and one two-case value)
- `a1_sun_hub_dia`, `a2_sun_hub_dia` (Dependent / formula): `rotor_ID - 2 x (standard_clearance_1_5mm + 2)`, the 2 hard-coded.
- `rotor_mount_hole_PCD` (Dependent / formula): `rotor_ID` less the countersink head, a hard-coded `2 x 2` and one clearance.
- `a1_fw_s_used` (Dependent / formula): a hard-coded `2 x`, and for a 19 mm rotor (RI80) an extra `0.5 x standard_clearance_1_5mm`.
- `a1_sun_bottom_casing_bearing_ID` / `_OD` / `_height` (and the code-only mass `a1_sun_bottom_casing_bearing_massKg`) (Dependent / lookup with a condition): for a rotor 19 mm high (RI80) the bearing is the catalogue one for the rotor's bore; otherwise (RI100) it is the config value. The spec records both with a new `when` / `otherwise` field.
- `planet_bearing_gap` (code-only, Fixed): one key for both stages; the plan leaves open whether it should be one per stage.
- `maxGearboxDiameter_Stg1` (code-only, Dependent / formula): `rotor_ID - 4 x standard_clearance_1_5mm`, the 4 hard-coded in `gearbox_runner`.

**Config key added** to `indspg_design_parameters_3DP` in `indspg_params.json` (shared name, value that keeps every output bit-identical): `planet_bearing_gap` = 1.0 (was `standard_clearance_1_5mm * 2 / 3` in both stages; 1.5 * 2 / 3 is exactly 1.0), in `mitStressAnalysisMinFacewidth`. The other shared keys have no counterpart (no motor-case clearance rule, no `bearing_mount_thickness`). A test shows `planet_bearing_gap` drives exactly its CAD variables in both stages (stage 1's planet width is a fixed config value and does not move).

**Stage-1 output bearing moved to the config (2026-10-31, ISSUES bug 22):** it was hard-coded as 38.1 / 47.625 / 4.763 mm (an inch thin-section bearing) in the CAD code, and the mass code repeated the three numbers and its mass (22.7 g). It is now `a1_bearing_ID`, `a1_bearing_OD`, `a1_bearing_height` and `a1_bearing_massKg` in `indspg_design_parameters_3DP`, read by both; same values, so every output is bit-identical. `a1_bearing_*` and the `a2_bearing1_*` aliases are Fixed / bearing, high confidence, and `a1_bearing_massKg` is a new code-only entry. Tests show each size key drives exactly its CAD variable under both prefixes (and what depends on it), and the mass key adds to the actuator mass one for one. Counts after the move: code-only 44 (fixed 39); confidence 244 high, 10 medium. The stage-1 carrier mass still uses the lookup bearing (bug 22, open).

**Shared tooling changed:** `tests/test_variable_categories.py` and `tools/variables/render.py` (a lookup can carry `when` and `otherwise`: it applies when the condition holds and the other config source otherwise; the config-key, source, depends_on and value checks follow it), `tests/variable_helpers.py` (INDSPG entry and branch rules).

**Results:** `python tests/golden/golden.py check`: All 58 cases match the baseline. `python -m pytest -q`: 1135 passed. No `CADs/` file, no golden baseline touched.

**Open questions**
1. The stage-1 output bearing (now config keys, see above): whether a per-design bearing lookup should replace the fixed bearing, or the carrier mass should use the fixed one (ISSUES bug 22).
2. The hard-coded 2 in `sun_hub_dia`, the `2 x 2` in `rotor_mount_hole_PCD` and the 2 and 0.5 in `a1_fw_s_used`: geometry or tuning (new keys, plan decision 4).
3. The rotor-height-19 case (RI80) makes the stage-1 bottom casing bearing a lookup; RI100 uses the config value. The plan expected a dead lookup overwritten by the config; for RI80 the lookup is what the CAD gets.
4. One `planet_bearing_gap` for both stages, or one per stage (plan decision 1).
5. Bug-18 pattern does not apply (each stage has its own module in the CAD). `indspg_design_parameters` (29 keys) is never read; listed as an unused block. ISSUES bug 11 (rotor coupler ID) and bug 13 (crashes where there is no design: the tests use golden designs only) concern the mass code and the optimiser.
