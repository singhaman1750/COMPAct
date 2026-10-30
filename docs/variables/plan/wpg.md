# WPG: variable classification plan

Part of [the plan for all actuators](../PLAN.md). Survey only: nothing in the code, config or CAD output changes on this branch.

## Inventory

- **CAD interface:** `wpg_equations_onshape.txt`, **143 variables**; other files: `wpg_equations.txt` (144)
- **Code:** `wolfromPlanetaryActuator` in `ActuatorAndGearbox.py` (lines 4795-6619)
- **Config:** `wpg_params.json`, block(s) read: `wpg_3DP_design_parameters`; search bounds `wpg_optimization_parameters`; gear standard / MIT factors from `config.json`; driver: `OdrivePro`
- **Survey draft:** dependent 67, fixed 53, input 18, optimisation 5; 112 names also in SSPG / CPG; 0 alias names (same value written under a second name); 3 flagged by the survey

## Special cases

| Variable(s) | What the code does | Proposed classification |
|---|---|---|
| `Nr_b`, `Nr_s` | `Ns + 2·Np_b` and `Ns + Np_b + Np_s`: the two rings of a Wolfrom gearbox | Dependent / implicit constraint (both); extend the shared `Nr` rule to `Nr_b`, `Nr_s` |
| `module` | `moduleBig`; the CAD file has one module, the small ring (`dp_r_s = module·Nr_s`) and small planet use it too | Optimisation (attr `module`); **same issue as CPG bug 18** (one module in the CAD, `MODULE_SMALL_*` searched); propose `module_b` / `module_s` like CPG |
| `fw_s_calc`, `fw_p_b`, `fw_r_s` | from the MIT stress rule (three meshes) with a combined planet-bearing minimum | Dependent / stress rule (extend the shared pattern to `fw_r_s`) |
| `fw_r_b` = `fw_p_b`, `fw_p_s` = `fw_r_s + clearance_planet` | copies / formulas of other widths | Dependent / formula |
| `clearance_motor_and_case` | **the constant `5`** in `setVariables` (L5080), but the **mass code grows it** with the ring (`(ring1_OD − motor_OD)/2 + 5`, L6404-6406) | Fixed / hard-coded, **medium**; **CAD and mass disagree** (new bug); shared key `clearance_motor_and_case_min` |
| `motor_case_OD_base`, `Motor_case_ID` | sized from `maxGearboxDiameter` (the search limit) + ring wall, not from the chosen design | Dependent / formula (depends on the code-only `maxGearboxDiameter`); note in the reason |
| `sun_hub_dia` | two-case rule: motor output holes + CSK + 2·1.5, or the sun's tip diameter `module·Ns + 2·module` | Dependent / formula (two-case) |
| `ring_to_chamfer_clearance` | `= clearance_planet` (a copy) | Dependent / formula (alias of `clearance_planet`); SSPG/CPG have it as a config value |
| `ring_radial_thickness` | config value | Fixed (as SSPG) |
| `carrier_PCD` | assigned twice with the same formula (L4978, L5094) | Dependent / formula; note the duplicate assignment |

## Hard-coded numbers (medium; candidates for the config)

| Where | Number | Proposed key |
|---|---|---|
| `clearance_motor_and_case` (CAD L5080 = 5; mass L6404-6406 rule with 5) | 5 | `clearance_motor_and_case_min` (+ decide which rule is right: constant or growing) |
| `case_mounting_hole_shift` (L5079) | 0.5 | `case_mounting_hole_wall_overlap` |
| `bearing_mount_thickness` (CAD L5086; mass L6432 with a **different** ring term) | 2, 4 | `bearing_mount_wall_bolt_dia_multiple`; **CAD and mass use different ring terms** (check) |
| planet-bearing minimum (`mitStressAnalysisMinFacewidth` L6221-6225) | 2/3, 1/3 | `planet_bearing_gap` (as CPG: gap, gap/2) |
| mass code `ring_gear1_OD = bearing_ID + standard_clearance_1_5mm × 4` (L6449) | 4 | mass-only; list, decide later |

