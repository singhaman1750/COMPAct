# INWPG_INDEPENDENT variables by category

Generated from `config_files/variables/inwpg_independent_variables.json` by `python tools/variables/render.py`; edit the JSON, not this page.

Every INWPG independent variable sorted into input / optimisation / fixed / dependent. 'cad_variables' are the 150 variables INWPG independent writes to CADs/INWPG/inwpg_independent_equations_onshape.txt, in that order; 'code_only' are values the code uses but does not write to the CAD file (including the small module module_s: the CAD file has one module) and every config key the CAD does not use; 'unused_config_blocks' are config blocks INWPG never reads. tests/test_variable_categories.py checks the lists against the code and re-evaluates every formula and lookup; docs/variables/inwpg_independent.md is generated from this file (python tools/variables/render.py).

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
| Fixed | 62 | 20 |
| Dependent | 62 | 3 |
| **Total** | **150** | **26** |

CAD variables by confidence: high 150, medium 0, low 0

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
| 1 | `Ns` | teeth | optimiser (`optimizationInrunnerWolfromPlanetaryActuator`) |  | high | sun teeth: searched by the optimiser loop |
| 2 | `Np_b` | teeth | optimiser (`optimizationInrunnerWolfromPlanetaryActuator`) |  | high | big planet teeth: searched by the optimiser loop |
| 3 | `Np_s` | teeth | optimiser (`optimizationInrunnerWolfromPlanetaryActuator`) |  | high | small planet teeth: searched by the optimiser loop |
| 4 | `num_planet` | planets | optimiser (`optimizationInrunnerWolfromPlanetaryActuator`) |  | high | number of planets: searched by the optimiser loop |
| 5 | `module` | module | optimiser (`optimizationInrunnerWolfromPlanetaryActuator`) |  | high | the big module (sun, big planet, big ring): searched by the optimiser loop; the CAD file has this one module although the small planet and small ring use the small module module_s (code-only; same pattern as CPG bug 18) |

