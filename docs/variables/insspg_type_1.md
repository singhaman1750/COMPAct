# INSSPG_TYPE_1 variables by category

Generated from `config_files/variables/insspg_type_1_variables.json` by `python tools/variables/render.py`; edit the JSON, not this page.

Every INSSPG type 1 variable sorted into input / optimisation / fixed / dependent. 'cad_variables' are the 107 variables INSSPG type 1 writes to CADs/INSSPG/insspg_type_1_equations_onshape.txt, in that order (types 1 and 2 share one class and differ in fw_s_used and the mass code); 'code_only' are values the code uses but does not write to the CAD file, plus every config key the CAD does not use (the config has two blocks, both merged into the design parameters); 'unused_config_blocks' are config blocks INSSPG never reads. tests/test_variable_categories.py checks the lists against the code and re-evaluates every formula and lookup; docs/variables/insspg_type_1.md is generated from this file (python tools/variables/render.py).

## Categories

- **Input**: chosen parts and material: the motor's dimensions and torque, the motor driver's mount dimensions, the gear material's allowable stress
- **Optimisation**: searched by the optimiser: teeth, module, number of planets
- **Fixed**: constants that don't depend on the design: clearances, wall thicknesses, fastener and bearing choices, feature sizes, the gear standard
- **Dependent**: computed from the variables above, by a formula, a catalogue lookup (bearings, bolts, nuts) or a rule the code applies (the tooth-stress rule for face widths)

Confidence:

- **high**: the code reads it directly from one source, or computes it with an explicit formula
- **medium**: the code is clear, but the category is a judgement call (see the reason)
- **low**: can't be decided from the code alone

## Count

| Category | CAD variables | Code-only |
|---|---|---|
| Input | 12 | 4 |
| Optimisation | 4 | 0 |
| Fixed | 56 | 54 |
| Dependent | 35 | 2 |
| **Total** | **107** | **60** |

CAD variables by confidence: high 99, medium 8, low 0

## To review (not high confidence)

- `rotor_support_bearing_ID` (Dependent, medium): catalogue bearing whose outer diameter is at least Rotor_ID - 4 (first one in the table; bearings_discrete returns the first bearing with OD >= the request, which can exceed it, ISSUES bug 5); the 4 is hard-coded; this is its bore
- `rotor_support_bearing_OD` (Dependent, medium): catalogue bearing whose outer diameter is at least Rotor_ID - 4 (first one in the table; bearings_discrete returns the first bearing with OD >= the request, which can exceed it, ISSUES bug 5); the 4 is hard-coded; this is its outer diameter
- `rotor_support_bearing_height` (Dependent, medium): catalogue bearing whose outer diameter is at least Rotor_ID - 4 (first one in the table; bearings_discrete returns the first bearing with OD >= the request, which can exceed it, ISSUES bug 5); the 4 is hard-coded; this is its width
- `rotor_upper_support_bearing_ID` (Dependent, medium): catalogue bearing whose outer diameter is at least Stator_ID - 5 x standard_clearance_1_5mm (first one in the table, ISSUES bug 5); the 5 is hard-coded; this is its bore
- `rotor_upper_support_bearing_OD` (Dependent, medium): catalogue bearing whose outer diameter is at least Stator_ID - 5 x standard_clearance_1_5mm (first one in the table, ISSUES bug 5); the 5 is hard-coded; this is its outer diameter
- `rotor_upper_support_bearing_height` (Dependent, medium): catalogue bearing whose outer diameter is at least Stator_ID - 5 x standard_clearance_1_5mm (first one in the table, ISSUES bug 5); the 5 is hard-coded; this is its width
- `fw_s_used` (Dependent, medium): printed sun length, type 1: the sun length from the rotor support bearing, the carrier and clearances, with a hard-coded 1.5 x standard_clearance_1_5mm; type 2 uses a different rule
- `sun_support_OD` (Dependent, medium): sun support outer diameter: the space inside the planet shafts, capped at a hard-coded 21 mm (the 21 and the x 3 clearance are not in the config)
- `maxGearboxDiameter` (Dependent, medium): largest gearbox diameter the optimiser may use (gearbox_runner max_diameter): the stator's outer diameter less a hard-coded 5.5 mm and two clearances

## Rules shared by every gearbox

From `config_files/variables/rules.json`; the test holds every gearbox's file to them.