## Config
- `wpg_design_parameters` (24 keys): **not read** (the runner reads `wpg_3DP_design_parameters`) → unused block.
- Code-only keys of the 3DP block: `planetMinDistanceMM`, `ringRadialWidthMMSmall`, `ringRadialWidthMMBig`, `sCarrierExtrusionDiaMM`, `sCarrierExtrusionClearanceMM`, `gearbox_casing_thickness`, `small_ring_gear_casing_thickness`, `bearingIDClearanceMM`.
- Optimisation block: 15 search bounds (two module ranges).

## Test plan
- Registry: setter for Ns / Np_b / Np_s / Nr_b / Nr_s / modules / planets; 6 golden designs.
- Extra gear sets for: `sun_hub_dia` (both branches), `bearing_mount_thickness` (both branches).
- WPG-specific: stress-rule widths (three meshes), the planet-bearing minimum, each moved key.

## Risks / notes
- CAD vs mass mismatches (motor-case gap, bearing-mount ring term): classify the CAD as it is; log as bugs, fix in a results PR.
- Effort: ~1.5 h (similar size to CPG, two rings).

## Survey draft: every variable

Automatic first pass from the code (the special cases above take precedence). Category guesses come from the source of each value; *flags* mark hard-coded numbers, several assignments or a writer expression. The final category, sub-type, `depends_on`, confidence and reason are set during the classification itself.