## Fixed (62)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `pressure_angle_deg` | gear standard | config.json → Gear_standard_parameters → `pressureAngleDEG` |  | high | gear standard, the same for every gearbox type |
| 2 | `clearance_planet` | clearance | inwpg_params_independent.json → inwpg_3DP_design_parameters → `clearance_planet` |  | high | constant from the INWPG 3DP design parameters |
| 3 | `clearance_case_mount_holes_shell_thickness` | clearance | inwpg_params_independent.json → inwpg_3DP_design_parameters → `clearance_case_mount_holes_shell_thickness` |  | high | constant from the INWPG 3DP design parameters |
| 4 | `standard_clearance_1_5mm` | clearance | inwpg_params_independent.json → inwpg_3DP_design_parameters → `standard_clearance_1_5mm` |  | high | constant from the INWPG 3DP design parameters |
| 5 | `standard_clearance_2_mm` | clearance | inwpg_params_independent.json → inwpg_3DP_design_parameters → `standard_clearance_2_mm` |  | high | constant from the INWPG 3DP design parameters |
| 6 | `standard_fillet_1_5mm` | feature size | inwpg_params_independent.json → inwpg_3DP_design_parameters → `standard_fillet_1_5mm` |  | high | constant from the INWPG 3DP design parameters |
| 7 | `standard_fillet_3_mm` | feature size | inwpg_params_independent.json → inwpg_3DP_design_parameters → `standard_fillet_3_mm` |  | high | constant from the INWPG 3DP design parameters |
| 8 | `standard_bearing_insertion_chamfer` | feature size | inwpg_params_independent.json → inwpg_3DP_design_parameters → `standard_bearing_insertion_chamfer` |  | high | constant from the INWPG 3DP design parameters |
| 9 | `bearingIDClearanceMM` | constraint constant | inwpg_params_independent.json → inwpg_3DP_design_parameters → `bearingIDClearanceMM` |  | high | constant from the INWPG 3DP design parameters |
| 10 | `tight_clearance_3DP` | clearance | inwpg_params_independent.json → inwpg_3DP_design_parameters → `tight_clearance_3DP` |  | high | constant from the INWPG 3DP design parameters |
| 11 | `loose_clearance_3DP` | clearance | inwpg_params_independent.json → inwpg_3DP_design_parameters → `loose_clearance_3DP` |  | high | constant from the INWPG 3DP design parameters |
| 12 | `bearing_step_width` | bearing (chosen part) | inwpg_params_independent.json → inwpg_3DP_design_parameters → `bearing_step_width` |  | high | constant from the INWPG 3DP design parameters |
| 13 | `motor_mount_driver_hole_dia` | fastener size | inwpg_params_independent.json → inwpg_3DP_design_parameters → `motor_mount_driver_hole_dia` |  | high | constant from the INWPG 3DP design parameters |
| 14 | `motor_mount_driver_hole_num` | fastener size | inwpg_params_independent.json → inwpg_3DP_design_parameters → `motor_mount_driver_hole_num` |  | high | constant from the INWPG 3DP design parameters |
| 15 | `rotor_hub_thickness` | wall thickness | inwpg_params_independent.json → inwpg_3DP_design_parameters → `rotor_hub_thickness` |  | high | constant from the INWPG 3DP design parameters |
| 16 | `rotor_hub_height` | feature size | inwpg_params_independent.json → inwpg_3DP_design_parameters → `rotor_hub_height` |  | high | constant from the INWPG 3DP design parameters |
| 17 | `rotor_hub_sun_hole_dia` | fastener size | inwpg_params_independent.json → inwpg_3DP_design_parameters → `rotor_hub_sun_hole_dia` |  | high | constant from the INWPG 3DP design parameters |
| 18 | `rotor_hub_sun_hole_num` | fastener size | inwpg_params_independent.json → inwpg_3DP_design_parameters → `rotor_hub_sun_hole_num` |  | high | constant from the INWPG 3DP design parameters |
| 19 | `rotor_top_bearing_ID` | bearing (chosen part) | inwpg_params_independent.json → inwpg_3DP_design_parameters → `rotor_top_bearing_ID` |  | high | rotor bearing size chosen per motor in the params file (one value for each motor; ISSUES bug 12 fix) |
| 20 | `rotor_top_bearing_OD` | bearing (chosen part) | inwpg_params_independent.json → inwpg_3DP_design_parameters → `rotor_top_bearing_OD` |  | high | rotor bearing size chosen per motor in the params file (one value for each motor; ISSUES bug 12 fix) |
| 21 | `rotor_top_bearing_width` | bearing (chosen part) | inwpg_params_independent.json → inwpg_3DP_design_parameters → `rotor_top_bearing_width` |  | high | rotor bearing size chosen per motor in the params file (one value for each motor; ISSUES bug 12 fix) |
| 22 | `rotor_bottom_bearing_ID` | bearing (chosen part) | inwpg_params_independent.json → inwpg_3DP_design_parameters → `rotor_bottom_bearing_ID` |  | high | rotor bearing size chosen per motor in the params file (one value for each motor; ISSUES bug 12 fix) |
| 23 | `rotor_bottom_bearing_OD` | bearing (chosen part) | inwpg_params_independent.json → inwpg_3DP_design_parameters → `rotor_bottom_bearing_OD` |  | high | rotor bearing size chosen per motor in the params file (one value for each motor; ISSUES bug 12 fix) |
| 24 | `rotor_bottom_bearing_width` | bearing (chosen part) | inwpg_params_independent.json → inwpg_3DP_design_parameters → `rotor_bottom_bearing_width` |  | high | rotor bearing size chosen per motor in the params file (one value for each motor; ISSUES bug 12 fix) |
| 25 | `planet_pin_bolt_dia` | fastener size | inwpg_params_independent.json → inwpg_3DP_design_parameters → `planet_pin_bolt_dia` |  | high | constant from the INWPG 3DP design parameters |
| 26 | `planet_shaft_step_offset` | planet part | inwpg_params_independent.json → inwpg_3DP_design_parameters → `planet_shaft_step_offset` |  | high | constant from the INWPG 3DP design parameters |
| 27 | `planet_bearing_OD` | bearing (chosen part) | inwpg_params_independent.json → inwpg_3DP_design_parameters → `planet_bearing_OD` |  | high | constant from the INWPG 3DP design parameters |
| 28 | `planet_bearing_width` | bearing (chosen part) | inwpg_params_independent.json → inwpg_3DP_design_parameters → `planet_bearing_width` |  | high | constant from the INWPG 3DP design parameters |
| 29 | `planet_bearing_ID` | bearing (chosen part) | inwpg_params_independent.json → inwpg_3DP_design_parameters → `planet_bearing_ID` |  | high | constant from the INWPG 3DP design parameters |
| 30 | `sun_coupler_hub_thickness` | wall thickness | inwpg_params_independent.json → inwpg_3DP_design_parameters → `sun_coupler_hub_thickness` |  | high | constant from the INWPG 3DP design parameters |
| 31 | `sun_shaft_bearing_ID` | bearing (chosen part) | inwpg_params_independent.json → inwpg_3DP_design_parameters → `sun_shaft_bearing_ID` |  | high | constant from the INWPG 3DP design parameters |
| 32 | `sun_shaft_bearing_OD` | bearing (chosen part) | inwpg_params_independent.json → inwpg_3DP_design_parameters → `sun_shaft_bearing_OD` |  | high | constant from the INWPG 3DP design parameters |
| 33 | `sun_shaft_bearing_width` | bearing (chosen part) | inwpg_params_independent.json → inwpg_3DP_design_parameters → `sun_shaft_bearing_width` |  | high | constant from the INWPG 3DP design parameters |
| 34 | `sun_central_bolt_dia` | fastener size | inwpg_params_independent.json → inwpg_3DP_design_parameters → `sun_central_bolt_dia` |  | high | constant from the INWPG 3DP design parameters |
| 35 | `sec_carrier_thickness` | wall thickness | inwpg_params_independent.json → inwpg_3DP_design_parameters → `sec_carrier_thickness` |  | high | constant from the INWPG 3DP design parameters |
| 36 | `carrier_trapezoidal_support_sun_offset` | feature size | inwpg_params_independent.json → inwpg_3DP_design_parameters → `carrier_trapezoidal_support_sun_offset` |  | high | constant from the INWPG 3DP design parameters |
| 37 | `carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID` | bearing (chosen part) | inwpg_params_independent.json → inwpg_3DP_design_parameters → `carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID` |  | high | constant from the INWPG 3DP design parameters |
| 38 | `carrier_trapezoidal_support_hole_dia` | fastener size | inwpg_params_independent.json → inwpg_3DP_design_parameters → `carrier_trapezoidal_support_hole_dia` |  | high | constant from the INWPG 3DP design parameters |
| 39 | `case_mounting_surface_height` | wall thickness | inwpg_params_independent.json → inwpg_3DP_design_parameters → `case_mounting_surface_height` |  | high | constant from the INWPG 3DP design parameters |
| 40 | `case_mounting_hole_dia` | fastener size | inwpg_params_independent.json → inwpg_3DP_design_parameters → `case_mounting_hole_dia` |  | high | constant from the INWPG 3DP design parameters |
| 41 | `motor_case_thickness` | wall thickness | inwpg_params_independent.json → inwpg_3DP_design_parameters → `motor_case_thickness` |  | high | constant from the INWPG 3DP design parameters |
| 42 | `output_mount_hole_dia` | fastener size | inwpg_params_independent.json → inwpg_3DP_design_parameters → `output_mount_hole_dia` |  | high | constant from the INWPG 3DP design parameters |
| 43 | `actuactor_mount_hole_dia` | fastener size | inwpg_params_independent.json → inwpg_3DP_design_parameters → `actuactor_mount_hole_dia` |  | high | constant from the INWPG 3DP design parameters |
| 44 | `motor_case_OD_base_to_chamfer` | feature size | inwpg_params_independent.json → inwpg_3DP_design_parameters → `motor_case_OD_base_to_chamfer` |  | high | constant from the INWPG 3DP design parameters |
| 45 | `pattern_offset_from_motor_case_OD_base` | feature size | inwpg_params_independent.json → inwpg_3DP_design_parameters → `pattern_offset_from_motor_case_OD_base` |  | high | constant from the INWPG 3DP design parameters |
| 46 | `pattern_bulge_dia` | feature size | inwpg_params_independent.json → inwpg_3DP_design_parameters → `pattern_bulge_dia` |  | high | constant from the INWPG 3DP design parameters |
| 47 | `pattern_num_bulge` | feature size | inwpg_params_independent.json → inwpg_3DP_design_parameters → `pattern_num_bulge` |  | high | constant from the INWPG 3DP design parameters |
| 48 | `pattern_depth` | feature size | inwpg_params_independent.json → inwpg_3DP_design_parameters → `pattern_depth` |  | high | constant from the INWPG 3DP design parameters |
| 49 | `magnet_mount_hole_dia` | fastener size | inwpg_params_independent.json → inwpg_3DP_design_parameters → `magnet_mount_hole_dia` |  | high | constant from the INWPG 3DP design parameters |
| 50 | `magnet_thickness` | wall thickness | inwpg_params_independent.json → inwpg_3DP_design_parameters → `magnet_thickness` |  | high | constant from the INWPG 3DP design parameters |
| 51 | `magnet_dia` | feature size | inwpg_params_independent.json → inwpg_3DP_design_parameters → `magnet_dia` |  | high | constant from the INWPG 3DP design parameters |
| 52 | `magnet_mount_thickness` | wall thickness | inwpg_params_independent.json → inwpg_3DP_design_parameters → `magnet_mount_thickness` |  | high | constant from the INWPG 3DP design parameters |
| 53 | `magnet_pattern_bulge_dia` | feature size | inwpg_params_independent.json → inwpg_3DP_design_parameters → `magnet_pattern_bulge_dia` |  | high | constant from the INWPG 3DP design parameters |
| 54 | `magnet_pattern_bulge_number` | feature size | inwpg_params_independent.json → inwpg_3DP_design_parameters → `magnet_pattern_bulge_number` |  | high | constant from the INWPG 3DP design parameters |
| 55 | `magnet_mount_height` | feature size | inwpg_params_independent.json → inwpg_3DP_design_parameters → `magnet_mount_height` |  | high | constant from the INWPG 3DP design parameters |
| 56 | `big_ring_radial_width` | feature size | inwpg_params_independent.json → inwpg_3DP_design_parameters → `ringRadialWidthMMBig` |  | high | constant from the INWPG 3DP design parameters |
| 57 | `small_ring_radial_width` | feature size | inwpg_params_independent.json → inwpg_3DP_design_parameters → `ringRadialWidthMMSmall` |  | high | constant from the INWPG 3DP design parameters |
| 58 | `ring_gearbox_casing_thickness` | wall thickness | inwpg_params_independent.json → inwpg_3DP_design_parameters → `ring_gearbox_casing_thickness` |  | high | constant from the INWPG 3DP design parameters |
| 59 | `carrier_thickness` | wall thickness | inwpg_params_independent.json → inwpg_3DP_design_parameters → `carrier_thickness` |  | high | constant from the INWPG 3DP design parameters |
| 60 | `carrier_ring_bearing_ID` | bearing (chosen part) | inwpg_params_independent.json → inwpg_3DP_design_parameters → `carrier_ring_bearing_ID` |  | high | constant from the INWPG 3DP design parameters |
| 61 | `carrier_ring_bearing_OD` | bearing (chosen part) | inwpg_params_independent.json → inwpg_3DP_design_parameters → `carrier_ring_bearing_OD` |  | high | constant from the INWPG 3DP design parameters |
| 62 | `carrier_ring_bearing_width` | bearing (chosen part) | inwpg_params_independent.json → inwpg_3DP_design_parameters → `carrier_ring_bearing_width` |  | high | constant from the INWPG 3DP design parameters |

