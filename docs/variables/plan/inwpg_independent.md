# INWPG independent: variable classification plan

Part of [the plan for all actuators](../PLAN.md). Survey only: nothing in the code, config or CAD output changes on this branch.

## Inventory

- **CAD interface:** `inwpg_independent_equations_onshape.txt`, **150 variables**; other files: `inwpg_independent_equations.txt` (150)
- **Code:** `inrunnerWolfromPlanetaryActuator` in `ActuatorAndGearbox_INWPG_independent.py` (lines 786-2746)
- **Config:** `inwpg_params_independent.json`, block(s) read: `inwpg_3DP_design_parameters`; search bounds `inwpg_optimization_parameters`; gear standard / MIT factors from `config.json`; driver: `OdrivePro`
- **Survey draft:** dependent 66, fixed 57, input 22, optimisation 5; 69 names also in SSPG / CPG; 0 alias names (same value written under a second name); 0 flagged by the survey

## Special cases

Same structure as INWPG dependent (see its plan); differences:

| Variable(s) | Independent | Dependent |
|---|---|---|
| `stator_hole_nut_depth`, `stator_hole_nut_wrench_size`, `stator_hole_allen_socket_dia`, `rotor_top_bearing_holder_thickness` | written (independent only) | — |
| `rotor_top_bearing_*`, `rotor_bottom_bearing_*` | per-motor config (`per_motor_value`, ISSUES bug 12 fix) → Fixed / config (per motor) | top: lookup; bottom: config |
| `sun_hub_dia` | `rotor_top_bearing_ID − 2 × rotor_hub_thickness` | `rotor_ID − …` |
| `fw_s_used` | longer stack (as INCPG independent) | shorter stack |

## Hard-coded numbers
As dependent (planet-bearing minimum; mass-only list incl. `1.5 × 3` motor-case base, bearing masses).

## Test plan / effort
As dependent; ~0.5 h after dependent.

## Survey draft: every variable

Automatic first pass from the code (the special cases above take precedence). Category guesses come from the source of each value; *flags* mark hard-coded numbers, several assignments or a writer expression. The final category, sub-type, `depends_on`, confidence and reason are set during the classification itself.

