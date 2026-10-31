# ICPG: variable classification plan

Part of [the plan for all actuators](../PLAN.md). Survey only: nothing in the code, config or CAD output changes on this branch.

## Inventory

- **CAD interface:** `icpg_equations_onshape.txt`, **117 variables**; other files: `icpg_equations.txt` (117)
- **Code:** `internalcompoundPlanetaryActuator` in `ActuatorandGearbox_ICPG.py` (lines 375-1341)
- **Config:** `icpg_params.json`, block(s) read: `cpg_3DP_design_parameters`; search bounds `cpg_optimization_parameters`; gear standard / MIT factors from `motor_config.json`; driver: `omit`
- **Survey draft:** dependent 39, fixed 54, input 19, optimisation 5; 77 names also in SSPG / CPG; 0 alias names (same value written under a second name); 1 flagged by the survey

## Special cases (frameless outrunner, compound)

| Variable(s) | What the code does | Proposed classification |
|---|---|---|
| `stator_*`, `Rotor_*`, `rotor_*` | frameless-motor geometry | Input / motor |
| `Nr` | read from the gearbox (`internalcompoundPlanetaryGearbox.Nr`, set by the optimiser from the coaxial constraint) | Dependent / implicit constraint (the source is the gearbox, not a formula in `setVariables`) |
| `module` | `moduleBig`; one module in the CAD | Optimisation; **bug-18 pattern** (check the ring side, propose `module_b` / `module_s`) |
| `pressure_angle` | `pressure_angle (rad) × 180/π` | Fixed / gear standard (the survey's "formula" guess is the unit conversion) |
| `fw_s_calc`, `fw_p_b`, `fw_r` | MIT stress rule (two meshes) with the **stator-height width cap** (`gear_axial_margin_mm`, `planet_step_gap_mm`) and the CPG-style planet-bearing minimum | Dependent / stress rule |
| `fw_p_s` | `fw_r + clearance_planet` (from the config directly) | Dependent / formula (as CPG) |
| `fw_s_used` | **two-case floor rule**: the motor height when the stator leaves less than 2 × 1.5 mm around the bearing, else the stack | Dependent / formula (two-case) |
| `sun_hub_dia` | capped at `Rotor_OD` (`min`-style two-case) | Dependent / formula (two-case) |
| `driver_*` (6) | from **the gearbox config** (`icpg_params.json`), not from `Motor_drivers` (the runner passes no driver) | **Input / driver** for consistency with the other types, source = config, **medium** (decide in review: Input or Fixed) |
| `case_mounting_wrench_size`, `case_mounting_hole_allen_socket_dia` | **config values** (not the bolt lookup used elsewhere) | Fixed / config; note: inconsistent with the other types' lookups |

## Hard-coded numbers (medium; candidates for the config)

| Where | Number | Proposed key |
|---|---|---|
| planet-bearing minimum (L919-923) | 2/3, 1/3 | `planet_bearing_gap` (gap, gap/2 as CPG) |
| `fw_s_used` floor condition (stator clearance < `1.5 × 2`) | 2 | review: geometry or tuning? |
| mass code: bolt bosses (`6 × π × … (7.5/2000)² − (3/2000)²`), casing bearing recess (10 mm), `+ 3` mm ring-bolt length, `1.5 × 4` margins, sun-shaft bearing 4 g | various | mass-only list |

## Config (`icpg_params.json`)
- Reads the block `cpg_3DP_design_parameters` (same block name as CPG, different file); `cpg_design_parameters` (19 keys) is **not read** → unused block.
- Code-only keys: `ringRadialWidthMM`, `planetMinDistanceMM`, `sCarrierExtrusion*`, `bearingIDClearanceMM`, `gear_axial_margin_mm`, `planet_step_gap_mm`, `carrier_trapezoidal_support_hole_wrench_size` (read but not written).
- **Never used:** `sun_sec_carrier_bearing_massKG`.
- The config file for gear standard / MIT factors is `motor_config.json` (not `config.json`).

## Test plan
- Registry: compound setter (as CPG); RO100 / RO80; 3 golden designs.
- Extra gear sets for `fw_s_used` (floor / no floor) and `sun_hub_dia` (capped / not).
- Specific: stress-rule widths with the cap, the planet-bearing gap.

## Risks / notes
- Effort: ~1.5 h.

## Survey draft: every variable

Automatic first pass from the code (the special cases above take precedence). Category guesses come from the source of each value; *flags* mark hard-coded numbers, several assignments or a writer expression. The final category, sub-type, `depends_on`, confidence and reason are set during the classification itself.

| # | Variable | Draft category / sub-type | Conf. | Line | Code | Flags | SSPG / CPG |
|---|---|---|---|---|---|---|---|
| 1 | `Ns` | optimisation / teeth | high | 424 | `self.internalcompoundPlanetaryGearbox.Ns` |  | sspg: optimisation, cpg: optimisation |
| 2 | `Np_b` | optimisation / teeth | high | 425 | `self.internalcompoundPlanetaryGearbox.NpBig` |  | cpg: optimisation |
| 3 | `Np_s` | optimisation / teeth | high | 426 | `self.internalcompoundPlanetaryGearbox.NpSmall` |  | cpg: optimisation |
| 4 | `Nr` | dependent / implicit constraint? | medium | 427 | `self.internalcompoundPlanetaryGearbox.Nr` | Nr read from the gearbox | sspg: dependent, cpg: dependent |
| 5 | `num_planet` | optimisation / planets | high | 428 | `self.internalcompoundPlanetaryGearbox.numPlanet` |  | sspg: optimisation, cpg: optimisation |
| 6 | `module` | optimisation / module | high | 429 | `self.internalcompoundPlanetaryGearbox.moduleBig` |  | sspg: optimisation, cpg: optimisation |
| 7 | `pressure_angle` | dependent / formula | high | 433 | `self.pressure_angle * 180 / np.pi` |  | sspg: fixed, cpg: fixed |
| 8 | `h_a` | dependent / formula | high | 436 | `1    * self.module` |  | sspg: dependent, cpg: dependent |
| 9 | `h_b` | dependent / formula | high | 437 | `1.25 * self.module` |  | sspg: dependent, cpg: dependent |
| 10 | `clr_tip_root` | dependent / formula | high | 439 | `self.h_f - self.h_a` |  | sspg: dependent, cpg: dependent |
| 11 | `dp_s` | dependent / formula | high | 442 | `self.module * self.Ns` |  | sspg: dependent, cpg: dependent |
| 12 | `db_s` | dependent / formula | high | 443 | `self.dp_s * np.cos(self.pressure_angle)` |  | sspg: dependent, cpg: dependent |
| 13 | `fw_s_calc` | dependent / stress rule (face width) | high | 446 | `self.internalcompoundPlanetaryGearbox.fwSunMM` |  | sspg: dependent, cpg: dependent |
| 14 | `alpha_s` | dependent / formula | high | 444 | `(np.sqrt(self.dp_s**2 - self.db_s**2) / self.db_s) * 180 / np.pi - self.pressure_angle_deg` |  | sspg: dependent, cpg: dependent |
| 15 | `beta_s` | dependent / formula | high | 445 | `(360 / (4 * self.Ns) - self.alpha_s) * 2` |  | sspg: dependent, cpg: dependent |
| 16 | `dp_p_b` | dependent / formula | high | 449 | `self.module * self.Np_b` |  | cpg: dependent |
| 17 | `db_p_b` | dependent / formula | high | 450 | `self.dp_p_b * np.cos(self.pressure_angle)` |  | cpg: dependent |
| 18 | `fw_p_s` | fixed / config | high | 467 | `self.fw_r + self.design_params["clearance_planet"]` |  | cpg: dependent |
| 19 | `alpha_p_b` | dependent / formula | high | 451 | `(np.sqrt(self.dp_p_b**2 - self.db_p_b**2) / self.db_p_b) * 180 / np.pi - self.pressure_angle_deg` |  | cpg: dependent |
| 20 | `beta_p_b` | dependent / formula | high | 452 | `(360 / (4 * self.Np_b) - self.alpha_p_b) * 2` |  | cpg: dependent |
| 21 | `h_f` | dependent / formula | high | 438 | `1.25 * self.module` |  | sspg: dependent, cpg: dependent |
| 22 | `dp_r` | dependent / formula | high | 456 | `self.module * self.Nr` |  | sspg: dependent, cpg: dependent |
| 23 | `db_r` | dependent / formula | high | 457 | `self.dp_r * np.cos(self.pressure_angle)` |  | sspg: dependent, cpg: dependent |
| 24 | `fw_r` | dependent / stress rule (face width) | high | 460 | `self.internalcompoundPlanetaryGearbox.fwRingMM` |  | sspg: dependent, cpg: dependent |
| 25 | `alpha_r` | dependent / formula | high | 458 | `(np.sqrt(self.dp_r**2 - self.db_r**2) / self.db_r) * 180 / np.pi - self.pressure_angle_deg` |  | sspg: dependent, cpg: dependent |
| 26 | `beta_r` | dependent / formula | high | 459 | `(360 / (4 * self.Nr) + self.alpha_r) * 2` |  | sspg: dependent, cpg: dependent |
| 27 | `bearing_ID` | dependent / lookup (bearing) | high | 607 | `outer_bearing.getBearingIDMM()` |  | sspg: dependent, cpg: dependent |
| 28 | `bearing_OD` | dependent / lookup (bearing) | high | 608 | `outer_bearing.getBearingODMM()` |  | sspg: dependent, cpg: dependent |
| 29 | `bearing_height` | dependent / lookup (bearing) | high | 609 | `outer_bearing.getBearingWidthMM()` |  | sspg: dependent, cpg: dependent |
| 30 | `clearance_planet` | fixed / config | high | 470 | `self.design_params["clearance_planet"]` |  | sspg: fixed, cpg: fixed |
| 31 | `sec_carrier_thickness` | fixed / config | high | 557 | `self.design_params["sec_carrier_thickness"]` |  | sspg: fixed, cpg: fixed |
| 32 | `sun_coupler_hub_thickness` | fixed / config | high | 521 | `self.design_params["sun_coupler_hub_thickness"]` |  | sspg: fixed, cpg: fixed |
| 33 | `rotor_mount_hole_PCD` | input / motor | high | 500 | `self.motor.getRotorMountHolePCDMM()` |  |  |
| 34 | `rotor_mount_hole_dia` | input / motor | high | 501 | `self.motor.getRotorMountHoleDiaMM()` |  |  |
| 35 | `rotor_mount_hole_num` | input / motor | high | 502 | `self.motor.getMotorRotorHoleNum()` |  |  |
| 36 | `planet_pin_bolt_dia` | fixed / config | high | 506 | `self.design_params["planet_pin_bolt_dia"]` |  | sspg: fixed, cpg: fixed |
| 37 | `planet_pin_socket_head_dia` | dependent / lookup (bolt/nut) | high | 514 | `planet_pin_bolt.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 38 | `carrier_PCD` | dependent / formula | high | 604 | `self.module * (self.Ns + self.Np_b)` |  | sspg: dependent, cpg: dependent |
| 39 | `planet_shaft_dia` | fixed / config | high | 507 | `self.design_params["planet_shaft_dia"]` |  | sspg: fixed, cpg: fixed |
| 40 | `planet_shaft_step_offset` | fixed / config | high | 508 | `self.design_params["planet_shaft_step_offset"]` |  | sspg: fixed, cpg: fixed |
| 41 | `carrier_trapezoidal_support_sun_offset` | fixed / config | high | 558 | `self.design_params["carrier_trapezoidal_support_sun_offset"]` |  | sspg: fixed, cpg: fixed |
| 42 | `carrier_trapezoidal_support_hole_PCD_offset_bearing_ID` | fixed / config | high | 559 | `self.design_params["carrier_trapezoidal_support_hole_PCD_offset_bearing_ID"]` |  | sspg: fixed, cpg: fixed |
| 43 | `carrier_trapezoidal_support_hole_dia` | fixed / config | high | 560 | `self.design_params["carrier_trapezoidal_support_hole_dia"]` |  | sspg: fixed, cpg: fixed |
| 44 | `carrier_trapezoidal_support_hole_socket_head_dia` | dependent / lookup (bolt/nut) | high | 564 | `carrier_trap_hole.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 45 | `carrier_bearing_step_width` | fixed / config | high | 561 | `self.design_params["carrier_bearing_step_width"]` |  | sspg: fixed, cpg: fixed |
| 46 | `standard_clearance_1_5mm` | fixed / config | high | 471 | `self.design_params["standard_clearance_1_5mm"]` |  | sspg: fixed, cpg: fixed |
| 47 | `standard_fillet_1_5mm` | fixed / config | high | 472 | `self.design_params["standard_fillet_1_5mm"]` |  | sspg: fixed, cpg: fixed |
| 48 | `sun_shaft_bearing_OD` | fixed / config | high | 519 | `self.design_params["sun_shaft_bearing_OD"]` |  | sspg: fixed, cpg: fixed |
| 49 | `sun_shaft_bearing_width` | fixed / config | high | 520 | `self.design_params["sun_shaft_bearing_width"]` |  | sspg: fixed, cpg: fixed |
| 50 | `sun_shaft_bearing_ID` | fixed / config | high | 518 | `self.design_params["sun_shaft_bearing_ID"]` |  | sspg: fixed, cpg: fixed |
| 51 | `standard_bearing_insertion_chamfer` | fixed / config | high | 473 | `self.design_params["standard_bearing_insertion_chamfer"]` |  | sspg: fixed, cpg: fixed |
| 52 | `carrier_trapezoidal_support_hole_wrench_size` | dependent / lookup (bolt/nut) | high | 565 | `carrier_trap_hole.nut_width_across_flats` |  | sspg: dependent, cpg: dependent |
| 53 | `planet_pin_bolt_wrench_size` | dependent / lookup (bolt/nut) | high | 515 | `planet_pin_bolt.nut_width_across_flats` |  | sspg: dependent, cpg: dependent |
| 54 | `planet_bearing_OD` | fixed / config | high | 509 | `self.design_params["planet_bearing_OD"]` |  | sspg: fixed, cpg: fixed |
| 55 | `planet_bearing_width` | fixed / config | high | 510 | `self.design_params["planet_bearing_width"]` |  | sspg: fixed, cpg: fixed |
| 56 | `planet_bore` | fixed / config | high | 511 | `self.design_params["planet_bore"]` |  | sspg: fixed, cpg: fixed |
| 57 | `sun_hub_dia` | dependent / formula | high | 601 | `cap if sun_hub_dia_calc > self.Rotor_OD else sun_hub_dia_calc` |  | sspg: dependent, cpg: dependent |
| 58 | `sun_central_bolt_dia` | fixed / config | high | 522 | `self.design_params["sun_central_bolt_dia"]` |  | sspg: fixed, cpg: fixed |
| 59 | `sun_central_bolt_socket_head_dia` | dependent / lookup (bolt/nut) | high | 525 | `sun_central_bolt.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 60 | `fw_p_b` | dependent / stress rule (face width) | high | 453 | `self.internalcompoundPlanetaryGearbox.fwPlanetBigMM` |  | cpg: dependent |
| 61 | `fw_s_used` | dependent / formula | high | 624, 626 | `fw_s_used_floor ‖ fw_s_used_calc` | 2 assignments (two-case rule or reassigned) | sspg: dependent, cpg: dependent |
| 62 | `bearing_retainer_thickness` | fixed / config | high | 552 | `self.design_params["bearing_retainer_thickness"]` |  | sspg: fixed, cpg: fixed |
| 63 | `dp_p_s` | dependent / formula | high | 463 | `self.module * self.Np_s` |  | cpg: dependent |
| 64 | `db_p_s` | dependent / formula | high | 464 | `self.dp_p_s * np.cos(self.pressure_angle)` |  | cpg: dependent |
| 65 | `alpha_p_s` | dependent / formula | high | 465 | `(np.sqrt(self.dp_p_s**2 - self.db_p_s**2) / self.db_p_s) * 180 / np.pi - self.pressure_angle_deg` |  | cpg: dependent |
| 66 | `beta_p_s` | dependent / formula | high | 466 | `(360 / (4 * self.Np_s) - self.alpha_p_s) * 2` |  | cpg: dependent |
| 67 | `tight_clearance_3DP` | fixed / config | high | 474 | `self.design_params["tight_clearance_3DP"]` |  | sspg: fixed, cpg: fixed |
| 68 | `loose_clearance_3DP` | fixed / config | high | 475 | `self.design_params["loose_clearance_3DP"]` |  | sspg: fixed, cpg: fixed |
| 69 | `sun_bottom_casing_bearing_ID` | dependent / lookup (bearing) | high | 542 | `sun_bottom_casing_bearing.getBearingIDMM()` |  |  |
| 70 | `sun_bottom_casing_bearing_OD` | dependent / lookup (bearing) | high | 543 | `sun_bottom_casing_bearing.getBearingODMM()` |  |  |
| 71 | `sun_bottom_casing_bearing_height` | dependent / lookup (bearing) | high | 541 | `sun_bottom_casing_bearing.getBearingWidthMM()` |  |  |
| 72 | `sun_gear_rotor_nut_wrench_size` | fixed / config | high | 528 | `self.design_params["sun_gear_rotor_nut_wrench_size"]` |  |  |
| 73 | `sun_gear_rotor_nut_height` | fixed / config | high | 529 | `self.design_params["sun_gear_rotor_nut_height"]` |  |  |
| 74 | `stator_OD` | input / motor | high | 483 | `self.motor.getStatorODMM()` |  |  |
| 75 | `stator_ID` | input / motor | high | 484 | `self.motor.getStatorIDMM()` |  |  |
| 76 | `stator_height` | input / motor | high | 485 | `self.motor.getStatorHeightMM()` |  |  |
| 77 | `stator_mounting_holes_PCD` | input / motor | high | 486 | `self.motor.getStatorMountingHolePCD()` |  |  |
| 78 | `stator_top_rotor_top_offset` | input / motor | high | 489 | `self.motor.getStatorTopRotorTopOffset()` |  |  |
| 79 | `stator_mounting_hole_allen_socket_head_dia` | fixed / config | high | 504 | `self.design_params["stator_mounting_hole_allen_socket_head_dia"]` |  |  |
| 80 | `stator_hole_dia` | input / motor | high | 490 | `self.motor.getStatorHoleDia()` |  |  |
| 81 | `bearing_retainer_hole_dia` | fixed / config | high | 553 | `self.design_params["bearing_retainer_hole_dia"]` |  |  |
| 82 | `bearing_retainer_hole_num` | fixed / config | high | 554 | `self.design_params["bearing_retainer_hole_num"]` |  |  |
| 83 | `Rotor_ID` | input / motor | high | 494 | `self.motor.getRotorIDMM()` |  |  |
| 84 | `Rotor_OD` | input / motor | high | 493 | `self.motor.getRotorODMM()` |  |  |
| 85 | `Rotor_height` | input / motor | high | 495 | `self.motor.getRotorHeightMM()` |  |  |
| 86 | `Rotor_bottom_ID` | input / motor | high | 496 | `self.motor.getRotorBottomIDMM()` |  |  |
| 87 | `rotor_bottom_thickness` | input / motor | high | 497 | `self.motor.getRotorBottomThicknessMM()` |  |  |
| 88 | `Rotor_csk_head_upper_dia` | input / motor | high | 498 | `self.motor.getRotorCSKHeadUpperDiaMM()` |  |  |
| 89 | `Rotor_csk_head_height` | input / motor | high | 499 | `self.motor.getRotorCSKHeadHeightMM()` |  |  |
| 90 | `ring_gear_thickness_mounting_casing` | fixed / config | high | 574 | `self.design_params["ring_gear_thickness_mounting_casing"]` |  |  |
| 91 | `motor_casing_thickness` | fixed / config | high | 573 | `self.design_params["Motor_case_thickness"]` |  |  |
| 92 | `sun_sec_carrier_bearing_height` | fixed / config | high | 547 | `self.design_params["sun_sec_carrier_bearing_height"]` |  |  |
| 93 | `sun_sec_carrier_bearing_ID` | fixed / config | high | 548 | `self.design_params["sun_sec_carrier_bearing_ID"]` |  |  |
| 94 | `sun_sec_carrier_bearing_OD` | fixed / config | high | 549 | `self.design_params["sun_sec_carrier_bearing_OD"]` |  |  |
| 95 | `motor_height` | input / motor | high | 480 | `self.motor.getMotorHeightMM()` |  | sspg: input, cpg: input |
| 96 | `motor_stator_extrusion_dia` | input / motor | high | 487 | `self.motor.getMotorStatorExtrusionDia()` |  |  |
| 97 | `motor_stator_extrusion_depth` | input / motor | high | 488 | `self.motor.getMotorStatorExtrusionDepth()` |  |  |
| 98 | `case_mounting_hole_dia` | fixed / config | high | 568 | `self.design_params["case_mounting_hole_dia"]` |  | sspg: fixed, cpg: fixed |
| 99 | `case_mounting_hole_wrench_size` | fixed / config | high | 569 | `self.design_params["case_mounting_hole_wrench_size"]` |  |  |
| 100 | `case_mounting_hole_wrench_thickness` | fixed / config | high | 570 | `self.design_params["case_mounting_hole_wrench_thickness"]` |  |  |
| 101 | `driver_mount_PCD` | fixed / config | high | 577 | `self.design_params["driver_mount_PCD"]` |  |  |
| 102 | `driver_mount_hole_dia` | fixed / config | high | 578 | `self.design_params["driver_mount_hole_dia"]` |  |  |
| 103 | `driver_mount_wrench_size` | fixed / config | high | 579 | `self.design_params["driver_mount_wrench_size"]` |  |  |
| 104 | `driver_mount_wrench_thickness` | fixed / config | high | 580 | `self.design_params["driver_mount_wrench_thickness"]` |  |  |
| 105 | `case_mounting_wrench_size` | fixed / config | high | 581 | `self.design_params["case_mounting_wrench_size"]` |  | sspg: dependent, cpg: dependent |
| 106 | `case_mounting_hole_allen_socket_dia` | fixed / config | high | 582 | `self.design_params["case_mounting_hole_allen_socket_dia"]` |  | sspg: dependent, cpg: dependent |
| 107 | `clearance_case_mount_holes_shell_thickness` | fixed / config | high | 583 | `self.design_params["clearance_case_mount_holes_shell_thickness"]` |  | sspg: fixed, cpg: fixed |
| 108 | `motor_case_mounting_hole_dia` | fixed / config | high | 584 | `self.design_params["motor_case_mounting_hole_dia"]` |  |  |
| 109 | `motor_case_wrench_size` | fixed / config | high | 585 | `self.design_params["motor_case_wrench_size"]` |  |  |
| 110 | `central_hole_offset_from_motor_mount_PCD` | fixed / config | high | 586 | `self.design_params["central_hole_offset_from_motor_mount_PCD"]` |  | sspg: fixed, cpg: fixed |
| 111 | `driver_mount_thickness` | fixed / config | high | 587 | `self.design_params["driver_mount_thickness"]` |  | sspg: input, cpg: input |
| 112 | `driver_mount_inserts_OD` | fixed / config | high | 588 | `self.design_params["driver_mount_inserts_OD"]` |  | sspg: input, cpg: input |
| 113 | `driver_upper_holes_dist_from_center` | fixed / config | high | 589 | `self.design_params["driver_upper_holes_dist_from_center"]` |  | sspg: input, cpg: input |
| 114 | `driver_lower_holes_dist_from_center` | fixed / config | high | 590 | `self.design_params["driver_lower_holes_dist_from_center"]` |  | sspg: input, cpg: input |
| 115 | `driver_mount_height` | fixed / config | high | 591 | `self.design_params["driver_mount_height"]` |  | sspg: input, cpg: input |
| 116 | `motor_mount_driver_hole_num` | fixed / config | high | 592 | `self.design_params["motor_mount_driver_hole_num"]` |  |  |
| 117 | `driver_side_holes_dist_from_center` | fixed / config | high | 593 | `self.design_params["driver_side_holes_dist_from_center"]` |  | sspg: input, cpg: input |

## Config accounting

| Block | Keys | Read by this type | Read but not written to the CAD | Never used |
|---|---|---|---|---|
| `cpg_design_parameters` | 19 | **no** | ringRadialWidthMM, planetMinDistanceMM, sCarrierExtrusionDiaMM, sCarrierExtrusionClearanceMM, bearingIDClearanceMM | baseThicknessMM, sCarrierThicknessMM, mainCoverThicknessMM, planetBoreMM, sunBoreMM, couplerRadiusMM, couplerThicknessMM, couplerShaftHeightMM, clearanceMotorandCaseMM, clearanceCarrierPlanetMM, upperHousingHeight, clearanceSCarrierMotorMM, carrierIDClearanceMM, sCarrierIDClearanceMM |
| `cpg_optimization_parameters` | 10 | yes | GEAR_RATIO_MIN, GEAR_RATIO_MAX, GEAR_RATIO_STEP, MODULE_MIN, MODULE_MAX, NUM_PLANET_MIN, NUM_PLANET_MAX, NUM_TEETH_SUN_MIN, NUM_TEETH_PLANET_MIN, MAX_GB_DIA_MULT_FACTOR | — |
| `cpg_3DP_design_parameters` | 62 | yes | ringRadialWidthMM, planetMinDistanceMM, sCarrierExtrusionDiaMM, sCarrierExtrusionClearanceMM, bearingIDClearanceMM, carrier_trapezoidal_support_hole_wrench_size, gear_axial_margin_mm, planet_step_gap_mm | sun_sec_carrier_bearing_massKG |


## Result (classification done)

Spec: [`config_files/variables/icpg_variables.json`](../../../config_files/variables/icpg_variables.json), page [`docs/variables/icpg.md`](../icpg.md) (generated). Tests: the generic `tests/test_variable_categories.py` (ICPG registered in `tests/variable_helpers.py`) and `tests/test_variable_categories_icpg.py`.

**Counts (CAD variables, 117):** input 25, optimisation 5, fixed 48, dependent 39 (24 formula, 11 lookup, 3 stress rule, 1 implicit constraint). The draft counted the six driver dimensions as fixed (input 19 / fixed 54); they are Input / driver with source = this gearbox's config, as the plan proposes. **Code-only values: 29** (fixed 22, dependent 4: `pressure_angle_rad`, `maxGearboxDiameter`, `actuator_width`, `fw_limit_mm`; input 2; optimisation 1: `module_s`), including `sun_sec_carrier_bearing_massKG` (never used) and `carrier_trapezoidal_support_hole_wrench_size_config` (read but the CAD uses the bolt lookup). Confidence: 135 high, 11 medium, 0 low.

**Medium-confidence entries**
- The six `driver_*` dimensions (`driver_mount_thickness`, `driver_mount_inserts_OD`, `driver_upper_holes_dist_from_center`, `driver_lower_holes_dist_from_center`, `driver_mount_height`, `driver_side_holes_dist_from_center`; Input / driver): the runner passes no driver (`driver=OMIT`), so the values come from `icpg_params.json`, not from `Motor_drivers`. Plan decision 3: Input (as here, for consistency) or Fixed.
- `sun_hub_dia` (Dependent / formula): the rotor's mount-hole circle plus a hard-coded `x 4` clearance margin (the shared sun-hub item), capped at the rotor OD less two clearances.
- `fw_s_used` (Dependent / formula): a two-case floor rule, the motor height when the stator's radial clearance around the output bearing is below a hard-coded `2 x standard_clearance_1_5mm` and the stack is shorter; the plan asks whether the 2 is geometry or tuning.
- `sun_bottom_casing_bearing_ID` / `_OD` / `_height` (Dependent / lookup): the bearing request is the sun-hub size with the same hard-coded `x 4` margin.

**Config key added** to `cpg_3DP_design_parameters` in `icpg_params.json` (shared name, value that keeps every output bit-identical): `planet_bearing_gap` = 1.0 (was `standard_clearance_1_5mm * 2 / 3` for the pair and `* 1 / 3` per gear; the code reads `planet_bearing_gap` and `planet_bearing_gap / 2`), in `mitStressAnalysisMinFacewidth`. The other shared keys have no counterpart (no motor-case clearance rule, no `bearing_mount_thickness`). Tests show `planet_bearing_gap`, `gear_axial_margin_mm` and `planet_step_gap_mm` (the stator-height cap) each drive exactly their CAD variables.

**Shared tooling changed:** `tests/variable_helpers.py` (ICPG entry and a branch rule; ICPG reads its gear standard and safety factors from `motor_config.json`).

**Results:** `python tests/golden/golden.py check`: All 58 cases match the baseline. `python -m pytest -q`: 1085 passed. No `CADs/` file, no golden baseline touched.

**Open questions**
1. **Bug-18 pattern**: `module` is `moduleBig`; the small planet and the ring are drawn with it although the stress rule uses `moduleSmall`. Logged, not fixed: `module_s` is a code-only optimisation entry. The plan's `module_b` / `module_s` code change is still open (plan decision 5).
2. Driver dimensions: Input / driver (medium) or Fixed (plan decision 3).
3. **The sun-hub cap is unreachable**: `sun_hub_dia` is capped at the rotor OD, but the mount-hole circle + hole diameter + `4 x standard_clearance_1_5mm` is 84 of 113.5 mm (RO100), 72 of 92.6 (RO80) and 55 of 73.8 (RO60), so the cap's branch never applies for any motor in `motors.json`; the branch test lists only the floor rule and the stator-height cap.
4. `case_mounting_wrench_size` and `case_mounting_hole_allen_socket_dia` are config values (Fixed), not bolt lookups as in other types; the `carrier_trapezoidal_support_hole_wrench_size` config value is read but the CAD uses the lookup.
5. `cpg_design_parameters` (19 keys) is never read; listed as an unused block. `sun_sec_carrier_bearing_massKG` is in the config and never used.
6. The mass-only hard-coded numbers (bolt bosses, the 10 mm casing recess, `+ 3` mm ring-bolt length, `1.5 x 4` margins, a 4 g sun-shaft bearing) stay out of scope.
