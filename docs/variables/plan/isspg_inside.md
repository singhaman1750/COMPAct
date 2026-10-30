# ISSPG inside: variable classification plan

Part of [the plan for all actuators](../PLAN.md). Survey only: nothing in the code, config or CAD output changes on this branch.

## Inventory

- **CAD interface:** `isspg_inside_equations_onshape.txt`, **147 variables**; other files: none
- **Code:** `internalsingleStagePlanetaryActuator` in `ActuatorAndGearbox_ISSPG_inside.py` (lines 472-1698)
- **Config:** `isspg_params.json`, block(s) read: `isspg_3DP_design_parameters`; search bounds `isspg_optimization_parameters`; gear standard / MIT factors from `config.json`; driver: `OdrivePro`
- **Survey draft:** dependent 65, fixed 54, input 24, optimisation 4; 69 names also in SSPG / CPG; 0 alias names (same value written under a second name); 2 flagged by the survey

## Special cases

Same structure as ISSPG compact (see its plan); differences:

| Variable(s) | Inside | Compact |
|---|---|---|
| `rotorCSKHeadUpperDiaMM`, `rotorCSKHeadHeightMM` | written (inside only) | — |
| `input_bearing_ID/OD/width` | Dependent / lookup (`bearings_discrete`) | Fixed / config |
| `sun_hub_dia` | `= input_bearing_ID` (formula, no hard-coded number) | rotor holes + nut + `1.5 × 4` |
| `sun_coupler_hub_thickness` | `input_bearing_width + bearing_step_width` | `3 + bearing_step_width/2 + sun2_bearing_width` |
| `fw_s_used` | longer formula (bearing, step, carrier, clearance, planet width, minus hub) | `sec_carrier_thickness + clearance_planet + fw_p` |

## Hard-coded numbers (medium)
- `carrier_thickness_mid` = 6 (L782), `ring_hub_thickness` = 3 (L794): same as compact.
- Planet-bearing minimum 2/3 (L1185-1186) → `planet_bearing_gap`.
- Mass code: `sun_hub_carrier_OD` (× 5), `sec_carrier_bottom_OD` (× 4), motor-case mounting volume (6), bearing masses: mass-only list.

## Config
As compact; additionally `input_bearing_ID/OD/width` are in the config but the CAD values come from the bearing lookup (read but not used for the CAD).

