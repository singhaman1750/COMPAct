# INWPG dependent: variable classification plan

Part of [the plan for all actuators](../PLAN.md). Survey only: nothing in the code, config or CAD output changes on this branch.

## Inventory

- **CAD interface:** `inwpg_dependent_equations_onshape.txt`, **146 variables**; other files: `inwpg_dependent_equations.txt` (146)
- **Code:** `inrunnerWolfromPlanetaryActuator` in `ActuatorAndGearbox_INWPG_dependent.py` (lines 786-2736)
- **Config:** `inwpg_params_dependent.json`, block(s) read: `inwpg_3DP_design_parameters`; search bounds `inwpg_optimization_parameters`; gear standard / MIT factors from `config.json`; driver: `OdrivePro`
- **Survey draft:** dependent 59, fixed 60, input 22, optimisation 5; 69 names also in SSPG / CPG; 0 alias names (same value written under a second name); 0 flagged by the survey

## Special cases (frameless inrunner, Wolfrom)

| Variable(s) | What the code does | Proposed classification |
|---|---|---|
| `rotor_*`, `stator_*` | frameless inrunner geometry | Input / motor |
| `Nr_b`, `Nr_s` | `Ns + 2·Np_b`, `Ns + Np_b + Np_s` | Dependent / implicit constraint (as WPG) |
| `module` | `moduleBig`; one module in the CAD, used for both rings (`dp_r_b`, `dp_r_s`) | Optimisation; **bug-18 pattern** |
| `fw_s_calc`, `fw_r_b`, `fw_r_s` | MIT stress rule (three meshes) with the **width cap** (`planet_stack_stator_heights` = 2 stator heights, PR #97) and the CPG-style bearing minimum | Dependent / stress rule |
| `fw_p_b` | `= fw_r_b` (**the reverse of WPG**, where `fw_p_b` is the stress width and `fw_r_b` the copy) | Dependent / formula |
| `fw_p_s` | `fw_r_s + clearance_planet` | Dependent / formula |
| `rotor_top_bearing_*` | catalogue lookup (assigned twice, L880 / L1117) | Dependent / lookup |
| `bearingIDClearanceMM` | written to the CAD (unusual: a code-only key in other types) | Fixed / config |
| `sun_hub_dia`, `case_mounting_hole_shift` | `rotor_ID − 2 × rotor_hub_thickness`; `dia / 2` | Dependent / formula (as INCPG) |

## Hard-coded numbers (medium)

| Where | Number | Proposed key |
|---|---|---|
| planet-bearing minimum (L2289-2293) | 2/3, 1/3 | `planet_bearing_gap` |
| mass code: `+ 1.25 × module` ring tip, `1.5 × 3`, bearing masses (5 g, 5 g, 4 g) | various | mass-only list |

## Config (`inwpg_params_dependent.json`)
- Code-only keys: `planetMinDistanceMM`, `sCarrierExtrusion*`, `min_rotor_top_bearing_ID`, `planet_stack_stator_heights` (width cap).
- Optimisation block: 13 search bounds (two module ranges).
- CAD 7 (output ring gear / bearing don't move with RI80) concerns the Onshape model, not the classification.

## Test plan
- Registry: Wolfrom setter (as WPG); RI100 / RI80; 3 golden designs.
- Specific: stress-rule widths with the width cap (cap active / not), the planet-bearing gap.

## Risks / notes
- **The shared face-width rule must not be name-based for Wolfrom types**: `fw_p_b` is the stress width in WPG but a copy in INWPG (see the plan's cross-cutting section). Effort: ~1.5 h.

## Survey draft: every variable

Automatic first pass from the code (the special cases above take precedence). Category guesses come from the source of each value; *flags* mark hard-coded numbers, several assignments or a writer expression. The final category, sub-type, `depends_on`, confidence and reason are set during the classification itself.

| # | Variable | Draft category / sub-type | Conf. | Line | Code | Flags | SSPG / CPG |
|---|---|---|---|---|---|---|---|
| 1 | `Ns` | optimisation / teeth | high | 899 | `self.inrunnerWolfromPlanetaryGearbox.Ns` |  | sspg: optimisation, cpg: optimisation |
| 2 | `Np_b` | optimisation / teeth | high | 900 | `self.inrunnerWolfromPlanetaryGearbox.NpBig` |  | cpg: optimisation |
| 3 | `Np_s` | optimisation / teeth | high | 901 | `self.inrunnerWolfromPlanetaryGearbox.NpSmall` |  | cpg: optimisation |
| 4 | `Nr_b` | dependent / formula | high | 902 | `self.Ns + self.Np_b * 2` |  |  |
| 5 | `Nr_s` | dependent / formula | high | 903 | `self.Ns + self.Np_b + self.Np_s` |  |  |
| 6 | `num_planet` | optimisation / planets | high | 905 | `self.inrunnerWolfromPlanetaryGearbox.numPlanet` |  | sspg: optimisation, cpg: optimisation |
| 7 | `module` | optimisation / module | high | 904 | `self.inrunnerWolfromPlanetaryGearbox.moduleBig` |  | sspg: optimisation, cpg: optimisation |
| 8 | `pressure_angle` | fixed / gear standard | high | 911 | `self.inrunnerWolfromPlanetaryGearbox.getPressureAngleRad()` |  | sspg: fixed, cpg: fixed |
| 9 | `pressure_angle_deg` | fixed / gear standard | high | 912 | `self.inrunnerWolfromPlanetaryGearbox.getPressureAngleRad() * 180 / np.pi` |  |  |
| 10 | `clearance_planet` | fixed / config | high | 915 | `self.design_params["clearance_planet"]` |  | sspg: fixed, cpg: fixed |
| 11 | `clearance_case_mount_holes_shell_thickness` | fixed / config | high | 916 | `self.design_params["clearance_case_mount_holes_shell_thickness"]` |  | sspg: fixed, cpg: fixed |
| 12 | `standard_clearance_1_5mm` | fixed / config | high | 917 | `self.design_params["standard_clearance_1_5mm"]` |  | sspg: fixed, cpg: fixed |
| 13 | `standard_clearance_2_mm` | fixed / config | high | 918 | `self.design_params["standard_clearance_2_mm"]` |  |  |
| 14 | `standard_fillet_1_5mm` | fixed / config | high | 920 | `self.design_params["standard_fillet_1_5mm"]` |  | sspg: fixed, cpg: fixed |
| 15 | `standard_fillet_3_mm` | fixed / config | high | 921 | `self.design_params["standard_fillet_3_mm"]` |  |  |
| 16 | `standard_bearing_insertion_chamfer` | fixed / config | high | 922 | `self.design_params["standard_bearing_insertion_chamfer"]` |  | sspg: fixed, cpg: fixed |
| 17 | `bearingIDClearanceMM` | fixed / config | high | 829, 923 | `design_parameters["bearingIDClearanceMM"] ‖ self.design_params["bearingIDClearanceMM"]` | 2 assignments (two-case rule or reassigned) | sspg: fixed, cpg: fixed |
| 18 | `tight_clearance_3DP` | fixed / config | high | 924 | `self.design_params["tight_clearance_3DP"]` |  | sspg: fixed, cpg: fixed |
| 19 | `loose_clearance_3DP` | fixed / config | high | 925 | `self.design_params["loose_clearance_3DP"]` |  | sspg: fixed, cpg: fixed |
| 20 | `bearing_step_width` | fixed / config | high | 926 | `self.design_params["bearing_step_width"]` |  |  |
| 21 | `motor_OD` | input / motor | high | 929 | `self.motorDiaMM` |  | sspg: input, cpg: input |
| 22 | `motor_height` | input / motor | high | 930 | `self.motorLengthMM` |  | sspg: input, cpg: input |
| 23 | `rotor_OD` | input / motor | high | 931 | `self.motor.rotor_OD` |  |  |
| 24 | `stator_ID` | input / motor | high | 932 | `self.motor.stator_ID` |  |  |
| 25 | `rotor_height` | input / motor | high | 933 | `self.motor.rotor_height` |  |  |
| 26 | `rotor_ID` | input / motor | high | 934 | `self.motor.rotor_ID` |  |  |
| 27 | `stator_height` | input / motor | high | 935 | `self.motor.stator_height` |  |  |
| 28 | `stator_OD` | input / motor | high | 936 | `self.motor.stator_OD` |  |  |
| 29 | `stator_hole_dia` | input / motor | high | 937 | `self.motor.stator_hole_dia` |  |  |
| 30 | `stator_top_height` | input / motor | high | 938 | `self.motor.stator_wire_top_height` |  |  |
| 31 | `stator_mid_height` | input / motor | high | 939 | `self.motor.stator_mid_height` |  |  |
| 32 | `stator_bottom_height` | input / motor | high | 940 | `self.motor.stator_wire_bottom_height` |  |  |
| 33 | `stator_inside_OD` | input / motor | high | 941 | `self.motor.stator_wire_OD` |  |  |
| 34 | `stator_hole_num` | input / motor | high | 942 | `self.motor.stator_hole_num` |  |  |
| 35 | `stator_inside_ID` | input / motor | high | 943 | `self.motor.stator_wire_ID` |  |  |
| 36 | `driver_upper_holes_dist_from_center` | input / driver | high | 946 | `self.motor_driver_params["driver_upper_holes_dist_from_center"]` |  | sspg: input, cpg: input |
| 37 | `driver_lower_holes_dist_from_center` | input / driver | high | 947 | `self.motor_driver_params["driver_lower_holes_dist_from_center"]` |  | sspg: input, cpg: input |
| 38 | `driver_side_holes_dist_from_center` | input / driver | high | 948 | `self.motor_driver_params["driver_side_holes_dist_from_center"]` |  | sspg: input, cpg: input |
| 39 | `driver_mount_holes_dia` | input / driver | high | 949 | `self.motor_driver_params["driver_mount_holes_dia"]` |  | sspg: input, cpg: input |
| 40 | `driver_mount_inserts_OD` | input / driver | high | 950 | `self.motor_driver_params["driver_mount_inserts_OD"]` |  | sspg: input, cpg: input |
| 41 | `driver_mount_thickness` | input / driver | high | 951 | `self.motor_driver_params["driver_mount_thickness"]` |  | sspg: input, cpg: input |
| 42 | `driver_mount_height` | input / driver | high | 952 | `self.motor_driver_params["driver_mount_height"]` |  | sspg: input, cpg: input |
| 43 | `motor_mount_driver_hole_dia` | fixed / config | high | 953 | `self.design_params["motor_mount_driver_hole_dia"]` |  |  |
| 44 | `motor_mount_driver_hole_num` | fixed / config | high | 954 | `self.design_params["motor_mount_driver_hole_num"]` |  |  |
| 45 | `rotor_hub_thickness` | fixed / config | high | 957 | `self.design_params["rotor_hub_thickness"]` |  |  |
| 46 | `rotor_hub_height` | fixed / config | high | 958 | `self.design_params["rotor_hub_height"]` |  |  |
| 47 | `rotor_hub_sun_hole_dia` | fixed / config | high | 959 | `self.design_params["rotor_hub_sun_hole_dia"]` |  |  |
| 48 | `rotor_hub_sun_hole_num` | fixed / config | high | 960 | `self.design_params["rotor_hub_sun_hole_num"]` |  |  |
| 49 | `rotor_top_bearing_ID` | dependent / lookup (bearing) | high | 880, 1117 | `RotorTopBearings.getBearingIDMM() ‖ RotorTopBearings.getBearingIDMM()` | 2 assignments (two-case rule or reassigned) |  |
| 50 | `rotor_top_bearing_OD` | dependent / lookup (bearing) | high | 881, 1118 | `RotorTopBearings.getBearingODMM() ‖ RotorTopBearings.getBearingODMM()` | 2 assignments (two-case rule or reassigned) |  |
| 51 | `rotor_top_bearing_width` | dependent / lookup (bearing) | high | 882, 1119 | `RotorTopBearings.getBearingWidthMM() ‖ RotorTopBearings.getBearingWidthMM()` | 2 assignments (two-case rule or reassigned) |  |
| 52 | `rotor_bottom_bearing_ID` | fixed / config | high | 962 | `self.design_params["rotor_bottom_bearing_ID"]` |  |  |
| 53 | `rotor_bottom_bearing_OD` | fixed / config | high | 963 | `self.design_params["rotor_bottom_bearing_OD"]` |  |  |
| 54 | `rotor_bottom_bearing_width` | fixed / config | high | 964 | `self.design_params["rotor_bottom_bearing_width"]` |  |  |
| 55 | `planet_pin_bolt_dia` | fixed / config | high | 967 | `self.design_params["planet_pin_bolt_dia"]` |  | sspg: fixed, cpg: fixed |
| 56 | `planet_shaft_step_offset` | fixed / config | high | 969 | `self.design_params["planet_shaft_step_offset"]` |  | sspg: fixed, cpg: fixed |
| 57 | `planet_bearing_OD` | fixed / config | high | 970 | `self.design_params["planet_bearing_OD"]` |  | sspg: fixed, cpg: fixed |
| 58 | `planet_bearing_width` | fixed / config | high | 971 | `self.design_params["planet_bearing_width"]` |  | sspg: fixed, cpg: fixed |
| 59 | `planet_bearing_ID` | fixed / config | high | 972 | `self.design_params["planet_bearing_ID"]` |  |  |
| 60 | `sun_coupler_hub_thickness` | fixed / config | high | 975 | `self.design_params["sun_coupler_hub_thickness"]` |  | sspg: fixed, cpg: fixed |
| 61 | `sun_shaft_bearing_ID` | fixed / config | high | 976 | `self.design_params["sun_shaft_bearing_ID"]` |  | sspg: fixed, cpg: fixed |
| 62 | `sun_shaft_bearing_OD` | fixed / config | high | 977 | `self.design_params["sun_shaft_bearing_OD"]` |  | sspg: fixed, cpg: fixed |
| 63 | `sun_shaft_bearing_width` | fixed / config | high | 978 | `self.design_params["sun_shaft_bearing_width"]` |  | sspg: fixed, cpg: fixed |
| 64 | `sun_central_bolt_dia` | fixed / config | high | 979 | `self.design_params["sun_central_bolt_dia"]` |  | sspg: fixed, cpg: fixed |
| 65 | `sec_carrier_thickness` | fixed / config | high | 982 | `self.design_params["sec_carrier_thickness"]` |  | sspg: fixed, cpg: fixed |
| 66 | `carrier_trapezoidal_support_sun_offset` | fixed / config | high | 985 | `self.design_params["carrier_trapezoidal_support_sun_offset"]` |  | sspg: fixed, cpg: fixed |
| 67 | `carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID` | fixed / config | high | 986 | `self.design_params["carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID"]` |  |  |
| 68 | `carrier_trapezoidal_support_hole_dia` | fixed / config | high | 987 | `self.design_params["carrier_trapezoidal_support_hole_dia"]` |  | sspg: fixed, cpg: fixed |
| 69 | `case_mounting_surface_height` | fixed / config | high | 994 | `self.design_params["case_mounting_surface_height"]` |  | sspg: fixed, cpg: fixed |
| 70 | `case_mounting_hole_dia` | fixed / config | high | 995 | `self.design_params["case_mounting_hole_dia"]` |  | sspg: fixed, cpg: fixed |
| 71 | `motor_case_thickness` | fixed / config | high | 997 | `self.design_params["motor_case_thickness"]` |  |  |
| 72 | `output_mount_hole_dia` | fixed / config | high | 999 | `self.design_params["output_mount_hole_dia"]` |  |  |
| 73 | `actuactor_mount_hole_dia` | fixed / config | high | 1001 | `self.design_params["actuactor_mount_hole_dia"]` |  |  |
| 74 | `motor_case_OD_base_to_chamfer` | fixed / config | high | 1003 | `self.design_params["motor_case_OD_base_to_chamfer"]` |  |  |
| 75 | `pattern_offset_from_motor_case_OD_base` | fixed / config | high | 1004 | `self.design_params["pattern_offset_from_motor_case_OD_base"]` |  | sspg: fixed, cpg: fixed |
| 76 | `pattern_bulge_dia` | fixed / config | high | 1005 | `self.design_params["pattern_bulge_dia"]` |  | sspg: fixed, cpg: fixed |
| 77 | `pattern_num_bulge` | fixed / config | high | 1006 | `self.design_params["pattern_num_bulge"]` |  | sspg: fixed, cpg: fixed |
| 78 | `pattern_depth` | fixed / config | high | 1007 | `self.design_params["pattern_depth"]` |  | sspg: fixed, cpg: fixed |
| 79 | `magnet_mount_hole_dia` | fixed / config | high | 1012 | `self.design_params["magnet_mount_hole_dia"]` |  |  |
| 80 | `magnet_thickness` | fixed / config | high | 1013 | `self.design_params["magnet_thickness"]` |  |  |
| 81 | `magnet_dia` | fixed / config | high | 1014 | `self.design_params["magnet_dia"]` |  |  |
| 82 | `magnet_mount_thickness` | fixed / config | high | 1015 | `self.design_params["magnet_mount_thickness"]` |  |  |
| 83 | `magnet_pattern_bulge_dia` | fixed / config | high | 1016 | `self.design_params["magnet_pattern_bulge_dia"]` |  |  |
| 84 | `magnet_pattern_bulge_number` | fixed / config | high | 1017 | `self.design_params["magnet_pattern_bulge_number"]` |  |  |
| 85 | `magnet_mount_height` | fixed / config | high | 1018 | `self.design_params["magnet_mount_height"]` |  |  |
| 86 | `big_ring_radial_width` | fixed / config | high | 1021 | `self.design_params["ringRadialWidthMMBig"]` |  |  |
| 87 | `small_ring_radial_width` | fixed / config | high | 1022 | `self.design_params["ringRadialWidthMMSmall"]` |  |  |
| 88 | `ring_gearbox_casing_thickness` | fixed / config | high | 1009 | `self.design_params["ring_gearbox_casing_thickness"]` |  |  |
| 89 | `h_a` | dependent / formula | high | 1032 | `1 * self.module` |  | sspg: dependent, cpg: dependent |
| 90 | `h_b` | dependent / formula | high | 1034 | `1.25 * self.module` |  | sspg: dependent, cpg: dependent |
| 91 | `h_f` | dependent / formula | high | 1033 | `1.25 * self.module` |  | sspg: dependent, cpg: dependent |
| 92 | `clr_tip_root` | dependent / formula | high | 1035 | `self.h_f - self.h_a` |  | sspg: dependent, cpg: dependent |
| 93 | `clr_tip_root_s` | dependent / formula | high | 1036 | `self.h_f - self.h_a` |  |  |
| 94 | `dp_s` | dependent / formula | high | 1073 | `self.module * self.Ns` |  | sspg: dependent, cpg: dependent |
| 95 | `db_s` | dependent / formula | high | 1074 | `self.dp_s * np.cos ( self.pressure_angle )` |  | sspg: dependent, cpg: dependent |
| 96 | `alpha_s` | dependent / formula | high | 1075 | `( self.dp_s ** 2 - self.db_s ** 2 )**0.5 / self.db_s * 180 / np.pi - self.pressure_angle_deg` |  | sspg: dependent, cpg: dependent |
| 97 | `beta_s` | dependent / formula | high | 1076 | `( 360 / ( 4 * self.Ns ) - self.alpha_s ) * 2` |  | sspg: dependent, cpg: dependent |
| 98 | `fw_s_calc` | dependent / stress rule (face width) | high | 1078 | `self.inrunnerWolfromPlanetaryGearbox.fwSunMM` |  | sspg: dependent, cpg: dependent |
| 99 | `dp_p_b` | dependent / formula | high | 1058 | `self.module * self.Np_b` |  | cpg: dependent |
| 100 | `db_p_b` | dependent / formula | high | 1059 | `self.dp_p_b * np.cos ( self.pressure_angle )` |  | cpg: dependent |
| 101 | `alpha_p_b` | dependent / formula | high | 1060 | `( self.dp_p_b ** 2 - self.db_p_b ** 2 )**0.5 / self.db_p_b * 180 / np.pi - self.pressure_angle_deg` |  | cpg: dependent |
| 102 | `beta_p_b` | dependent / formula | high | 1061 | `( 360 / ( 4 * self.Np_b ) - self.alpha_p_b ) * 2` |  | cpg: dependent |
| 103 | `fw_p_b` | dependent / formula | high | 1062 | `self.fw_r_b` |  | cpg: dependent |
| 104 | `dp_r_b` | dependent / formula | high | 1040 | `self.module * self.Nr_b` |  |  |
| 105 | `db_r_b` | dependent / formula | high | 1041 | `self.dp_r_b * np.cos ( self.pressure_angle )` |  |  |
| 106 | `alpha_r_b` | dependent / formula | high | 1042 | `( self.dp_r_b ** 2 - self.db_r_b ** 2 )**0.5 / self.db_r_b * 180 / np.pi - self.pressure_angle_deg` |  |  |
| 107 | `beta_r_b` | dependent / formula | high | 1043 | `( 360 / ( 4 * self.Nr_b ) + self.alpha_r_b ) * 2` |  |  |
| 108 | `fw_r_b` | dependent / stress rule (face width) | high | 1045 | `self.inrunnerWolfromPlanetaryGearbox.fwRingBigMM` |  |  |
| 109 | `dp_r_s` | dependent / formula | high | 1050 | `self.module * self.Nr_s` |  |  |
| 110 | `db_r_s` | dependent / formula | high | 1051 | `self.dp_r_s * np.cos ( self.pressure_angle )` |  |  |
| 111 | `alpha_r_s` | dependent / formula | high | 1052 | `( self.dp_r_s ** 2 - self.db_r_s ** 2 )**0.5 / self.db_r_s * 180 / np.pi - self.pressure_angle_deg` |  |  |
| 112 | `beta_r_s` | dependent / formula | high | 1053 | `( 360 / ( 4 * self.Nr_s ) + self.alpha_r_s ) * 2` |  |  |
| 113 | `fw_r_s` | dependent / stress rule (face width) | high | 1054 | `self.inrunnerWolfromPlanetaryGearbox.fwRingSmallMM` |  |  |
| 114 | `dp_p_s` | dependent / formula | high | 1065 | `self.module * self.Np_s` |  | cpg: dependent |
| 115 | `db_p_s` | dependent / formula | high | 1066 | `self.dp_p_s * np.cos ( self.pressure_angle )` |  | cpg: dependent |
| 116 | `alpha_p_s` | dependent / formula | high | 1067 | `( self.dp_p_s ** 2 - self.db_p_s ** 2 )**0.5 / self.db_p_s * 180 / np.pi - self.pressure_angle_deg` |  | cpg: dependent |
| 117 | `beta_p_s` | dependent / formula | high | 1068 | `( 360 / ( 4 * self.Np_s ) - self.alpha_p_s ) * 2` |  | cpg: dependent |
| 118 | `fw_p_s` | dependent / formula | high | 1070 | `self.fw_r_s + self.clearance_planet` |  | cpg: dependent |
| 119 | `motor_mount_driver_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 1083 | `motor_mount_driver_bolt.nut_width_across_flats` |  |  |
| 120 | `motor_mount_driver_nut_depth` | dependent / lookup (bolt/nut) | high | 1084 | `motor_mount_driver_bolt.nut_thickness` |  |  |
| 121 | `planet_pin_socket_head_dia` | dependent / lookup (bolt/nut) | high | 1089 | `planet_pin_bolt.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 122 | `planet_pin_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 1090 | `planet_pin_bolt.nut_width_across_flats` |  |  |
| 123 | `planet_pin_nut_depth` | dependent / lookup (bolt/nut) | high | 1091 | `planet_pin_bolt.nut_thickness` |  |  |
| 124 | `sun_central_bolt_socket_head_dia` | dependent / lookup (bolt/nut) | high | 1095 | `sun_central_bolt.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 125 | `rotor_hub_sun_hole_CSK_OD` | dependent / lookup (bolt/nut) | high | 1099 | `rotor_hub_sun_bolt.bolt_head_dia` |  |  |
| 126 | `rotor_hub_sun_hole_CSK_head_height` | dependent / lookup (bolt/nut) | high | 1100 | `rotor_hub_sun_bolt.bolt_head_height` |  |  |
| 127 | `sun_hub_dia` | dependent / formula | high | 1102 | `self.rotor_ID - 2*self.rotor_hub_thickness` |  | sspg: dependent, cpg: dependent |
| 128 | `output_bearing_ID` | dependent / lookup (bearing) | high | 1107 | `OutputBearings.getBearingIDMM()` |  |  |
| 129 | `output_bearing_OD` | dependent / lookup (bearing) | high | 1108 | `OutputBearings.getBearingODMM()` |  |  |
| 130 | `output_bearing_width` | dependent / lookup (bearing) | high | 1109 | `OutputBearings.getBearingWidthMM()` |  |  |
| 131 | `carrier_trapezoidal_support_hole_socket_head_dia` | dependent / lookup (bolt/nut) | high | 1124 | `carrier_trapezoidal_support_hole.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 132 | `carrier_trapezoidal_support_hole_wrench_size` | dependent / lookup (bolt/nut) | high | 1125 | `carrier_trapezoidal_support_hole.nut_width_across_flats` |  | sspg: dependent, cpg: dependent |
| 133 | `carrier_trapezoidal_support_nut_depth` | dependent / lookup (bolt/nut) | high | 1126 | `carrier_trapezoidal_support_hole.nut_thickness` |  |  |
| 134 | `case_mounting_hole_allen_socket_dia` | dependent / lookup (bolt/nut) | high | 1138 | `case_mounting_hole_bolt.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 135 | `case_mounting_wrench_size` | dependent / lookup (bolt/nut) | high | 1139 | `case_mounting_hole_bolt.nut_width_across_flats` |  | sspg: dependent, cpg: dependent |
| 136 | `case_mounting_nut_depth` | dependent / lookup (bolt/nut) | high | 1140 | `case_mounting_hole_bolt.nut_thickness` |  |  |
| 137 | `output_mount_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 1144 | `output_mount_hole_bolt.nut_width_across_flats` |  |  |
| 138 | `output_mount_hole_nut_depth` | dependent / lookup (bolt/nut) | high | 1145 | `output_mount_hole_bolt.nut_thickness` |  |  |
| 139 | `actuactor_mount_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 1149 | `actuactor_mount_hole_bolt.nut_width_across_flats` |  |  |
| 140 | `actuactor_mount_nut_depth` | dependent / lookup (bolt/nut) | high | 1150 | `actuactor_mount_hole_bolt.nut_thickness` |  |  |
| 141 | `case_mounting_hole_shift` | dependent / formula | high | 1152 | `self.case_mounting_hole_dia / 2` |  | sspg: dependent, cpg: dependent |
| 142 | `fw_s_used` | dependent / formula | high | 1156 | `self.bearing_step_width + self.sec_carrier_thickness +self.clearance_planet +self.fw_p_b+self.fw_p_s` |  | sspg: dependent, cpg: dependent |
| 143 | `carrier_thickness` | fixed / config | high | 983 | `self.design_params["carrier_thickness"]` |  |  |
| 144 | `carrier_ring_bearing_ID` | fixed / config | high | 991 | `self.design_params["carrier_ring_bearing_ID"]` |  |  |
| 145 | `carrier_ring_bearing_OD` | fixed / config | high | 989 | `self.design_params["carrier_ring_bearing_OD"]` |  |  |
| 146 | `carrier_ring_bearing_width` | fixed / config | high | 990 | `self.design_params["carrier_ring_bearing_width"]` |  |  |

## Config accounting

| Block | Keys | Read by this type | Read but not written to the CAD | Never used |
|---|---|---|---|---|
| `inwpg_optimization_parameters` | 13 | yes | GEAR_RATIO_MIN, GEAR_RATIO_MAX, GEAR_RATIO_STEP, MODULE_BIG_MIN, MODULE_BIG_MAX, MODULE_SMALL_MIN, MODULE_SMALL_MAX, NUM_PLANET_MIN, NUM_PLANET_MAX, NUM_TEETH_SUN_MIN, NUM_TEETH_PLANET_BIG_MIN, NUM_TEETH_PLANET_SMALL_MIN, MAX_GB_DIA_MULT_FACTOR | — |
| `inwpg_3DP_design_parameters` | 63 | yes | planetMinDistanceMM, sCarrierExtrusionDiaMM, sCarrierExtrusionClearanceMM, min_rotor_top_bearing_ID, planet_stack_stator_heights | — |
