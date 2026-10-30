# INCPG independent: variable classification plan

Part of [the plan for all actuators](../PLAN.md). Survey only: nothing in the code, config or CAD output changes on this branch.

## Inventory

- **CAD interface:** `incpg_independent_equations_onshape.txt`, **138 variables**; other files: `incpg_independent_equations.txt` (138)
- **Code:** `inrunnerCompoundPlanetaryActuator` in `ActuatorAndGearbox_INCPG_independent.py` (lines 527-2175)
- **Config:** `incpg_independent_params.json`, block(s) read: `incpg_3DP_design_parameters`; search bounds `incpg_optimization_parameters`; gear standard / MIT factors from `config.json`; driver: `OdrivePro`
- **Survey draft:** dependent 59, fixed 52, input 22, optimisation 5; 75 names also in SSPG / CPG; 0 alias names (same value written under a second name); 0 flagged by the survey

## Special cases

Same structure as INCPG dependent (see its plan); differences:

| Variable(s) | Independent | Dependent |
|---|---|---|
| `rotor_top_bearing_holder_thickness`, `stator_hole_nut_depth`, `stator_hole_nut_wrench_size`, `stator_hole_allen_socket_dia` | written (independent only) | — |
| `rotor_top_bearing_*`, `rotor_bottom_bearing_*` | per-motor config (`per_motor_value`) → Fixed / config (per motor) | top: lookup; bottom: config |
| `output_bearing_*` | lookup (`Bearings`) | lookup (`OutputBearings`) |
| `sun_hub_dia` | `rotor_top_bearing_ID − 2 × rotor_hub_thickness` | `rotor_ID − 2 × rotor_hub_thickness` |
| `fw_s_used` | longer stack (top bearing, two steps, hub, clearance, carrier, planets) | `bearing_step + carrier + clearance + fw_p_b + fw_p_s` |

## Hard-coded numbers
As dependent (planet-bearing minimum 2/3, 1/3; mass-only list incl. `1.5 × 3` motor-case base, 0.2146 fillet factor).

## Config (`incpg_independent_params.json`)
As dependent; per-motor values for the rotor bearings.

## Test plan / effort
As dependent; ~0.5 h after dependent.

## Survey draft: every variable

Automatic first pass from the code (the special cases above take precedence). Category guesses come from the source of each value; *flags* mark hard-coded numbers, several assignments or a writer expression. The final category, sub-type, `depends_on`, confidence and reason are set during the classification itself.

