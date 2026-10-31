# INSSPG type 1: variable classification plan

Part of [the plan for all actuators](../PLAN.md). Survey only: nothing in the code, config or CAD output changes on this branch.

## Inventory

- **CAD interface:** `insspg_type_1_equations_onshape.txt`, **107 variables**; other files: `insspg_type_1_equations.txt` (107)
- **Code:** `singleStagePlanetaryActuator` in `ActuatorandGearbox_INSSPG.py` (lines 328-1477)
- **Config:** `insspg_params.json`, block(s) read: `sspg_design_parameters`, `sspg_3DP_design_parameters`; search bounds `sspg_optimization_parameters`; gear standard / MIT factors from `insspg_motor_config.json`; driver: `None`
- **Survey draft:** dependent 34, fixed 56, input 13, optimisation 4; 71 names also in SSPG / CPG; 0 alias names (same value written under a second name); 2 flagged by the survey

## Special cases (frameless inrunner, single stage; type 1 and type 2 share one class)

| Variable(s) | What the code does | Proposed classification |
|---|---|---|
| all 107 names | **the same names and rules in type 1 and type 2**, except `fw_s_used` (L597-610, `if self.insspg_type == "insspg_type_2"`) | one spec per type; type 2 copies type 1 except `fw_s_used` |
| `Stator_*`, `Rotor_*`, `stator_height` | frameless inrunner geometry | Input / motor |
| fastener sizes: `case_mounting_hole_allen_socket_dia`, `case_mounting_wrench_size`, `output_mounting_nut_thickness`, `output_mounting_nut_wrench_size`, `planet_pin_socket_head_dia`, `planet_pin_bolt_wrench_size`, `carrier_trapezoidal_support_hole_socket_head_dia`, `carrier_trapezoidal_support_hole_wrench_size`, `sun_central_bolt_socket_head_dia` | **looked up from the bolt table, then overwritten by config values** (e.g. L376 then L512) | Fixed / config (the CAD gets the config value); note the dead lookup |
| `bearing_mount_thickness` | `self.design_params.get("bearing_mount_thickness")` | Fixed / config (SSPG/CPG compute it) |
| `rotor_support_bearing_*`, `rotor_upper_support_bearing_*` | catalogue bearings (`bearings_discrete`) chosen per motor (ISSUES bug 12 fix) | Dependent / lookup |
| `rotor_output_hole_PCD` | `sun_hub_dia − rotor_mount_hole_CSK_OD` | Dependent / formula |
| `sun_support_OD` | `min(carrier_PCD − planet shaft − 2·step − 1.5 × 3, 21)` | Dependent / formula (two-case); **medium** (hard-coded 21 and × 3) |
| `fw_s_used` | type 1: `… + 1.5 + 1.5 × 1.5 …`; type 2: `Rotor_height − 2 − hub + loose clearance + …` | Dependent / formula; **medium** (hard-coded 1.5 and 2) |
| `fw_s_calc`, `fw_p`, `fw_r` | MIT stress rule with the SSPG-style planet-bearing minimum | Dependent / stress rule |
| driver | the runner passes no driver (`driver None`); no driver variables in the CAD | — |

## Hard-coded numbers (medium)

| Where | Number | Proposed key |
|---|---|---|
| `sun_support_OD` (L593-594) | 21, 3 | new: `sun_support_OD_max`? (review) |
| `fw_s_used` type 1 / type 2 (L597-610) | 1.5, 2 | review per type |
| planet-bearing minimum (L873-874) | 2/3 | `planet_bearing_gap` |
| mass code: **ISSUES bug 10** (`(14/2)**` exponent typo, L1301), 14, 50, 9, 5.5 mm features, extra bearing masses (6.6 g, 7.9 g), `gearbox_mass` adds 0.01 / 0.02 kg | various | mass-only list; bug 10 already logged |