- names matching `^(a[12]_)?Nr(_[bs]|[0-9]*)$` are **Dependent / implicit constraint**: ring-gear teeth are implicitly constrained: the coaxial geometric constraint (e.g. Nr = Ns + 2 x Np) fixes them once the sun and planet teeth are chosen, so the optimiser sets them instead of searching them
- names matching `^fw_(s_calc|p|p_b|r|r_s)$` are **Dependent / stress rule**: gear face widths follow from the tooth-stress rule: the optimisation variables, the motor torque, the gear material and the safety factors fix them, and the optimiser always takes the smallest width that passes (widths that are a formula of another width, e.g. CPG's fw_p_s = fw_r + clearance_planet, are dependent / formula)
- names matching `^a[12]_fw_(s_calc|r)[12]?$` are **Dependent / stress rule**: the same stress-rule face widths in a two-stage gearbox, under the stage prefixes a1_ / a2_ (the planet width a1_fw_p / a2_fw_p is a copy of the ring width, so it is dependent / formula and not in this rule)

## Input (12)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `motor_OD` | motor | motors.json → motors.<motor>.geometry → `stator_OD` |  | high | read from the chosen motor's geometry (the stator's outer diameter) |
| 2 | `Stator_ID` | motor | motors.json → motors.<motor>.geometry → `stator_ID` |  | high | read from the chosen motor's geometry |
| 3 | `Stator_OD` | motor | motors.json → motors.<motor>.geometry → `stator_OD` |  | high | read from the chosen motor's geometry |
| 4 | `stator_height` | motor | motors.json → motors.<motor>.geometry → `stator_height` |  | high | read from the chosen motor's geometry |
| 5 | `stator_bottom_step_height_` | motor | motors.json → motors.<motor>.geometry → `stator_wire_bottom_height` |  | high | read from the chosen motor's geometry |
| 6 | `stator_upper_step_height` | motor | motors.json → motors.<motor>.geometry → `stator_wire_top_height` |  | high | read from the chosen motor's geometry |
| 7 | `stator_side_step_OD` | motor | motors.json → motors.<motor>.geometry → `stator_wire_OD` |  | high | read from the chosen motor's geometry |
| 8 | `stator_side_step_ID` | motor | motors.json → motors.<motor>.geometry → `stator_wire_ID` |  | high | read from the chosen motor's geometry |
| 9 | `stator_mounting_holes_dia` | motor | motors.json → motors.<motor>.geometry → `stator_hole_dia` |  | high | read from the chosen motor's geometry |
| 10 | `Rotor_height` | motor | motors.json → motors.<motor>.geometry → `rotor_height` |  | high | read from the chosen motor's geometry |
| 11 | `Rotor_OD` | motor | motors.json → motors.<motor>.geometry → `rotor_OD` |  | high | read from the chosen motor's geometry |
| 12 | `Rotor_ID` | motor | motors.json → motors.<motor>.geometry → `rotor_ID` |  | high | read from the chosen motor's geometry |

## Optimisation (4)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `Ns` | teeth | optimiser (`optimizationSingleStageActuator`) |  | high | sun teeth: searched by the optimiser loop |
| 2 | `Np` | teeth | optimiser (`optimizationSingleStageActuator`) |  | high | planet teeth: searched by the optimiser loop |
| 3 | `module` | module | optimiser (`optimizationSingleStageActuator`) |  | high | module: searched by the optimiser loop |
| 4 | `num_planet` | planets | optimiser (`optimizationSingleStageActuator`) |  | high | number of planets: searched by the optimiser loop |

## Fixed (56)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `pressure_angle` | gear standard | insspg_motor_config.json → Gear_standard_parameters → `pressureAngleDEG` |  | high | gear standard, the same for every gearbox type |
| 2 | `planet_bore` | planet part | insspg_params.json → sspg_3DP_design_parameters → `planet_bore` |  | high | constant from the INSSPG design parameters |
| 3 | `clearance_planet` | clearance | insspg_params.json → sspg_3DP_design_parameters → `clearance_planet` |  | high | constant from the INSSPG design parameters |
| 4 | `sec_carrier_thickness` | wall thickness | insspg_params.json → sspg_3DP_design_parameters → `sec_carrier_thickness` |  | high | constant from the INSSPG design parameters |
| 5 | `sun_coupler_hub_thickness` | wall thickness | insspg_params.json → sspg_3DP_design_parameters → `sun_coupler_hub_thickness` |  | high | constant from the INSSPG design parameters |
| 6 | `clearance_sun_coupler_sec_carrier` | clearance | insspg_params.json → sspg_3DP_design_parameters → `clearance_sun_coupler_sec_carrier` |  | high | constant from the INSSPG design parameters |
| 7 | `case_mounting_hole_dia` | fastener size | insspg_params.json → sspg_3DP_design_parameters → `case_mounting_hole_dia` |  | high | constant from the INSSPG design parameters |
| 8 | `case_mounting_wrench_thickness` | fastener size | insspg_params.json → sspg_3DP_design_parameters → `case_mounting_wrench_thickness` |  | high | constant from the INSSPG design parameters |
| 9 | `case_mounting_hole_allen_socket_dia` | feature size | insspg_params.json → sspg_3DP_design_parameters → `case_mounting_hole_allen_socket_dia` |  | high | constant from the INSSPG design parameters |
| 10 | `bearing_mount_thickness` | wall thickness | insspg_params.json → sspg_3DP_design_parameters → `bearing_mount_thickness` |  | high | output-bearing wall: a config value here (SSPG and CPG compute it from the ring and bolt size); the code reads it with .get, so a missing key would give None |
| 11 | `Rotor_output_hole_num` | fastener size | insspg_params.json → sspg_3DP_design_parameters → `Rotor_output_hole_num` |  | high | constant from the INSSPG design parameters |
| 12 | `output_mounting_nut_thickness` | wall thickness | insspg_params.json → sspg_3DP_design_parameters → `output_mounting_nut_thickness` |  | high | constant from the INSSPG design parameters |
| 13 | `output_mounting_nut_wrench_size` | fastener size | insspg_params.json → sspg_3DP_design_parameters → `output_mounting_nut_wrench_size` |  | high | constant from the INSSPG design parameters |
| 14 | `output_mounting_hole_dia` | fastener size | insspg_params.json → sspg_3DP_design_parameters → `output_mounting_hole_dia` |  | high | constant from the INSSPG design parameters |
| 15 | `case_mounting_bolt_depth` | fastener size | insspg_params.json → sspg_3DP_design_parameters → `case_mounting_bolt_depth` |  | high | constant from the INSSPG design parameters |
| 16 | `case_mounting_wrench_size` | fastener size | insspg_params.json → sspg_3DP_design_parameters → `case_mounting_wrench_size` |  | high | constant from the INSSPG design parameters |
| 17 | `planet_pin_bolt_dia` | fastener size | insspg_params.json → sspg_3DP_design_parameters → `planet_pin_bolt_dia` |  | high | constant from the INSSPG design parameters |
| 18 | `planet_pin_socket_head_dia` | fastener size | insspg_params.json → sspg_3DP_design_parameters → `planet_pin_socket_head_dia` |  | high | constant from the INSSPG design parameters |
| 19 | `planet_shaft_dia` | planet part | insspg_params.json → sspg_3DP_design_parameters → `planet_shaft_dia` |  | high | constant from the INSSPG design parameters |
| 20 | `planet_pin_bolt_wrench_size` | fastener size | insspg_params.json → sspg_3DP_design_parameters → `planet_pin_bolt_wrench_size` |  | high | constant from the INSSPG design parameters |
| 21 | `planet_shaft_step_offset` | planet part | insspg_params.json → sspg_3DP_design_parameters → `planet_shaft_step_offset` |  | high | constant from the INSSPG design parameters |
| 22 | `planet_bearing_OD` | bearing (chosen part) | insspg_params.json → sspg_3DP_design_parameters → `planet_bearing_OD` |  | high | constant from the INSSPG design parameters |
| 23 | `planet_bearing_width` | bearing (chosen part) | insspg_params.json → sspg_3DP_design_parameters → `planet_bearing_width` |  | high | constant from the INSSPG design parameters |
| 24 | `carrier_trapezoidal_support_sun_offset` | feature size | insspg_params.json → sspg_3DP_design_parameters → `carrier_trapezoidal_support_sun_offset` |  | high | constant from the INSSPG design parameters |
| 25 | `carrier_trapezoidal_support_hole_PCD_offset_bearing_ID` | feature size | insspg_params.json → sspg_3DP_design_parameters → `carrier_trapezoidal_support_hole_PCD_offset_bearing_ID` |  | high | constant from the INSSPG design parameters |
| 26 | `carrier_trapezoidal_support_hole_dia` | fastener size | insspg_params.json → sspg_3DP_design_parameters → `carrier_trapezoidal_support_hole_dia` |  | high | constant from the INSSPG design parameters |
| 27 | `carrier_trapezoidal_support_hole_socket_head_dia` | fastener size | insspg_params.json → sspg_3DP_design_parameters → `carrier_trapezoidal_support_hole_socket_head_dia` |  | high | constant from the INSSPG design parameters |
| 28 | `carrier_trapezoidal_support_hole_wrench_size` | fastener size | insspg_params.json → sspg_3DP_design_parameters → `carrier_trapezoidal_support_hole_wrench_size` |  | high | constant from the INSSPG design parameters |
| 29 | `carrier_bearing_step_width` | feature size | insspg_params.json → sspg_3DP_design_parameters → `carrier_bearing_step_width` |  | high | constant from the INSSPG design parameters |
| 30 | `standard_clearance_1_5mm` | clearance | insspg_params.json → sspg_3DP_design_parameters → `standard_clearance_1_5mm` |  | high | constant from the INSSPG design parameters |
| 31 | `standard_fillet_1_5mm` | feature size | insspg_params.json → sspg_3DP_design_parameters → `standard_fillet_1_5mm` |  | high | constant from the INSSPG design parameters |
| 32 | `sun_shaft_bearing_OD` | bearing (chosen part) | insspg_params.json → sspg_3DP_design_parameters → `sun_shaft_bearing_OD` |  | high | constant from the INSSPG design parameters |
| 33 | `sun_shaft_bearing_width` | bearing (chosen part) | insspg_params.json → sspg_3DP_design_parameters → `sun_shaft_bearing_width` |  | high | constant from the INSSPG design parameters |
| 34 | `sun_shaft_bearing_ID` | bearing (chosen part) | insspg_params.json → sspg_3DP_design_parameters → `sun_shaft_bearing_ID` |  | high | constant from the INSSPG design parameters |
| 35 | `standard_bearing_insertion_chamfer` | feature size | insspg_params.json → sspg_3DP_design_parameters → `standard_bearing_insertion_chamfer` |  | high | constant from the INSSPG design parameters |
| 36 | `sun_central_bolt_dia` | fastener size | insspg_params.json → sspg_3DP_design_parameters → `sun_central_bolt_dia` |  | high | constant from the INSSPG design parameters |
| 37 | `sun_central_bolt_socket_head_dia` | fastener size | insspg_params.json → sspg_3DP_design_parameters → `sun_central_bolt_socket_head_dia` |  | high | constant from the INSSPG design parameters |
| 38 | `bearing_retainer_thickness` | wall thickness | insspg_params.json → sspg_3DP_design_parameters → `bearing_retainer_thickness` |  | high | constant from the INSSPG design parameters |
| 39 | `tight_clearance_3DP` | clearance | insspg_params.json → sspg_3DP_design_parameters → `tight_clearance_3DP` |  | high | constant from the INSSPG design parameters |
| 40 | `loose_clearance_3DP` | clearance | insspg_params.json → sspg_3DP_design_parameters → `loose_clearance_3DP` |  | high | constant from the INSSPG design parameters |
| 41 | `stator_casing_thickness` | wall thickness | insspg_params.json → sspg_3DP_design_parameters → `stator_casing_thickness` |  | high | constant from the INSSPG design parameters |
| 42 | `stator_hole_bolt_socket_head_dia` | fastener size | insspg_params.json → sspg_3DP_design_parameters → `stator_hole_bolt_socket_head_dia` |  | high | constant from the INSSPG design parameters |
| 43 | `rotor_mount_hole_dia` | fastener size | insspg_params.json → sspg_3DP_design_parameters → `rotor_mount_hole_dia` |  | high | constant from the INSSPG design parameters |
| 44 | `rotor_mount_hole_CSK_OD` | fastener size | insspg_params.json → sspg_3DP_design_parameters → `rotor_mount_hole_CSK_OD` |  | high | constant from the INSSPG design parameters |
| 45 | `rotor_mount_hole_CSK_head_hight` | fastener size | insspg_params.json → sspg_3DP_design_parameters → `rotor_mount_hole_CSK_head_hight` |  | high | constant from the INSSPG design parameters |
| 46 | `Rotor_tight_clearance` | clearance | insspg_params.json → sspg_3DP_design_parameters → `Rotor_tight_clearance` |  | high | constant from the INSSPG design parameters |
| 47 | `stator_bearing_support_casing_thickness` | wall thickness | insspg_params.json → sspg_3DP_design_parameters → `stator_bearing_support_casing_thickness` |  | high | constant from the INSSPG design parameters |
| 48 | `ringRadialWidthMM` | constraint constant | insspg_params.json → sspg_design_parameters → `ringRadialWidthMM` |  | high | ring wall: read from the config (the gearbox's own value is only the fallback); also used by the gearbox class and the mass code |
| 49 | `stator_casing_hole_dia` | fastener size | insspg_params.json → sspg_3DP_design_parameters → `stator_casing_hole_dia` |  | high | constant from the INSSPG design parameters |
| 50 | `stator_casing_hole_socket_head_dia` | fastener size | insspg_params.json → sspg_3DP_design_parameters → `stator_casing_hole_socket_head_dia` |  | high | constant from the INSSPG design parameters |
| 51 | `sun_bottom_casing_bearing_OD` | bearing (chosen part) | insspg_params.json → sspg_3DP_design_parameters → `sun_bottom_casing_bearing_OD` |  | high | constant from the INSSPG design parameters |
| 52 | `sun_bottom_casing_bearing_ID` | bearing (chosen part) | insspg_params.json → sspg_3DP_design_parameters → `sun_bottom_casing_bearing_ID` |  | high | constant from the INSSPG design parameters |
| 53 | `sun_bottom_casing_bearing_height` | bearing (chosen part) | insspg_params.json → sspg_3DP_design_parameters → `sun_bottom_casing_bearing_height` |  | high | constant from the INSSPG design parameters |
| 54 | `sun_sec_carrier_bearing_ID` | bearing (chosen part) | insspg_params.json → sspg_3DP_design_parameters → `sun_sec_carrier_bearing_ID` |  | high | constant from the INSSPG design parameters |
| 55 | `sun_sec_carrier_bearing_OD` | bearing (chosen part) | insspg_params.json → sspg_3DP_design_parameters → `sun_sec_carrier_bearing_OD` |  | high | constant from the INSSPG design parameters |
| 56 | `sun_sec_carrier_bearing_height` | bearing (chosen part) | insspg_params.json → sspg_3DP_design_parameters → `sun_sec_carrier_bearing_height` |  | high | constant from the INSSPG design parameters |

## Dependent (35)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `Nr` | implicit constraint | `Ns + 2 * Np` | Ns, Np | high | implicitly constrained: the geometric (coaxial) constraint Ns + 2 x Np = Nr fixes it, and the optimiser sets it from Ns and Np instead of searching it (the code lists it among the optimisation variables) |
| 2 | `h_a` | formula | `1 * module` | module | high | addendum, standard proportion of the module |
| 3 | `h_b` | formula | `1.25 * module` | module | high | standard proportion of the module (same value as h_f) |
| 4 | `clr_tip_root` | formula | `h_f - h_a` | h_f, h_a | high | tip-root clearance from addendum and dedendum |
| 5 | `h_f` | formula | `1.25 * module` | module | high | dedendum, standard proportion of the module |
| 6 | `motor_height` | formula | `stator_upper_step_height + stator_mid_height + stator_bottom_step_height_` | stator_bottom_step_height_, stator_upper_step_height, stator_mid_height | high | motor length of a frameless inrunner: the stator's top wire height, middle height and bottom wire height (motorLengthMM) |
| 7 | `bearing_ID` | lookup | `bearings_discrete(idRequiredMM=module * (Ns + Np) + planet_pin_socket_head_dia + loose_clearance_3DP * 2)` → getBearingIDMM | planet_pin_socket_head_dia, loose_clearance_3DP, module, Ns, Np | high | smallest catalogue bearing whose bore fits around the sun and planets plus the planet-pin head and clearances; this is its bore |
| 8 | `bearing_OD` | lookup | `bearings_discrete(idRequiredMM=module * (Ns + Np) + planet_pin_socket_head_dia + loose_clearance_3DP * 2)` → getBearingODMM | planet_pin_socket_head_dia, loose_clearance_3DP, module, Ns, Np | high | smallest catalogue bearing whose bore fits around the sun and planets plus the planet-pin head and clearances; this is its outer diameter |
| 9 | `bearing_height` | lookup | `bearings_discrete(idRequiredMM=module * (Ns + Np) + planet_pin_socket_head_dia + loose_clearance_3DP * 2)` → getBearingWidthMM | planet_pin_socket_head_dia, loose_clearance_3DP, module, Ns, Np | high | smallest catalogue bearing whose bore fits around the sun and planets plus the planet-pin head and clearances; this is its width |
| 10 | `dp_s` | formula | `module * Ns` | module, Ns | high | pitch diameter |
| 11 | `db_s` | formula | `dp_s * cos(pressure_angle_rad)` | dp_s, pressure_angle_rad | high | base-circle diameter |
| 12 | `fw_s_calc` | stress rule | b = FOS x Ft x qe x qk / (gear_allowable_stress x module) (mitStressAnalysisMinFacewidth), with Ft = serviceFactor x motor_peak_torque / (num_planet x sun pitch radius), qe = 1 / sun-planet contact ratio, qk = curve fit in Ns; fw_s_calc = b | module, Ns, Np, Nr, num_planet, pressure_angle_rad, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor | high | sun face width from the tooth-stress rule: fixed by the optimisation variables, the motor torque, the gear material and the safety factors, so the optimiser has no freedom over it |
| 13 | `alpha_s` | formula | `sqrt(dp_s ** 2 - db_s ** 2) / db_s * 180 / pi - pressure_angle` | pressure_angle, db_s, dp_s | high | involute angle used to draw the tooth |
| 14 | `beta_s` | formula | `(360 / (4 * Ns) - alpha_s) * 2` | alpha_s, Ns | high | tooth angle used to draw the tooth |
| 15 | `dp_p` | formula | `module * Np` | module, Np | high | pitch diameter |
| 16 | `db_p` | formula | `dp_p * cos(pressure_angle_rad)` | dp_p, pressure_angle_rad | high | base-circle diameter |
| 17 | `fw_p` | stress rule | b = FOS x Ft x qe x qk / (gear_allowable_stress x module) (mitStressAnalysisMinFacewidth), with Ft = serviceFactor x motor_peak_torque / (num_planet x sun pitch radius), qe = 1 / sun-planet contact ratio, qk = curve fit in Ns; if b < 2 x planet_bearing_width + planet_bearing_gap, b is raised to that value; fw_p = b | module, Ns, Np, Nr, num_planet, pressure_angle_rad, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor, planet_bearing_width, planet_bearing_gap | high | planet face width from the tooth-stress rule, raised to hold its two bearings; the ring width is the same value |
| 18 | `alpha_p` | formula | `sqrt(dp_p ** 2 - db_p ** 2) / db_p * 180 / pi - pressure_angle` | pressure_angle, db_p, dp_p | high | involute angle used to draw the tooth |
| 19 | `beta_p` | formula | `(360 / (4 * Np) - alpha_p) * 2` | alpha_p, Np | high | tooth angle used to draw the tooth |
| 20 | `dp_r` | formula | `module * Nr` | module, Nr | high | pitch diameter |
| 21 | `db_r` | formula | `dp_r * cos(pressure_angle_rad)` | dp_r, pressure_angle_rad | high | base-circle diameter |
| 22 | `fw_r` | stress rule | b = FOS x Ft x qe x qk / (gear_allowable_stress x module) (mitStressAnalysisMinFacewidth), with Ft = serviceFactor x motor_peak_torque / (num_planet x sun pitch radius), qe = 1 / sun-planet contact ratio, qk = curve fit in Ns; if b < 2 x planet_bearing_width + planet_bearing_gap, b is raised to that value; fw_r = b | module, Ns, Np, Nr, num_planet, pressure_angle_rad, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor, planet_bearing_width, planet_bearing_gap | high | ring face width from the tooth-stress rule, raised to the planet-bearing minimum (the same value as the planet) |
| 23 | `alpha_r` | formula | `sqrt(dp_r ** 2 - db_r ** 2) / db_r * 180 / pi - pressure_angle` | pressure_angle, db_r, dp_r | high | involute angle used to draw the tooth |
| 24 | `beta_r` | formula | `(360 / (4 * Nr) + alpha_r) * 2` | alpha_r, Nr | high | tooth angle used to draw the tooth |
| 25 | `carrier_PCD` | formula | `module * (Ns + Np)` | module, Ns, Np | high | planet-centre circle (twice the centre distance) |
| 26 | `rotor_output_hole_PCD` | formula | `sun_hub_dia - rotor_mount_hole_CSK_OD` | sun_hub_dia, rotor_mount_hole_CSK_OD | high | rotor output-hole circle: the sun hub less the rotor mount hole's countersink diameter (the config's rotor_output_hole_PCD is not read) |
| 27 | `sun_hub_dia` | formula | `rotor_upper_support_bearing_ID - standard_clearance_1_5mm * 2` | rotor_upper_support_bearing_ID, standard_clearance_1_5mm | high | sun hub: the upper rotor support bearing's bore less 2 x standard_clearance_1_5mm (the config's sun_hub_dia is not read) |
| 28 | `rotor_support_bearing_ID` | lookup | `bearings_discrete(idRequiredMM=0, odRequiredMM=Rotor_ID - 4)` → getBearingIDMM | Rotor_ID | medium | catalogue bearing whose outer diameter is at least Rotor_ID - 4 (first one in the table; bearings_discrete returns the first bearing with OD >= the request, which can exceed it, ISSUES bug 5); the 4 is hard-coded; this is its bore |
| 29 | `rotor_support_bearing_OD` | lookup | `bearings_discrete(idRequiredMM=0, odRequiredMM=Rotor_ID - 4)` → getBearingODMM | Rotor_ID | medium | catalogue bearing whose outer diameter is at least Rotor_ID - 4 (first one in the table; bearings_discrete returns the first bearing with OD >= the request, which can exceed it, ISSUES bug 5); the 4 is hard-coded; this is its outer diameter |
| 30 | `rotor_support_bearing_height` | lookup | `bearings_discrete(idRequiredMM=0, odRequiredMM=Rotor_ID - 4)` → getBearingWidthMM | Rotor_ID | medium | catalogue bearing whose outer diameter is at least Rotor_ID - 4 (first one in the table; bearings_discrete returns the first bearing with OD >= the request, which can exceed it, ISSUES bug 5); the 4 is hard-coded; this is its width |
| 31 | `rotor_upper_support_bearing_ID` | lookup | `bearings_discrete(idRequiredMM=0, odRequiredMM=Stator_ID - standard_clearance_1_5mm * 5)` → getBearingIDMM | Stator_ID, standard_clearance_1_5mm | medium | catalogue bearing whose outer diameter is at least Stator_ID - 5 x standard_clearance_1_5mm (first one in the table, ISSUES bug 5); the 5 is hard-coded; this is its bore |
| 32 | `rotor_upper_support_bearing_OD` | lookup | `bearings_discrete(idRequiredMM=0, odRequiredMM=Stator_ID - standard_clearance_1_5mm * 5)` → getBearingODMM | Stator_ID, standard_clearance_1_5mm | medium | catalogue bearing whose outer diameter is at least Stator_ID - 5 x standard_clearance_1_5mm (first one in the table, ISSUES bug 5); the 5 is hard-coded; this is its outer diameter |
| 33 | `rotor_upper_support_bearing_height` | lookup | `bearings_discrete(idRequiredMM=0, odRequiredMM=Stator_ID - standard_clearance_1_5mm * 5)` → getBearingWidthMM | Stator_ID, standard_clearance_1_5mm | medium | catalogue bearing whose outer diameter is at least Stator_ID - 5 x standard_clearance_1_5mm (first one in the table, ISSUES bug 5); the 5 is hard-coded; this is its width |
| 34 | `fw_s_used` | formula | `-sun_coupler_hub_thickness + standard_clearance_1_5mm + standard_clearance_1_5mm * 1.5 + rotor_support_bearing_height + standard_clearance_1_5mm + sec_carrier_thickness + clearance_planet + fw_p` | fw_p, clearance_planet, sec_carrier_thickness, standard_clearance_1_5mm, rotor_support_bearing_height, sun_coupler_hub_thickness | medium | printed sun length, type 1: the sun length from the rotor support bearing, the carrier and clearances, with a hard-coded 1.5 x standard_clearance_1_5mm; type 2 uses a different rule |
| 35 | `sun_support_OD` | formula | `21 if 21 < carrier_PCD - (planet_shaft_dia + planet_shaft_step_offset * 2) - standard_clearance_1_5mm * 3 else carrier_PCD - (planet_shaft_dia + planet_shaft_step_offset * 2) - standard_clearance_1_5mm * 3` | carrier_PCD, standard_clearance_1_5mm, planet_shaft_dia, planet_shaft_step_offset | medium | sun support outer diameter: the space inside the planet shafts, capped at a hard-coded 21 mm (the 21 and the x 3 clearance are not in the config) |

