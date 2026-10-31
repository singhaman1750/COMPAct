# INCPG_INDEPENDENT variables by category

Generated from `config_files/variables/incpg_independent_variables.json` by `python tools/variables/render.py`; edit the JSON, not this page.

Every INCPG independent variable sorted into input / optimisation / fixed / dependent. 'cad_variables' are the 138 variables INCPG independent writes to CADs/INCPG/incpg_independent_equations_onshape.txt, in that order; 'code_only' are values the code uses but does not write to the CAD file (including the small module module_s: the CAD file has one module) and every config key the CAD does not use; 'unused_config_blocks' are config blocks INCPG never reads. tests/test_variable_categories.py checks the lists against the code and re-evaluates every formula and lookup; docs/variables/incpg_independent.md is generated from this file (python tools/variables/render.py).

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
| Input | 21 | 2 |
| Optimisation | 5 | 1 |
| Fixed | 57 | 16 |
| Dependent | 55 | 2 |
| **Total** | **138** | **21** |

CAD variables by confidence: high 137, medium 1, low 0

## To review (not high confidence)

- `fw_r` (Dependent, medium): ring face width: the small planet - ring stress width (raised to hold the planet bearing) plus standard_clearance_1_5mm; kept as a stress rule because the shared rule names fw_r that way, and the small planet's width fw_p_s is a copy of it

## Rules shared by every gearbox

From `config_files/variables/rules.json`; the test holds every gearbox's file to them.