| # | Variable | Draft category / sub-type | Conf. | Line | Code | Flags | SSPG / CPG |
|---|---|---|---|---|---|---|---|
| 1 | `Np_b` | optimisation / teeth | high | 4857 | `self.wolfromPlanetaryGearbox.NpBig` |  | cpg: optimisation |
| 2 | `Np_s` | optimisation / teeth | high | 4858 | `self.wolfromPlanetaryGearbox.NpSmall` |  | cpg: optimisation |
| 3 | `Nr_b` | dependent / formula | high | 4859 | `self.Ns + self.Np_b * 2` |  |  |
| 4 | `Nr_s` | dependent / formula | high | 4860 | `self.Ns + self.Np_b + self.Np_s` |  |  |
| 5 | `Ns` | optimisation / teeth | high | 4856 | `self.wolfromPlanetaryGearbox.Ns` |  | sspg: optimisation, cpg: optimisation |
| 6 | `Motor_case_ID` | dependent / formula | high | 5089 | `self.maxGearboxDiameter + self.clearance_motor_and_case * 2 + 2*self.ring_radial_thickness` |  | sspg: dependent, cpg: dependent |
| 7 | `Motor_case_OD_base_to_chamfer` | fixed / config | high | 4916 | `self.design_params["Motor_case_OD_base_to_chamfer"]` |  | sspg: fixed, cpg: fixed |
| 8 | `Motor_case_OD_max` | dependent / formula | high | 5085 | `self.case_mounting_PCD + self.case_mounting_hole_allen_socket_dia + self.clearance_case_mount_holes_shell_thic…` |  | sspg: dependent, cpg: dependent |
| 9 | `Motor_case_thickness` | fixed / config | high | 4914 | `self.design_params["Motor_case_thickness"]` |  | sspg: fixed, cpg: fixed |
| 10 | `air_flow_hole_offset` | fixed / config | high | 4923 | `self.design_params["air_flow_hole_offset"]` |  | sspg: fixed, cpg: fixed |
| 11 | `standard_bearing_insertion_chamfer` | fixed / config | high | 4874 | `self.design_params["standard_bearing_insertion_chamfer"]` |  | sspg: fixed, cpg: fixed |
| 12 | `alpha_p_b` | dependent / formula | high | 5046 | `( self.dp_p_b ** 2 - self.db_p_b ** 2 )**0.5 / self.db_p_b * 180 / np.pi - self.pressure_angle_deg` |  | cpg: dependent |
| 13 | `alpha_p_s` | dependent / formula | high | 5052 | `( self.dp_p_s ** 2 - self.db_p_s ** 2 )**0.5 / self.db_p_s * 180 / np.pi - self.pressure_angle_deg` |  | cpg: dependent |
| 14 | `alpha_r_b` | dependent / formula | high | 5031 | `( self.dp_r_b ** 2 - self.db_r_b ** 2 )**0.5 / self.db_r_b * 180 / np.pi - self.pressure_angle_deg` |  |  |
| 15 | `alpha_r_s` | dependent / formula | high | 5039 | `( self.dp_r_s ** 2 - self.db_r_s ** 2 )**0.5 / self.db_r_s * 180 / np.pi - self.pressure_angle_deg` |  |  |
| 16 | `alpha_s` | dependent / formula | high | 5060 | `( self.dp_s ** 2 - self.db_s ** 2 )**0.5 / self.db_s * 180 / np.pi - self.pressure_angle_deg` |  | sspg: dependent, cpg: dependent |
| 17 | `base_plate_thickness` | fixed / config | high | 4921 | `self.design_params["base_plate_thickness"]` |  | sspg: fixed, cpg: fixed |
| 18 | `bearing_ID` | dependent / lookup (bearing) | high | 5073 | `Bearings.getBearingIDMM()` |  | sspg: dependent, cpg: dependent |
| 19 | `bearing_OD` | dependent / lookup (bearing) | high | 5074 | `Bearings.getBearingODMM()` |  | sspg: dependent, cpg: dependent |
| 20 | `bearing_height` | dependent / lookup (bearing) | high | 5075 | `Bearings.getBearingWidthMM()` |  | sspg: dependent, cpg: dependent |
| 21 | `bearing_mount_thickness` | dependent / formula | medium | 5086 | `(self.output_mounting_hole_dia * 2 if (self.bearing_OD + self.output_mounting_hole_dia * 4) > (self.Nr_s * sel…` | numbers 4 | sspg: dependent, cpg: dependent |
| 22 | `bearing_retainer_thickness` | fixed / config | high | 4988 | `self.design_params["bearing_retainer_thickness"]` |  | sspg: fixed, cpg: fixed |
| 23 | `beta_p_b` | dependent / formula | high | 5047 | `( 360 / ( 4 * self.Np_b ) - self.alpha_p_b ) * 2` |  | cpg: dependent |
| 24 | `beta_p_s` | dependent / formula | high | 5053 | `( 360 / ( 4 * self.Np_s ) - self.alpha_p_s ) * 2` |  | cpg: dependent |
| 25 | `beta_r_b` | dependent / formula | high | 5032 | `( 360 / ( 4 * self.Nr_b ) + self.alpha_r_b ) * 2` |  |  |
| 26 | `beta_r_s` | dependent / formula | high | 5040 | `( 360 / ( 4 * self.Nr_s ) + self.alpha_r_s ) * 2` |  |  |
| 27 | `beta_s` | dependent / formula | high | 5061 | `( 360 / ( 4 * self.Ns ) - self.alpha_s ) * 2` |  | sspg: dependent, cpg: dependent |
| 28 | `carrier_PCD` | dependent / formula | high | 4978, 5094 | `(self.Np_b + self.Ns) * self.module ‖ ( self.Np_b + self.Ns ) * self.module` | 2 assignments (two-case rule or reassigned) | sspg: dependent, cpg: dependent |
| 29 | `carrier_bearing_step_width` | fixed / config | high | 4976 | `self.design_params["carrier_bearing_step_width"]` |  | sspg: fixed, cpg: fixed |
| 30 | `carrier_small_ring_inner_bearing_ID` | fixed / config | high | 4996 | `self.design_params["carrier_small_ring_inner_bearing_ID"]` |  |  |
| 31 | `carrier_small_ring_inner_bearing_OD` | dependent / lookup (bearing) | high | 5001 | `carrier_small_ring_inner_bearing.getBearingODMM()` |  |  |
| 32 | `carrier_small_ring_inner_bearing_flap` | fixed / config | high | 4997 | `self.design_params["carrier_small_ring_inner_bearing_flap"]` |  |  |
| 33 | `carrier_small_ring_inner_bearing_height` | dependent / lookup (bearing) | high | 5002 | `carrier_small_ring_inner_bearing.getBearingWidthMM()` |  |  |
| 34 | `carrier_thickness` | fixed / config | high | 4985 | `self.design_params["carrier_thickness"]` |  |  |
| 35 | `carrier_trapezoidal_support_hole_PCD_offset_bearing_ID` | fixed / config | high | 4974 | `self.design_params["carrier_trapezoidal_support_hole_PCD_offset_bearing_ID"]` |  | sspg: fixed, cpg: fixed |
| 36 | `carrier_trapezoidal_support_hole_dia` | fixed / config | high | 4975 | `self.design_params["carrier_trapezoidal_support_hole_dia"]` |  | sspg: fixed, cpg: fixed |
| 37 | `carrier_trapezoidal_support_hole_socket_head_dia` | dependent / lookup (bolt/nut) | high | 4982 | `carrier_trapezoidal_support_hole.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 38 | `carrier_trapezoidal_support_hole_wrench_size` | dependent / lookup (bolt/nut) | high | 4983 | `carrier_trapezoidal_support_hole.nut_width_across_flats` |  | sspg: dependent, cpg: dependent |
| 39 | `carrier_trapezoidal_support_sun_offset` | fixed / config | high | 4973 | `self.design_params["carrier_trapezoidal_support_sun_offset"]` |  | sspg: fixed, cpg: fixed |
| 40 | `case_dist` | dependent / formula | high | 5078 | `self.sec_carrier_thickness + self.clearance_planet + self.sun_coupler_hub_thickness - self.case_mounting_surfa…` |  | sspg: dependent, cpg: dependent |
| 41 | `case_mounting_PCD` | dependent / formula | high | 5084 | `self.motor_case_OD_base + self.case_mounting_hole_shift * 2` |  | sspg: dependent, cpg: dependent |
| 42 | `case_mounting_bolt_depth` | fixed / config | high | 4912 | `self.design_params["case_mounting_bolt_depth"]` |  | sspg: fixed, cpg: fixed |
| 43 | `case_mounting_hole_allen_socket_dia` | dependent / lookup (bolt/nut) | high | 4927 | `case_mounting_hole_bolt.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 44 | `case_mounting_hole_dia` | fixed / config | high | 4911 | `self.design_params["case_mounting_hole_dia"]` |  | sspg: fixed, cpg: fixed |
| 45 | `case_mounting_hole_shift` | dependent / formula | medium | 5079 | `self.case_mounting_hole_dia / 2 - 0.5` | numbers 0.5 | sspg: dependent, cpg: dependent |
| 46 | `case_mounting_nut_clearance` | fixed / config | high | 4871 | `self.design_params["case_mounting_nut_clearance"]` |  | sspg: fixed, cpg: fixed |
| 47 | `case_mounting_nut_thickness` | dependent / lookup (bolt/nut) | high | 4929 | `case_mounting_hole_bolt.nut_thickness` |  | sspg: dependent, cpg: dependent |
| 48 | `case_mounting_surface_height` | fixed / config | high | 4922 | `self.design_params["case_mounting_surface_height"]` |  | sspg: fixed, cpg: fixed |
| 49 | `case_mounting_wrench_size` | dependent / lookup (bolt/nut) | high | 4928 | `case_mounting_hole_bolt.nut_width_across_flats` |  | sspg: dependent, cpg: dependent |
| 50 | `central_hole_offset_from_motor_mount_PCD` | fixed / config | high | 4903 | `self.design_params["central_hole_offset_from_motor_mount_PCD"]` |  | sspg: fixed, cpg: fixed |
| 51 | `clearance_case_mount_holes_shell_thickness` | fixed / config | high | 4870 | `self.design_params["clearance_case_mount_holes_shell_thickness"]` |  | sspg: fixed, cpg: fixed |
| 52 | `clearance_motor_and_case` | fixed / hard-coded constant | medium | 5080 | `5` | value hard-coded in the code; numbers 5 | sspg: dependent, cpg: dependent |
| 53 | `clearance_planet` | fixed / config | high | 4868 | `self.design_params["clearance_planet"]` |  | sspg: fixed, cpg: fixed |
| 54 | `clearance_sun_coupler_sec_carrier` | fixed / config | high | 4869 | `self.design_params["clearance_sun_coupler_sec_carrier"]` |  | sspg: fixed, cpg: fixed |
| 55 | `clr_tip_root` | dependent / formula | high | 5023 | `self.h_f - self.h_a` |  | sspg: dependent, cpg: dependent |
| 56 | `clr_tip_root_s` | dependent / formula | high | 5024 | `self.h_f - self.h_a` |  |  |
| 57 | `db_p_b` | dependent / formula | high | 5045 | `self.dp_p_b * np.cos ( self.pressure_angle )` |  | cpg: dependent |
| 58 | `db_p_s` | dependent / formula | high | 5051 | `self.dp_p_s * np.cos ( self.pressure_angle )` |  | cpg: dependent |
| 59 | `db_r_b` | dependent / formula | high | 5029 | `self.dp_r_b * np.cos ( self.pressure_angle )` |  |  |
| 60 | `db_r_s` | dependent / formula | high | 5038 | `self.dp_r_s * np.cos ( self.pressure_angle )` |  |  |
| 61 | `db_s` | dependent / formula | high | 5059 | `self.dp_s * np.cos ( self.pressure_angle )` |  | sspg: dependent, cpg: dependent |
| 62 | `dp_p_b` | dependent / formula | high | 5044 | `self.module * self.Np_b` |  | cpg: dependent |
| 63 | `dp_p_s` | dependent / formula | high | 5050 | `self.module * self.Np_s` |  | cpg: dependent |
| 64 | `dp_r_b` | dependent / formula | high | 5028 | `self.module * self.Nr_b` |  |  |
| 65 | `dp_r_s` | dependent / formula | high | 5037 | `self.module * self.Nr_s` |  |  |
| 66 | `dp_s` | dependent / formula | high | 5058 | `self.module * self.Ns` |  | sspg: dependent, cpg: dependent |
| 67 | `driver_lower_holes_dist_from_center` | input / driver | high | 4896 | `self.motor_driver_params["driver_lower_holes_dist_from_center"]` |  | sspg: input, cpg: input |
| 68 | `driver_mount_height` | input / driver | high | 4901 | `self.motor_driver_params["driver_mount_height"]` |  | sspg: input, cpg: input |
| 69 | `driver_mount_holes_dia` | input / driver | high | 4898 | `self.motor_driver_params["driver_mount_holes_dia"]` |  | sspg: input, cpg: input |
| 70 | `driver_mount_inserts_OD` | input / driver | high | 4899 | `self.motor_driver_params["driver_mount_inserts_OD"]` |  | sspg: input, cpg: input |
| 71 | `driver_mount_thickness` | input / driver | high | 4900 | `self.motor_driver_params["driver_mount_thickness"]` |  | sspg: input, cpg: input |
| 72 | `driver_side_holes_dist_from_center` | input / driver | high | 4897 | `self.motor_driver_params["driver_side_holes_dist_from_center"]` |  | sspg: input, cpg: input |
| 73 | `driver_upper_holes_dist_from_center` | input / driver | high | 4895 | `self.motor_driver_params["driver_upper_holes_dist_from_center"]` |  | sspg: input, cpg: input |
| 74 | `fw_p_b` | dependent / stress rule (face width) | high | 4961 | `self.wolfromPlanetaryGearbox.fwPlanetBigMM` |  | cpg: dependent |
| 75 | `fw_p_s` | dependent / formula | high | 5055 | `self.fw_r_s + self.clearance_planet` |  | cpg: dependent |
| 76 | `fw_r_b` | dependent / formula | high | 5030 | `self.fw_p_b` |  |  |
| 77 | `fw_r_s` | dependent / stress rule (face width) | high | 4965 | `self.wolfromPlanetaryGearbox.fwRingSmallMM` |  |  |
| 78 | `fw_s_calc` | dependent / stress rule (face width) | high | 4946 | `self.wolfromPlanetaryGearbox.fwSunMM` |  | sspg: dependent, cpg: dependent |
| 79 | `fw_s_used` | dependent / formula | high | 5068 | `self.fw_p_s + self.fw_p_b + self.clearance_planet + self.sec_carrier_thickness + self.standard_clearance_1_5mm` |  | sspg: dependent, cpg: dependent |
| 80 | `gear_casing_big_ring_to_bearing_dist` | dependent / formula | high | 5091 | `self.fw_p_s + self.clearance_planet + self.carrier_thickness + self.carrier_bearing_step_width + self.carrier_…` |  |  |
| 81 | `gear_casing_thickness` | fixed / config | high | 4968 | `self.design_params["gear_casing_thickness"]` |  |  |
| 82 | `h_a` | dependent / formula | high | 5020 | `1 * self.module` |  | sspg: dependent, cpg: dependent |
| 83 | `h_b` | dependent / formula | high | 5022 | `1.25 * self.module` |  | sspg: dependent, cpg: dependent |
| 84 | `h_f` | dependent / formula | high | 5021 | `1.25 * self.module` |  | sspg: dependent, cpg: dependent |
| 85 | `module` | optimisation / module | high | 4861 | `self.wolfromPlanetaryGearbox.moduleBig` |  | sspg: optimisation, cpg: optimisation |
| 86 | `motor_OD` | input / motor | high | 4883 | `self.motorDiaMM` |  | sspg: input, cpg: input |
| 87 | `motor_case_OD_base` | dependent / formula | high | 5083 | `self.maxGearboxDiameter + 2*self.ring_radial_thickness + self.clearance_motor_and_case * 2 + self.Motor_case_t…` |  | sspg: dependent, cpg: dependent |
| 88 | `motor_height` | input / motor | high | 4884 | `self.motorLengthMM` |  | sspg: input, cpg: input |
| 89 | `motor_mount_hole_PCD` | input / motor | high | 4885 | `self.motor.motor_mount_hole_PCD` |  | sspg: input, cpg: input |
| 90 | `motor_mount_hole_dia` | input / motor | high | 4886 | `self.motor.motor_mount_hole_dia` |  | sspg: input, cpg: input |
| 91 | `motor_mount_hole_num` | input / motor | high | 4887 | `self.motor.motor_mount_hole_num` |  | sspg: input, cpg: input |
| 92 | `motor_output_hole_CSK_OD` | dependent / lookup (bolt/nut) | high | 4906 | `motor_output_hole_bolt.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 93 | `motor_output_hole_CSK_head_height` | dependent / lookup (bolt/nut) | high | 4907 | `motor_output_hole_bolt.bolt_head_height` |  | sspg: dependent, cpg: dependent |
| 94 | `motor_output_hole_PCD` | input / motor | high | 4888 | `self.motor.motor_output_hole_PCD` |  | sspg: input, cpg: input |
| 95 | `motor_output_hole_dia` | input / motor | high | 4889 | `self.motor.motor_output_hole_dia` |  | sspg: input, cpg: input |
| 96 | `motor_output_hole_num` | input / motor | high | 4890 | `self.motor.motor_output_hole_num` |  | sspg: input, cpg: input |
| 97 | `num_planet` | optimisation / planets | high | 4862 | `self.wolfromPlanetaryGearbox.numPlanet` |  | sspg: optimisation, cpg: optimisation |
| 98 | `output_mounting_PCD` | dependent / formula | high | 5087 | `self.bearing_OD + self.bearing_mount_thickness` |  | sspg: dependent, cpg: dependent |
| 99 | `output_mounting_hole_dia` | fixed / config | high | 4913 | `self.design_params["output_mounting_hole_dia"]` |  | sspg: fixed, cpg: fixed |
| 100 | `output_mounting_nut_depth` | fixed / config | high | 4915 | `self.design_params["output_mounting_nut_depth"]` |  | sspg: fixed, cpg: fixed |
| 101 | `output_mounting_nut_thickness` | dependent / lookup (bolt/nut) | high | 4933 | `output_mounting_hole_bolt.nut_thickness` |  | sspg: dependent, cpg: dependent |
| 102 | `output_mounting_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 4934 | `output_mounting_hole_bolt.nut_width_across_flats` |  | sspg: dependent, cpg: dependent |
| 103 | `pattern_bulge_dia` | fixed / config | high | 4918 | `self.design_params["pattern_bulge_dia"]` |  | sspg: fixed, cpg: fixed |
| 104 | `pattern_depth` | fixed / config | high | 4920 | `self.design_params["pattern_depth"]` |  | sspg: fixed, cpg: fixed |
| 105 | `pattern_num_bulge` | fixed / config | high | 4919 | `self.design_params["pattern_num_bulge"]` |  | sspg: fixed, cpg: fixed |
| 106 | `pattern_offset_from_motor_case_OD_base` | fixed / config | high | 4917 | `self.design_params["pattern_offset_from_motor_case_OD_base"]` |  | sspg: fixed, cpg: fixed |
| 107 | `planet_bearing_OD` | fixed / config | high | 4953 | `self.design_params["planet_bearing_OD"]` |  | sspg: fixed, cpg: fixed |
| 108 | `planet_bearing_width` | fixed / config | high | 4954 | `self.design_params["planet_bearing_width"]` |  | sspg: fixed, cpg: fixed |
| 109 | `planet_bore` | fixed / config | high | 4955 | `self.design_params["planet_bore"]` |  | sspg: fixed, cpg: fixed |
| 110 | `planet_pin_bolt_dia` | fixed / config | high | 4950 | `self.design_params["planet_pin_bolt_dia"]` |  | sspg: fixed, cpg: fixed |
| 111 | `planet_pin_bolt_wrench_size` | dependent / lookup (bolt/nut) | high | 4959 | `planet_pin_bolt.nut_width_across_flats` |  | sspg: dependent, cpg: dependent |
| 112 | `planet_pin_socket_head_dia` | dependent / lookup (bolt/nut) | high | 4958 | `planet_pin_bolt.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 113 | `planet_shaft_dia` | fixed / config | high | 4951 | `self.design_params["planet_shaft_dia"]` |  | sspg: fixed, cpg: fixed |
| 114 | `planet_shaft_step_offset` | fixed / config | high | 4952 | `self.design_params["planet_shaft_step_offset"]` |  | sspg: fixed, cpg: fixed |
| 115 | `pressure_angle` | fixed / gear standard | high | 4880 | `self.wolfromPlanetaryGearbox.getPressureAngleRad() * 180 / np.pi` |  | sspg: fixed, cpg: fixed |
| 116 | `ring_OD_b` | dependent / formula | high | 5034 | `self.Nr_b * self.module + self.ring_radial_thickness * 2` |  |  |
| 117 | `ring_radial_thickness` | fixed / config | high | 4964 | `self.design_params["ring_radial_thickness"]` |  | sspg: fixed, cpg: dependent |
| 118 | `ring_to_chamfer_clearance` | dependent / formula | high | 5017 | `self.clearance_planet` |  | sspg: fixed, cpg: fixed |
| 119 | `sec_carrier_thickness` | fixed / config | high | 4971 | `self.design_params["sec_carrier_thickness"]` |  | sspg: fixed, cpg: fixed |
| 120 | `small_ring_case_thickness` | fixed / config | high | 4998 | `self.design_params["small_ring_case_thickness"]` |  |  |
| 121 | `small_ring_output_wall_thickness` | fixed / config | high | 4991 | `self.design_params["small_ring_output_wall_thickness"]` |  |  |
| 122 | `small_ring_output_wall_to_bearing_shaft_attachement_hole_CSK_OD` | dependent / lookup (bolt/nut) | high | 5010 | `small_ring_output_wall_to_bearing_shaft_attachement_bolt.bolt_head_dia` |  |  |
| 123 | `small_ring_output_wall_to_bearing_shaft_attachement_hole_CSK_head_height` | dependent / lookup (bolt/nut) | high | 5011 | `small_ring_output_wall_to_bearing_shaft_attachement_bolt.bolt_head_height` |  |  |
| 124 | `small_ring_output_wall_to_bearing_shaft_attachement_hole_depth` | fixed / config | high | 4993 | `self.design_params["small_ring_output_wall_to_bearing_shaft_attachement_hole_depth"]` |  |  |
| 125 | `small_ring_output_wall_to_bearing_shaft_attachement_hole_dia` | fixed / config | high | 4992 | `self.design_params["small_ring_output_wall_to_bearing_shaft_attachement_hole_dia"]` |  |  |
| 126 | `small_ring_output_wall_to_bearing_shaft_attachement_hole_num` | fixed / config | high | 4995 | `self.design_params["small_ring_output_wall_to_bearing_shaft_attachement_hole_num"]` |  |  |
| 127 | `small_ring_output_wall_to_bearing_shaft_attachement_hole_pcd` | fixed / config | high | 4994 | `self.design_params["small_ring_output_wall_to_bearing_shaft_attachement_hole_pcd"]` |  |  |
| 128 | `small_ring_output_wall_to_bearing_shaft_attachement_nut_thickness` | dependent / lookup (bolt/nut) | high | 5008 | `small_ring_output_wall_to_bearing_shaft_attachement_bolt.nut_thickness` |  |  |
| 129 | `small_ring_output_wall_to_bearing_shaft_attachement_nut_wrench` | dependent / lookup (bolt/nut) | high | 5007 | `small_ring_output_wall_to_bearing_shaft_attachement_bolt.nut_width_across_flats` |  |  |
| 130 | `standard_clearance_1_5mm` | fixed / config | high | 4872 | `self.design_params["standard_clearance_1_5mm"]` |  | sspg: fixed, cpg: fixed |
| 131 | `standard_fillet_1_5mm` | fixed / config | high | 4873 | `self.design_params["standard_fillet_1_5mm"]` |  | sspg: fixed, cpg: fixed |
| 132 | `sun_central_bolt_dia` | fixed / config | high | 4941 | `self.design_params["sun_central_bolt_dia"]` |  | sspg: fixed, cpg: fixed |
| 133 | `sun_central_bolt_socket_head_dia` | dependent / lookup (bolt/nut) | high | 4944 | `sun_central_bolt.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 134 | `sun_coupler_hub_thickness` | fixed / config | high | 4939 | `self.design_params["sun_coupler_hub_thickness"]` |  | sspg: fixed, cpg: fixed |
| 135 | `sun_hub_dia` | dependent / formula | high | 5064, 5066 | `self.motor_output_hole_PCD + self.motor_output_hole_CSK_OD + self.standard_clearance_1_5mm * 2 ‖ self.module *…` | 2 assignments (two-case rule or reassigned) | sspg: dependent, cpg: dependent |
| 136 | `sun_shaft_bearing_ID` | fixed / config | high | 4937 | `self.design_params["sun_shaft_bearing_ID"]` |  | sspg: fixed, cpg: fixed |
| 137 | `sun_shaft_bearing_OD` | fixed / config | high | 4938 | `self.design_params["sun_shaft_bearing_OD"]` |  | sspg: fixed, cpg: fixed |
| 138 | `sun_shaft_bearing_width` | fixed / config | high | 4940 | `self.design_params["sun_shaft_bearing_width"]` |  | sspg: fixed, cpg: fixed |
| 139 | `wire_slot_dist_from_center` | input / motor | high | 4891 | `self.motor.wire_slot_dist_from_center` |  | sspg: input, cpg: input |
| 140 | `wire_slot_length` | input / motor | high | 4892 | `self.motor.wire_slot_length` |  | sspg: input, cpg: input |
| 141 | `wire_slot_radius` | input / motor | high | 4893 | `self.motor.wire_slot_radius` |  | sspg: input, cpg: input |
| 142 | `tight_clearance_3DP` | fixed / config | high | 4875 | `self.design_params["tight_clearance_3DP"]` |  | sspg: fixed, cpg: fixed |
| 143 | `loose_clearance_3DP` | fixed / config | high | 4876 | `self.design_params["loose_clearance_3DP"]` |  | sspg: fixed, cpg: fixed |