## Used by the code, not written to the CAD file (60)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `pressure_angle_rad` | formula | `pressure_angle * pi / 180` | pressure_angle | high | pressure angle in radians (code attribute pressure_angle) |
| 2 | `motor_peak_torque` | motor | motors.json → motors.<motor>.electrical → `peak_torque_Nm` |  | high | motor torque the gears are sized for (peak torque under the default rating setting); sets the face widths |
| 3 | `gear_allowable_stress` | material | config.json → Material_properties.<gear material> → `maxAllowableStressMPa` |  | high | allowable tooth stress of the gear material, chosen with the material mode (3dp: PLA, metal: steel); sets the face widths |
| 4 | `FOS` | safety factor | insspg_motor_config.json → MIT_params → `FOS` |  | high | factor of safety in the tooth-stress rule |
| 5 | `serviceFactor` | safety factor | insspg_motor_config.json → MIT_params → `serviceFactor` |  | high | service factor on the motor torque in the tooth-stress rule |
| 6 | `planet_bearing_gap` | clearance | insspg_params.json → sspg_3DP_design_parameters → `planet_bearing_gap` |  | high | axial gap between the two planet bearings (one in each planet gear); with the bearing width it sets the smallest planet and ring widths |
| 7 | `stator_mid_height` | motor | motors.json → motors.<motor>.geometry → `stator_mid_height` |  | high | read from the chosen motor's geometry; with the two wire heights it gives motor_height |
| 8 | `stator_hole_num` | motor | motors.json → motors.<motor>.geometry → `stator_hole_num` |  | high | read from the chosen motor's geometry; not written to the CAD file |
| 9 | `maxGearboxDiameter` | formula | `Stator_OD - 5.5 - standard_clearance_1_5mm * 2 - loose_clearance_3DP / 2` | Stator_OD, standard_clearance_1_5mm, loose_clearance_3DP | medium | largest gearbox diameter the optimiser may use (gearbox_runner max_diameter): the stator's outer diameter less a hard-coded 5.5 mm and two clearances |
| 10 | `planetMinDistanceMM` | constraint constant | insspg_params.json → sspg_design_parameters → `planetMinDistanceMM` |  | high | minimum gap between neighbouring planets; read by the gearbox class, not used in the checks INSSPG runs |
| 11 | `sCarrierExtrusionDiaMM` | constraint constant | insspg_params.json → sspg_design_parameters → `sCarrierExtrusionDiaMM` |  | high | carrier extrusion diameter, read by the gearbox class for its planet-interference check |
| 12 | `sCarrierExtrusionClearanceMM` | constraint constant | insspg_params.json → sspg_design_parameters → `sCarrierExtrusionClearanceMM` |  | high | carrier extrusion clearance, read by the gearbox class for its planet-interference check |
| 13 | `carrier1ShaftHeightMM` | planet part | insspg_params.json → sspg_design_parameters → `carrier1ShaftHeightMM` |  | high | in the older design block; merged into design_params but never read by INSSPG |
| 14 | `mainCase2AttachmentHeightMM` | feature size | insspg_params.json → sspg_design_parameters → `mainCase2AttachmentHeightMM` |  | high | in the older design block; merged into design_params but never read by INSSPG |
| 15 | `baseThicknessMM` | wall thickness | insspg_params.json → sspg_design_parameters → `baseThicknessMM` |  | high | in the older design block; merged into design_params but never read by INSSPG |
| 16 | `sCarrierThicknessMM` | wall thickness | insspg_params.json → sspg_design_parameters → `sCarrierThicknessMM` |  | high | in the older design block; merged into design_params but never read by INSSPG |
| 17 | `mainCoverThicknessMM` | wall thickness | insspg_params.json → sspg_design_parameters → `mainCoverThicknessMM` |  | high | in the older design block; merged into design_params but never read by INSSPG |
| 18 | `planetBoreMM` | planet part | insspg_params.json → sspg_design_parameters → `planetBoreMM` |  | high | in the older design block; merged into design_params but never read by INSSPG |
| 19 | `sunBoreMM` | feature size | insspg_params.json → sspg_design_parameters → `sunBoreMM` |  | high | in the older design block; merged into design_params but never read by INSSPG |
| 20 | `couplerRadiusMM` | feature size | insspg_params.json → sspg_design_parameters → `couplerRadiusMM` |  | high | in the older design block; merged into design_params but never read by INSSPG |
| 21 | `couplerThicknessMM` | wall thickness | insspg_params.json → sspg_design_parameters → `couplerThicknessMM` |  | high | in the older design block; merged into design_params but never read by INSSPG |
| 22 | `couplerShaftHeightMM` | planet part | insspg_params.json → sspg_design_parameters → `couplerShaftHeightMM` |  | high | in the older design block; merged into design_params but never read by INSSPG |
| 23 | `clearanceMotorandCaseMM` | clearance | insspg_params.json → sspg_design_parameters → `clearanceMotorandCaseMM` |  | high | in the older design block; merged into design_params but never read by INSSPG |
| 24 | `clearanceRingandCaseMM` | clearance | insspg_params.json → sspg_design_parameters → `clearanceRingandCaseMM` |  | high | in the older design block; merged into design_params but never read by INSSPG |
| 25 | `clearance1RingandCaseMM` | clearance | insspg_params.json → sspg_design_parameters → `clearance1RingandCaseMM` |  | high | in the older design block; merged into design_params but never read by INSSPG |
| 26 | `clearanceCarrierPlanetMM` | clearance | insspg_params.json → sspg_design_parameters → `clearanceCarrierPlanetMM` |  | high | in the older design block; merged into design_params but never read by INSSPG |
| 27 | `upperHousingHeight` | feature size | insspg_params.json → sspg_design_parameters → `upperHousingHeight` |  | high | in the older design block; merged into design_params but never read by INSSPG |
| 28 | `clearanceSCarrierMotorMM` | clearance | insspg_params.json → sspg_design_parameters → `clearanceSCarrierMotorMM` |  | high | in the older design block; merged into design_params but never read by INSSPG |
| 29 | `carrierIDClearanceMM` | clearance | insspg_params.json → sspg_design_parameters → `carrierIDClearanceMM` |  | high | in the older design block; merged into design_params but never read by INSSPG |
| 30 | `sCarrierIDClearanceMM` | clearance | insspg_params.json → sspg_design_parameters → `sCarrierIDClearanceMM` |  | high | in the older design block; merged into design_params but never read by INSSPG |
| 31 | `bearingIDClearanceMM` | clearance | insspg_params.json → sspg_design_parameters → `bearingIDClearanceMM` |  | high | extra bore in a bearing request; read by the actuator class but not used in the INSSPG bearing choices |
| 32 | `smallBearingMassKG` | bearing (chosen part) | insspg_params.json → sspg_design_parameters → `smallBearingMassKG` |  | high | in the older design block; merged into design_params but never read by INSSPG |
| 33 | `smallBearingODMM` | bearing (chosen part) | insspg_params.json → sspg_design_parameters → `smallBearingODMM` |  | high | in the older design block; merged into design_params but never read by INSSPG |
| 34 | `smallBearingWidth` | bearing (chosen part) | insspg_params.json → sspg_design_parameters → `smallBearingWidth` |  | high | in the older design block; merged into design_params but never read by INSSPG |
| 35 | `bearing_ID_config` | bearing (chosen part) | insspg_params.json → sspg_3DP_design_parameters → `bearing_ID` |  | high | config value bearing_ID (the CAD variable of the same name is not read from it): in the config but never read: the CAD gets this value from the motor, a bearing lookup or a formula |
| 36 | `bearing_OD_config` | bearing (chosen part) | insspg_params.json → sspg_3DP_design_parameters → `bearing_OD` |  | high | config value bearing_OD (the CAD variable of the same name is not read from it): in the config but never read: the CAD gets this value from the motor, a bearing lookup or a formula |
| 37 | `bearing_height_config` | bearing (chosen part) | insspg_params.json → sspg_3DP_design_parameters → `bearing_height` |  | high | config value bearing_height (the CAD variable of the same name is not read from it): in the config but never read: the CAD gets this value from the motor, a bearing lookup or a formula |
| 38 | `rotor_output_hole_PCD_config` | feature size | insspg_params.json → sspg_3DP_design_parameters → `rotor_output_hole_PCD` |  | high | config value rotor_output_hole_PCD (the CAD variable of the same name is not read from it): read by the code but not written to the CAD file |
| 39 | `sun_hub_dia_config` | feature size | insspg_params.json → sspg_3DP_design_parameters → `sun_hub_dia` |  | high | config value sun_hub_dia (the CAD variable of the same name is not read from it): read by the code but not written to the CAD file |
| 40 | `stator_bottom_step_height__config` | feature size | insspg_params.json → sspg_3DP_design_parameters → `stator_bottom_step_height_` |  | high | config value stator_bottom_step_height_ (the CAD variable of the same name is not read from it): read by the code but not written to the CAD file |
| 41 | `stator_upper_step_height_config` | feature size | insspg_params.json → sspg_3DP_design_parameters → `stator_upper_step_height` |  | high | config value stator_upper_step_height (the CAD variable of the same name is not read from it): read by the code but not written to the CAD file |
| 42 | `stator_side_step_OD_config` | feature size | insspg_params.json → sspg_3DP_design_parameters → `stator_side_step_OD` |  | high | config value stator_side_step_OD (the CAD variable of the same name is not read from it): read by the code but not written to the CAD file |
| 43 | `stator_mounting_holes_dia_config` | feature size | insspg_params.json → sspg_3DP_design_parameters → `stator_mounting_holes_dia` |  | high | config value stator_mounting_holes_dia (the CAD variable of the same name is not read from it): read by the code but not written to the CAD file |
| 44 | `rotor_support_bearing_ID_config` | bearing (chosen part) | insspg_params.json → sspg_3DP_design_parameters → `rotor_support_bearing_ID` |  | high | config value rotor_support_bearing_ID (the CAD variable of the same name is not read from it): read by the code but not written to the CAD file |
| 45 | `rotor_support_bearing_OD_config` | bearing (chosen part) | insspg_params.json → sspg_3DP_design_parameters → `rotor_support_bearing_OD` |  | high | config value rotor_support_bearing_OD (the CAD variable of the same name is not read from it): read by the code but not written to the CAD file |
| 46 | `rotor_support_bearing_height_config` | bearing (chosen part) | insspg_params.json → sspg_3DP_design_parameters → `rotor_support_bearing_height` |  | high | config value rotor_support_bearing_height (the CAD variable of the same name is not read from it): read by the code but not written to the CAD file |
| 47 | `rotor_upper_support_bearing_ID_config` | bearing (chosen part) | insspg_params.json → sspg_3DP_design_parameters → `rotor_upper_support_bearing_ID` |  | high | config value rotor_upper_support_bearing_ID (the CAD variable of the same name is not read from it): read by the code but not written to the CAD file |
| 48 | `rotor_upper_support_bearing_OD_config` | bearing (chosen part) | insspg_params.json → sspg_3DP_design_parameters → `rotor_upper_support_bearing_OD` |  | high | config value rotor_upper_support_bearing_OD (the CAD variable of the same name is not read from it): read by the code but not written to the CAD file |
| 49 | `rotor_upper_support_bearing_height_config` | bearing (chosen part) | insspg_params.json → sspg_3DP_design_parameters → `rotor_upper_support_bearing_height` |  | high | config value rotor_upper_support_bearing_height (the CAD variable of the same name is not read from it): read by the code but not written to the CAD file |
| 50 | `stator_casing_hole_wrench_size` | fastener size | insspg_params.json → sspg_3DP_design_parameters → `stator_casing_hole_wrench_size` |  | high | read by the code but not written to the CAD file |
| 51 | `GEAR_RATIO_MIN` | search bound | insspg_params.json → sspg_optimization_parameters → `GEAR_RATIO_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 52 | `GEAR_RATIO_MAX` | search bound | insspg_params.json → sspg_optimization_parameters → `GEAR_RATIO_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 53 | `GEAR_RATIO_STEP` | search bound | insspg_params.json → sspg_optimization_parameters → `GEAR_RATIO_STEP` |  | high | optimiser setting: limits of the search, not a part dimension |
| 54 | `MODULE_MIN` | search bound | insspg_params.json → sspg_optimization_parameters → `MODULE_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 55 | `MODULE_MAX` | search bound | insspg_params.json → sspg_optimization_parameters → `MODULE_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 56 | `NUM_PLANET_MIN` | search bound | insspg_params.json → sspg_optimization_parameters → `NUM_PLANET_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 57 | `NUM_PLANET_MAX` | search bound | insspg_params.json → sspg_optimization_parameters → `NUM_PLANET_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 58 | `NUM_TEETH_SUN_MIN` | search bound | insspg_params.json → sspg_optimization_parameters → `NUM_TEETH_SUN_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 59 | `NUM_TEETH_PLANET_MIN` | search bound | insspg_params.json → sspg_optimization_parameters → `NUM_TEETH_PLANET_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 60 | `MAX_GB_DIA_MULT_FACTOR` | search bound | insspg_params.json → sspg_optimization_parameters → `MAX_GB_DIA_MULT_FACTOR` |  | high | optimiser setting: limits of the search, not a part dimension |

## Config blocks INSSPG_TYPE_1 doesn't read