| # | Variable | Draft category / sub-type | Conf. | Line | Code | Flags | SSPG / CPG |
|---|---|---|---|---|---|---|---|
| 1 | `Ns` | optimisation / teeth | high | 624 | `self.inrunnerCompoundPlanetaryGearbox.Ns` |  | sspg: optimisation, cpg: optimisation |
| 2 | `Np_b` | optimisation / teeth | high | 625 | `self.inrunnerCompoundPlanetaryGearbox.NpBig` |  | cpg: optimisation |
| 3 | `Np_s` | optimisation / teeth | high | 626 | `self.inrunnerCompoundPlanetaryGearbox.NpSmall` |  | cpg: optimisation |
| 4 | `Nr` | dependent / formula | high | 627 | `self.Ns + self.Np_b + self.Np_s` |  | sspg: dependent, cpg: dependent |
| 5 | `num_planet` | optimisation / planets | high | 628 | `self.inrunnerCompoundPlanetaryGearbox.numPlanet` |  | sspg: optimisation, cpg: optimisation |
| 6 | `module` | optimisation / module | high | 629 | `self.inrunnerCompoundPlanetaryGearbox.moduleBig` |  | sspg: optimisation, cpg: optimisation |
| 7 | `pressure_angle` | fixed / gear standard | high | 635 | `self.inrunnerCompoundPlanetaryGearbox.getPressureAngleRad()` |  | sspg: fixed, cpg: fixed |
| 8 | `pressure_angle_deg` | fixed / gear standard | high | 636 | `self.inrunnerCompoundPlanetaryGearbox.getPressureAngleRad() * 180 / np.pi` |  |  |
| 9 | `clearance_planet` | fixed / config | high | 639 | `self.design_params["clearance_planet"]` |  | sspg: fixed, cpg: fixed |
| 10 | `clearance_case_mount_holes_shell_thickness` | fixed / config | high | 640 | `self.design_params["clearance_case_mount_holes_shell_thickness"]` |  | sspg: fixed, cpg: fixed |
| 11 | `standard_clearance_1_5mm` | fixed / config | high | 641 | `self.design_params["standard_clearance_1_5mm"]` |  | sspg: fixed, cpg: fixed |
| 12 | `standard_clearance_2_mm` | fixed / config | high | 642 | `self.design_params["standard_clearance_2_mm"]` |  |  |
| 13 | `standard_fillet_1_5mm` | fixed / config | high | 644 | `self.design_params["standard_fillet_1_5mm"]` |  | sspg: fixed, cpg: fixed |
| 14 | `standard_fillet_3_mm` | fixed / config | high | 645 | `self.design_params["standard_fillet_3_mm"]` |  |  |
| 15 | `standard_bearing_insertion_chamfer` | fixed / config | high | 646 | `self.design_params["standard_bearing_insertion_chamfer"]` |  | sspg: fixed, cpg: fixed |
| 16 | `bearingIDClearanceMM` | fixed / config | high | 647 | `self.design_params["bearingIDClearanceMM"]` |  | sspg: fixed, cpg: fixed |
| 17 | `tight_clearance_3DP` | fixed / config | high | 648 | `self.design_params["tight_clearance_3DP"]` |  | sspg: fixed, cpg: fixed |
| 18 | `loose_clearance_3DP` | fixed / config | high | 649 | `self.design_params["loose_clearance_3DP"]` |  | sspg: fixed, cpg: fixed |
| 19 | `bearing_step_width` | fixed / config | high | 650 | `self.design_params["bearing_step_width"]` |  |  |
| 20 | `motor_OD` | input / motor | high | 653 | `self.motorDiaMM` |  | sspg: input, cpg: input |
| 21 | `motor_height` | input / motor | high | 654 | `self.motorLengthMM` |  | sspg: input, cpg: input |
| 22 | `rotor_OD` | input / motor | high | 655 | `self.motor.rotor_OD` |  |  |
| 23 | `stator_ID` | input / motor | high | 656 | `self.motor.stator_ID` |  |  |
| 24 | `rotor_height` | input / motor | high | 657 | `self.motor.rotor_height` |  |  |
| 25 | `rotor_ID` | input / motor | high | 658 | `self.motor.rotor_ID` |  |  |
| 26 | `stator_height` | input / motor | high | 659 | `self.motor.stator_height` |  |  |
| 27 | `stator_OD` | input / motor | high | 660 | `self.motor.stator_OD` |  |  |
| 28 | `stator_hole_dia` | input / motor | high | 661 | `self.motor.stator_hole_dia` |  |  |
| 29 | `stator_top_height` | input / motor | high | 662 | `self.motor.stator_wire_top_height` |  |  |
| 30 | `stator_mid_height` | input / motor | high | 663 | `self.motor.stator_mid_height` |  |  |
| 31 | `stator_bottom_height` | input / motor | high | 664 | `self.motor.stator_wire_bottom_height` |  |  |
| 32 | `stator_inside_OD` | input / motor | high | 665 | `self.motor.stator_wire_OD` |  |  |
| 33 | `stator_hole_num` | input / motor | high | 666 | `self.motor.stator_hole_num` |  |  |
| 34 | `stator_inside_ID` | input / motor | high | 667 | `self.motor.stator_wire_ID` |  |  |
| 35 | `driver_upper_holes_dist_from_center` | input / driver | high | 670 | `self.motor_driver_params["driver_upper_holes_dist_from_center"]` |  | sspg: input, cpg: input |
| 36 | `driver_lower_holes_dist_from_center` | input / driver | high | 671 | `self.motor_driver_params["driver_lower_holes_dist_from_center"]` |  | sspg: input, cpg: input |
| 37 | `driver_side_holes_dist_from_center` | input / driver | high | 672 | `self.motor_driver_params["driver_side_holes_dist_from_center"]` |  | sspg: input, cpg: input |
| 38 | `driver_mount_holes_dia` | input / driver | high | 673 | `self.motor_driver_params["driver_mount_holes_dia"]` |  | sspg: input, cpg: input |
| 39 | `driver_mount_inserts_OD` | input / driver | high | 674 | `self.motor_driver_params["driver_mount_inserts_OD"]` |  | sspg: input, cpg: input |
| 40 | `driver_mount_thickness` | input / driver | high | 675 | `self.motor_driver_params["driver_mount_thickness"]` |  | sspg: input, cpg: input |
| 41 | `driver_mount_height` | input / driver | high | 676 | `self.motor_driver_params["driver_mount_height"]` |  | sspg: input, cpg: input |
| 42 | `motor_mount_driver_hole_dia` | fixed / config | high | 677 | `self.design_params["motor_mount_driver_hole_dia"]` |  |  |
| 43 | `motor_mount_driver_hole_num` | fixed / config | high | 678 | `self.design_params["motor_mount_driver_hole_num"]` |  |  |
| 44 | `rotor_hub_thickness` | fixed / config | high | 681 | `self.design_params["rotor_hub_thickness"]` |  |  |
| 45 | `rotor_hub_height` | fixed / config | high | 682 | `self.design_params["rotor_hub_height"]` |  |  |
| 46 | `rotor_hub_sun_hole_dia` | fixed / config | high | 683 | `self.design_params["rotor_hub_sun_hole_dia"]` |  |  |
| 47 | `rotor_hub_sun_hole_num` | fixed / config | high | 684 | `self.design_params["rotor_hub_sun_hole_num"]` |  |  |
| 48 | `rotor_top_bearing_ID` | dependent / formula | high | 687 | `per_motor_value(self.design_params, "rotor_top_bearing_ID", self.motor_name)` |  |  |
| 49 | `rotor_top_bearing_OD` | dependent / formula | high | 688 | `per_motor_value(self.design_params, "rotor_top_bearing_OD", self.motor_name)` |  |  |
| 50 | `rotor_top_bearing_width` | dependent / formula | high | 689 | `per_motor_value(self.design_params, "rotor_top_bearing_width", self.motor_name)` |  |  |
| 51 | `rotor_bottom_bearing_ID` | dependent / formula | high | 690 | `per_motor_value(self.design_params, "rotor_bottom_bearing_ID", self.motor_name)` |  |  |
| 52 | `rotor_bottom_bearing_OD` | dependent / formula | high | 691 | `per_motor_value(self.design_params, "rotor_bottom_bearing_OD", self.motor_name)` |  |  |
| 53 | `rotor_bottom_bearing_width` | dependent / formula | high | 692 | `per_motor_value(self.design_params, "rotor_bottom_bearing_width", self.motor_name)` |  |  |
| 54 | `planet_pin_bolt_dia` | fixed / config | high | 699 | `self.design_params["planet_pin_bolt_dia"]` |  | sspg: fixed, cpg: fixed |
| 55 | `planet_shaft_step_offset` | fixed / config | high | 701 | `self.design_params["planet_shaft_step_offset"]` |  | sspg: fixed, cpg: fixed |
| 56 | `planet_bearing_OD` | fixed / config | high | 702 | `self.design_params["planet_bearing_OD"]` |  | sspg: fixed, cpg: fixed |
| 57 | `planet_bearing_width` | fixed / config | high | 703 | `self.design_params["planet_bearing_width"]` |  | sspg: fixed, cpg: fixed |
| 58 | `planet_bearing_ID` | fixed / config | high | 704 | `self.design_params["planet_bearing_ID"]` |  |  |
| 59 | `sun_coupler_hub_thickness` | fixed / config | high | 707 | `self.design_params["sun_coupler_hub_thickness"]` |  | sspg: fixed, cpg: fixed |
| 60 | `sun_shaft_bearing_ID` | fixed / config | high | 708 | `self.design_params["sun_shaft_bearing_ID"]` |  | sspg: fixed, cpg: fixed |
| 61 | `sun_shaft_bearing_OD` | fixed / config | high | 709 | `self.design_params["sun_shaft_bearing_OD"]` |  | sspg: fixed, cpg: fixed |
| 62 | `sun_shaft_bearing_width` | fixed / config | high | 710 | `self.design_params["sun_shaft_bearing_width"]` |  | sspg: fixed, cpg: fixed |
| 63 | `sun_central_bolt_dia` | fixed / config | high | 711 | `self.design_params["sun_central_bolt_dia"]` |  | sspg: fixed, cpg: fixed |
| 64 | `sec_carrier_thickness` | fixed / config | high | 714 | `self.design_params["sec_carrier_thickness"]` |  | sspg: fixed, cpg: fixed |
| 65 | `carrier_trapezoidal_support_sun_offset` | fixed / config | high | 716 | `self.design_params["carrier_trapezoidal_support_sun_offset"]` |  | sspg: fixed, cpg: fixed |
| 66 | `carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID` | fixed / config | high | 717 | `self.design_params["carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID"]` |  |  |
| 67 | `carrier_trapezoidal_support_hole_dia` | fixed / config | high | 718 | `self.design_params["carrier_trapezoidal_support_hole_dia"]` |  | sspg: fixed, cpg: fixed |
| 68 | `case_mounting_surface_height` | fixed / config | high | 721 | `self.design_params["case_mounting_surface_height"]` |  | sspg: fixed, cpg: fixed |
| 69 | `case_mounting_hole_dia` | fixed / config | high | 722 | `self.design_params["case_mounting_hole_dia"]` |  | sspg: fixed, cpg: fixed |
| 70 | `motor_case_thickness` | fixed / config | high | 724 | `self.design_params["motor_case_thickness"]` |  |  |
| 71 | `output_mount_hole_dia` | fixed / config | high | 726 | `self.design_params["output_mount_hole_dia"]` |  |  |
| 72 | `actuactor_mount_hole_dia` | fixed / config | high | 728 | `self.design_params["actuactor_mount_hole_dia"]` |  |  |
| 73 | `motor_case_OD_base_to_chamfer` | fixed / config | high | 730 | `self.design_params["motor_case_OD_base_to_chamfer"]` |  |  |
| 74 | `pattern_offset_from_motor_case_OD_base` | fixed / config | high | 731 | `self.design_params["pattern_offset_from_motor_case_OD_base"]` |  | sspg: fixed, cpg: fixed |
| 75 | `pattern_bulge_dia` | fixed / config | high | 732 | `self.design_params["pattern_bulge_dia"]` |  | sspg: fixed, cpg: fixed |
| 76 | `pattern_num_bulge` | fixed / config | high | 733 | `self.design_params["pattern_num_bulge"]` |  | sspg: fixed, cpg: fixed |
| 77 | `pattern_depth` | fixed / config | high | 734 | `self.design_params["pattern_depth"]` |  | sspg: fixed, cpg: fixed |
| 78 | `magnet_mount_hole_dia` | fixed / config | high | 739 | `self.design_params["magnet_mount_hole_dia"]` |  |  |
| 79 | `magnet_thickness` | fixed / config | high | 740 | `self.design_params["magnet_thickness"]` |  |  |
| 80 | `magnet_dia` | fixed / config | high | 741 | `self.design_params["magnet_dia"]` |  |  |
| 81 | `magnet_mount_thickness` | fixed / config | high | 742 | `self.design_params["magnet_mount_thickness"]` |  |  |
| 82 | `magnet_pattern_bulge_dia` | fixed / config | high | 743 | `self.design_params["magnet_pattern_bulge_dia"]` |  |  |
| 83 | `magnet_pattern_bulge_number` | fixed / config | high | 744 | `self.design_params["magnet_pattern_bulge_number"]` |  |  |
| 84 | `magnet_mount_height` | fixed / config | high | 745 | `self.design_params["magnet_mount_height"]` |  |  |
| 85 | `ring_radial_width` | fixed / config | high | 748 | `self.design_params["ringRadialWidthMM"]` |  |  |
| 86 | `ring_gearbox_casing_thickness` | fixed / config | high | 736 | `self.design_params["ring_gearbox_casing_thickness"]` |  |  |
| 87 | `rotor_top_bearing_holder_thickness` | dependent / formula | high | 751 | `(self.bearing_step_width + self.rotor_top_bearing_width - (self.standard_clearance_1_5mm/2 + self.stator_top_h…` |  |  |
| 88 | `h_a` | dependent / formula | high | 761 | `1 * self.module` |  | sspg: dependent, cpg: dependent |
| 89 | `h_b` | dependent / formula | high | 762 | `1.25 * self.module` |  | sspg: dependent, cpg: dependent |
| 90 | `h_f` | dependent / formula | high | 763 | `1.25 * self.module` |  | sspg: dependent, cpg: dependent |
| 91 | `clr_tip_root` | dependent / formula | high | 764 | `self.h_f - self.h_a` |  | sspg: dependent, cpg: dependent |
| 92 | `dp_s` | dependent / formula | high | 766 | `self.module * self.Ns` |  | sspg: dependent, cpg: dependent |
| 93 | `db_s` | dependent / formula | high | 767 | `self.dp_s * np.cos((self.pressure_angle))` |  | sspg: dependent, cpg: dependent |
| 94 | `alpha_s` | dependent / formula | high | 768 | `(np.sqrt(self.dp_s ** 2 - self.db_s ** 2) / self.db_s) * 180 / np.pi - self.pressure_angle_deg` |  | sspg: dependent, cpg: dependent |
| 95 | `beta_s` | dependent / formula | high | 769 | `(360 / (4 * self.Ns) - self.alpha_s) * 2` |  | sspg: dependent, cpg: dependent |
| 96 | `fw_s_calc` | dependent / stress rule (face width) | high | 770 | `self.inrunnerCompoundPlanetaryGearbox.fwSunMM` |  | sspg: dependent, cpg: dependent |
| 97 | `dp_p_b` | dependent / formula | high | 772 | `self.module * self.Np_b` |  | cpg: dependent |
| 98 | `db_p_b` | dependent / formula | high | 773 | `self.dp_p_b * np.cos((self.pressure_angle))` |  | cpg: dependent |
| 99 | `alpha_p_b` | dependent / formula | high | 774 | `(np.sqrt(self.dp_p_b ** 2 - self.db_p_b ** 2) / self.db_p_b) * 180 / np.pi - self.pressure_angle_deg` |  | cpg: dependent |
| 100 | `beta_p_b` | dependent / formula | high | 775 | `(360 / (4 * self.Np_b) - self.alpha_p_b) * 2` |  | cpg: dependent |
| 101 | `fw_p_b` | dependent / stress rule (face width) | high | 776 | `self.inrunnerCompoundPlanetaryGearbox.fwPlanetBigMM` |  | cpg: dependent |
| 102 | `dp_r` | dependent / formula | high | 778 | `self.module * self.Nr` |  | sspg: dependent, cpg: dependent |
| 103 | `db_r` | dependent / formula | high | 779 | `self.dp_r * np.cos((self.pressure_angle))` |  | sspg: dependent, cpg: dependent |
| 104 | `alpha_r` | dependent / formula | high | 780 | `(np.sqrt(self.dp_r ** 2 - self.db_r ** 2) / self.db_r) * 180 / np.pi - self.pressure_angle_deg` |  | sspg: dependent, cpg: dependent |
| 105 | `beta_r` | dependent / formula | high | 781 | `(360 / (4 * self.Nr) + self.alpha_r) * 2` |  | sspg: dependent, cpg: dependent |
| 106 | `fw_r` | dependent / stress rule (face width) | high | 782 | `self.inrunnerCompoundPlanetaryGearbox.fwRingMM + self.standard_clearance_1_5mm` |  | sspg: dependent, cpg: dependent |
| 107 | `dp_p_s` | dependent / formula | high | 784 | `self.module * self.Np_s` |  | cpg: dependent |
| 108 | `db_p_s` | dependent / formula | high | 785 | `self.dp_p_s * np.cos((self.pressure_angle))` |  | cpg: dependent |
| 109 | `alpha_p_s` | dependent / formula | high | 786 | `(np.sqrt(self.dp_p_s ** 2 - self.db_p_s ** 2) / self.db_p_s) * 180 / np.pi - self.pressure_angle_deg` |  | cpg: dependent |
| 110 | `beta_p_s` | dependent / formula | high | 787 | `(360 / (4 * self.Np_s) - self.alpha_p_s) * 2` |  | cpg: dependent |
| 111 | `fw_p_s` | dependent / formula | high | 788 | `self.fw_r` |  | cpg: dependent |
| 112 | `motor_mount_driver_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 792 | `motor_mount_driver_bolt.nut_width_across_flats` |  |  |
| 113 | `motor_mount_driver_nut_depth` | dependent / lookup (bolt/nut) | high | 793 | `motor_mount_driver_bolt.nut_thickness` |  |  |
| 114 | `planet_pin_socket_head_dia` | dependent / lookup (bolt/nut) | high | 798 | `planet_pin_bolt.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 115 | `planet_pin_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 799 | `planet_pin_bolt.nut_width_across_flats` |  |  |
| 116 | `planet_pin_nut_depth` | dependent / lookup (bolt/nut) | high | 800 | `planet_pin_bolt.nut_thickness` |  |  |
| 117 | `sun_central_bolt_socket_head_dia` | dependent / lookup (bolt/nut) | high | 804 | `sun_central_bolt.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 118 | `rotor_hub_sun_hole_CSK_OD` | dependent / lookup (bolt/nut) | high | 808 | `rotor_hub_sun_bolt.bolt_head_dia` |  |  |
| 119 | `rotor_hub_sun_hole_CSK_head_height` | dependent / lookup (bolt/nut) | high | 809 | `rotor_hub_sun_bolt.bolt_head_height` |  |  |
| 120 | `sun_hub_dia` | dependent / formula | high | 811 | `self.rotor_top_bearing_ID - 2*self.rotor_hub_thickness` |  | sspg: dependent, cpg: dependent |
| 121 | `output_bearing_ID` | dependent / lookup (bearing) | high | 816 | `Bearings.getBearingIDMM()` |  |  |
| 122 | `output_bearing_OD` | dependent / lookup (bearing) | high | 817 | `Bearings.getBearingODMM()` |  |  |
| 123 | `output_bearing_width` | dependent / lookup (bearing) | high | 818 | `Bearings.getBearingWidthMM()` |  |  |
| 124 | `carrier_trapezoidal_support_hole_socket_head_dia` | dependent / lookup (bolt/nut) | high | 823 | `carrier_trapezoidal_support_hole.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 125 | `carrier_trapezoidal_support_hole_wrench_size` | dependent / lookup (bolt/nut) | high | 824 | `carrier_trapezoidal_support_hole.nut_width_across_flats` |  | sspg: dependent, cpg: dependent |
| 126 | `stator_hole_nut_depth` | dependent / lookup (bolt/nut) | high | 837 | `stator_case_mounting_hole_bolt.nut_thickness` |  |  |
| 127 | `stator_hole_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 836 | `stator_case_mounting_hole_bolt.nut_width_across_flats` |  |  |
| 128 | `stator_hole_allen_socket_dia` | dependent / lookup (bolt/nut) | high | 835 | `stator_case_mounting_hole_bolt.bolt_head_dia` |  |  |
| 129 | `carrier_trapezoidal_support_nut_depth` | dependent / lookup (bolt/nut) | high | 825 | `carrier_trapezoidal_support_hole.nut_thickness` |  |  |
| 130 | `case_mounting_hole_allen_socket_dia` | dependent / lookup (bolt/nut) | high | 841 | `case_mounting_hole_bolt.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 131 | `case_mounting_wrench_size` | dependent / lookup (bolt/nut) | high | 842 | `case_mounting_hole_bolt.nut_width_across_flats` |  | sspg: dependent, cpg: dependent |
| 132 | `case_mounting_nut_depth` | dependent / lookup (bolt/nut) | high | 843 | `case_mounting_hole_bolt.nut_thickness` |  |  |
| 133 | `output_mount_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 847 | `output_mount_hole_bolt.nut_width_across_flats` |  |  |
| 134 | `output_mount_hole_nut_depth` | dependent / lookup (bolt/nut) | high | 848 | `output_mount_hole_bolt.nut_thickness` |  |  |
| 135 | `actuactor_mount_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 852 | `actuactor_mount_hole_bolt.nut_width_across_flats` |  |  |
| 136 | `actuactor_mount_nut_depth` | dependent / lookup (bolt/nut) | high | 853 | `actuactor_mount_hole_bolt.nut_thickness` |  |  |
| 137 | `case_mounting_hole_shift` | dependent / formula | high | 855 | `self.case_mounting_hole_dia / 2` |  | sspg: dependent, cpg: dependent |
| 138 | `fw_s_used` | dependent / formula | high | 857 | `(self.bearing_step_width + self.rotor_top_bearing_width - self.sun_coupler_hub_thickness + self.bearing_step_w…` |  | sspg: dependent, cpg: dependent |

## Config accounting

| Block | Keys | Read by this type | Read but not written to the CAD | Never used |
|---|---|---|---|---|
| `incpg_optimization_parameters` | 10 | yes | GEAR_RATIO_MIN, GEAR_RATIO_MAX, GEAR_RATIO_STEP, MODULE_MIN, MODULE_MAX, NUM_PLANET_MIN, NUM_PLANET_MAX, NUM_TEETH_SUN_MIN, NUM_TEETH_PLANET_MIN, MAX_GB_DIA_MULT_FACTOR | — |
| `incpg_3DP_design_parameters` | 59 | yes | planetMinDistanceMM, sCarrierExtrusionDiaMM, sCarrierExtrusionClearanceMM | — |
