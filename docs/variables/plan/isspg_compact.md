# ISSPG compact: variable classification plan

Part of [the plan for all actuators](../PLAN.md). Survey only: nothing in the code, config or CAD output changes on this branch.

## Inventory

- **CAD interface:** `isspg_compact_equations_onshape.txt`, **145 variables**; other files: none
- **Code:** `internalsingleStagePlanetaryActuator` in `ActuatorAndGearbox_ISSPG_compact.py` (lines 472-1686)
- **Config:** `isspg_params.json`, block(s) read: `isspg_3DP_design_parameters`; search bounds `isspg_optimization_parameters`; gear standard / MIT factors from `config.json`; driver: `OdrivePro`
- **Survey draft:** dependent 62, fixed 57, input 22, optimisation 4; 69 names also in SSPG / CPG; 0 alias names (same value written under a second name); 4 flagged by the survey

## Special cases (frameless outrunner; shared with ISSPG inside unless noted)

| Variable(s) | What the code does | Proposed classification |
|---|---|---|
| `stator_*`, `rotor_*`, `motor_rotor_*`, `motor_stator_*` | frameless-motor geometry from `motors.json` | Input / motor |
| `motor_OD`, `motor_height` | `self.motorODMM` / `self.motorHeightMM` (from `motor.getMotorODMM()` etc.) | Input / motor (the survey's "formula" guess is wrong: the attribute is read straight from the motor) |
| `wire_slot_length`, `wire_slot_radius` | **config** values here (frameless motors have no wire-slot data) | Fixed / config (differs from SSPG/CPG's Input: correct for this type) |
| `clearance_motor_and_case` | a **config value** here | Fixed / config (differs from SSPG/CPG, where it is computed) |
| `magnet_*` | magnet sizes from the config | Fixed / config |
| `fw_s_calc`, `fw_p`, `fw_r` | MIT stress rule **with the stator-height width cap** (`gear_axial_margin_mm`, torque derating) | Dependent / stress rule (depends also on `stator_height`, `gear_axial_margin_mm`) |
| `carrier_thickness`, `carrier_thickness_mid`, `ring_hub_thickness` | an **iterative / two-case rule**: start with `carrier_thickness_mid = 6`, then if the stack is short of the motor, grow the ring hub; else `ring_hub_thickness = 3` and recompute the carrier | Dependent / formula (two-case); **medium** (hard-coded 6 and 3) |
| `sun_coupler_hub_thickness` | compact: `3 + bearing_step_width/2 + sun2_bearing_width`; inside: `input_bearing_width + bearing_step_width` | Dependent / formula; compact **medium** (hard-coded 3); SSPG/CPG have it as config |
| `sun_hub_dia` | compact: rotor hole PCD + nut + `1.5 × 4`; inside: `= input_bearing_ID` | Dependent / formula; compact **medium** (× 4, shared item) |
| `input_bearing_ID/OD/width` | compact: **config**; inside: **catalogue lookup** | compact Fixed / config; inside Dependent / lookup |
| `rotorCSKHeadUpperDiaMM`, `rotorCSKHeadHeightMM` | **inside only** | classify in the inside spec |
| `sun1_*`, `sun2_*`, `output_bearing_*` | sun bearings (config / lookup) and the output bearing (lookup) | Fixed / config or Dependent / lookup per line |

## Hard-coded numbers (medium; candidates for the config)

| Where | Number | Proposed key |
|---|---|---|
| `carrier_thickness_mid` (L775 / inside L782) | 6 | new: `carrier_thickness_mid_min`? (decide in review) |
| `ring_hub_thickness` (L787 / inside L794) | 3 | new: `ring_hub_thickness_min`? |
| `sun_coupler_hub_thickness` (compact L801) | 3 | new key or reuse; decide in review |
| `sun_hub_dia` (compact L763) | 4 | shared `sun_hub_dia` margin item |
| planet-bearing minimum (L1178-1179 / inside L1185-1186) | 2/3 | `planet_bearing_gap` |
| mass code: `input_bearing_structure_OD` (× 4 × 2), `sun_hub_carrier_ID/OD` (× 4, × 5), `sec_carrier_bottom_ID/OD` (× 3, × 4), motor-case mounting volume (6), bearing masses (0.004 kg) | various | mass-only; list for the metal-mass work |

## Config (`isspg_params.json`, shared by compact and inside)
- Config values that the CAD **does not use** because the code computes the CAD value: `sun_hub_dia`, `sun_coupler_hub_thickness`, `ring_hub_thickness`, `case_mounting_hole_shift`, `stator_hole_PCD`, `stator_hole_dia`, `ring_hub_to_case_hole_nut_*` (and inside: `input_bearing_*`). They are read but overwritten or unused → list them as code-only "read but not used for the CAD" (low-risk tidy-up later, not in this plan).
- Code-only: `planetMinDistanceMM`, `sCarrierExtrusion*`, `gear_axial_margin_mm` (width cap).
- Optimisation block: 9 search bounds.

## Test plan
- Registry entries for both (same setter as SSPG; the frameless motor RO100/RO80; 4 golden designs each).
- Extra gear sets for the carrier / ring-hub two-case rule (both branches).
- Specific: stress-rule widths with the width cap (cap active / not active), each moved key.

## Risks / notes
- The two variants share `isspg_params.json`; moved keys must work for both (same names, same values).
- Effort: ~1.5 h each (inside reuses most of compact).

## Survey draft: every variable

Automatic first pass from the code (the special cases above take precedence). Category guesses come from the source of each value; *flags* mark hard-coded numbers, several assignments or a writer expression. The final category, sub-type, `depends_on`, confidence and reason are set during the classification itself.

| # | Variable | Draft category / sub-type | Conf. | Line | Code | Flags | SSPG / CPG |
|---|---|---|---|---|---|---|---|
| 1 | `Ns` | optimisation / teeth | high | 539 | `self.planetaryGearbox.Ns` |  | sspg: optimisation, cpg: optimisation |
| 2 | `Np` | optimisation / teeth | high | 540 | `self.planetaryGearbox.Np` |  | sspg: optimisation |
| 3 | `Nr` | dependent / formula | high | 541 | `self.Ns + 2 * self.Np` |  | sspg: dependent, cpg: dependent |
| 4 | `module` | optimisation / module | high | 542 | `self.planetaryGearbox.module` |  | sspg: optimisation, cpg: optimisation |
| 5 | `num_planet` | optimisation / planets | high | 543 | `self.planetaryGearbox.numPlanet` |  | sspg: optimisation, cpg: optimisation |
| 6 | `pressure_angle_deg` | fixed / gear standard | high | 550 | `self.planetaryGearbox.getPressureAngleRad() * 180 / np.pi` |  |  |
| 7 | `clearance_planet` | fixed / config | high | 559 | `self.design_params["clearance_planet"]` |  | sspg: fixed, cpg: fixed |
| 8 | `clearance_case_mount_holes_shell_thickness` | fixed / config | high | 560 | `self.design_params["clearance_case_mount_holes_shell_thickness"]` |  | sspg: fixed, cpg: fixed |
| 9 | `standard_clearance_1_5mm` | fixed / config | high | 561 | `self.design_params["standard_clearance_1_5mm"]` |  | sspg: fixed, cpg: fixed |
| 10 | `standard_clearance_2_mm` | fixed / config | high | 562 | `self.design_params["standard_clearance_2_mm"]` |  |  |
| 11 | `standard_fillet_1_5mm` | fixed / config | high | 564 | `self.design_params["standard_fillet_1_5mm"]` |  | sspg: fixed, cpg: fixed |
| 12 | `standard_fillet_3_mm` | fixed / config | high | 565 | `self.design_params["standard_fillet_3_mm"]` |  |  |
| 13 | `standard_bearing_insertion_chamfer` | fixed / config | high | 566 | `self.design_params["standard_bearing_insertion_chamfer"]` |  | sspg: fixed, cpg: fixed |
| 14 | `bearingIDClearanceMM` | fixed / config | high | 567 | `self.design_params["bearingIDClearanceMM"]` |  | sspg: fixed, cpg: fixed |
| 15 | `tight_clearance_3DP` | fixed / config | high | 568 | `self.design_params["tight_clearance_3DP"]` |  | sspg: fixed, cpg: fixed |
| 16 | `loose_clearance_3DP` | fixed / config | high | 569 | `self.design_params["loose_clearance_3DP"]` |  | sspg: fixed, cpg: fixed |
| 17 | `bearing_step_width` | fixed / config | high | 570 | `self.design_params["bearing_step_width"]` |  |  |
| 18 | `sun1_bearing_ID` | fixed / config | high | 573 | `self.design_params["sun1_bearing_ID"]` |  |  |
| 19 | `sun1_bearing_OD` | fixed / config | high | 574 | `self.design_params["sun1_bearing_OD"]` |  |  |
| 20 | `sun_coupler_hub_thickness` | dependent / formula | medium | 801 | `3 + self.bearing_step_width/2 + self.sun2_bearing_width` | numbers 3 | sspg: fixed, cpg: fixed |
| 21 | `sun1_bearing_width` | fixed / config | high | 575 | `self.design_params["sun1_bearing_width"]` |  |  |
| 22 | `sun_central_bolt_dia` | fixed / config | high | 576 | `self.design_params["sun_central_bolt_dia"]` |  | sspg: fixed, cpg: fixed |
| 23 | `case_mounting_surface_height` | fixed / config | high | 579 | `self.design_params["case_mounting_surface_height"]` |  | sspg: fixed, cpg: fixed |
| 24 | `case_mounting_hole_dia` | fixed / config | high | 580 | `self.design_params["case_mounting_hole_dia"]` |  | sspg: fixed, cpg: fixed |
| 25 | `motor_case_thickness` | fixed / config | high | 581 | `self.design_params["motor_case_thickness"]` |  |  |
| 26 | `output_mount_hole_dia` | fixed / config | high | 584 | `self.design_params["output_mount_hole_dia"]` |  |  |
| 27 | `motor_case_OD_base_to_chamfer` | fixed / config | high | 585 | `self.design_params["motor_case_OD_base_to_chamfer"]` |  |  |
| 28 | `pattern_offset_from_motor_case_OD_base` | fixed / config | high | 586 | `self.design_params["pattern_offset_from_motor_case_OD_base"]` |  | sspg: fixed, cpg: fixed |
| 29 | `pattern_bulge_dia` | fixed / config | high | 587 | `self.design_params["pattern_bulge_dia"]` |  | sspg: fixed, cpg: fixed |
| 30 | `pattern_num_bulge` | fixed / config | high | 588 | `self.design_params["pattern_num_bulge"]` |  | sspg: fixed, cpg: fixed |
| 31 | `pattern_depth` | fixed / config | high | 589 | `self.design_params["pattern_depth"]` |  | sspg: fixed, cpg: fixed |
| 32 | `clearance_motor_and_case` | fixed / config | high | 590 | `self.design_params["clearance_motor_and_case"]` |  | sspg: dependent, cpg: dependent |
| 33 | `case_mounting_hole_shift` | dependent / formula | high | 591 | `self.case_mounting_hole_dia / 2` |  | sspg: dependent, cpg: dependent |
| 34 | `ring_hub_to_case_hole_num` | fixed / config | high | 592 | `self.design_params["ring_hub_to_case_hole_num"]` |  |  |
| 35 | `ring_hub_to_case_hole_dia` | fixed / config | high | 593 | `self.design_params["ring_hub_to_case_hole_dia"]` |  |  |
| 36 | `case_mounting_hole_allen_socket_dia` | dependent / lookup (bolt/nut) | high | 600 | `case_mounting_hole_bolt.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 37 | `case_mounting_wrench_size` | dependent / lookup (bolt/nut) | high | 601 | `case_mounting_hole_bolt.nut_width_across_flats` |  | sspg: dependent, cpg: dependent |
| 38 | `case_mounting_nut_depth` | dependent / lookup (bolt/nut) | high | 602 | `case_mounting_hole_bolt.nut_thickness` |  |  |
| 39 | `output_mount_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 606 | `output_mount_hole_bolt.nut_width_across_flats` |  |  |
| 40 | `output_mount_hole_nut_depth` | dependent / lookup (bolt/nut) | high | 607 | `output_mount_hole_bolt.nut_thickness` |  |  |
| 41 | `ring_hub_to_case_hole_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 611 | `ring_hub_to_case_hole_bolt.nut_width_across_flats` |  |  |
| 42 | `ring_hub_to_case_hole_nut_depth` | dependent / lookup (bolt/nut) | high | 612 | `ring_hub_to_case_hole_bolt.nut_thickness` |  |  |
| 43 | `planet_pin_bolt_dia` | fixed / config | high | 623 | `self.design_params["planet_pin_bolt_dia"]` |  | sspg: fixed, cpg: fixed |
| 44 | `planet_shaft_step_offset` | fixed / config | high | 625 | `self.design_params["planet_shaft_step_offset"]` |  | sspg: fixed, cpg: fixed |
| 45 | `planet_bearing_OD` | fixed / config | high | 626 | `self.design_params["planet_bearing_OD"]` |  | sspg: fixed, cpg: fixed |
| 46 | `planet_bearing_width` | fixed / config | high | 627 | `self.design_params["planet_bearing_width"]` |  | sspg: fixed, cpg: fixed |
| 47 | `planet_bearing_ID` | fixed / config | high | 628 | `self.design_params["planet_bearing_ID"]` |  |  |
| 48 | `carrier_trapezoidal_support_sun_offset` | fixed / config | high | 631 | `self.design_params["carrier_trapezoidal_support_sun_offset"]` |  | sspg: fixed, cpg: fixed |
| 49 | `carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID` | fixed / config | high | 632 | `self.design_params["carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID"]` |  |  |
| 50 | `carrier_trapezoidal_support_hole_dia` | fixed / config | high | 633 | `self.design_params["carrier_trapezoidal_support_hole_dia"]` |  | sspg: fixed, cpg: fixed |
| 51 | `carrier_trapezoidal_support_hole_socket_head_dia` | dependent / lookup (bolt/nut) | high | 637 | `carrier_trapezoidal_support_hole.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 52 | `carrier_trapezoidal_support_hole_wrench_size` | dependent / lookup (bolt/nut) | high | 638 | `carrier_trapezoidal_support_hole.nut_width_across_flats` |  | sspg: dependent, cpg: dependent |
| 53 | `carrier_trapezoidal_support_nut_depth` | dependent / lookup (bolt/nut) | high | 639 | `carrier_trapezoidal_support_hole.nut_thickness` |  |  |
| 54 | `planet_pin_socket_head_dia` | dependent / lookup (bolt/nut) | high | 643 | `planet_pin_bolt.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 55 | `planet_pin_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 644 | `planet_pin_bolt.nut_width_across_flats` |  |  |
| 56 | `planet_pin_nut_depth` | dependent / lookup (bolt/nut) | high | 645 | `planet_pin_bolt.nut_thickness` |  |  |
| 57 | `driver_upper_holes_dist_from_center` | input / driver | high | 656 | `self.motor_driver_params["driver_upper_holes_dist_from_center"]` |  | sspg: input, cpg: input |
| 58 | `driver_lower_holes_dist_from_center` | input / driver | high | 657 | `self.motor_driver_params["driver_lower_holes_dist_from_center"]` |  | sspg: input, cpg: input |
| 59 | `driver_side_holes_dist_from_center` | input / driver | high | 658 | `self.motor_driver_params["driver_side_holes_dist_from_center"]` |  | sspg: input, cpg: input |
| 60 | `driver_mount_holes_dia` | input / driver | high | 659 | `self.motor_driver_params["driver_mount_holes_dia"]` |  | sspg: input, cpg: input |
| 61 | `driver_mount_inserts_OD` | input / driver | high | 660 | `self.motor_driver_params["driver_mount_inserts_OD"]` |  | sspg: input, cpg: input |
| 62 | `driver_mount_thickness` | input / driver | high | 661 | `self.motor_driver_params["driver_mount_thickness"]` |  | sspg: input, cpg: input |
| 63 | `driver_mount_height` | input / driver | high | 662 | `self.motor_driver_params["driver_mount_height"]` |  | sspg: input, cpg: input |
| 64 | `motor_mount_driver_hole_dia` | fixed / config | high | 663 | `self.design_params["motor_mount_driver_hole_dia"]` |  |  |
| 65 | `central_hole_offset_from_motor_mount_PCD` | fixed / config | high | 583 | `self.design_params["central_hole_offset_from_motor_mount_PCD"]` |  | sspg: fixed, cpg: fixed |
| 66 | `motor_mount_driver_hole_num` | fixed / config | high | 664 | `self.design_params["motor_mount_driver_hole_num"]` |  |  |
| 67 | `motor_mount_driver_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 668 | `motor_mount_driver_bolt.nut_width_across_flats` |  |  |
| 68 | `motor_mount_driver_nut_depth` | dependent / lookup (bolt/nut) | high | 669 | `motor_mount_driver_bolt.nut_thickness` |  |  |
| 69 | `magnet_mount_hole_dia` | fixed / config | high | 672 | `self.design_params["magnet_mount_hole_dia"]` |  |  |
| 70 | `magnet_thickness` | fixed / config | high | 673 | `self.design_params["magnet_thickness"]` |  |  |
| 71 | `magnet_dia` | fixed / config | high | 674 | `self.design_params["magnet_dia"]` |  |  |
| 72 | `magnet_mount_thickness` | fixed / config | high | 675 | `self.design_params["magnet_mount_thickness"]` |  |  |
| 73 | `magnet_pattern_bulge_dia` | fixed / config | high | 676 | `self.design_params["magnet_pattern_bulge_dia"]` |  |  |
| 74 | `magnet_pattern_bulge_number` | fixed / config | high | 677 | `self.design_params["magnet_pattern_bulge_number"]` |  |  |
| 75 | `magnet_mount_height` | fixed / config | high | 678 | `self.design_params["magnet_mount_height"]` |  |  |
| 76 | `motor_OD` | dependent / formula | high | 681 | `self.motorODMM` |  | sspg: input, cpg: input |
| 77 | `motor_height` | dependent / formula | high | 682 | `self.motorHeightMM` |  | sspg: input, cpg: input |
| 78 | `stator_ID` | input / motor | high | 683 | `self.motor.getStatorIDMM()` |  |  |
| 79 | `motor_rotor_base_thickness` | input / motor | high | 684 | `self.motor.getRotorBottomThicknessMM()` |  |  |
| 80 | `motor_rotor_base_ID` | input / motor | high | 685 | `self.motor.getRotorBottomIDMM()` |  |  |
| 81 | `rotor_height` | input / motor | high | 686 | `self.motor.getRotorHeightMM()` |  |  |
| 82 | `rotor_ID` | input / motor | high | 687 | `self.motor.getRotorIDMM()` |  |  |
| 83 | `motor_stator_extrusion_depth` | input / motor | high | 688 | `self.motor.getMotorStatorExtrusionDepth()` |  |  |
| 84 | `motor_stator_extrusion_dia` | input / motor | high | 689 | `self.motor.getMotorStatorExtrusionDia()` |  |  |
| 85 | `stator_height` | input / motor | high | 690 | `self.motor.getStatorHeightMM()` |  |  |
| 86 | `stator_OD` | input / motor | high | 691 | `self.motor.getStatorODMM()` |  |  |
| 87 | `stator_top_rotor_top_offset` | input / motor | high | 692 | `self.motor.getStatorTopRotorTopOffset()` |  |  |
| 88 | `stator_hole_dia` | input / motor | high | 693 | `self.motor.getStatorHoleDia()` |  |  |
| 89 | `stator_hole_PCD` | input / motor | high | 694 | `self.motor.getStatorMountingHolePCD()` |  |  |
| 90 | `motor_rotor_hole_num` | input / motor | high | 695 | `self.motor.getMotorRotorHoleNum()` |  |  |
| 91 | `motor_rotor_hole_dia` | input / motor | high | 696 | `self.motor.getRotorMountHoleDiaMM()` |  |  |
| 92 | `motor_rotor_hole_PCD` | input / motor | high | 697 | `self.motor.getRotorMountHolePCDMM()` |  |  |
| 93 | `h_a` | dependent / formula | high | 703 | `1 * self.module` |  | sspg: dependent, cpg: dependent |
| 94 | `h_b` | dependent / formula | high | 704 | `1.25 * self.module` |  | sspg: dependent, cpg: dependent |
| 95 | `h_f` | dependent / formula | high | 705 | `1.25 * self.module` |  | sspg: dependent, cpg: dependent |
| 96 | `clr_tip_root` | dependent / formula | high | 706 | `self.h_f - self.h_a` |  | sspg: dependent, cpg: dependent |
| 97 | `dp_s` | dependent / formula | high | 709 | `self.module * self.Ns` |  | sspg: dependent, cpg: dependent |
| 98 | `db_s` | dependent / formula | high | 710 | `self.dp_s * np.cos(self.pressure_angle)` |  | sspg: dependent, cpg: dependent |
| 99 | `fw_s_calc` | dependent / stress rule (face width) | high | 711 | `self.planetaryGearbox.fwSunMM` |  | sspg: dependent, cpg: dependent |
| 100 | `alpha_s` | dependent / formula | high | 712 | `(np.sqrt(self.dp_s**2 - self.db_s**2) / self.db_s) * 180 / np.pi - self.pressure_angle * 180 / np.pi` |  | sspg: dependent, cpg: dependent |
| 101 | `beta_s` | dependent / formula | high | 713 | `(360 / (4 * self.Ns) - self.alpha_s) * 2` |  | sspg: dependent, cpg: dependent |
| 102 | `dp_p` | dependent / formula | high | 715 | `self.module * self.Np` |  | sspg: dependent |
| 103 | `db_p` | dependent / formula | high | 716 | `self.dp_p * np.cos(self.pressure_angle)` |  | sspg: dependent |
| 104 | `fw_p` | dependent / stress rule (face width) | high | 717 | `self.planetaryGearbox.fwPlanetMM` |  | sspg: dependent |
| 105 | `alpha_p` | dependent / formula | high | 718 | `(np.sqrt(self.dp_p**2 - self.db_p**2) / self.db_p) * 180 / np.pi - self.pressure_angle * 180 / np.pi` |  | sspg: dependent |
| 106 | `beta_p` | dependent / formula | high | 719 | `(360 / (4 * self.Np) - self.alpha_p) * 2` |  | sspg: dependent |
| 107 | `dp_r` | dependent / formula | high | 725 | `self.module * self.Nr` |  | sspg: dependent, cpg: dependent |
| 108 | `db_r` | dependent / formula | high | 726 | `self.dp_r * np.cos(self.pressure_angle)` |  | sspg: dependent, cpg: dependent |
| 109 | `fw_r` | dependent / stress rule (face width) | high | 727 | `self.planetaryGearbox.fwRingMM` |  | sspg: dependent, cpg: dependent |
| 110 | `alpha_r` | dependent / formula | high | 728 | `(np.sqrt(self.dp_r**2 - self.db_r**2) / self.db_r) * 180 / np.pi - self.pressure_angle * 180 / np.pi` |  | sspg: dependent, cpg: dependent |
| 111 | `beta_r` | dependent / formula | high | 729 | `(360 / (4 * self.Nr) + self.alpha_r) * 2` |  | sspg: dependent, cpg: dependent |
| 112 | `output_bearing_ID` | dependent / lookup (bearing) | high | 736 | `outputbearing.getBearingIDMM()` |  |  |
| 113 | `output_bearing_OD` | dependent / lookup (bearing) | high | 737 | `outputbearing.getBearingODMM()` |  |  |
| 114 | `output_bearing_width` | dependent / lookup (bearing) | high | 738 | `outputbearing.getBearingWidthMM()` |  |  |
| 115 | `sun2_bearing_ID` | dependent / lookup (bearing) | high | 744 | `sun2bearing.getBearingIDMM()` |  |  |
| 116 | `sun2_bearing_OD` | dependent / lookup (bearing) | high | 745 | `sun2bearing.getBearingODMM()` |  |  |
| 117 | `sun2_bearing_width` | dependent / lookup (bearing) | high | 746 | `sun2bearing.getBearingWidthMM()` |  |  |
| 118 | `input_bearing_ID` | fixed / config | high | 750 | `self.design_params["input_bearing_ID"]` |  |  |
| 119 | `input_bearing_OD` | fixed / config | high | 751 | `self.design_params["input_bearing_OD"]` |  |  |
| 120 | `input_bearing_width` | fixed / config | high | 752 | `self.design_params["input_bearing_width"]` |  |  |
| 121 | `sec_carrier_thickness` | fixed / config | high | 755 | `self.design_params["sec_carrier_thickness"]` |  | sspg: fixed, cpg: fixed |
| 122 | `sun_hub_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 760 | `sun_hub_bolt.nut_width_across_flats` |  |  |
| 123 | `sun_hub_nut_depth` | dependent / lookup (bolt/nut) | high | 761 | `sun_hub_bolt.nut_thickness` |  |  |
| 124 | `sun_hub_dia` | dependent / formula | medium | 763 | `self.motor_rotor_hole_PCD + self.sun_hub_nut_wrench_size + self.standard_clearance_1_5mm * 4` | numbers 4 | sspg: dependent, cpg: dependent |
| 125 | `sun_central_bolt_socket_head_dia` | dependent / lookup (bolt/nut) | high | 766 | `sun_central_bolt.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 126 | `sun_central_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 767 | `sun_central_bolt.nut_width_across_flats` |  |  |
| 127 | `sun_central_nut_depth` | dependent / lookup (bolt/nut) | high | 768 | `sun_central_bolt.nut_thickness` |  |  |
| 128 | `fw_s_used` | dependent / formula | high | 770 | `self.sec_carrier_thickness + self.clearance_planet + self.fw_p` |  | sspg: dependent, cpg: dependent |
| 129 | `carrier_thickness_top` | dependent / formula | high | 772 | `self.output_bearing_width + self.bearing_step_width + self.standard_clearance_1_5mm` |  |  |
| 130 | `carrier_top_to_mid_hole_dia` | fixed / config | high | 647 | `self.design_params["carrier_top_to_mid_hole_dia"]` |  |  |
| 131 | `carrier_top_to_mid_bolt_socket_dia` | dependent / lookup (bolt/nut) | high | 651 | `carrier_top_to_mid_hole_bolt.bolt_head_dia` |  |  |
| 132 | `carrier_top_to_mid_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 652 | `carrier_top_to_mid_hole_bolt.nut_width_across_flats` |  |  |
| 133 | `carrier_top_to_mid_nut_depth` | dependent / lookup (bolt/nut) | high | 653 | `carrier_top_to_mid_hole_bolt.nut_thickness` |  |  |
| 134 | `carrier_thickness_mid` | dependent / formula | medium | 775, 794 | `6 ‖ self.carrier_thickness - self.carrier_thickness_top` | 2 assignments (two-case rule or reassigned); numbers 6 |  |
| 135 | `carrier_thickness` | dependent / formula | high | 778, 788 | `self.carrier_thickness_mid + self.carrier_thickness_top ‖ ( self.motor_height + self.ring_hub_thickness + self…` | 2 assignments (two-case rule or reassigned) |  |
| 136 | `ring_hub_thickness` | dependent / formula | medium | 782, 787 | `(self.fw_s_used + self.clearance_planet + self.carrier_thickness - (self.motor_case_thickness-self.bearing_ste…` | 2 assignments (two-case rule or reassigned); numbers 3 |  |
| 137 | `ring_stator_case_thickness` | fixed / config | high | 796 | `self.design_params["ring_stator_case_thickness"]` |  |  |
| 138 | `ring_hub_offset_stator_hole_PCD` | fixed / config | high | 797 | `self.design_params["ring_hub_offset_stator_hole_PCD"]` |  |  |
| 139 | `stator_ring_hub_hole_num` | fixed / config | high | 798 | `self.design_params["stator_ring_hub_hole_num"]` |  |  |
| 140 | `motor_case_height` | dependent / formula | high | 804 | `( self.motor_height + self.ring_hub_thickness + self.sun_coupler_hub_thickness + self.bearing_step_width )` |  |  |
| 141 | `wire_slot_length` | fixed / config | high | 595 | `self.design_params["wire_slot_length"]` |  | sspg: input, cpg: input |
| 142 | `wire_slot_radius` | fixed / config | high | 594 | `self.design_params["wire_slot_radius"]` |  | sspg: input, cpg: input |
| 143 | `actuactor_mount_hole_dia` | fixed / config | high | 596 | `self.design_params["actuactor_mount_hole_dia"]` |  |  |
| 144 | `actuactor_mount_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 619 | `actuactor_mount_hole_bolt.nut_width_across_flats` |  |  |
| 145 | `actuactor_mount_nut_depth` | dependent / lookup (bolt/nut) | high | 620 | `actuactor_mount_hole_bolt.nut_thickness` |  |  |

## Config accounting

| Block | Keys | Read by this type | Read but not written to the CAD | Never used |
|---|---|---|---|---|
| `isspg_optimization_parameters` | 9 | yes | GEAR_RATIO_MIN, GEAR_RATIO_MAX, GEAR_RATIO_STEP, MODULE_MIN, MODULE_MAX, NUM_PLANET_MIN, NUM_PLANET_MAX, NUM_TEETH_SUN_MIN, NUM_TEETH_PLANET_MIN | — |
| `isspg_3DP_design_parameters` | 68 | yes | planetMinDistanceMM, sCarrierExtrusionDiaMM, sCarrierExtrusionClearanceMM, ring_hub_thickness, ring_hub_to_case_hole_nut_wrench_size, ring_hub_to_case_hole_nut_depth, stator_hole_PCD, stator_hole_dia, sun_hub_dia, sun_coupler_hub_thickness, case_mounting_hole_shift, gear_axial_margin_mm | — |


## Result (classification done)

Spec: [`config_files/variables/isspg_compact_variables.json`](../../../config_files/variables/isspg_compact_variables.json), page [`docs/variables/isspg_compact.md`](../isspg_compact.md) (generated). Tests: the generic `tests/test_variable_categories.py` (ISSPG compact registered in `tests/variable_helpers.py`) and `tests/test_variable_categories_isspg.py` (parametrized over the ISSPG variants that have a spec; inside follows in its own commit).

**Counts (CAD variables, 145):** input 24, optimisation 4, fixed 57, dependent 60 (25 formula, 31 lookup, 3 stress rule, 1 implicit constraint). The draft said input 22 / dependent 62: `motor_OD` and `motor_height` are read straight from the motor (Input), as the plan's special-case table says. **Code-only values: 30** (fixed 24, dependent 4: `pressure_angle_rad`, `maxGearboxDiameter`, `actuator_width`, `fw_limit_mm`; input 2). Eight of them are config keys the code computes instead (`sun_hub_dia`, `sun_coupler_hub_thickness`, `ring_hub_thickness`, `case_mounting_hole_shift`, `stator_hole_PCD`, `stator_hole_dia`, `ring_hub_to_case_hole_nut_*`), named `<key>_config`. Confidence: 164 high, 11 medium, 0 low.

**Medium-confidence entries** (hard-coded numbers with no shared key)
- `ring_hub_thickness`, `carrier_thickness`, `carrier_thickness_mid` (Dependent / formula): an iterative two-case rule. The carrier starts with a hard-coded 6 mm middle plate; if the ring hub that closes the stack would be thinner than a hard-coded 3 mm, the hub is set to 3 and the carrier takes up the difference. The three are written as one conditional formula each.
- `sun_coupler_hub_thickness` (Dependent / formula): a hard-coded 3 mm term (the config's value is not read).
- `sun_hub_dia` (Dependent / formula): a hard-coded `x 4` clearance margin, the shared sun-hub item the plan still has to decide (the config's value is not read).
- `output_bearing_ID` / `_OD` / `_width` (Dependent / lookup): the bore request carries a hard-coded 20 mm clearance.
- `sun2_bearing_ID` / `_OD` / `_width` (Dependent / lookup): requested by outer diameter (`motor_rotor_base_ID`); `bearings_discrete` returns the first bearing with OD >= the request, which can exceed it (ISSUES bug 5).

**Config key added** to `isspg_3DP_design_parameters` in `isspg_params.json` (shared by compact and inside; shared name, value that keeps every output bit-identical): `planet_bearing_gap` = 1.0 (was `standard_clearance_1_5mm * 2 / 3`; 1.5 * 2 / 3 is exactly 1.0), read in `mitStressAnalysisMinFacewidth` of both variants. The other shared keys have no counterpart here (`clearance_motor_and_case` is already a config value, there is no `bearing_mount_thickness`, `case_mounting_hole_shift = case_mounting_hole_dia / 2`). Tests show `planet_bearing_gap` and `gear_axial_margin_mm` (the stator-height cap) each drive exactly their CAD variables.

**Shared tooling changed:** `tests/variable_helpers.py` (ISSPG entries and a branch rule; a gearbox can write only the Onshape file, `has_plain=False`; golden cases without a design, such as RO60 where the motor is too small, are skipped).

**Results:** `python tests/golden/golden.py check`: All 58 cases match the baseline. `python -m pytest -q`: 1024 passed. No `CADs/` file, no golden baseline touched.

**Open questions**
1. The hard-coded 6 and 3 (carrier and ring hub), the 3 in `sun_coupler_hub_thickness`, the 20 in the output bearing request and the `x 4` in `sun_hub_dia` are left in the code (medium); the plan proposed new keys (`carrier_thickness_mid_min`, `ring_hub_thickness_min`) to be decided in review (plan decision 4).
2. `clearance_motor_and_case`, `wire_slot_length` and `wire_slot_radius` are config values here (Fixed), unlike SSPG and CPG (computed / read from the motor): a frameless motor has no wire-slot data.
3. Width cap: the gears must fit `stator_height - gear_axial_margin_mm`; a wider design is scaled by `torque_carried_fraction`. `fw_limit_mm` is a code-only formula and the margin a code-only Fixed value.
4. The CAD's `motor_OD` / `motor_height` come from the motor (Input / motor); the file has no wire-slot or driver-mount data of the motor.
5. ISSPG writes only the Onshape file (no plain `isspg_compact_equations.txt`).