| # | Variable | Draft category / sub-type | Conf. | Line | Code | Flags | SSPG / CPG |
|---|---|---|---|---|---|---|---|
| 1 | `Ns` | optimisation / teeth | high | 872 | `self.inrunnerWolfromPlanetaryGearbox.Ns` |  | sspg: optimisation, cpg: optimisation |
| 2 | `Np_b` | optimisation / teeth | high | 873 | `self.inrunnerWolfromPlanetaryGearbox.NpBig` |  | cpg: optimisation |
| 3 | `Np_s` | optimisation / teeth | high | 874 | `self.inrunnerWolfromPlanetaryGearbox.NpSmall` |  | cpg: optimisation |
| 4 | `Nr_b` | dependent / formula | high | 875 | `self.Ns + self.Np_b * 2` |  |  |
| 5 | `Nr_s` | dependent / formula | high | 876 | `self.Ns + self.Np_b + self.Np_s` |  |  |
| 6 | `num_planet` | optimisation / planets | high | 878 | `self.inrunnerWolfromPlanetaryGearbox.numPlanet` |  | sspg: optimisation, cpg: optimisation |
| 7 | `module` | optimisation / module | high | 877 | `self.inrunnerWolfromPlanetaryGearbox.moduleBig` |  | sspg: optimisation, cpg: optimisation |
| 8 | `pressure_angle` | fixed / gear standard | high | 884 | `self.inrunnerWolfromPlanetaryGearbox.getPressureAngleRad()` |  | sspg: fixed, cpg: fixed |
| 9 | `pressure_angle_deg` | fixed / gear standard | high | 885 | `self.inrunnerWolfromPlanetaryGearbox.getPressureAngleRad() * 180 / np.pi` |  |  |
| 10 | `clearance_planet` | fixed / config | high | 888 | `self.design_params["clearance_planet"]` |  | sspg: fixed, cpg: fixed |
| 11 | `clearance_case_mount_holes_shell_thickness` | fixed / config | high | 889 | `self.design_params["clearance_case_mount_holes_shell_thickness"]` |  | sspg: fixed, cpg: fixed |
| 12 | `standard_clearance_1_5mm` | fixed / config | high | 890 | `self.design_params["standard_clearance_1_5mm"]` |  | sspg: fixed, cpg: fixed |
| 13 | `standard_clearance_2_mm` | fixed / config | high | 891 | `self.design_params["standard_clearance_2_mm"]` |  |  |
| 14 | `standard_fillet_1_5mm` | fixed / config | high | 893 | `self.design_params["standard_fillet_1_5mm"]` |  | sspg: fixed, cpg: fixed |
| 15 | `standard_fillet_3_mm` | fixed / config | high | 894 | `self.design_params["standard_fillet_3_mm"]` |  |  |
| 16 | `standard_bearing_insertion_chamfer` | fixed / config | high | 895 | `self.design_params["standard_bearing_insertion_chamfer"]` |  | sspg: fixed, cpg: fixed |
| 17 | `bearingIDClearanceMM` | fixed / config | high | 830, 896 | `design_parameters["bearingIDClearanceMM"] ‖ self.design_params["bearingIDClearanceMM"]` | 2 assignments (two-case rule or reassigned) | sspg: fixed, cpg: fixed |
| 18 | `tight_clearance_3DP` | fixed / config | high | 897 | `self.design_params["tight_clearance_3DP"]` |  | sspg: fixed, cpg: fixed |
| 19 | `loose_clearance_3DP` | fixed / config | high | 898 | `self.design_params["loose_clearance_3DP"]` |  | sspg: fixed, cpg: fixed |
| 20 | `bearing_step_width` | fixed / config | high | 899 | `self.design_params["bearing_step_width"]` |  |  |
| 21 | `motor_OD` | input / motor | high | 902 | `self.motorDiaMM` |  | sspg: input, cpg: input |
| 22 | `motor_height` | input / motor | high | 903 | `self.motorLengthMM` |  | sspg: input, cpg: input |
| 23 | `rotor_OD` | input / motor | high | 904 | `self.motor.rotor_OD` |  |  |
| 24 | `stator_ID` | input / motor | high | 905 | `self.motor.stator_ID` |  |  |
| 25 | `rotor_height` | input / motor | high | 906 | `self.motor.rotor_height` |  |  |
| 26 | `rotor_ID` | input / motor | high | 907 | `self.motor.rotor_ID` |  |  |
| 27 | `stator_height` | input / motor | high | 908 | `self.motor.stator_height` |  |  |
| 28 | `stator_OD` | input / motor | high | 909 | `self.motor.stator_OD` |  |  |
| 29 | `stator_hole_dia` | input / motor | high | 910 | `self.motor.stator_hole_dia` |  |  |
| 30 | `stator_top_height` | input / motor | high | 911 | `self.motor.stator_wire_top_height` |  |  |
| 31 | `stator_mid_height` | input / motor | high | 912 | `self.motor.stator_mid_height` |  |  |
| 32 | `stator_bottom_height` | input / motor | high | 913 | `self.motor.stator_wire_bottom_height` |  |  |
| 33 | `stator_inside_OD` | input / motor | high | 914 | `self.motor.stator_wire_OD` |  |  |
| 34 | `stator_hole_num` | input / motor | high | 915 | `self.motor.stator_hole_num` |  |  |
| 35 | `stator_inside_ID` | input / motor | high | 916 | `self.motor.stator_wire_ID` |  |  |
| 36 | `driver_upper_holes_dist_from_center` | input / driver | high | 919 | `self.motor_driver_params["driver_upper_holes_dist_from_center"]` |  | sspg: input, cpg: input |
| 37 | `driver_lower_holes_dist_from_center` | input / driver | high | 920 | `self.motor_driver_params["driver_lower_holes_dist_from_center"]` |  | sspg: input, cpg: input |
| 38 | `driver_side_holes_dist_from_center` | input / driver | high | 921 | `self.motor_driver_params["driver_side_holes_dist_from_center"]` |  | sspg: input, cpg: input |
| 39 | `driver_mount_holes_dia` | input / driver | high | 922 | `self.motor_driver_params["driver_mount_holes_dia"]` |  | sspg: input, cpg: input |
| 40 | `driver_mount_inserts_OD` | input / driver | high | 923 | `self.motor_driver_params["driver_mount_inserts_OD"]` |  | sspg: input, cpg: input |
| 41 | `driver_mount_thickness` | input / driver | high | 924 | `self.motor_driver_params["driver_mount_thickness"]` |  | sspg: input, cpg: input |
| 42 | `driver_mount_height` | input / driver | high | 925 | `self.motor_driver_params["driver_mount_height"]` |  | sspg: input, cpg: input |
| 43 | `motor_mount_driver_hole_dia` | fixed / config | high | 926 | `self.design_params["motor_mount_driver_hole_dia"]` |  |  |
| 44 | `motor_mount_driver_hole_num` | fixed / config | high | 927 | `self.design_params["motor_mount_driver_hole_num"]` |  |  |
| 45 | `rotor_hub_thickness` | fixed / config | high | 930 | `self.design_params["rotor_hub_thickness"]` |  |  |
| 46 | `rotor_hub_height` | fixed / config | high | 931 | `self.design_params["rotor_hub_height"]` |  |  |
| 47 | `rotor_hub_sun_hole_dia` | fixed / config | high | 932 | `self.design_params["rotor_hub_sun_hole_dia"]` |  |  |
| 48 | `rotor_hub_sun_hole_num` | fixed / config | high | 933 | `self.design_params["rotor_hub_sun_hole_num"]` |  |  |
| 49 | `rotor_top_bearing_ID` | dependent / formula | high | 936 | `per_motor_value(self.design_params, "rotor_top_bearing_ID", self.motor_name)` |  |  |
| 50 | `rotor_top_bearing_OD` | dependent / formula | high | 937 | `per_motor_value(self.design_params, "rotor_top_bearing_OD", self.motor_name)` |  |  |
| 51 | `rotor_top_bearing_width` | dependent / formula | high | 938 | `per_motor_value(self.design_params, "rotor_top_bearing_width", self.motor_name)` |  |  |
| 52 | `rotor_bottom_bearing_ID` | dependent / formula | high | 939 | `per_motor_value(self.design_params, "rotor_bottom_bearing_ID", self.motor_name)` |  |  |
| 53 | `rotor_bottom_bearing_OD` | dependent / formula | high | 940 | `per_motor_value(self.design_params, "rotor_bottom_bearing_OD", self.motor_name)` |  |  |
| 54 | `rotor_bottom_bearing_width` | dependent / formula | high | 941 | `per_motor_value(self.design_params, "rotor_bottom_bearing_width", self.motor_name)` |  |  |
| 55 | `planet_pin_bolt_dia` | fixed / config | high | 944 | `self.design_params["planet_pin_bolt_dia"]` |  | sspg: fixed, cpg: fixed |
| 56 | `planet_shaft_step_offset` | fixed / config | high | 946 | `self.design_params["planet_shaft_step_offset"]` |  | sspg: fixed, cpg: fixed |
| 57 | `planet_bearing_OD` | fixed / config | high | 947 | `self.design_params["planet_bearing_OD"]` |  | sspg: fixed, cpg: fixed |
| 58 | `planet_bearing_width` | fixed / config | high | 948 | `self.design_params["planet_bearing_width"]` |  | sspg: fixed, cpg: fixed |
| 59 | `planet_bearing_ID` | fixed / config | high | 949 | `self.design_params["planet_bearing_ID"]` |  |  |
| 60 | `sun_coupler_hub_thickness` | fixed / config | high | 952 | `self.design_params["sun_coupler_hub_thickness"]` |  | sspg: fixed, cpg: fixed |
| 61 | `sun_shaft_bearing_ID` | fixed / config | high | 953 | `self.design_params["sun_shaft_bearing_ID"]` |  | sspg: fixed, cpg: fixed |
| 62 | `sun_shaft_bearing_OD` | fixed / config | high | 954 | `self.design_params["sun_shaft_bearing_OD"]` |  | sspg: fixed, cpg: fixed |
| 63 | `sun_shaft_bearing_width` | fixed / config | high | 955 | `self.design_params["sun_shaft_bearing_width"]` |  | sspg: fixed, cpg: fixed |
| 64 | `sun_central_bolt_dia` | fixed / config | high | 956 | `self.design_params["sun_central_bolt_dia"]` |  | sspg: fixed, cpg: fixed |
| 65 | `sec_carrier_thickness` | fixed / config | high | 959 | `self.design_params["sec_carrier_thickness"]` |  | sspg: fixed, cpg: fixed |
| 66 | `carrier_trapezoidal_support_sun_offset` | fixed / config | high | 962 | `self.design_params["carrier_trapezoidal_support_sun_offset"]` |  | sspg: fixed, cpg: fixed |
| 67 | `carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID` | fixed / config | high | 963 | `self.design_params["carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID"]` |  |  |
| 68 | `carrier_trapezoidal_support_hole_dia` | fixed / config | high | 964 | `self.design_params["carrier_trapezoidal_support_hole_dia"]` |  | sspg: fixed, cpg: fixed |
| 69 | `case_mounting_surface_height` | fixed / config | high | 971 | `self.design_params["case_mounting_surface_height"]` |  | sspg: fixed, cpg: fixed |
| 70 | `case_mounting_hole_dia` | fixed / config | high | 972 | `self.design_params["case_mounting_hole_dia"]` |  | sspg: fixed, cpg: fixed |
| 71 | `motor_case_thickness` | fixed / config | high | 974 | `self.design_params["motor_case_thickness"]` |  |  |
| 72 | `output_mount_hole_dia` | fixed / config | high | 976 | `self.design_params["output_mount_hole_dia"]` |  |  |
| 73 | `actuactor_mount_hole_dia` | fixed / config | high | 978 | `self.design_params["actuactor_mount_hole_dia"]` |  |  |
| 74 | `motor_case_OD_base_to_chamfer` | fixed / config | high | 980 | `self.design_params["motor_case_OD_base_to_chamfer"]` |  |  |
| 75 | `pattern_offset_from_motor_case_OD_base` | fixed / config | high | 981 | `self.design_params["pattern_offset_from_motor_case_OD_base"]` |  | sspg: fixed, cpg: fixed |
| 76 | `pattern_bulge_dia` | fixed / config | high | 982 | `self.design_params["pattern_bulge_dia"]` |  | sspg: fixed, cpg: fixed |
| 77 | `pattern_num_bulge` | fixed / config | high | 983 | `self.design_params["pattern_num_bulge"]` |  | sspg: fixed, cpg: fixed |
| 78 | `pattern_depth` | fixed / config | high | 984 | `self.design_params["pattern_depth"]` |  | sspg: fixed, cpg: fixed |
| 79 | `magnet_mount_hole_dia` | fixed / config | high | 989 | `self.design_params["magnet_mount_hole_dia"]` |  |  |
| 80 | `magnet_thickness` | fixed / config | high | 990 | `self.design_params["magnet_thickness"]` |  |  |
| 81 | `magnet_dia` | fixed / config | high | 991 | `self.design_params["magnet_dia"]` |  |  |
| 82 | `magnet_mount_thickness` | fixed / config | high | 992 | `self.design_params["magnet_mount_thickness"]` |  |  |
| 83 | `magnet_pattern_bulge_dia` | fixed / config | high | 993 | `self.design_params["magnet_pattern_bulge_dia"]` |  |  |
| 84 | `magnet_pattern_bulge_number` | fixed / config | high | 994 | `self.design_params["magnet_pattern_bulge_number"]` |  |  |
| 85 | `magnet_mount_height` | fixed / config | high | 995 | `self.design_params["magnet_mount_height"]` |  |  |
| 86 | `big_ring_radial_width` | fixed / config | high | 998 | `self.design_params["ringRadialWidthMMBig"]` |  |  |
| 87 | `small_ring_radial_width` | fixed / config | high | 999 | `self.design_params["ringRadialWidthMMSmall"]` |  |  |
| 88 | `ring_gearbox_casing_thickness` | fixed / config | high | 986 | `self.design_params["ring_gearbox_casing_thickness"]` |  |  |
| 89 | `h_a` | dependent / formula | high | 1009 | `1 * self.module` |  | sspg: dependent, cpg: dependent |
| 90 | `h_b` | dependent / formula | high | 1011 | `1.25 * self.module` |  | sspg: dependent, cpg: dependent |
| 91 | `h_f` | dependent / formula | high | 1010 | `1.25 * self.module` |  | sspg: dependent, cpg: dependent |
| 92 | `clr_tip_root` | dependent / formula | high | 1012 | `self.h_f - self.h_a` |  | sspg: dependent, cpg: dependent |
| 93 | `clr_tip_root_s` | dependent / formula | high | 1013 | `self.h_f - self.h_a` |  |  |
| 94 | `dp_s` | dependent / formula | high | 1050 | `self.module * self.Ns` |  | sspg: dependent, cpg: dependent |
| 95 | `db_s` | dependent / formula | high | 1051 | `self.dp_s * np.cos ( self.pressure_angle )` |  | sspg: dependent, cpg: dependent |
| 96 | `alpha_s` | dependent / formula | high | 1052 | `( self.dp_s ** 2 - self.db_s ** 2 )**0.5 / self.db_s * 180 / np.pi - self.pressure_angle_deg` |  | sspg: dependent, cpg: dependent |
| 97 | `beta_s` | dependent / formula | high | 1053 | `( 360 / ( 4 * self.Ns ) - self.alpha_s ) * 2` |  | sspg: dependent, cpg: dependent |
| 98 | `fw_s_calc` | dependent / stress rule (face width) | high | 1055 | `self.inrunnerWolfromPlanetaryGearbox.fwSunMM` |  | sspg: dependent, cpg: dependent |
| 99 | `dp_p_b` | dependent / formula | high | 1035 | `self.module * self.Np_b` |  | cpg: dependent |
| 100 | `db_p_b` | dependent / formula | high | 1036 | `self.dp_p_b * np.cos ( self.pressure_angle )` |  | cpg: dependent |
| 101 | `alpha_p_b` | dependent / formula | high | 1037 | `( self.dp_p_b ** 2 - self.db_p_b ** 2 )**0.5 / self.db_p_b * 180 / np.pi - self.pressure_angle_deg` |  | cpg: dependent |
| 102 | `beta_p_b` | dependent / formula | high | 1038 | `( 360 / ( 4 * self.Np_b ) - self.alpha_p_b ) * 2` |  | cpg: dependent |
| 103 | `fw_p_b` | dependent / formula | high | 1039 | `self.fw_r_b` |  | cpg: dependent |
| 104 | `dp_r_b` | dependent / formula | high | 1017 | `self.module * self.Nr_b` |  |  |
| 105 | `db_r_b` | dependent / formula | high | 1018 | `self.dp_r_b * np.cos ( self.pressure_angle )` |  |  |
| 106 | `alpha_r_b` | dependent / formula | high | 1019 | `( self.dp_r_b ** 2 - self.db_r_b ** 2 )**0.5 / self.db_r_b * 180 / np.pi - self.pressure_angle_deg` |  |  |
| 107 | `beta_r_b` | dependent / formula | high | 1020 | `( 360 / ( 4 * self.Nr_b ) + self.alpha_r_b ) * 2` |  |  |
| 108 | `fw_r_b` | dependent / stress rule (face width) | high | 1022 | `self.inrunnerWolfromPlanetaryGearbox.fwRingBigMM` |  |  |
| 109 | `dp_r_s` | dependent / formula | high | 1027 | `self.module * self.Nr_s` |  |  |
| 110 | `db_r_s` | dependent / formula | high | 1028 | `self.dp_r_s * np.cos ( self.pressure_angle )` |  |  |
| 111 | `alpha_r_s` | dependent / formula | high | 1029 | `( self.dp_r_s ** 2 - self.db_r_s ** 2 )**0.5 / self.db_r_s * 180 / np.pi - self.pressure_angle_deg` |  |  |
| 112 | `beta_r_s` | dependent / formula | high | 1030 | `( 360 / ( 4 * self.Nr_s ) + self.alpha_r_s ) * 2` |  |  |
| 113 | `fw_r_s` | dependent / stress rule (face width) | high | 1031 | `self.inrunnerWolfromPlanetaryGearbox.fwRingSmallMM` |  |  |
| 114 | `dp_p_s` | dependent / formula | high | 1042 | `self.module * self.Np_s` |  | cpg: dependent |
| 115 | `db_p_s` | dependent / formula | high | 1043 | `self.dp_p_s * np.cos ( self.pressure_angle )` |  | cpg: dependent |
| 116 | `alpha_p_s` | dependent / formula | high | 1044 | `( self.dp_p_s ** 2 - self.db_p_s ** 2 )**0.5 / self.db_p_s * 180 / np.pi - self.pressure_angle_deg` |  | cpg: dependent |
| 117 | `beta_p_s` | dependent / formula | high | 1045 | `( 360 / ( 4 * self.Np_s ) - self.alpha_p_s ) * 2` |  | cpg: dependent |
| 118 | `fw_p_s` | dependent / formula | high | 1047 | `self.fw_r_s + self.clearance_planet` |  | cpg: dependent |
| 119 | `motor_mount_driver_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 1060 | `motor_mount_driver_bolt.nut_width_across_flats` |  |  |
| 120 | `motor_mount_driver_nut_depth` | dependent / lookup (bolt/nut) | high | 1061 | `motor_mount_driver_bolt.nut_thickness` |  |  |
| 121 | `planet_pin_socket_head_dia` | dependent / lookup (bolt/nut) | high | 1066 | `planet_pin_bolt.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 122 | `planet_pin_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 1067 | `planet_pin_bolt.nut_width_across_flats` |  |  |
| 123 | `planet_pin_nut_depth` | dependent / lookup (bolt/nut) | high | 1068 | `planet_pin_bolt.nut_thickness` |  |  |
| 124 | `sun_central_bolt_socket_head_dia` | dependent / lookup (bolt/nut) | high | 1072 | `sun_central_bolt.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 125 | `rotor_hub_sun_hole_CSK_OD` | dependent / lookup (bolt/nut) | high | 1076 | `rotor_hub_sun_bolt.bolt_head_dia` |  |  |
| 126 | `rotor_hub_sun_hole_CSK_head_height` | dependent / lookup (bolt/nut) | high | 1077 | `rotor_hub_sun_bolt.bolt_head_height` |  |  |
| 127 | `sun_hub_dia` | dependent / formula | high | 1079 | `self.rotor_top_bearing_ID - 2*self.rotor_hub_thickness` |  | sspg: dependent, cpg: dependent |
| 128 | `output_bearing_ID` | dependent / lookup (bearing) | high | 1084 | `OutputBearings.getBearingIDMM()` |  |  |
| 129 | `output_bearing_OD` | dependent / lookup (bearing) | high | 1085 | `OutputBearings.getBearingODMM()` |  |  |
| 130 | `output_bearing_width` | dependent / lookup (bearing) | high | 1086 | `OutputBearings.getBearingWidthMM()` |  |  |
| 131 | `carrier_trapezoidal_support_hole_socket_head_dia` | dependent / lookup (bolt/nut) | high | 1091 | `carrier_trapezoidal_support_hole.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 132 | `carrier_trapezoidal_support_hole_wrench_size` | dependent / lookup (bolt/nut) | high | 1092 | `carrier_trapezoidal_support_hole.nut_width_across_flats` |  | sspg: dependent, cpg: dependent |
| 133 | `carrier_trapezoidal_support_nut_depth` | dependent / lookup (bolt/nut) | high | 1093 | `carrier_trapezoidal_support_hole.nut_thickness` |  |  |
| 134 | `stator_hole_nut_depth` | dependent / lookup (bolt/nut) | high | 1106 | `stator_case_mounting_hole_bolt.nut_thickness` |  |  |
| 135 | `stator_hole_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 1105 | `stator_case_mounting_hole_bolt.nut_width_across_flats` |  |  |
| 136 | `stator_hole_allen_socket_dia` | dependent / lookup (bolt/nut) | high | 1104 | `stator_case_mounting_hole_bolt.bolt_head_dia` |  |  |
| 137 | `case_mounting_hole_allen_socket_dia` | dependent / lookup (bolt/nut) | high | 1110 | `case_mounting_hole_bolt.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 138 | `case_mounting_wrench_size` | dependent / lookup (bolt/nut) | high | 1111 | `case_mounting_hole_bolt.nut_width_across_flats` |  | sspg: dependent, cpg: dependent |
| 139 | `case_mounting_nut_depth` | dependent / lookup (bolt/nut) | high | 1112 | `case_mounting_hole_bolt.nut_thickness` |  |  |
| 140 | `output_mount_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 1116 | `output_mount_hole_bolt.nut_width_across_flats` |  |  |
| 141 | `output_mount_hole_nut_depth` | dependent / lookup (bolt/nut) | high | 1117 | `output_mount_hole_bolt.nut_thickness` |  |  |
| 142 | `actuactor_mount_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 1121 | `actuactor_mount_hole_bolt.nut_width_across_flats` |  |  |
| 143 | `actuactor_mount_nut_depth` | dependent / lookup (bolt/nut) | high | 1122 | `actuactor_mount_hole_bolt.nut_thickness` |  |  |
| 144 | `case_mounting_hole_shift` | dependent / formula | high | 1124 | `self.case_mounting_hole_dia / 2` |  | sspg: dependent, cpg: dependent |
| 145 | `fw_s_used` | dependent / formula | high | 1130 | `(self.bearing_step_width + self.rotor_top_bearing_width - self.sun_coupler_hub_thickness + self.bearing_step_w…` |  | sspg: dependent, cpg: dependent |
| 146 | `carrier_thickness` | fixed / config | high | 960 | `self.design_params["carrier_thickness"]` |  |  |
| 147 | `carrier_ring_bearing_ID` | fixed / config | high | 968 | `self.design_params["carrier_ring_bearing_ID"]` |  |  |
| 148 | `carrier_ring_bearing_OD` | fixed / config | high | 966 | `self.design_params["carrier_ring_bearing_OD"]` |  |  |
| 149 | `carrier_ring_bearing_width` | fixed / config | high | 967 | `self.design_params["carrier_ring_bearing_width"]` |  |  |
| 150 | `rotor_top_bearing_holder_thickness` | dependent / formula | high | 1126 | `(self.bearing_step_width + self.rotor_top_bearing_width - (self.standard_clearance_1_5mm/2 + self.stator_top_h…` |  |  |

## Config accounting

| Block | Keys | Read by this type | Read but not written to the CAD | Never used |
|---|---|---|---|---|
| `inwpg_optimization_parameters` | 13 | yes | GEAR_RATIO_MIN, GEAR_RATIO_MAX, GEAR_RATIO_STEP, MODULE_BIG_MIN, MODULE_BIG_MAX, MODULE_SMALL_MIN, MODULE_SMALL_MAX, NUM_PLANET_MIN, NUM_PLANET_MAX, NUM_TEETH_SUN_MIN, NUM_TEETH_PLANET_BIG_MIN, NUM_TEETH_PLANET_SMALL_MIN, MAX_GB_DIA_MULT_FACTOR | — |
| `inwpg_3DP_design_parameters` | 65 | yes | planetMinDistanceMM, sCarrierExtrusionDiaMM, sCarrierExtrusionClearanceMM, planet_stack_stator_heights | — |