## Config accounting

| Block | Keys | Read by this type | Read but not written to the CAD | Never used |
|---|---|---|---|---|
| `wpg_design_parameters` | 24 | **no** | planetMinDistanceMM, ringRadialWidthMMSmall, ringRadialWidthMMBig, sCarrierExtrusionDiaMM, sCarrierExtrusionClearanceMM, gearbox_casing_thickness, small_ring_gear_casing_thickness, bearingIDClearanceMM | mainCoverThicknessMM, baseThicknessMM, planetBoreMM, sunBoreMM, couplerRadiusMM, couplerThicknessMM, couplerShaftHeightMM, clearanceMotorandCaseMM, clearanceCarrierPlanetMM, clearanceSCarrierMotorMM, carrierThicknessMM, CarrierRadialThicknessClearance1, carrierInnerDiaClearanceMM1, sCarrierInnerDiaClearanceMM1, MainCover3AndCarrierClearanceMM, CarrierAndMainCaseClearanceMM |
| `wpg_optimization_parameters` | 15 | yes | GEAR_RATIO_MIN, GEAR_RATIO_MAX, GEAR_RATIO_STEP, MODULE_BIG_MIN, MODULE_BIG_MAX, MODULE_SMALL_MIN, MODULE_SMALL_MAX, NUM_PLANET_MIN, NUM_PLANET_MAX, NUM_TEETH_SUN_MIN, NUM_TEETH_PLANET_BIG_MIN, NUM_TEETH_PLANET_SMALL_MIN, MAX_GB_DIA_MULT_FACTOR, MAX_GB_DIA_MULT_FACTOR_SMALL_MOTOR, SMALL_MOTOR_DIA_MM | — |
| `wpg_3DP_design_parameters` | 59 | yes | planetMinDistanceMM, ringRadialWidthMMSmall, ringRadialWidthMMBig, sCarrierExtrusionDiaMM, sCarrierExtrusionClearanceMM, gearbox_casing_thickness, small_ring_gear_casing_thickness, bearingIDClearanceMM | — |