- names matching `^(a[12]_)?Nr(_[bs]|[0-9]*)$` are **Dependent / implicit constraint**: ring-gear teeth are implicitly constrained: the coaxial geometric constraint (e.g. Nr = Ns + 2 x Np) fixes them once the sun and planet teeth are chosen, so the optimiser sets them instead of searching them
- names matching `^fw_(s_calc|p|p_b|r|r_s)$` are **Dependent / stress rule**: gear face widths follow from the tooth-stress rule: the optimisation variables, the motor torque, the gear material and the safety factors fix them, and the optimiser always takes the smallest width that passes (widths that are a formula of another width, e.g. CPG's fw_p_s = fw_r + clearance_planet, are dependent / formula) Exceptions: inwpg_dependent: `fw_p_b`; inwpg_independent: `fw_p_b`.
- names matching `^a[12]_fw_(s_calc|r)[12]?$` are **Dependent / stress rule**: the same stress-rule face widths in a two-stage gearbox, under the stage prefixes a1_ / a2_ (the planet width a1_fw_p / a2_fw_p is a copy of the ring width, so it is dependent / formula and not in this rule)

## Input (21)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `motor_OD` | motor | motors.json → motors.<motor>.geometry → `stator_OD` |  | high | read from the chosen motor's geometry (the stator's outer diameter) |
| 2 | `rotor_OD` | motor | motors.json → motors.<motor>.geometry → `rotor_OD` |  | high | read from the chosen motor's geometry |
| 3 | `stator_ID` | motor | motors.json → motors.<motor>.geometry → `stator_ID` |  | high | read from the chosen motor's geometry |
| 4 | `rotor_height` | motor | motors.json → motors.<motor>.geometry → `rotor_height` |  | high | read from the chosen motor's geometry |
| 5 | `rotor_ID` | motor | motors.json → motors.<motor>.geometry → `rotor_ID` |  | high | read from the chosen motor's geometry |
| 6 | `stator_height` | motor | motors.json → motors.<motor>.geometry → `stator_height` |  | high | read from the chosen motor's geometry |
| 7 | `stator_OD` | motor | motors.json → motors.<motor>.geometry → `stator_OD` |  | high | read from the chosen motor's geometry |
| 8 | `stator_hole_dia` | motor | motors.json → motors.<motor>.geometry → `stator_hole_dia` |  | high | read from the chosen motor's geometry |
| 9 | `stator_top_height` | motor | motors.json → motors.<motor>.geometry → `stator_wire_top_height` |  | high | read from the chosen motor's geometry |
| 10 | `stator_mid_height` | motor | motors.json → motors.<motor>.geometry → `stator_mid_height` |  | high | read from the chosen motor's geometry |
| 11 | `stator_bottom_height` | motor | motors.json → motors.<motor>.geometry → `stator_wire_bottom_height` |  | high | read from the chosen motor's geometry |
| 12 | `stator_inside_OD` | motor | motors.json → motors.<motor>.geometry → `stator_wire_OD` |  | high | read from the chosen motor's geometry |
| 13 | `stator_hole_num` | motor | motors.json → motors.<motor>.geometry → `stator_hole_num` |  | high | read from the chosen motor's geometry |
| 14 | `stator_inside_ID` | motor | motors.json → motors.<motor>.geometry → `stator_wire_ID` |  | high | read from the chosen motor's geometry |
| 15 | `driver_upper_holes_dist_from_center` | driver | config.json → Motor_drivers.OdrivePro → `driver_upper_holes_dist_from_center` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 16 | `driver_lower_holes_dist_from_center` | driver | config.json → Motor_drivers.OdrivePro → `driver_lower_holes_dist_from_center` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 17 | `driver_side_holes_dist_from_center` | driver | config.json → Motor_drivers.OdrivePro → `driver_side_holes_dist_from_center` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 18 | `driver_mount_holes_dia` | driver | config.json → Motor_drivers.OdrivePro → `driver_mount_holes_dia` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 19 | `driver_mount_inserts_OD` | driver | config.json → Motor_drivers.OdrivePro → `driver_mount_inserts_OD` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 20 | `driver_mount_thickness` | driver | config.json → Motor_drivers.OdrivePro → `driver_mount_thickness` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 21 | `driver_mount_height` | driver | config.json → Motor_drivers.OdrivePro → `driver_mount_height` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |

## Optimisation (5)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `Ns` | teeth | optimiser (`optimizationInrunnerCompoundPlanetaryActuator`) |  | high | sun teeth: searched by the optimiser loop |
| 2 | `Np_b` | teeth | optimiser (`optimizationInrunnerCompoundPlanetaryActuator`) |  | high | big planet teeth: searched by the optimiser loop |
| 3 | `Np_s` | teeth | optimiser (`optimizationInrunnerCompoundPlanetaryActuator`) |  | high | small planet teeth: searched by the optimiser loop |
| 4 | `num_planet` | planets | optimiser (`optimizationInrunnerCompoundPlanetaryActuator`) |  | high | number of planets: searched by the optimiser loop |
| 5 | `module` | module | optimiser (`optimizationInrunnerCompoundPlanetaryActuator`) |  | high | the big module (sun, big planet): searched by the optimiser loop; the CAD file has this one module although the small planet and the ring use the small module module_s (code-only; same pattern as CPG bug 18) |

## Fixed (57)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `pressure_angle_deg` | gear standard | config.json → Gear_standard_parameters → `pressureAngleDEG` |  | high | gear standard, the same for every gearbox type |
| 2 | `clearance_planet` | clearance | incpg_independent_params.json → incpg_3DP_design_parameters → `clearance_planet` |  | high | constant from the INCPG 3DP design parameters |
| 3 | `clearance_case_mount_holes_shell_thickness` | clearance | incpg_independent_params.json → incpg_3DP_design_parameters → `clearance_case_mount_holes_shell_thickness` |  | high | constant from the INCPG 3DP design parameters |
| 4 | `standard_clearance_1_5mm` | clearance | incpg_independent_params.json → incpg_3DP_design_parameters → `standard_clearance_1_5mm` |  | high | constant from the INCPG 3DP design parameters |
| 5 | `standard_clearance_2_mm` | clearance | incpg_independent_params.json → incpg_3DP_design_parameters → `standard_clearance_2_mm` |  | high | constant from the INCPG 3DP design parameters |
| 6 | `standard_fillet_1_5mm` | feature size | incpg_independent_params.json → incpg_3DP_design_parameters → `standard_fillet_1_5mm` |  | high | constant from the INCPG 3DP design parameters |
| 7 | `standard_fillet_3_mm` | feature size | incpg_independent_params.json → incpg_3DP_design_parameters → `standard_fillet_3_mm` |  | high | constant from the INCPG 3DP design parameters |
| 8 | `standard_bearing_insertion_chamfer` | feature size | incpg_independent_params.json → incpg_3DP_design_parameters → `standard_bearing_insertion_chamfer` |  | high | constant from the INCPG 3DP design parameters |
| 9 | `bearingIDClearanceMM` | constraint constant | incpg_independent_params.json → incpg_3DP_design_parameters → `bearingIDClearanceMM` |  | high | constant from the INCPG 3DP design parameters |
| 10 | `tight_clearance_3DP` | clearance | incpg_independent_params.json → incpg_3DP_design_parameters → `tight_clearance_3DP` |  | high | constant from the INCPG 3DP design parameters |
| 11 | `loose_clearance_3DP` | clearance | incpg_independent_params.json → incpg_3DP_design_parameters → `loose_clearance_3DP` |  | high | constant from the INCPG 3DP design parameters |
| 12 | `bearing_step_width` | bearing (chosen part) | incpg_independent_params.json → incpg_3DP_design_parameters → `bearing_step_width` |  | high | constant from the INCPG 3DP design parameters |
| 13 | `motor_mount_driver_hole_dia` | fastener size | incpg_independent_params.json → incpg_3DP_design_parameters → `motor_mount_driver_hole_dia` |  | high | constant from the INCPG 3DP design parameters |
| 14 | `motor_mount_driver_hole_num` | fastener size | incpg_independent_params.json → incpg_3DP_design_parameters → `motor_mount_driver_hole_num` |  | high | constant from the INCPG 3DP design parameters |
| 15 | `rotor_hub_thickness` | wall thickness | incpg_independent_params.json → incpg_3DP_design_parameters → `rotor_hub_thickness` |  | high | constant from the INCPG 3DP design parameters |
| 16 | `rotor_hub_height` | feature size | incpg_independent_params.json → incpg_3DP_design_parameters → `rotor_hub_height` |  | high | constant from the INCPG 3DP design parameters |
| 17 | `rotor_hub_sun_hole_dia` | fastener size | incpg_independent_params.json → incpg_3DP_design_parameters → `rotor_hub_sun_hole_dia` |  | high | constant from the INCPG 3DP design parameters |
| 18 | `rotor_hub_sun_hole_num` | fastener size | incpg_independent_params.json → incpg_3DP_design_parameters → `rotor_hub_sun_hole_num` |  | high | constant from the INCPG 3DP design parameters |
| 19 | `rotor_top_bearing_ID` | bearing (chosen part) | incpg_independent_params.json → incpg_3DP_design_parameters → `rotor_top_bearing_ID` |  | high | rotor bearing size chosen per motor in the params file (one value for each motor; ISSUES bug 12 fix) |
| 20 | `rotor_top_bearing_OD` | bearing (chosen part) | incpg_independent_params.json → incpg_3DP_design_parameters → `rotor_top_bearing_OD` |  | high | rotor bearing size chosen per motor in the params file (one value for each motor; ISSUES bug 12 fix) |
| 21 | `rotor_top_bearing_width` | bearing (chosen part) | incpg_independent_params.json → incpg_3DP_design_parameters → `rotor_top_bearing_width` |  | high | rotor bearing size chosen per motor in the params file (one value for each motor; ISSUES bug 12 fix) |
| 22 | `rotor_bottom_bearing_ID` | bearing (chosen part) | incpg_independent_params.json → incpg_3DP_design_parameters → `rotor_bottom_bearing_ID` |  | high | rotor bearing size chosen per motor in the params file (one value for each motor; ISSUES bug 12 fix) |
| 23 | `rotor_bottom_bearing_OD` | bearing (chosen part) | incpg_independent_params.json → incpg_3DP_design_parameters → `rotor_bottom_bearing_OD` |  | high | rotor bearing size chosen per motor in the params file (one value for each motor; ISSUES bug 12 fix) |
| 24 | `rotor_bottom_bearing_width` | bearing (chosen part) | incpg_independent_params.json → incpg_3DP_design_parameters → `rotor_bottom_bearing_width` |  | high | rotor bearing size chosen per motor in the params file (one value for each motor; ISSUES bug 12 fix) |
| 25 | `planet_pin_bolt_dia` | fastener size | incpg_independent_params.json → incpg_3DP_design_parameters → `planet_pin_bolt_dia` |  | high | constant from the INCPG 3DP design parameters |
| 26 | `planet_shaft_step_offset` | planet part | incpg_independent_params.json → incpg_3DP_design_parameters → `planet_shaft_step_offset` |  | high | constant from the INCPG 3DP design parameters |
| 27 | `planet_bearing_OD` | bearing (chosen part) | incpg_independent_params.json → incpg_3DP_design_parameters → `planet_bearing_OD` |  | high | constant from the INCPG 3DP design parameters |
| 28 | `planet_bearing_width` | bearing (chosen part) | incpg_independent_params.json → incpg_3DP_design_parameters → `planet_bearing_width` |  | high | constant from the INCPG 3DP design parameters |
| 29 | `planet_bearing_ID` | bearing (chosen part) | incpg_independent_params.json → incpg_3DP_design_parameters → `planet_bearing_ID` |  | high | constant from the INCPG 3DP design parameters |
| 30 | `sun_coupler_hub_thickness` | wall thickness | incpg_independent_params.json → incpg_3DP_design_parameters → `sun_coupler_hub_thickness` |  | high | constant from the INCPG 3DP design parameters |
| 31 | `sun_shaft_bearing_ID` | bearing (chosen part) | incpg_independent_params.json → incpg_3DP_design_parameters → `sun_shaft_bearing_ID` |  | high | constant from the INCPG 3DP design parameters |
| 32 | `sun_shaft_bearing_OD` | bearing (chosen part) | incpg_independent_params.json → incpg_3DP_design_parameters → `sun_shaft_bearing_OD` |  | high | constant from the INCPG 3DP design parameters |
| 33 | `sun_shaft_bearing_width` | bearing (chosen part) | incpg_independent_params.json → incpg_3DP_design_parameters → `sun_shaft_bearing_width` |  | high | constant from the INCPG 3DP design parameters |
| 34 | `sun_central_bolt_dia` | fastener size | incpg_independent_params.json → incpg_3DP_design_parameters → `sun_central_bolt_dia` |  | high | constant from the INCPG 3DP design parameters |
| 35 | `sec_carrier_thickness` | wall thickness | incpg_independent_params.json → incpg_3DP_design_parameters → `sec_carrier_thickness` |  | high | constant from the INCPG 3DP design parameters |
| 36 | `carrier_trapezoidal_support_sun_offset` | feature size | incpg_independent_params.json → incpg_3DP_design_parameters → `carrier_trapezoidal_support_sun_offset` |  | high | constant from the INCPG 3DP design parameters |
| 37 | `carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID` | bearing (chosen part) | incpg_independent_params.json → incpg_3DP_design_parameters → `carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID` |  | high | constant from the INCPG 3DP design parameters |
| 38 | `carrier_trapezoidal_support_hole_dia` | fastener size | incpg_independent_params.json → incpg_3DP_design_parameters → `carrier_trapezoidal_support_hole_dia` |  | high | constant from the INCPG 3DP design parameters |
| 39 | `case_mounting_surface_height` | wall thickness | incpg_independent_params.json → incpg_3DP_design_parameters → `case_mounting_surface_height` |  | high | constant from the INCPG 3DP design parameters |
| 40 | `case_mounting_hole_dia` | fastener size | incpg_independent_params.json → incpg_3DP_design_parameters → `case_mounting_hole_dia` |  | high | constant from the INCPG 3DP design parameters |
| 41 | `motor_case_thickness` | wall thickness | incpg_independent_params.json → incpg_3DP_design_parameters → `motor_case_thickness` |  | high | constant from the INCPG 3DP design parameters |
| 42 | `output_mount_hole_dia` | fastener size | incpg_independent_params.json → incpg_3DP_design_parameters → `output_mount_hole_dia` |  | high | constant from the INCPG 3DP design parameters |
| 43 | `actuactor_mount_hole_dia` | fastener size | incpg_independent_params.json → incpg_3DP_design_parameters → `actuactor_mount_hole_dia` |  | high | constant from the INCPG 3DP design parameters |
| 44 | `motor_case_OD_base_to_chamfer` | feature size | incpg_independent_params.json → incpg_3DP_design_parameters → `motor_case_OD_base_to_chamfer` |  | high | constant from the INCPG 3DP design parameters |
| 45 | `pattern_offset_from_motor_case_OD_base` | feature size | incpg_independent_params.json → incpg_3DP_design_parameters → `pattern_offset_from_motor_case_OD_base` |  | high | constant from the INCPG 3DP design parameters |
| 46 | `pattern_bulge_dia` | feature size | incpg_independent_params.json → incpg_3DP_design_parameters → `pattern_bulge_dia` |  | high | constant from the INCPG 3DP design parameters |
| 47 | `pattern_num_bulge` | feature size | incpg_independent_params.json → incpg_3DP_design_parameters → `pattern_num_bulge` |  | high | constant from the INCPG 3DP design parameters |
| 48 | `pattern_depth` | feature size | incpg_independent_params.json → incpg_3DP_design_parameters → `pattern_depth` |  | high | constant from the INCPG 3DP design parameters |
| 49 | `magnet_mount_hole_dia` | fastener size | incpg_independent_params.json → incpg_3DP_design_parameters → `magnet_mount_hole_dia` |  | high | constant from the INCPG 3DP design parameters |
| 50 | `magnet_thickness` | wall thickness | incpg_independent_params.json → incpg_3DP_design_parameters → `magnet_thickness` |  | high | constant from the INCPG 3DP design parameters |
| 51 | `magnet_dia` | feature size | incpg_independent_params.json → incpg_3DP_design_parameters → `magnet_dia` |  | high | constant from the INCPG 3DP design parameters |
| 52 | `magnet_mount_thickness` | wall thickness | incpg_independent_params.json → incpg_3DP_design_parameters → `magnet_mount_thickness` |  | high | constant from the INCPG 3DP design parameters |
| 53 | `magnet_pattern_bulge_dia` | feature size | incpg_independent_params.json → incpg_3DP_design_parameters → `magnet_pattern_bulge_dia` |  | high | constant from the INCPG 3DP design parameters |
| 54 | `magnet_pattern_bulge_number` | feature size | incpg_independent_params.json → incpg_3DP_design_parameters → `magnet_pattern_bulge_number` |  | high | constant from the INCPG 3DP design parameters |
| 55 | `magnet_mount_height` | feature size | incpg_independent_params.json → incpg_3DP_design_parameters → `magnet_mount_height` |  | high | constant from the INCPG 3DP design parameters |
| 56 | `ring_radial_width` | constraint constant | incpg_independent_params.json → incpg_3DP_design_parameters → `ringRadialWidthMM` |  | high | ring wall: the config's ringRadialWidthMM (also used by the gearbox class and the mass code) |
| 57 | `ring_gearbox_casing_thickness` | wall thickness | incpg_independent_params.json → incpg_3DP_design_parameters → `ring_gearbox_casing_thickness` |  | high | constant from the INCPG 3DP design parameters |

## Dependent (55)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `Nr` | implicit constraint | `Ns + Np_b + Np_s` | Np_s, Ns, Np_b | high | implicitly constrained: with equal modules the coaxial constraint gives Nr = Ns + Np_b + Np_s, which the code writes (the code lists it among the optimisation variables) |
| 2 | `pressure_angle` | formula | `pressure_angle_deg * pi / 180` | pressure_angle_deg | high | pressure angle in radians (the CAD file also carries it in degrees as pressure_angle_deg) |
| 3 | `motor_height` | formula | `stator_top_height + stator_mid_height + stator_bottom_height` | stator_top_height, stator_mid_height, stator_bottom_height | high | motor length of a frameless inrunner: the stator's top wire height, middle height and bottom wire height (motorLengthMM) |
| 4 | `rotor_top_bearing_holder_thickness` | formula | `bearing_step_width + rotor_top_bearing_width - (standard_clearance_1_5mm / 2 + stator_top_height + stator_mid_height - rotor_height - bearing_step_width)` | bearing_step_width, rotor_top_bearing_width, rotor_height, stator_mid_height, stator_top_height, standard_clearance_1_5mm | high | computed by the code: bearing_step_width + rotor_top_bearing_width - (standard_clearance_1_5mm / 2 + stator_top_height + stator_mid_height - rotor_height - bearing_step_width) |
| 5 | `h_a` | formula | `1 * module` | module | high | addendum, standard proportion of the module |
| 6 | `h_b` | formula | `1.25 * module` | module | high | standard proportion of the module (same value as h_f) |
| 7 | `h_f` | formula | `1.25 * module` | module | high | dedendum, standard proportion of the module |
| 8 | `clr_tip_root` | formula | `h_f - h_a` | h_f, h_a | high | tip-root clearance from addendum and dedendum |
| 9 | `dp_s` | formula | `module * Ns` | module, Ns | high | pitch diameter |
| 10 | `db_s` | formula | `dp_s * cos(pressure_angle)` | dp_s, pressure_angle | high | base-circle diameter |
| 11 | `alpha_s` | formula | `sqrt(dp_s ** 2 - db_s ** 2) / db_s * 180 / pi - pressure_angle_deg` | pressure_angle_deg, db_s, dp_s | high | involute angle used to draw the tooth |
| 12 | `beta_s` | formula | `(360 / (4 * Ns) - alpha_s) * 2` | alpha_s, Ns | high | tooth angle used to draw the tooth |
| 13 | `fw_s_calc` | stress rule | two stress widths, b = FOS x Ft x qe x qk / (gear_allowable_stress x module): b1 for the sun - big planet mesh (module, Ft from serviceFactor x motor_peak_torque at the sun, qe from the sun-planet contact ratio, qk from Ns) and b2 for the small planet - ring mesh (module_s, qk from Np_s); then, if b1 + b2 < 2 x planet_bearing_width + planet_bearing_gap, each planet gear is raised to at least planet_bearing_width + planet_bearing_gap / 2 (one bearing per gear, half the gap each; mitStressAnalysisMinFacewidth); fw_s_calc = b1 | module, module_s, Ns, Np_b, Np_s, Nr, num_planet, pressure_angle, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor | high | sun face width from the tooth-stress rule: fixed by the optimisation variables, the motor torque, the gear material and the safety factors, so the optimiser has no freedom over it |
| 14 | `dp_p_b` | formula | `module * Np_b` | module, Np_b | high | big-planet pitch diameter |
| 15 | `db_p_b` | formula | `dp_p_b * cos(pressure_angle)` | dp_p_b, pressure_angle | high | base-circle diameter |
| 16 | `alpha_p_b` | formula | `sqrt(dp_p_b ** 2 - db_p_b ** 2) / db_p_b * 180 / pi - pressure_angle_deg` | pressure_angle_deg, db_p_b, dp_p_b | high | involute angle used to draw the tooth |
| 17 | `beta_p_b` | formula | `(360 / (4 * Np_b) - alpha_p_b) * 2` | alpha_p_b, Np_b | high | tooth angle used to draw the tooth |
| 18 | `fw_p_b` | stress rule | two stress widths, b = FOS x Ft x qe x qk / (gear_allowable_stress x module): b1 for the sun - big planet mesh (module, Ft from serviceFactor x motor_peak_torque at the sun, qe from the sun-planet contact ratio, qk from Ns) and b2 for the small planet - ring mesh (module_s, qk from Np_s); then, if b1 + b2 < 2 x planet_bearing_width + planet_bearing_gap, each planet gear is raised to at least planet_bearing_width + planet_bearing_gap / 2 (one bearing per gear, half the gap each; mitStressAnalysisMinFacewidth); fw_p_b = b1 (raised) | module, module_s, Ns, Np_b, Np_s, Nr, num_planet, pressure_angle, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor, planet_bearing_width, planet_bearing_gap | high | big-planet face width from the tooth-stress rule, raised to hold its bearing |
| 19 | `dp_r` | formula | `module * Nr` | module, Nr | high | ring pitch diameter, drawn with the CAD file's single module (the ring's own module is module_s, which the CAD file does not carry; same pattern as CPG bug 18) |
| 20 | `db_r` | formula | `dp_r * cos(pressure_angle)` | dp_r, pressure_angle | high | base-circle diameter |
| 21 | `alpha_r` | formula | `sqrt(dp_r ** 2 - db_r ** 2) / db_r * 180 / pi - pressure_angle_deg` | pressure_angle_deg, db_r, dp_r | high | involute angle used to draw the tooth |
| 22 | `beta_r` | formula | `(360 / (4 * Nr) + alpha_r) * 2` | alpha_r, Nr | high | tooth angle used to draw the tooth |
| 23 | `fw_r` | stress rule | two stress widths, b = FOS x Ft x qe x qk / (gear_allowable_stress x module): b1 for the sun - big planet mesh (module, Ft from serviceFactor x motor_peak_torque at the sun, qe from the sun-planet contact ratio, qk from Ns) and b2 for the small planet - ring mesh (module_s, qk from Np_s); then, if b1 + b2 < 2 x planet_bearing_width + planet_bearing_gap, each planet gear is raised to at least planet_bearing_width + planet_bearing_gap / 2 (one bearing per gear, half the gap each; mitStressAnalysisMinFacewidth); fw_r = b2 (raised) + standard_clearance_1_5mm (the CAD's ring width is the stress width plus one standard clearance) | module, module_s, Ns, Np_b, Np_s, Nr, num_planet, pressure_angle, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor, planet_bearing_width, planet_bearing_gap, standard_clearance_1_5mm | medium | ring face width: the small planet - ring stress width (raised to hold the planet bearing) plus standard_clearance_1_5mm; kept as a stress rule because the shared rule names fw_r that way, and the small planet's width fw_p_s is a copy of it |
| 24 | `dp_p_s` | formula | `module * Np_s` | module, Np_s | high | small-planet pitch diameter, drawn with the CAD file's single module (the small planet's own module is module_s, which the CAD file does not carry; same pattern as CPG bug 18) |
| 25 | `db_p_s` | formula | `dp_p_s * cos(pressure_angle)` | dp_p_s, pressure_angle | high | base-circle diameter |
| 26 | `alpha_p_s` | formula | `sqrt(dp_p_s ** 2 - db_p_s ** 2) / db_p_s * 180 / pi - pressure_angle_deg` | pressure_angle_deg, db_p_s, dp_p_s | high | involute angle used to draw the tooth |
| 27 | `beta_p_s` | formula | `(360 / (4 * Np_s) - alpha_p_s) * 2` | alpha_p_s, Np_s | high | tooth angle used to draw the tooth |
| 28 | `fw_p_s` | formula | `fw_r` | fw_r | high | small-planet width: the ring width plus a clearance (a formula, not the stress rule) |
| 29 | `motor_mount_driver_nut_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=motor_mount_driver_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | motor_mount_driver_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 30 | `motor_mount_driver_nut_depth` | lookup | `nuts_and_bolts_dimensions(bolt_dia=motor_mount_driver_hole_dia, bolt_type=socket_head)` → nut_thickness | motor_mount_driver_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 31 | `planet_pin_socket_head_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=planet_pin_bolt_dia, bolt_type=socket_head)` → bolt_head_dia | planet_pin_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 32 | `planet_pin_nut_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=planet_pin_bolt_dia, bolt_type=socket_head)` → nut_width_across_flats | planet_pin_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 33 | `planet_pin_nut_depth` | lookup | `nuts_and_bolts_dimensions(bolt_dia=planet_pin_bolt_dia, bolt_type=socket_head)` → nut_thickness | planet_pin_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 34 | `sun_central_bolt_socket_head_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=sun_central_bolt_dia, bolt_type=socket_head)` → bolt_head_dia | sun_central_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 35 | `rotor_hub_sun_hole_CSK_OD` | lookup | `nuts_and_bolts_dimensions(bolt_dia=rotor_hub_sun_hole_dia, bolt_type=CSK)` → bolt_head_dia | rotor_hub_sun_hole_dia | high | standard countersunk fastener size for the chosen bolt diameter |
| 36 | `rotor_hub_sun_hole_CSK_head_height` | lookup | `nuts_and_bolts_dimensions(bolt_dia=rotor_hub_sun_hole_dia, bolt_type=CSK)` → bolt_head_height | rotor_hub_sun_hole_dia | high | standard countersunk fastener size for the chosen bolt diameter |
| 37 | `sun_hub_dia` | formula | `rotor_top_bearing_ID - 2 * rotor_hub_thickness` | rotor_top_bearing_ID, rotor_hub_thickness | high | sun coupler hub, sized to the motor's output holes |
| 38 | `output_bearing_ID` | lookup | `bearings_discrete(idRequiredMM=module * (Ns + Np_b) + bearingIDClearanceMM)` → getBearingIDMM | bearingIDClearanceMM, module, Ns, Np_b | high | catalogue bearing chosen by bearings_discrete for the bore the design needs (smallest one that fits); this is its bore |
| 39 | `output_bearing_OD` | lookup | `bearings_discrete(idRequiredMM=module * (Ns + Np_b) + bearingIDClearanceMM)` → getBearingODMM | bearingIDClearanceMM, module, Ns, Np_b | high | catalogue bearing chosen by bearings_discrete for the bore the design needs (smallest one that fits); this is its outer diameter |
| 40 | `output_bearing_width` | lookup | `bearings_discrete(idRequiredMM=module * (Ns + Np_b) + bearingIDClearanceMM)` → getBearingWidthMM | bearingIDClearanceMM, module, Ns, Np_b | high | catalogue bearing chosen by bearings_discrete for the bore the design needs (smallest one that fits); this is its width |
| 41 | `carrier_trapezoidal_support_hole_socket_head_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=carrier_trapezoidal_support_hole_dia, bolt_type=socket_head)` → bolt_head_dia | carrier_trapezoidal_support_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 42 | `carrier_trapezoidal_support_hole_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=carrier_trapezoidal_support_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | carrier_trapezoidal_support_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 43 | `stator_hole_nut_depth` | lookup | `nuts_and_bolts_dimensions(bolt_dia=stator_hole_dia, bolt_type=socket_head)` → nut_thickness | stator_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 44 | `stator_hole_nut_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=stator_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | stator_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 45 | `stator_hole_allen_socket_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=stator_hole_dia, bolt_type=socket_head)` → bolt_head_dia | stator_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 46 | `carrier_trapezoidal_support_nut_depth` | lookup | `nuts_and_bolts_dimensions(bolt_dia=carrier_trapezoidal_support_hole_dia, bolt_type=socket_head)` → nut_thickness | carrier_trapezoidal_support_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 47 | `case_mounting_hole_allen_socket_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=case_mounting_hole_dia, bolt_type=socket_head)` → bolt_head_dia | case_mounting_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 48 | `case_mounting_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=case_mounting_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | case_mounting_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 49 | `case_mounting_nut_depth` | lookup | `nuts_and_bolts_dimensions(bolt_dia=case_mounting_hole_dia, bolt_type=socket_head)` → nut_thickness | case_mounting_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 50 | `output_mount_nut_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=output_mount_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | output_mount_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 51 | `output_mount_hole_nut_depth` | lookup | `nuts_and_bolts_dimensions(bolt_dia=output_mount_hole_dia, bolt_type=socket_head)` → nut_thickness | output_mount_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 52 | `actuactor_mount_nut_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=actuactor_mount_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | actuactor_mount_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 53 | `actuactor_mount_nut_depth` | lookup | `nuts_and_bolts_dimensions(bolt_dia=actuactor_mount_hole_dia, bolt_type=socket_head)` → nut_thickness | actuactor_mount_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 54 | `case_mounting_hole_shift` | formula | `case_mounting_hole_dia / 2` | case_mounting_hole_dia | high | how far the case bolt circle sits outside the case wall: half the bolt hole, less the configured overlap |
| 55 | `fw_s_used` | formula | `bearing_step_width + rotor_top_bearing_width - sun_coupler_hub_thickness + bearing_step_width + standard_clearance_1_5mm + sec_carrier_thickness + clearance_planet + fw_p_b + fw_p_s` | fw_p_s, fw_p_b, clearance_planet, sec_carrier_thickness, standard_clearance_1_5mm, bearing_step_width, sun_coupler_hub_thickness, rotor_top_bearing_width | high | printed sun length: planet width plus the carrier and clearances |