## Dependent (62)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `Nr_b` | implicit constraint | `Ns + Np_b * 2` | Ns, Np_b | high | implicitly constrained: the geometric constraints fix the ring teeth once the sun and planet teeth are chosen (Ns + 2 x Np_b: the big ring), and the optimiser sets them instead of searching them (the code lists them among the optimisation variables) |
| 2 | `Nr_s` | implicit constraint | `Ns + Np_b + Np_s` | Np_s, Ns, Np_b | high | implicitly constrained: the geometric constraints fix the ring teeth once the sun and planet teeth are chosen (Ns + Np_b + Np_s: the small ring), and the optimiser sets them instead of searching them (the code lists them among the optimisation variables) |
| 3 | `pressure_angle` | formula | `pressure_angle_deg * pi / 180` | pressure_angle_deg | high | pressure angle in radians (the CAD file also carries it in degrees as pressure_angle_deg) |
| 4 | `motor_height` | formula | `stator_top_height + stator_mid_height + stator_bottom_height` | stator_top_height, stator_mid_height, stator_bottom_height | high | motor length of a frameless inrunner: the stator's top wire height, middle height and bottom wire height (motorLengthMM) |
| 5 | `h_a` | formula | `1 * module` | module | high | addendum, standard proportion of the module |
| 6 | `h_b` | formula | `1.25 * module` | module | high | standard proportion of the module (same value as h_f) |
| 7 | `h_f` | formula | `1.25 * module` | module | high | dedendum, standard proportion of the module |
| 8 | `clr_tip_root` | formula | `h_f - h_a` | h_f, h_a | high | tip-root clearance from addendum and dedendum |
| 9 | `clr_tip_root_s` | formula | `h_f - h_a` | h_f, h_a | high | computed by the code: h_f - h_a |
| 10 | `dp_s` | formula | `module * Ns` | module, Ns | high | pitch diameter |
| 11 | `db_s` | formula | `dp_s * cos(pressure_angle)` | dp_s, pressure_angle | high | base-circle diameter |
| 12 | `alpha_s` | formula | `(dp_s ** 2 - db_s ** 2) ** 0.5 / db_s * 180 / pi - pressure_angle_deg` | pressure_angle_deg, db_s, dp_s | high | involute angle used to draw the tooth |
| 13 | `beta_s` | formula | `(360 / (4 * Ns) - alpha_s) * 2` | alpha_s, Ns | high | tooth angle used to draw the tooth |
| 14 | `fw_s_calc` | stress rule | b = FOS x |Ft_sp_big| x qe x qk / (gear_allowable_stress x module) on the sun - big planet mesh (mitStressAnalysisMinFacewidth); Ft_sp_big, Ft_rp_big, Ft_rp_small = serviceFactor x motor_peak_torque / (num_planet x pitch radius) with the Wolfrom force ratios (the code takes their absolute values: Ft_rp_small is negative); qe = 1 / contact ratio of the mesh, qk = curve fit in the tooth count of the mesh; then the planet stack (big ring + small ring + clearance_planet) is capped at planet_stack_stator_heights x stator_height: when it is longer, all five widths are scaled by (cap - clearance_planet) / stack, so the capped gears carry the same fraction of the torque; fw_s_calc = b (scaled) | module, module_s, Ns, Np_b, Np_s, Nr_b, Nr_s, num_planet, pressure_angle, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor, planet_bearing_width, planet_bearing_gap, planet_stack_stator_heights, stator_height, clearance_planet | high | sun face width from the tooth-stress rule, scaled by the planet-stack cap when it applies: fixed by the optimisation variables, the motor torque, the gear material, the safety factors and the cap |
| 15 | `dp_p_b` | formula | `module * Np_b` | module, Np_b | high | big-planet pitch diameter |
| 16 | `db_p_b` | formula | `dp_p_b * cos(pressure_angle)` | dp_p_b, pressure_angle | high | base-circle diameter |
| 17 | `alpha_p_b` | formula | `(dp_p_b ** 2 - db_p_b ** 2) ** 0.5 / db_p_b * 180 / pi - pressure_angle_deg` | pressure_angle_deg, db_p_b, dp_p_b | high | involute angle used to draw the tooth |
| 18 | `beta_p_b` | formula | `(360 / (4 * Np_b) - alpha_p_b) * 2` | alpha_p_b, Np_b | high | tooth angle used to draw the tooth |
| 19 | `fw_p_b` | formula | `fw_r_b` | fw_r_b | high | computed by the code: fw_r_b |
| 20 | `dp_r_b` | formula | `module * Nr_b` | module, Nr_b | high | computed by the code: module * Nr_b |
| 21 | `db_r_b` | formula | `dp_r_b * cos(pressure_angle)` | dp_r_b, pressure_angle | high | computed by the code: dp_r_b * cos(pressure_angle) |
| 22 | `alpha_r_b` | formula | `(dp_r_b ** 2 - db_r_b ** 2) ** 0.5 / db_r_b * 180 / pi - pressure_angle_deg` | pressure_angle_deg, db_r_b, dp_r_b | high | computed by the code: (dp_r_b ** 2 - db_r_b ** 2) ** 0.5 / db_r_b * 180 / pi - pressure_angle_deg |
| 23 | `beta_r_b` | formula | `(360 / (4 * Nr_b) + alpha_r_b) * 2` | alpha_r_b, Nr_b | high | computed by the code: (360 / (4 * Nr_b) + alpha_r_b) * 2 |
| 24 | `fw_r_b` | stress rule | b1 = FOS x |Ft_sp_big| x qe x qk / (gear_allowable_stress x module) (sun - big planet), b2 = the same with |Ft_rp_big| on the big planet - big ring mesh; big-planet width = max(b1, b2) (the big ring takes b2); the small planet takes b3 = FOS x |Ft_rp_small| x qe x qk / (gear_allowable_stress x module_s); if the big and small planets together are below 2 x planet_bearing_width + planet_bearing_gap, each is raised to at least planet_bearing_width + planet_bearing_gap / 2 (the rings take the planets' widths); Ft_sp_big, Ft_rp_big, Ft_rp_small = serviceFactor x motor_peak_torque / (num_planet x pitch radius) with the Wolfrom force ratios (the code takes their absolute values: Ft_rp_small is negative); qe = 1 / contact ratio of the mesh, qk = curve fit in the tooth count of the mesh; then the planet stack (big ring + small ring + clearance_planet) is capped at planet_stack_stator_heights x stator_height: when it is longer, all five widths are scaled by (cap - clearance_planet) / stack, so the capped gears carry the same fraction of the torque; fw_r_b = the big width (scaled) | module, module_s, Ns, Np_b, Np_s, Nr_b, Nr_s, num_planet, pressure_angle, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor, planet_bearing_width, planet_bearing_gap, planet_stack_stator_heights, stator_height, clearance_planet | high | big-ring face width from the tooth-stress rule (the larger of the planet's two meshes), raised to hold the planet bearing and scaled by the planet-stack cap; the big planet's width fw_p_b is a copy of it (the reverse of WPG) |
| 25 | `dp_r_s` | formula | `module * Nr_s` | module, Nr_s | high | small-ring pitch diameter, drawn with the CAD file's single module (the small gears' own module is module_s, which the CAD file does not carry; same pattern as CPG bug 18) |
| 26 | `db_r_s` | formula | `dp_r_s * cos(pressure_angle)` | dp_r_s, pressure_angle | high | computed by the code: dp_r_s * cos(pressure_angle) |
| 27 | `alpha_r_s` | formula | `(dp_r_s ** 2 - db_r_s ** 2) ** 0.5 / db_r_s * 180 / pi - pressure_angle_deg` | pressure_angle_deg, db_r_s, dp_r_s | high | computed by the code: (dp_r_s ** 2 - db_r_s ** 2) ** 0.5 / db_r_s * 180 / pi - pressure_angle_deg |
| 28 | `beta_r_s` | formula | `(360 / (4 * Nr_s) + alpha_r_s) * 2` | alpha_r_s, Nr_s | high | computed by the code: (360 / (4 * Nr_s) + alpha_r_s) * 2 |
| 29 | `fw_r_s` | stress rule | b3 = FOS x |Ft_rp_small| x qe x qk / (gear_allowable_stress x module_s) on the small planet - small ring mesh; if the big and small planets together are below 2 x planet_bearing_width + planet_bearing_gap, each is raised to at least planet_bearing_width + planet_bearing_gap / 2 (the rings take the planets' widths); Ft_sp_big, Ft_rp_big, Ft_rp_small = serviceFactor x motor_peak_torque / (num_planet x pitch radius) with the Wolfrom force ratios (the code takes their absolute values: Ft_rp_small is negative); qe = 1 / contact ratio of the mesh, qk = curve fit in the tooth count of the mesh; then the planet stack (big ring + small ring + clearance_planet) is capped at planet_stack_stator_heights x stator_height: when it is longer, all five widths are scaled by (cap - clearance_planet) / stack, so the capped gears carry the same fraction of the torque; fw_r_s = the small width (scaled) | module, module_s, Ns, Np_b, Np_s, Nr_b, Nr_s, num_planet, pressure_angle, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor, planet_bearing_width, planet_bearing_gap, planet_stack_stator_heights, stator_height, clearance_planet | high | small-ring face width from the tooth-stress rule, raised to hold the planet bearing and scaled by the planet-stack cap; the small planet's width fw_p_s is this plus clearance_planet; it uses the small module, which the CAD file does not carry |
| 30 | `dp_p_s` | formula | `module * Np_s` | module, Np_s | high | small-planet pitch diameter, drawn with the CAD file's single module (the small gears' own module is module_s, which the CAD file does not carry; same pattern as CPG bug 18) |
| 31 | `db_p_s` | formula | `dp_p_s * cos(pressure_angle)` | dp_p_s, pressure_angle | high | base-circle diameter |
| 32 | `alpha_p_s` | formula | `(dp_p_s ** 2 - db_p_s ** 2) ** 0.5 / db_p_s * 180 / pi - pressure_angle_deg` | pressure_angle_deg, db_p_s, dp_p_s | high | involute angle used to draw the tooth |
| 33 | `beta_p_s` | formula | `(360 / (4 * Np_s) - alpha_p_s) * 2` | alpha_p_s, Np_s | high | tooth angle used to draw the tooth |
| 34 | `fw_p_s` | formula | `fw_r_s + clearance_planet` | fw_r_s, clearance_planet | high | small-planet width: the ring width plus a clearance (a formula, not the stress rule) |
| 35 | `motor_mount_driver_nut_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=motor_mount_driver_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | motor_mount_driver_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 36 | `motor_mount_driver_nut_depth` | lookup | `nuts_and_bolts_dimensions(bolt_dia=motor_mount_driver_hole_dia, bolt_type=socket_head)` → nut_thickness | motor_mount_driver_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 37 | `planet_pin_socket_head_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=planet_pin_bolt_dia, bolt_type=socket_head)` → bolt_head_dia | planet_pin_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 38 | `planet_pin_nut_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=planet_pin_bolt_dia, bolt_type=socket_head)` → nut_width_across_flats | planet_pin_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 39 | `planet_pin_nut_depth` | lookup | `nuts_and_bolts_dimensions(bolt_dia=planet_pin_bolt_dia, bolt_type=socket_head)` → nut_thickness | planet_pin_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 40 | `sun_central_bolt_socket_head_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=sun_central_bolt_dia, bolt_type=socket_head)` → bolt_head_dia | sun_central_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 41 | `rotor_hub_sun_hole_CSK_OD` | lookup | `nuts_and_bolts_dimensions(bolt_dia=rotor_hub_sun_hole_dia, bolt_type=CSK)` → bolt_head_dia | rotor_hub_sun_hole_dia | high | standard countersunk fastener size for the chosen bolt diameter |
| 42 | `rotor_hub_sun_hole_CSK_head_height` | lookup | `nuts_and_bolts_dimensions(bolt_dia=rotor_hub_sun_hole_dia, bolt_type=CSK)` → bolt_head_height | rotor_hub_sun_hole_dia | high | standard countersunk fastener size for the chosen bolt diameter |
| 43 | `sun_hub_dia` | formula | `rotor_top_bearing_ID - 2 * rotor_hub_thickness` | rotor_top_bearing_ID, rotor_hub_thickness | high | sun coupler hub, sized to the motor's output holes |
| 44 | `output_bearing_ID` | lookup | `bearings_discrete(idRequiredMM=module * Nr_s + 2 * module + 2 * small_ring_radial_width)` → getBearingIDMM | small_ring_radial_width, module, Nr_s | high | catalogue bearing chosen by bearings_discrete for the bore the design needs (smallest one that fits); this is its bore |
| 45 | `output_bearing_OD` | lookup | `bearings_discrete(idRequiredMM=module * Nr_s + 2 * module + 2 * small_ring_radial_width)` → getBearingODMM | small_ring_radial_width, module, Nr_s | high | catalogue bearing chosen by bearings_discrete for the bore the design needs (smallest one that fits); this is its outer diameter |
| 46 | `output_bearing_width` | lookup | `bearings_discrete(idRequiredMM=module * Nr_s + 2 * module + 2 * small_ring_radial_width)` → getBearingWidthMM | small_ring_radial_width, module, Nr_s | high | catalogue bearing chosen by bearings_discrete for the bore the design needs (smallest one that fits); this is its width |
| 47 | `carrier_trapezoidal_support_hole_socket_head_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=carrier_trapezoidal_support_hole_dia, bolt_type=socket_head)` → bolt_head_dia | carrier_trapezoidal_support_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 48 | `carrier_trapezoidal_support_hole_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=carrier_trapezoidal_support_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | carrier_trapezoidal_support_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 49 | `carrier_trapezoidal_support_nut_depth` | lookup | `nuts_and_bolts_dimensions(bolt_dia=carrier_trapezoidal_support_hole_dia, bolt_type=socket_head)` → nut_thickness | carrier_trapezoidal_support_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 50 | `stator_hole_nut_depth` | lookup | `nuts_and_bolts_dimensions(bolt_dia=stator_hole_dia, bolt_type=socket_head)` → nut_thickness | stator_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 51 | `stator_hole_nut_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=stator_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | stator_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 52 | `stator_hole_allen_socket_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=stator_hole_dia, bolt_type=socket_head)` → bolt_head_dia | stator_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 53 | `case_mounting_hole_allen_socket_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=case_mounting_hole_dia, bolt_type=socket_head)` → bolt_head_dia | case_mounting_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 54 | `case_mounting_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=case_mounting_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | case_mounting_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 55 | `case_mounting_nut_depth` | lookup | `nuts_and_bolts_dimensions(bolt_dia=case_mounting_hole_dia, bolt_type=socket_head)` → nut_thickness | case_mounting_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 56 | `output_mount_nut_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=output_mount_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | output_mount_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 57 | `output_mount_hole_nut_depth` | lookup | `nuts_and_bolts_dimensions(bolt_dia=output_mount_hole_dia, bolt_type=socket_head)` → nut_thickness | output_mount_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 58 | `actuactor_mount_nut_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=actuactor_mount_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | actuactor_mount_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 59 | `actuactor_mount_nut_depth` | lookup | `nuts_and_bolts_dimensions(bolt_dia=actuactor_mount_hole_dia, bolt_type=socket_head)` → nut_thickness | actuactor_mount_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 60 | `case_mounting_hole_shift` | formula | `case_mounting_hole_dia / 2` | case_mounting_hole_dia | high | how far the case bolt circle sits outside the case wall: half the bolt hole, less the configured overlap |
| 61 | `fw_s_used` | formula | `bearing_step_width + rotor_top_bearing_width - sun_coupler_hub_thickness + bearing_step_width + standard_clearance_1_5mm + sec_carrier_thickness + clearance_planet + fw_p_b + fw_p_s` | fw_p_s, fw_p_b, clearance_planet, sec_carrier_thickness, standard_clearance_1_5mm, bearing_step_width, sun_coupler_hub_thickness, rotor_top_bearing_width | high | printed sun length: planet width plus the carrier and clearances |
| 62 | `rotor_top_bearing_holder_thickness` | formula | `bearing_step_width + rotor_top_bearing_width - (standard_clearance_1_5mm / 2 + stator_top_height + stator_mid_height - rotor_height - bearing_step_width)` | bearing_step_width, rotor_top_bearing_width, rotor_height, stator_mid_height, stator_top_height, standard_clearance_1_5mm | high | computed by the code: bearing_step_width + rotor_top_bearing_width - (standard_clearance_1_5mm / 2 + stator_top_height + stator_mid_height - rotor_height - bearing_step_width) |