## Config (`insspg_params.json`)
- Reads **two** blocks: `sspg_design_parameters` and `sspg_3DP_design_parameters` (block names shared with SSPG's file, different file).
- Many 3DP keys are read but the CAD value is computed (code-only / overwritten): `bearing_ID`, `bearing_OD`, `bearing_height`, `rotor_output_hole_PCD`, `sun_hub_dia`, stator step heights, … (full list in the table).
- Config file: `insspg_motor_config.json`.

## Test plan
- Registry: SSPG setter, `passes_gearbox_type` (the runner passes `insspg_type`); RI100 / RI80; 3 golden designs each.
- Specific: `fw_s_used` per type, `sun_support_OD` both branches (cap / no cap).

## Risks / notes
- ISSUES bugs 4, 6, 9, 10 touch INSSPG (mass / bearings); classification doesn't change them.
- Effort: ~1.5 h for type 1, ~0.5 h for type 2.

## Survey draft: every variable

Automatic first pass from the code (the special cases above take precedence). Category guesses come from the source of each value; *flags* mark hard-coded numbers, several assignments or a writer expression. The final category, sub-type, `depends_on`, confidence and reason are set during the classification itself.

| # | Variable | Draft category / sub-type | Conf. | Line | Code | Flags | SSPG / CPG |
|---|---|---|---|---|---|---|---|
| 1 | `Ns` | optimisation / teeth | high | 397 | `self.planetaryGearbox.Ns` |  | sspg: optimisation, cpg: optimisation |
| 2 | `Np` | optimisation / teeth | high | 398 | `self.planetaryGearbox.Np` |  | sspg: optimisation |
| 3 | `Nr` | dependent / formula | high | 399 | `self.Ns + 2 * self.Np` |  | sspg: dependent, cpg: dependent |
| 4 | `module` | optimisation / module | high | 400 | `self.planetaryGearbox.module` |  | sspg: optimisation, cpg: optimisation |
| 5 | `num_planet` | optimisation / planets | high | 401 | `self.planetaryGearbox.numPlanet` |  | sspg: optimisation, cpg: optimisation |
| 6 | `pressure_angle` | fixed / gear standard | high | 407 | `self.planetaryGearbox.getPressureAngleRad() * 180 / np.pi` |  | sspg: fixed, cpg: fixed |
| 7 | `h_a` | dependent / formula | high | 564 | `1 * self.module` |  | sspg: dependent, cpg: dependent |
| 8 | `h_b` | dependent / formula | high | 565 | `1.25 * self.module` |  | sspg: dependent, cpg: dependent |
| 9 | `clr_tip_root` | dependent / formula | high | 567 | `self.h_f - self.h_a` |  | sspg: dependent, cpg: dependent |
| 10 | `h_f` | dependent / formula | high | 566 | `1.25 * self.module` |  | sspg: dependent, cpg: dependent |
| 11 | `motor_OD` | input / motor | high | 429 | `self.motorDiaMM` |  | sspg: input, cpg: input |
| 12 | `planet_bore` | fixed / config | high | 528 | `self.design_params["planet_bore"]` |  | sspg: fixed, cpg: fixed |
| 13 | `motor_height` | input / motor | high | 430 | `self.motorLengthMM` |  | sspg: input, cpg: input |
| 14 | `bearing_ID` | dependent / lookup (bearing) | high | 423 | `Bearings.getBearingIDMM()` |  | sspg: dependent, cpg: dependent |
| 15 | `bearing_OD` | dependent / lookup (bearing) | high | 424 | `Bearings.getBearingODMM()` |  | sspg: dependent, cpg: dependent |
| 16 | `bearing_height` | dependent / lookup (bearing) | high | 425 | `Bearings.getBearingWidthMM()` |  | sspg: dependent, cpg: dependent |
| 17 | `clearance_planet` | fixed / config | high | 410 | `self.design_params["clearance_planet"]` |  | sspg: fixed, cpg: fixed |
| 18 | `sec_carrier_thickness` | fixed / config | high | 523 | `self.design_params["sec_carrier_thickness"]` |  | sspg: fixed, cpg: fixed |
| 19 | `sun_coupler_hub_thickness` | fixed / config | high | 524 | `self.design_params["sun_coupler_hub_thickness"]` |  | sspg: fixed, cpg: fixed |
| 20 | `clearance_sun_coupler_sec_carrier` | fixed / config | high | 525 | `self.design_params["clearance_sun_coupler_sec_carrier"]` |  | sspg: fixed, cpg: fixed |
| 21 | `case_mounting_hole_dia` | fixed / config | high | 510 | `self.design_params["case_mounting_hole_dia"]` |  | sspg: fixed, cpg: fixed |
| 22 | `case_mounting_wrench_thickness` | fixed / config | high | 511 | `self.design_params["case_mounting_wrench_thickness"]` |  |  |
| 23 | `case_mounting_hole_allen_socket_dia` | fixed / config | high | 376, 512 | `case_mounting_hole_bolt.bolt_head_dia ‖ self.design_params["case_mounting_hole_allen_socket_dia"]` | 2 assignments (two-case rule or reassigned) | sspg: dependent, cpg: dependent |
| 24 | `dp_s` | dependent / formula | high | 569 | `self.module * self.Ns` |  | sspg: dependent, cpg: dependent |
| 25 | `db_s` | dependent / formula | high | 570 | `self.dp_s * np.cos(self.pressure_angle)` |  | sspg: dependent, cpg: dependent |
| 26 | `fw_s_calc` | dependent / stress rule (face width) | high | 571 | `self.planetaryGearbox.fwSunMM` |  | sspg: dependent, cpg: dependent |
| 27 | `alpha_s` | dependent / formula | high | 572 | `(np.sqrt(self.dp_s**2 - self.db_s**2) / self.db_s) * 180 / np.pi - self.pressure_angle_deg` |  | sspg: dependent, cpg: dependent |
| 28 | `beta_s` | dependent / formula | high | 573 | `(360 / (4 * self.Ns) - self.alpha_s) * 2` |  | sspg: dependent, cpg: dependent |
| 29 | `dp_p` | dependent / formula | high | 575 | `self.module * self.Np` |  | sspg: dependent |
| 30 | `db_p` | dependent / formula | high | 576 | `self.dp_p * np.cos(self.pressure_angle)` |  | sspg: dependent |
| 31 | `fw_p` | dependent / stress rule (face width) | high | 577 | `self.planetaryGearbox.fwPlanetMM` |  | sspg: dependent |
| 32 | `alpha_p` | dependent / formula | high | 578 | `(np.sqrt(self.dp_p**2 - self.db_p**2) / self.db_p) * 180 / np.pi - self.pressure_angle_deg` |  | sspg: dependent |
| 33 | `beta_p` | dependent / formula | high | 579 | `(360 / (4 * self.Np) - self.alpha_p) * 2` |  | sspg: dependent |
| 34 | `dp_r` | dependent / formula | high | 581 | `self.module * self.Nr` |  | sspg: dependent, cpg: dependent |
| 35 | `db_r` | dependent / formula | high | 582 | `self.dp_r * np.cos(self.pressure_angle)` |  | sspg: dependent, cpg: dependent |
| 36 | `fw_r` | dependent / stress rule (face width) | high | 583 | `self.planetaryGearbox.fwRingMM` |  | sspg: dependent, cpg: dependent |
| 37 | `alpha_r` | dependent / formula | high | 584 | `(np.sqrt(self.dp_r**2 - self.db_r**2) / self.db_r) * 180 / np.pi - self.pressure_angle_deg` |  | sspg: dependent, cpg: dependent |
| 38 | `beta_r` | dependent / formula | high | 585 | `(360 / (4 * self.Nr) + self.alpha_r) * 2` |  | sspg: dependent, cpg: dependent |
| 39 | `bearing_mount_thickness` | fixed / config | high | 559 | `self.design_params.get("bearing_mount_thickness")` |  | sspg: dependent, cpg: dependent |
| 40 | `carrier_PCD` | dependent / formula | high | 590 | `self.module * (self.Ns + self.Np)` |  | sspg: dependent, cpg: dependent |
| 41 | `rotor_output_hole_PCD` | dependent / formula | high | 556 | `self.sun_hub_dia - self.rotor_mount_hole_CSK_OD` |  |  |
| 42 | `Rotor_output_hole_num` | fixed / config | high | 517 | `self.design_params["Rotor_output_hole_num"]` |  |  |
| 43 | `output_mounting_nut_thickness` | fixed / config | high | 380, 518 | `output_mounting_hole_bolt.nut_thickness ‖ self.design_params["output_mounting_nut_thickness"]` | 2 assignments (two-case rule or reassigned) | sspg: dependent, cpg: dependent |
| 44 | `output_mounting_nut_wrench_size` | fixed / config | high | 381, 519 | `output_mounting_hole_bolt.nut_width_across_flats ‖ self.design_params["output_mounting_nut_wrench_size"]` | 2 assignments (two-case rule or reassigned) | sspg: dependent, cpg: dependent |
| 45 | `output_mounting_hole_dia` | fixed / config | high | 520 | `self.design_params["output_mounting_hole_dia"]` |  | sspg: fixed, cpg: fixed |
| 46 | `case_mounting_bolt_depth` | fixed / config | high | 513 | `self.design_params["case_mounting_bolt_depth"]` |  | sspg: fixed, cpg: fixed |
| 47 | `case_mounting_wrench_size` | fixed / config | high | 377, 514 | `case_mounting_hole_bolt.nut_width_across_flats ‖ self.design_params["case_mounting_wrench_size"]` | 2 assignments (two-case rule or reassigned) | sspg: dependent, cpg: dependent |
| 48 | `planet_pin_bolt_dia` | fixed / config | high | 529 | `self.design_params["planet_pin_bolt_dia"]` |  | sspg: fixed, cpg: fixed |
| 49 | `planet_pin_socket_head_dia` | fixed / config | high | 365, 530 | `planet_pin_bolt.bolt_head_dia ‖ self.design_params["planet_pin_socket_head_dia"]` | 2 assignments (two-case rule or reassigned) | sspg: dependent, cpg: dependent |
| 50 | `planet_shaft_dia` | fixed / config | high | 531 | `self.design_params["planet_shaft_dia"]` |  | sspg: fixed, cpg: fixed |
| 51 | `planet_pin_bolt_wrench_size` | fixed / config | high | 366, 532 | `planet_pin_bolt.nut_width_across_flats ‖ self.design_params["planet_pin_bolt_wrench_size"]` | 2 assignments (two-case rule or reassigned) | sspg: dependent, cpg: dependent |
| 52 | `planet_shaft_step_offset` | fixed / config | high | 533 | `self.design_params["planet_shaft_step_offset"]` |  | sspg: fixed, cpg: fixed |
| 53 | `planet_bearing_OD` | fixed / config | high | 534 | `self.design_params["planet_bearing_OD"]` |  | sspg: fixed, cpg: fixed |
| 54 | `planet_bearing_width` | fixed / config | high | 535 | `self.design_params["planet_bearing_width"]` |  | sspg: fixed, cpg: fixed |
| 55 | `carrier_trapezoidal_support_sun_offset` | fixed / config | high | 539 | `self.design_params["carrier_trapezoidal_support_sun_offset"]` |  | sspg: fixed, cpg: fixed |
| 56 | `carrier_trapezoidal_support_hole_PCD_offset_bearing_ID` | fixed / config | high | 540 | `self.design_params["carrier_trapezoidal_support_hole_PCD_offset_bearing_ID"]` |  | sspg: fixed, cpg: fixed |
| 57 | `carrier_trapezoidal_support_hole_dia` | fixed / config | high | 541 | `self.design_params["carrier_trapezoidal_support_hole_dia"]` |  | sspg: fixed, cpg: fixed |
| 58 | `carrier_trapezoidal_support_hole_socket_head_dia` | fixed / config | high | 372, 542 | `carrier_trap_hole.bolt_head_dia ‖ self.design_params["carrier_trapezoidal_support_hole_socket_head_dia"]` | 2 assignments (two-case rule or reassigned) | sspg: dependent, cpg: dependent |
| 59 | `carrier_trapezoidal_support_hole_wrench_size` | fixed / config | high | 373, 543 | `carrier_trap_hole.nut_width_across_flats ‖ self.design_params["carrier_trapezoidal_support_hole_wrench_size"]` | 2 assignments (two-case rule or reassigned) | sspg: dependent, cpg: dependent |
| 60 | `carrier_bearing_step_width` | fixed / config | high | 544 | `self.design_params["carrier_bearing_step_width"]` |  | sspg: fixed, cpg: fixed |
| 61 | `standard_clearance_1_5mm` | fixed / config | high | 411 | `self.design_params["standard_clearance_1_5mm" ]` |  | sspg: fixed, cpg: fixed |
| 62 | `standard_fillet_1_5mm` | fixed / config | high | 412 | `self.design_params["standard_fillet_1_5mm"]` |  | sspg: fixed, cpg: fixed |
| 63 | `sun_shaft_bearing_OD` | fixed / config | high | 552 | `self.design_params["sun_shaft_bearing_OD"]` |  | sspg: fixed, cpg: fixed |
| 64 | `sun_shaft_bearing_width` | fixed / config | high | 553 | `self.design_params["sun_shaft_bearing_width"]` |  | sspg: fixed, cpg: fixed |
| 65 | `sun_shaft_bearing_ID` | fixed / config | high | 551 | `self.design_params["sun_shaft_bearing_ID"]` |  | sspg: fixed, cpg: fixed |
| 66 | `standard_bearing_insertion_chamfer` | fixed / config | high | 413 | `self.design_params["standard_bearing_insertion_chamfer"]` |  | sspg: fixed, cpg: fixed |
| 67 | `sun_hub_dia` | dependent / formula | high | 548 | `self.rotor_upper_support_bearing_ID - self.standard_clearance_1_5mm * 2` |  | sspg: dependent, cpg: dependent |
| 68 | `sun_central_bolt_dia` | fixed / config | high | 549 | `self.design_params["sun_central_bolt_dia"]` |  | sspg: fixed, cpg: fixed |
| 69 | `sun_central_bolt_socket_head_dia` | fixed / config | high | 369, 550 | `sun_central_bolt.bolt_head_dia ‖ self.design_params["sun_central_bolt_socket_head_dia"]` | 2 assignments (two-case rule or reassigned) | sspg: dependent, cpg: dependent |
| 70 | `bearing_retainer_thickness` | fixed / config | high | 536 | `self.design_params["bearing_retainer_thickness"]` |  | sspg: fixed, cpg: fixed |
| 71 | `tight_clearance_3DP` | fixed / config | high | 414 | `self.design_params["tight_clearance_3DP"]` |  | sspg: fixed, cpg: fixed |
| 72 | `loose_clearance_3DP` | fixed / config | high | 415 | `self.design_params["loose_clearance_3DP"]` |  | sspg: fixed, cpg: fixed |
| 73 | `Stator_ID` | input / motor | high | 434 | `self.motor.stator_ID` |  |  |
| 74 | `Stator_OD` | input / motor | high | 435 | `self.motor.stator_OD` |  |  |
| 75 | `stator_height` | input / motor | high | 436 | `self.motor.stator_height` |  |  |
| 76 | `stator_casing_thickness` | fixed / config | high | 502 | `self.design_params["stator_casing_thickness"]` |  |  |
| 77 | `stator_bottom_step_height_` | input / motor | high | 440 | `self.motor.stator_wire_bottom_height` |  |  |
| 78 | `stator_upper_step_height` | input / motor | high | 438 | `self.motor.stator_wire_top_height` |  |  |
| 79 | `stator_side_step_OD` | input / motor | high | 441 | `self.motor.stator_wire_OD` |  |  |
| 80 | `stator_side_step_ID` | input / motor | high | 442 | `self.motor.stator_wire_ID` |  |  |
| 81 | `stator_mounting_holes_dia` | input / motor | high | 437 | `self.motor.stator_hole_dia` |  |  |
| 82 | `stator_hole_bolt_socket_head_dia` | fixed / config | high | 504 | `self.design_params["stator_hole_bolt_socket_head_dia"]` |  |  |
| 83 | `Rotor_height` | input / motor | high | 433 | `self.motor.rotor_height` |  |  |
| 84 | `Rotor_OD` | input / motor | high | 432 | `self.motor.rotor_OD` |  |  |
| 85 | `Rotor_ID` | input / motor | high | 431 | `self.motor.rotor_ID` |  |  |
| 86 | `rotor_mount_hole_dia` | fixed / config | high | 452 | `self.design_params["rotor_mount_hole_dia"]` |  |  |
| 87 | `rotor_mount_hole_CSK_OD` | fixed / config | high | 453 | `self.design_params["rotor_mount_hole_CSK_OD"]` |  |  |
| 88 | `rotor_mount_hole_CSK_head_hight` | fixed / config | high | 454 | `self.design_params["rotor_mount_hole_CSK_head_hight"]` |  |  |
| 89 | `rotor_support_bearing_ID` | dependent / formula | high | 474 | `self.bearing_ID_R_S` |  |  |
| 90 | `rotor_support_bearing_OD` | dependent / formula | high | 475 | `self.bearing_OD_R_S` |  |  |
| 91 | `rotor_support_bearing_height` | dependent / formula | high | 476 | `self.bearing_height_R_S` |  |  |
| 92 | `rotor_upper_support_bearing_ID` | dependent / formula | high | 489 | `self.bearing_ID_R_U_S` |  |  |
| 93 | `rotor_upper_support_bearing_OD` | dependent / formula | high | 490 | `self.bearing_OD_R_U_S` |  |  |
| 94 | `rotor_upper_support_bearing_height` | dependent / formula | high | 491 | `self.bearing_height_R_U_S` |  |  |
| 95 | `Rotor_tight_clearance` | fixed / config | high | 416 | `self.design_params["Rotor_tight_clearance"]` |  |  |
| 96 | `stator_bearing_support_casing_thickness` | fixed / config | high | 505 | `self.design_params["stator_bearing_support_casing_thickness"]` |  |  |
| 97 | `fw_s_used` | dependent / formula | medium | 599, 608 | `(self.Rotor_height - 2 - self.sun_coupler_hub_thickness + self.loose_clearance_3DP + self.sec_carrier_thicknes…` | 2 assignments (two-case rule or reassigned); numbers 1.5 | sspg: dependent, cpg: dependent |
| 98 | `ringRadialWidthMM` | fixed / config | high | 361 | `self.design_params.get("ringRadialWidthMM", self.planetaryGearbox.ringRadialWidthMM)` |  | sspg: fixed, cpg: fixed |
| 99 | `sun_support_OD` | dependent / formula | medium | 594 | `min(calculated_sun_support, 21)` | numbers 21 |  |
| 100 | `stator_casing_hole_dia` | fixed / config | high | 503 | `self.design_params["stator_casing_hole_dia"]` |  |  |
| 101 | `stator_casing_hole_socket_head_dia` | fixed / config | high | 506 | `self.design_params["stator_casing_hole_socket_head_dia"]` |  |  |
| 102 | `sun_bottom_casing_bearing_OD` | fixed / config | high | 494 | `self.design_params["sun_bottom_casing_bearing_OD"]` |  |  |
| 103 | `sun_bottom_casing_bearing_ID` | fixed / config | high | 495 | `self.design_params["sun_bottom_casing_bearing_ID"]` |  |  |
| 104 | `sun_bottom_casing_bearing_height` | fixed / config | high | 496 | `self.design_params["sun_bottom_casing_bearing_height"]` |  |  |
| 105 | `sun_sec_carrier_bearing_ID` | fixed / config | high | 497 | `self.design_params["sun_sec_carrier_bearing_ID"]` |  |  |
| 106 | `sun_sec_carrier_bearing_OD` | fixed / config | high | 498 | `self.design_params["sun_sec_carrier_bearing_OD"]` |  |  |
| 107 | `sun_sec_carrier_bearing_height` | fixed / config | high | 499 | `self.design_params["sun_sec_carrier_bearing_height"]` |  |  |

## Config accounting

| Block | Keys | Read by this type | Read but not written to the CAD | Never used |
|---|---|---|---|---|
| `sspg_design_parameters` | 26 | yes | planetMinDistanceMM, sCarrierExtrusionDiaMM, sCarrierExtrusionClearanceMM, bearingIDClearanceMM | carrier1ShaftHeightMM, mainCase2AttachmentHeightMM, baseThicknessMM, sCarrierThicknessMM, mainCoverThicknessMM, planetBoreMM, sunBoreMM, couplerRadiusMM, couplerThicknessMM, couplerShaftHeightMM, clearanceMotorandCaseMM, clearanceRingandCaseMM, clearance1RingandCaseMM, clearanceCarrierPlanetMM, upperHousingHeight, clearanceSCarrierMotorMM, carrierIDClearanceMM, sCarrierIDClearanceMM, smallBearingM… |
| `sspg_optimization_parameters` | 10 | yes | GEAR_RATIO_MIN, GEAR_RATIO_MAX, GEAR_RATIO_STEP, MODULE_MIN, MODULE_MAX, NUM_PLANET_MIN, NUM_PLANET_MAX, NUM_TEETH_SUN_MIN, NUM_TEETH_PLANET_MIN, MAX_GB_DIA_MULT_FACTOR | — |
| `sspg_3DP_design_parameters` | 70 | yes | bearing_ID, bearing_OD, bearing_height, rotor_output_hole_PCD, sun_hub_dia, stator_bottom_step_height_, stator_upper_step_height, stator_side_step_OD, stator_mounting_holes_dia, rotor_support_bearing_ID, rotor_support_bearing_OD, rotor_support_bearing_height, rotor_upper_support_bearing_ID, rotor_upper_support_bearing_OD, rotor_upper_support_bearing_height, stator_casing_hole_wrench_size | — |


## Result (classification done)

Spec: [`config_files/variables/insspg_type_1_variables.json`](../../../config_files/variables/insspg_type_1_variables.json), page [`docs/variables/insspg_type_1.md`](../insspg_type_1.md) (generated). Tests: the generic `tests/test_variable_categories.py` (INSSPG types 1 and 2 registered in `tests/variable_helpers.py`) and `tests/test_variable_categories_insspg.py` (parametrized over the types that have a spec; type 2 follows in the next commit).

**Counts (CAD variables, 107):** input 12, optimisation 4, fixed 56, dependent 35 (22 formula, 9 lookup, 3 stress rule, 1 implicit constraint). The draft said input 13 / dependent 34: `motor_height` is the sum of three motor heights (`motorLengthMM` = stator top wire + middle + bottom wire), so it is Dependent / formula. **Code-only values: 60** (fixed 54, input 4, dependent 2: `pressure_angle_rad`, `maxGearboxDiameter`). 24 of them are config keys the code never reads, 15 named `<key>_config` because the CAD variable of the same name does not come from them. Confidence: 158 high, 9 medium, 0 low.

**Medium-confidence entries**
- `rotor_support_bearing_ID` / `_OD` / `_height`, `rotor_upper_support_bearing_ID` / `_OD` / `_height` (Dependent / lookup): the catalogue bearing is requested by outer diameter (`Rotor_ID - 4`, `Stator_ID - 5 x standard_clearance_1_5mm`) with hard-coded 4 and 5; `bearings_discrete` returns the first bearing with OD >= the request, which can exceed it (ISSUES bug 5).
- `fw_s_used` (Dependent / formula): hard-coded `1.5 x standard_clearance_1_5mm` in type 1 (a hard-coded `2` in type 2).
- `sun_support_OD` (Dependent / formula): capped at a hard-coded 21 mm, with a hard-coded `x 3` clearance.
- `maxGearboxDiameter` (code-only, Dependent / formula): `Stator_OD - 5.5 - 2 x standard_clearance_1_5mm - loose_clearance_3DP / 2`, the 5.5 hard-coded in `gearbox_runner`.

**Config key added** to `sspg_3DP_design_parameters` in `insspg_params.json` (shared name, value that keeps every output bit-identical): `planet_bearing_gap` = 1.0 (was `standard_clearance_1_5mm * 2 / 3`; 1.5 * 2 / 3 is exactly 1.0), used by the stress rule in `mitStressAnalysisMinFacewidth` and the Lewis rule's copy. The other shared keys (`clearance_motor_and_case_min`, `case_mounting_hole_wall_overlap`, `bearing_mount_wall_bolt_dia_multiple`) have no counterpart in INSSPG: it has no motor-case clearance, no case bolt-hole shift, and `bearing_mount_thickness` is a config value. A test shows `planet_bearing_gap` drives exactly its CAD variables.

**Shared tooling changed:** `tests/variable_helpers.py` (a gearbox can name its own params file and its own config file; INSSPG entries and a branch rule), `tests/test_variable_categories.py` (sources are read from whichever config file the spec names; `bearings_discrete` lookups can pass `odRequiredMM`), `tools/variables/render.py` (names the plain file of a gearbox whose folder differs from its key).

**Results:** `python tests/golden/golden.py check`: All 58 cases match the baseline. `python -m pytest -q`: 851 passed, 1 skipped (the type-1 / type-2 comparison, which needs both specs). No `CADs/` file, no golden baseline touched.

**Open questions**
1. The hard-coded 21 and `x 3` (`sun_support_OD`), the type-specific `1.5` / `2` (`fw_s_used`), the 4 and 5 in the rotor bearing requests and the 5.5 in `gearbox_runner` have no shared key and are left in the code (medium). New key names are the plan's open decision 4.
2. The plan expected 9 fastener sizes "looked up from the bolt table, then overwritten by config values". This class has no bolt lookup: it reads the config values directly, so they are Fixed / config and there is no dead lookup. 15 other 3DP keys (`bearing_ID`, `sun_hub_dia`, `rotor_output_hole_PCD`, the stator step heights, the rotor support bearings, ...) are in the config but the CAD gets those values from the motor, a bearing lookup or a formula; they are listed as code-only `<key>_config` entries.
3. `bearing_mount_thickness` and `ringRadialWidthMM` are read with `.get` (a missing key gives `None` and the gearbox's value, respectively); both are Fixed / config here (SSPG and CPG compute the first).
4. `sspg_design_parameters` (26 keys, none also in the 3DP block) is merged into the design parameters; only `ringRadialWidthMM` reaches the CAD, 24 are never read, and `planetMinDistanceMM`, `sCarrierExtrusion*`, `bearingIDClearanceMM` are read without effect.
5. Types 1 and 2 share this class and config; type 2's spec (next commit) differs in `fw_s_used` only. The mass code, which differs per type, is out of scope.
6. The runner passes no motor driver: no driver variables exist in the CAD file.