## Test plan / risks
As compact. Effort: ~1 h after compact.

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
| 20 | `sun_coupler_hub_thickness` | dependent / formula | high | 772 | `self.input_bearing_width + self.bearing_step_width` |  | sspg: fixed, cpg: fixed |
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
| 43 | `planet_pin_bolt_dia` | fixed / config | high | 620 | `self.design_params["planet_pin_bolt_dia"]` |  | sspg: fixed, cpg: fixed |
| 44 | `planet_shaft_step_offset` | fixed / config | high | 622 | `self.design_params["planet_shaft_step_offset"]` |  | sspg: fixed, cpg: fixed |
| 45 | `planet_bearing_OD` | fixed / config | high | 623 | `self.design_params["planet_bearing_OD"]` |  | sspg: fixed, cpg: fixed |
| 46 | `planet_bearing_width` | fixed / config | high | 624 | `self.design_params["planet_bearing_width"]` |  | sspg: fixed, cpg: fixed |
| 47 | `planet_bearing_ID` | fixed / config | high | 625 | `self.design_params["planet_bearing_ID"]` |  |  |
| 48 | `carrier_trapezoidal_support_sun_offset` | fixed / config | high | 628 | `self.design_params["carrier_trapezoidal_support_sun_offset"]` |  | sspg: fixed, cpg: fixed |
| 49 | `carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID` | fixed / config | high | 629 | `self.design_params["carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID"]` |  |  |
| 50 | `carrier_trapezoidal_support_hole_dia` | fixed / config | high | 630 | `self.design_params["carrier_trapezoidal_support_hole_dia"]` |  | sspg: fixed, cpg: fixed |
| 51 | `carrier_trapezoidal_support_hole_socket_head_dia` | dependent / lookup (bolt/nut) | high | 634 | `carrier_trapezoidal_support_hole.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 52 | `carrier_trapezoidal_support_hole_wrench_size` | dependent / lookup (bolt/nut) | high | 635 | `carrier_trapezoidal_support_hole.nut_width_across_flats` |  | sspg: dependent, cpg: dependent |
| 53 | `carrier_trapezoidal_support_nut_depth` | dependent / lookup (bolt/nut) | high | 636 | `carrier_trapezoidal_support_hole.nut_thickness` |  |  |
| 54 | `planet_pin_socket_head_dia` | dependent / lookup (bolt/nut) | high | 640 | `planet_pin_bolt.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 55 | `planet_pin_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 641 | `planet_pin_bolt.nut_width_across_flats` |  |  |
| 56 | `planet_pin_nut_depth` | dependent / lookup (bolt/nut) | high | 642 | `planet_pin_bolt.nut_thickness` |  |  |
| 57 | `driver_upper_holes_dist_from_center` | input / driver | high | 653 | `self.motor_driver_params["driver_upper_holes_dist_from_center"]` |  | sspg: input, cpg: input |
| 58 | `driver_lower_holes_dist_from_center` | input / driver | high | 654 | `self.motor_driver_params["driver_lower_holes_dist_from_center"]` |  | sspg: input, cpg: input |
| 59 | `driver_side_holes_dist_from_center` | input / driver | high | 655 | `self.motor_driver_params["driver_side_holes_dist_from_center"]` |  | sspg: input, cpg: input |
| 60 | `driver_mount_holes_dia` | input / driver | high | 656 | `self.motor_driver_params["driver_mount_holes_dia"]` |  | sspg: input, cpg: input |
| 61 | `driver_mount_inserts_OD` | input / driver | high | 657 | `self.motor_driver_params["driver_mount_inserts_OD"]` |  | sspg: input, cpg: input |
| 62 | `driver_mount_thickness` | input / driver | high | 658 | `self.motor_driver_params["driver_mount_thickness"]` |  | sspg: input, cpg: input |
| 63 | `driver_mount_height` | input / driver | high | 659 | `self.motor_driver_params["driver_mount_height"]` |  | sspg: input, cpg: input |
| 64 | `motor_mount_driver_hole_dia` | fixed / config | high | 660 | `self.design_params["motor_mount_driver_hole_dia"]` |  |  |
| 65 | `central_hole_offset_from_motor_mount_PCD` | fixed / config | high | 583 | `self.design_params["central_hole_offset_from_motor_mount_PCD"]` |  | sspg: fixed, cpg: fixed |
| 66 | `motor_mount_driver_hole_num` | fixed / config | high | 661 | `self.design_params["motor_mount_driver_hole_num"]` |  |  |
| 67 | `motor_mount_driver_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 665 | `motor_mount_driver_bolt.nut_width_across_flats` |  |  |
| 68 | `motor_mount_driver_nut_depth` | dependent / lookup (bolt/nut) | high | 666 | `motor_mount_driver_bolt.nut_thickness` |  |  |
| 69 | `magnet_mount_hole_dia` | fixed / config | high | 669 | `self.design_params["magnet_mount_hole_dia"]` |  |  |
| 70 | `magnet_thickness` | fixed / config | high | 670 | `self.design_params["magnet_thickness"]` |  |  |
| 71 | `magnet_dia` | fixed / config | high | 671 | `self.design_params["magnet_dia"]` |  |  |
| 72 | `magnet_mount_thickness` | fixed / config | high | 672 | `self.design_params["magnet_mount_thickness"]` |  |  |
| 73 | `magnet_pattern_bulge_dia` | fixed / config | high | 673 | `self.design_params["magnet_pattern_bulge_dia"]` |  |  |
| 74 | `magnet_pattern_bulge_number` | fixed / config | high | 674 | `self.design_params["magnet_pattern_bulge_number"]` |  |  |
| 75 | `magnet_mount_height` | fixed / config | high | 675 | `self.design_params["magnet_mount_height"]` |  |  |
| 76 | `motor_OD` | dependent / formula | high | 678 | `self.motorODMM` |  | sspg: input, cpg: input |
| 77 | `motor_height` | dependent / formula | high | 679 | `self.motorHeightMM` |  | sspg: input, cpg: input |
| 78 | `stator_ID` | input / motor | high | 680 | `self.motor.getStatorIDMM()` |  |  |
| 79 | `motor_rotor_base_thickness` | input / motor | high | 681 | `self.motor.getRotorBottomThicknessMM()` |  |  |
| 80 | `motor_rotor_base_ID` | input / motor | high | 682 | `self.motor.getRotorBottomIDMM()` |  |  |
| 81 | `rotor_height` | input / motor | high | 683 | `self.motor.getRotorHeightMM()` |  |  |
| 82 | `rotor_ID` | input / motor | high | 684 | `self.motor.getRotorIDMM()` |  |  |
| 83 | `motor_stator_extrusion_depth` | input / motor | high | 685 | `self.motor.getMotorStatorExtrusionDepth()` |  |  |
| 84 | `motor_stator_extrusion_dia` | input / motor | high | 686 | `self.motor.getMotorStatorExtrusionDia()` |  |  |
| 85 | `stator_height` | input / motor | high | 687 | `self.motor.getStatorHeightMM()` |  |  |
| 86 | `stator_OD` | input / motor | high | 688 | `self.motor.getStatorODMM()` |  |  |
| 87 | `stator_top_rotor_top_offset` | input / motor | high | 689 | `self.motor.getStatorTopRotorTopOffset()` |  |  |
| 88 | `stator_hole_dia` | input / motor | high | 690 | `self.motor.getStatorHoleDia()` |  |  |
| 89 | `stator_hole_PCD` | input / motor | high | 691 | `self.motor.getStatorMountingHolePCD()` |  |  |
| 90 | `motor_rotor_hole_num` | input / motor | high | 692 | `self.motor.getMotorRotorHoleNum()` |  |  |
| 91 | `motor_rotor_hole_dia` | input / motor | high | 693 | `self.motor.getRotorMountHoleDiaMM()` |  |  |
| 92 | `motor_rotor_hole_PCD` | input / motor | high | 694 | `self.motor.getRotorMountHolePCDMM()` |  |  |
| 93 | `rotorCSKHeadUpperDiaMM` | input / motor | high | 695 | `self.motor.getRotorCSKHeadUpperDiaMM()` |  |  |
| 94 | `rotorCSKHeadHeightMM` | input / motor | high | 696 | `self.motor.getRotorCSKHeadHeightMM()` |  |  |
| 95 | `h_a` | dependent / formula | high | 702 | `1 * self.module` |  | sspg: dependent, cpg: dependent |
| 96 | `h_b` | dependent / formula | high | 703 | `1.25 * self.module` |  | sspg: dependent, cpg: dependent |
| 97 | `h_f` | dependent / formula | high | 704 | `1.25 * self.module` |  | sspg: dependent, cpg: dependent |
| 98 | `clr_tip_root` | dependent / formula | high | 705 | `self.h_f - self.h_a` |  | sspg: dependent, cpg: dependent |
| 99 | `dp_s` | dependent / formula | high | 708 | `self.module * self.Ns` |  | sspg: dependent, cpg: dependent |
| 100 | `db_s` | dependent / formula | high | 709 | `self.dp_s * np.cos(self.pressure_angle)` |  | sspg: dependent, cpg: dependent |
| 101 | `fw_s_calc` | dependent / stress rule (face width) | high | 710 | `self.planetaryGearbox.fwSunMM` |  | sspg: dependent, cpg: dependent |
| 102 | `alpha_s` | dependent / formula | high | 711 | `(np.sqrt(self.dp_s**2 - self.db_s**2) / self.db_s) * 180 / np.pi - self.pressure_angle * 180 / np.pi` |  | sspg: dependent, cpg: dependent |
| 103 | `beta_s` | dependent / formula | high | 712 | `(360 / (4 * self.Ns) - self.alpha_s) * 2` |  | sspg: dependent, cpg: dependent |
| 104 | `dp_p` | dependent / formula | high | 714 | `self.module * self.Np` |  | sspg: dependent |
| 105 | `db_p` | dependent / formula | high | 715 | `self.dp_p * np.cos(self.pressure_angle)` |  | sspg: dependent |
| 106 | `fw_p` | dependent / stress rule (face width) | high | 716 | `self.planetaryGearbox.fwPlanetMM` |  | sspg: dependent |
| 107 | `alpha_p` | dependent / formula | high | 717 | `(np.sqrt(self.dp_p**2 - self.db_p**2) / self.db_p) * 180 / np.pi - self.pressure_angle * 180 / np.pi` |  | sspg: dependent |
| 108 | `beta_p` | dependent / formula | high | 718 | `(360 / (4 * self.Np) - self.alpha_p) * 2` |  | sspg: dependent |
| 109 | `dp_r` | dependent / formula | high | 724 | `self.module * self.Nr` |  | sspg: dependent, cpg: dependent |
| 110 | `db_r` | dependent / formula | high | 725 | `self.dp_r * np.cos(self.pressure_angle)` |  | sspg: dependent, cpg: dependent |
| 111 | `fw_r` | dependent / stress rule (face width) | high | 726 | `self.planetaryGearbox.fwRingMM` |  | sspg: dependent, cpg: dependent |
| 112 | `alpha_r` | dependent / formula | high | 727 | `(np.sqrt(self.dp_r**2 - self.db_r**2) / self.db_r) * 180 / np.pi - self.pressure_angle * 180 / np.pi` |  | sspg: dependent, cpg: dependent |
| 113 | `beta_r` | dependent / formula | high | 728 | `(360 / (4 * self.Nr) + self.alpha_r) * 2` |  | sspg: dependent, cpg: dependent |
| 114 | `output_bearing_ID` | dependent / lookup (bearing) | high | 735 | `outputbearing.getBearingIDMM()` |  |  |
| 115 | `output_bearing_OD` | dependent / lookup (bearing) | high | 736 | `outputbearing.getBearingODMM()` |  |  |
| 116 | `output_bearing_width` | dependent / lookup (bearing) | high | 737 | `outputbearing.getBearingWidthMM()` |  |  |
| 117 | `sun2_bearing_ID` | dependent / lookup (bearing) | high | 742 | `sun2bearing.getBearingIDMM()` |  |  |
| 118 | `sun2_bearing_OD` | dependent / lookup (bearing) | high | 743 | `sun2bearing.getBearingODMM()` |  |  |
| 119 | `sun2_bearing_width` | dependent / lookup (bearing) | high | 744 | `sun2bearing.getBearingWidthMM()` |  |  |
| 120 | `input_bearing_ID` | dependent / lookup (bearing) | high | 762 | `inputbearing.getBearingIDMM()` |  |  |
| 121 | `input_bearing_OD` | dependent / lookup (bearing) | high | 763 | `inputbearing.getBearingODMM()` |  |  |
| 122 | `input_bearing_width` | dependent / lookup (bearing) | high | 764 | `inputbearing.getBearingWidthMM()` |  |  |
| 123 | `sec_carrier_thickness` | fixed / config | high | 769 | `self.design_params["sec_carrier_thickness"]` |  | sspg: fixed, cpg: fixed |
| 124 | `sun_hub_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 749 | `sun_hub_bolt.nut_width_across_flats` |  |  |
| 125 | `sun_hub_nut_depth` | dependent / lookup (bolt/nut) | high | 750 | `sun_hub_bolt.nut_thickness` |  |  |
| 126 | `sun_hub_dia` | dependent / formula | high | 766 | `self.input_bearing_ID` |  | sspg: dependent, cpg: dependent |
| 127 | `sun_central_bolt_socket_head_dia` | dependent / lookup (bolt/nut) | high | 755 | `sun_central_bolt.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 128 | `sun_central_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 756 | `sun_central_bolt.nut_width_across_flats` |  |  |
| 129 | `sun_central_nut_depth` | dependent / lookup (bolt/nut) | high | 757 | `sun_central_bolt.nut_thickness` |  |  |
| 130 | `fw_s_used` | dependent / formula | high | 775 | `(self.sun2_bearing_width + self.bearing_step_width + self.sec_carrier_thickness + self.clearance_planet + self…` |  | sspg: dependent, cpg: dependent |
| 131 | `carrier_thickness_top` | dependent / formula | high | 779 | `self.output_bearing_width + self.bearing_step_width + self.standard_clearance_1_5mm` |  |  |
| 132 | `carrier_top_to_mid_hole_dia` | fixed / config | high | 644 | `self.design_params["carrier_top_to_mid_hole_dia"]` |  |  |
| 133 | `carrier_top_to_mid_bolt_socket_dia` | dependent / lookup (bolt/nut) | high | 648 | `carrier_top_to_mid_hole_bolt.bolt_head_dia` |  |  |
| 134 | `carrier_top_to_mid_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 649 | `carrier_top_to_mid_hole_bolt.nut_width_across_flats` |  |  |
| 135 | `carrier_top_to_mid_nut_depth` | dependent / lookup (bolt/nut) | high | 650 | `carrier_top_to_mid_hole_bolt.nut_thickness` |  |  |
| 136 | `carrier_thickness_mid` | dependent / formula | medium | 782, 801 | `6 ‖ self.carrier_thickness - self.carrier_thickness_top` | 2 assignments (two-case rule or reassigned); numbers 6 |  |
| 137 | `carrier_thickness` | dependent / formula | high | 785, 795 | `self.carrier_thickness_mid + self.carrier_thickness_top ‖ ( self.motor_height + self.ring_hub_thickness + self…` | 2 assignments (two-case rule or reassigned) |  |
| 138 | `ring_hub_thickness` | dependent / formula | medium | 789, 794 | `(self.fw_s_used + self.clearance_planet + self.carrier_thickness - (self.motor_case_thickness-self.bearing_ste…` | 2 assignments (two-case rule or reassigned); numbers 3 |  |
| 139 | `ring_stator_case_thickness` | fixed / config | high | 803 | `self.design_params["ring_stator_case_thickness"]` |  |  |
| 140 | `ring_hub_offset_stator_hole_PCD` | fixed / config | high | 804 | `self.design_params["ring_hub_offset_stator_hole_PCD"]` |  |  |
| 141 | `stator_ring_hub_hole_num` | fixed / config | high | 805 | `self.design_params["stator_ring_hub_hole_num"]` |  |  |
| 142 | `motor_case_height` | dependent / formula | high | 809 | `( self.motor_height + self.ring_hub_thickness + self.sun_coupler_hub_thickness + self.bearing_step_width )` |  |  |
| 143 | `wire_slot_length` | fixed / config | high | 595 | `self.design_params["wire_slot_length"]` |  | sspg: input, cpg: input |
| 144 | `wire_slot_radius` | fixed / config | high | 594 | `self.design_params["wire_slot_radius"]` |  | sspg: input, cpg: input |
| 145 | `actuactor_mount_hole_dia` | fixed / config | high | 596 | `self.design_params["actuactor_mount_hole_dia"]` |  |  |
| 146 | `actuactor_mount_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 616 | `actuactor_mount_hole_bolt.nut_width_across_flats` |  |  |
| 147 | `actuactor_mount_nut_depth` | dependent / lookup (bolt/nut) | high | 617 | `actuactor_mount_hole_bolt.nut_thickness` |  |  |

## Config accounting

| Block | Keys | Read by this type | Read but not written to the CAD | Never used |
|---|---|---|---|---|
| `isspg_optimization_parameters` | 9 | yes | GEAR_RATIO_MIN, GEAR_RATIO_MAX, GEAR_RATIO_STEP, MODULE_MIN, MODULE_MAX, NUM_PLANET_MIN, NUM_PLANET_MAX, NUM_TEETH_SUN_MIN, NUM_TEETH_PLANET_MIN | — |
| `isspg_3DP_design_parameters` | 68 | yes | planetMinDistanceMM, sCarrierExtrusionDiaMM, sCarrierExtrusionClearanceMM, ring_hub_thickness, ring_hub_to_case_hole_nut_wrench_size, ring_hub_to_case_hole_nut_depth, stator_hole_PCD, stator_hole_dia, sun_hub_dia, sun_coupler_hub_thickness, case_mounting_hole_shift, input_bearing_ID, input_bearing_OD, input_bearing_width, gear_axial_margin_mm | — |