## Used by the code, not written to the CAD file (26)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `module_s` | module | optimiser (`optimizationInrunnerWolfromPlanetaryActuator`) |  | high | the small module (small planet, small ring): searched by the optimiser loop and used by the stress rule and the gearbox constraints, but not in the CAD file, which has one module (same pattern as CPG bug 18) |
| 2 | `motor_peak_torque` | motor | motors.json → motors.<motor>.electrical → `peak_torque_Nm` |  | high | motor torque the gears are sized for (peak torque under the default rating setting); sets the face widths |
| 3 | `gear_allowable_stress` | material | config.json → Material_properties.<gear material> → `maxAllowableStressMPa` |  | high | allowable tooth stress of the gear material, chosen with the material mode (3dp: PLA, metal: steel); sets the face widths |
| 4 | `FOS` | safety factor | config.json → MIT_params → `FOS` |  | high | factor of safety in the tooth-stress rule |
| 5 | `serviceFactor` | safety factor | config.json → MIT_params → `serviceFactor` |  | high | service factor on the motor torque in the tooth-stress rule |
| 6 | `planet_bearing_gap` | clearance | inwpg_params_independent.json → inwpg_3DP_design_parameters → `planet_bearing_gap` |  | high | axial gap between the two planet bearings (one in each planet gear); with the bearing width it sets the smallest planet and ring widths |
| 7 | `maxGearboxDiameter` | formula | `MAX_GB_DIA_MULT_FACTOR * motor_OD` | MAX_GB_DIA_MULT_FACTOR, motor_OD | high | largest gearbox diameter the optimiser may use (gearbox_runner max_diameter): the stator's outer diameter times a factor |
| 8 | `actuator_width` | formula | `motor_case_thickness + motor_height + standard_clearance_1_5mm + sec_carrier_thickness + clearance_planet + fw_p_b + fw_p_s + clearance_planet + bearing_step_width + output_bearing_width` | output_bearing_width, bearing_step_width, clearance_planet, fw_p_s, fw_p_b, sec_carrier_thickness, standard_clearance_1_5mm, motor_case_thickness, motor_height | high | axial width without the driver mount, written to the results CSV |
| 9 | `planet_stack_stator_heights` | constraint constant | inwpg_params_independent.json → inwpg_3DP_design_parameters → `planet_stack_stator_heights` |  | high | width cap: the planet stack (big ring + small ring + clearance_planet) is limited to this many stator heights; read in mitStressAnalysisMinFacewidth, not written to the CAD file |
| 10 | `fw_limit_mm` | formula | `planet_stack_stator_heights * stator_height` | planet_stack_stator_heights, stator_height | high | the longest planet stack the stress rule allows: the cap in stator heights times the motor's stator height |
| 11 | `planetMinDistanceMM` | constraint constant | inwpg_params_independent.json → inwpg_3DP_design_parameters → `planetMinDistanceMM` |  | high | read by the code but not written to the CAD file |
| 12 | `sCarrierExtrusionDiaMM` | constraint constant | inwpg_params_independent.json → inwpg_3DP_design_parameters → `sCarrierExtrusionDiaMM` |  | high | read by the code but not written to the CAD file |
| 13 | `sCarrierExtrusionClearanceMM` | constraint constant | inwpg_params_independent.json → inwpg_3DP_design_parameters → `sCarrierExtrusionClearanceMM` |  | high | read by the code but not written to the CAD file |
| 14 | `GEAR_RATIO_MIN` | search bound | inwpg_params_independent.json → inwpg_optimization_parameters → `GEAR_RATIO_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 15 | `GEAR_RATIO_MAX` | search bound | inwpg_params_independent.json → inwpg_optimization_parameters → `GEAR_RATIO_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 16 | `GEAR_RATIO_STEP` | search bound | inwpg_params_independent.json → inwpg_optimization_parameters → `GEAR_RATIO_STEP` |  | high | optimiser setting: limits of the search, not a part dimension |
| 17 | `MODULE_BIG_MIN` | search bound | inwpg_params_independent.json → inwpg_optimization_parameters → `MODULE_BIG_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 18 | `MODULE_BIG_MAX` | search bound | inwpg_params_independent.json → inwpg_optimization_parameters → `MODULE_BIG_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 19 | `MODULE_SMALL_MIN` | search bound | inwpg_params_independent.json → inwpg_optimization_parameters → `MODULE_SMALL_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 20 | `MODULE_SMALL_MAX` | search bound | inwpg_params_independent.json → inwpg_optimization_parameters → `MODULE_SMALL_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 21 | `NUM_PLANET_MIN` | search bound | inwpg_params_independent.json → inwpg_optimization_parameters → `NUM_PLANET_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 22 | `NUM_PLANET_MAX` | search bound | inwpg_params_independent.json → inwpg_optimization_parameters → `NUM_PLANET_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 23 | `NUM_TEETH_SUN_MIN` | search bound | inwpg_params_independent.json → inwpg_optimization_parameters → `NUM_TEETH_SUN_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 24 | `NUM_TEETH_PLANET_BIG_MIN` | search bound | inwpg_params_independent.json → inwpg_optimization_parameters → `NUM_TEETH_PLANET_BIG_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 25 | `NUM_TEETH_PLANET_SMALL_MIN` | search bound | inwpg_params_independent.json → inwpg_optimization_parameters → `NUM_TEETH_PLANET_SMALL_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 26 | `MAX_GB_DIA_MULT_FACTOR` | search bound | inwpg_params_independent.json → inwpg_optimization_parameters → `MAX_GB_DIA_MULT_FACTOR` |  | high | optimiser setting: limits of the search, not a part dimension |

## Config blocks INWPG_INDEPENDENT doesn't read