## Used by the code, not written to the CAD file (21)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `module_s` | module | optimiser (`optimizationInrunnerCompoundPlanetaryActuator`) |  | high | the small module (small planet, ring): searched by the optimiser loop and used by the stress rule and the gearbox constraints, but not in the CAD file, which has one module (same pattern as CPG bug 18) |
| 2 | `motor_peak_torque` | motor | motors.json → motors.<motor>.electrical → `peak_torque_Nm` |  | high | motor torque the gears are sized for (peak torque under the default rating setting); sets the face widths |
| 3 | `gear_allowable_stress` | material | config.json → Material_properties.<gear material> → `maxAllowableStressMPa` |  | high | allowable tooth stress of the gear material, chosen with the material mode (3dp: PLA, metal: steel); sets the face widths |
| 4 | `FOS` | safety factor | config.json → MIT_params → `FOS` |  | high | factor of safety in the tooth-stress rule |
| 5 | `serviceFactor` | safety factor | config.json → MIT_params → `serviceFactor` |  | high | service factor on the motor torque in the tooth-stress rule |
| 6 | `planet_bearing_gap` | clearance | incpg_independent_params.json → incpg_3DP_design_parameters → `planet_bearing_gap` |  | high | axial gap between the two planet bearings (one in each planet gear); with the bearing width it sets the smallest planet and ring widths |
| 7 | `maxGearboxDiameter` | formula | `MAX_GB_DIA_MULT_FACTOR * motor_OD` | MAX_GB_DIA_MULT_FACTOR, motor_OD | high | largest gearbox diameter the optimiser may use (gearbox_runner max_diameter): the stator's outer diameter times a factor |
| 8 | `actuator_width` | formula | `motor_case_thickness + standard_clearance_1_5mm / 2 + motor_height + standard_clearance_1_5mm / 2 + rotor_top_bearing_holder_thickness + standard_clearance_1_5mm + sec_carrier_thickness + clearance_planet + fw_p_b + fw_p_s + clearance_planet + bearing_step_width + output_bearing_width + bearing_step_width` | bearing_step_width, output_bearing_width, clearance_planet, fw_p_s, fw_p_b, sec_carrier_thickness, standard_clearance_1_5mm, rotor_top_bearing_holder_thickness, motor_height, motor_case_thickness | high | axial width without the driver mount, written to the results CSV |
| 9 | `planetMinDistanceMM` | constraint constant | incpg_independent_params.json → incpg_3DP_design_parameters → `planetMinDistanceMM` |  | high | read by the code but not written to the CAD file |
| 10 | `sCarrierExtrusionDiaMM` | constraint constant | incpg_independent_params.json → incpg_3DP_design_parameters → `sCarrierExtrusionDiaMM` |  | high | read by the code but not written to the CAD file |
| 11 | `sCarrierExtrusionClearanceMM` | constraint constant | incpg_independent_params.json → incpg_3DP_design_parameters → `sCarrierExtrusionClearanceMM` |  | high | read by the code but not written to the CAD file |
| 12 | `GEAR_RATIO_MIN` | search bound | incpg_independent_params.json → incpg_optimization_parameters → `GEAR_RATIO_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 13 | `GEAR_RATIO_MAX` | search bound | incpg_independent_params.json → incpg_optimization_parameters → `GEAR_RATIO_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 14 | `GEAR_RATIO_STEP` | search bound | incpg_independent_params.json → incpg_optimization_parameters → `GEAR_RATIO_STEP` |  | high | optimiser setting: limits of the search, not a part dimension |
| 15 | `MODULE_MIN` | search bound | incpg_independent_params.json → incpg_optimization_parameters → `MODULE_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 16 | `MODULE_MAX` | search bound | incpg_independent_params.json → incpg_optimization_parameters → `MODULE_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 17 | `NUM_PLANET_MIN` | search bound | incpg_independent_params.json → incpg_optimization_parameters → `NUM_PLANET_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 18 | `NUM_PLANET_MAX` | search bound | incpg_independent_params.json → incpg_optimization_parameters → `NUM_PLANET_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 19 | `NUM_TEETH_SUN_MIN` | search bound | incpg_independent_params.json → incpg_optimization_parameters → `NUM_TEETH_SUN_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 20 | `NUM_TEETH_PLANET_MIN` | search bound | incpg_independent_params.json → incpg_optimization_parameters → `NUM_TEETH_PLANET_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 21 | `MAX_GB_DIA_MULT_FACTOR` | search bound | incpg_independent_params.json → incpg_optimization_parameters → `MAX_GB_DIA_MULT_FACTOR` |  | high | optimiser setting: limits of the search, not a part dimension |

## Config blocks INCPG_INDEPENDENT doesn't read

