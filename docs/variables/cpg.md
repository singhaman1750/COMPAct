# CPG variables by category

Generated from `config_files/variables/cpg_variables.json` by `python tools/variables/render.py`; edit the JSON, not this page.

Every CPG variable sorted into input / optimisation / fixed / dependent. 'cad_variables' are the 119 variables CPG writes to CADs/CPG/cpg_equations_onshape.txt, in that order; 'code_only' are values the code uses but does not write to the CAD file (including the small module module_s: the CAD file has one module); 'unused_config_blocks' are config blocks CPG never reads. tests/test_variable_categories.py checks the lists against the code and re-evaluates every formula and lookup; docs/variables/cpg.md is generated from this file (python tools/variables/render.py).

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
| Input | 18 | 2 |
| Optimisation | 5 | 1 |
| Fixed | 42 | 24 |
| Dependent | 54 | 4 |
| **Total** | **119** | **31** |

CAD variables by confidence: high 119, medium 0, low 0

## Rules shared by every gearbox

From `config_files/variables/rules.json`; the test holds every gearbox's file to them.

- names matching `^(a[12]_)?Nr[0-9]*$` are **Dependent / implicit constraint**: ring-gear teeth are implicitly constrained: the coaxial geometric constraint (e.g. Nr = Ns + 2 x Np) fixes them once the sun and planet teeth are chosen, so the optimiser sets them instead of searching them
- names matching `^fw_(s_calc|p|p_b|r)$` are **Dependent / stress rule**: gear face widths follow from the tooth-stress rule: the optimisation variables, the motor torque, the gear material and the safety factors fix them, and the optimiser always takes the smallest width that passes (widths that are a formula of another width, e.g. CPG's fw_p_s = fw_r + clearance_planet, are dependent / formula)
- names matching `^a[12]_fw_(s_calc|r)[12]?$` are **Dependent / stress rule**: the same stress-rule face widths in a two-stage gearbox, under the stage prefixes a1_ / a2_ (the planet width a1_fw_p / a2_fw_p is a copy of the ring width, so it is dependent / formula and not in this rule)

## Input (18)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `motor_OD` | motor | motors.json → motors.<motor>.geometry → `motorDia` |  | high | read from the chosen motor's geometry |
| 2 | `motor_height` | motor | motors.json → motors.<motor>.geometry → `motorLength` |  | high | read from the chosen motor's geometry |
| 3 | `motor_mount_hole_PCD` | motor | motors.json → motors.<motor>.geometry → `motor_mount_hole_PCD` |  | high | read from the chosen motor's geometry |
| 4 | `motor_mount_hole_dia` | motor | motors.json → motors.<motor>.geometry → `motor_mount_hole_dia` |  | high | read from the chosen motor's geometry |
| 5 | `motor_mount_hole_num` | motor | motors.json → motors.<motor>.geometry → `motor_mount_hole_num` |  | high | read from the chosen motor's geometry |
| 6 | `wire_slot_dist_from_center` | motor | motors.json → motors.<motor>.geometry → `wire_slot_dist_from_center` |  | high | read from the chosen motor's geometry |
| 7 | `wire_slot_length` | motor | motors.json → motors.<motor>.geometry → `wire_slot_length` |  | high | read from the chosen motor's geometry |
| 8 | `wire_slot_radius` | motor | motors.json → motors.<motor>.geometry → `wire_slot_radius` |  | high | read from the chosen motor's geometry |
| 9 | `driver_upper_holes_dist_from_center` | driver | config.json → Motor_drivers.OdrivePro → `driver_upper_holes_dist_from_center` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 10 | `driver_lower_holes_dist_from_center` | driver | config.json → Motor_drivers.OdrivePro → `driver_lower_holes_dist_from_center` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 11 | `driver_side_holes_dist_from_center` | driver | config.json → Motor_drivers.OdrivePro → `driver_side_holes_dist_from_center` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 12 | `driver_mount_holes_dia` | driver | config.json → Motor_drivers.OdrivePro → `driver_mount_holes_dia` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 13 | `driver_mount_inserts_OD` | driver | config.json → Motor_drivers.OdrivePro → `driver_mount_inserts_OD` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 14 | `driver_mount_thickness` | driver | config.json → Motor_drivers.OdrivePro → `driver_mount_thickness` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 15 | `driver_mount_height` | driver | config.json → Motor_drivers.OdrivePro → `driver_mount_height` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 16 | `motor_output_hole_PCD` | motor | motors.json → motors.<motor>.geometry → `motor_output_hole_PCD` |  | high | read from the chosen motor's geometry |
| 17 | `motor_output_hole_dia` | motor | motors.json → motors.<motor>.geometry → `motor_output_hole_dia` |  | high | read from the chosen motor's geometry |
| 18 | `motor_output_hole_num` | motor | motors.json → motors.<motor>.geometry → `motor_output_hole_num` |  | high | read from the chosen motor's geometry |

## Optimisation (5)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `Ns` | teeth | optimiser (`optimizationCompoundPlanetaryActuator`) |  | high | sun teeth: searched by the optimiser loop |
| 2 | `Np_b` | teeth | optimiser (`optimizationCompoundPlanetaryActuator`) |  | high | big-planet teeth: searched by the optimiser loop |
| 3 | `Np_s` | teeth | optimiser (`optimizationCompoundPlanetaryActuator`) |  | high | small-planet teeth: searched by the optimiser loop |
| 4 | `num_planet` | planets | optimiser (`optimizationCompoundPlanetaryActuator`) |  | high | searched by the optimiser loop (NUM_PLANET_MIN..MAX) |
| 5 | `module` | module | optimiser (`optimizationCompoundPlanetaryActuator`) |  | high | the big module (sun, big planet): searched by the optimiser loop; the CAD file has this one module (code attribute module_b; the small module is module_s, code-only) |

## Fixed (42)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `pressure_angle` | gear standard | config.json → Gear_standard_parameters → `pressureAngleDEG` |  | high | gear standard, the same for every gearbox type |
| 2 | `clearance_planet` | clearance | cpg_params.json → cpg_3DP_design_parameters → `clearance_planet` |  | high | constant from the SSPG 3DP design parameters |
| 3 | `case_mounting_hole_dia` | fastener size | cpg_params.json → cpg_3DP_design_parameters → `case_mounting_hole_dia` |  | high | constant from the SSPG 3DP design parameters |
| 4 | `output_mounting_hole_dia` | fastener size | cpg_params.json → cpg_3DP_design_parameters → `output_mounting_hole_dia` |  | high | constant from the SSPG 3DP design parameters |
| 5 | `clearance_case_mount_holes_shell_thickness` | clearance | cpg_params.json → cpg_3DP_design_parameters → `clearance_case_mount_holes_shell_thickness` |  | high | constant from the SSPG 3DP design parameters |
| 6 | `sec_carrier_thickness` | wall thickness | cpg_params.json → cpg_3DP_design_parameters → `sec_carrier_thickness` |  | high | constant from the SSPG 3DP design parameters |
| 7 | `sun_coupler_hub_thickness` | wall thickness | cpg_params.json → cpg_3DP_design_parameters → `sun_coupler_hub_thickness` |  | high | constant from the SSPG 3DP design parameters |
| 8 | `clearance_sun_coupler_sec_carrier` | clearance | cpg_params.json → cpg_3DP_design_parameters → `clearance_sun_coupler_sec_carrier` |  | high | constant from the SSPG 3DP design parameters |
| 9 | `Motor_case_thickness` | wall thickness | cpg_params.json → cpg_3DP_design_parameters → `Motor_case_thickness` |  | high | constant from the SSPG 3DP design parameters |
| 10 | `output_mounting_nut_depth` | fastener size | cpg_params.json → cpg_3DP_design_parameters → `output_mounting_nut_depth` |  | high | constant from the SSPG 3DP design parameters |
| 11 | `case_mounting_bolt_depth` | fastener size | cpg_params.json → cpg_3DP_design_parameters → `case_mounting_bolt_depth` |  | high | constant from the SSPG 3DP design parameters |
| 12 | `ring_to_chamfer_clearance` | clearance | cpg_params.json → cpg_3DP_design_parameters → `ring_to_chamfer_clearance` |  | high | constant from the SSPG 3DP design parameters |
| 13 | `Motor_case_OD_base_to_chamfer` | feature size | cpg_params.json → cpg_3DP_design_parameters → `Motor_case_OD_base_to_chamfer` |  | high | constant from the SSPG 3DP design parameters |
| 14 | `pattern_offset_from_motor_case_OD_base` | feature size | cpg_params.json → cpg_3DP_design_parameters → `pattern_offset_from_motor_case_OD_base` |  | high | constant for the decorative/grip pattern on the case |
| 15 | `pattern_bulge_dia` | feature size | cpg_params.json → cpg_3DP_design_parameters → `pattern_bulge_dia` |  | high | constant for the decorative/grip pattern on the case |
| 16 | `pattern_num_bulge` | feature size | cpg_params.json → cpg_3DP_design_parameters → `pattern_num_bulge` |  | high | constant for the decorative/grip pattern on the case |
| 17 | `pattern_depth` | feature size | cpg_params.json → cpg_3DP_design_parameters → `pattern_depth` |  | high | constant for the decorative/grip pattern on the case |
| 18 | `case_mounting_nut_clearance` | clearance | cpg_params.json → cpg_3DP_design_parameters → `case_mounting_nut_clearance` |  | high | constant from the SSPG 3DP design parameters |
| 19 | `base_plate_thickness` | wall thickness | cpg_params.json → cpg_3DP_design_parameters → `base_plate_thickness` |  | high | constant from the SSPG 3DP design parameters |
| 20 | `case_mounting_surface_height` | wall thickness | cpg_params.json → cpg_3DP_design_parameters → `case_mounting_surface_height` |  | high | constant from the SSPG 3DP design parameters |
| 21 | `central_hole_offset_from_motor_mount_PCD` | feature size | cpg_params.json → cpg_3DP_design_parameters → `central_hole_offset_from_motor_mount_PCD` |  | high | constant from the SSPG 3DP design parameters |
| 22 | `air_flow_hole_offset` | feature size | cpg_params.json → cpg_3DP_design_parameters → `air_flow_hole_offset` |  | high | constant from the SSPG 3DP design parameters |
| 23 | `planet_pin_bolt_dia` | fastener size | cpg_params.json → cpg_3DP_design_parameters → `planet_pin_bolt_dia` |  | high | constant from the SSPG 3DP design parameters |
| 24 | `planet_shaft_dia` | planet part | cpg_params.json → cpg_3DP_design_parameters → `planet_shaft_dia` |  | high | constant from the SSPG 3DP design parameters |
| 25 | `planet_shaft_step_offset` | planet part | cpg_params.json → cpg_3DP_design_parameters → `planet_shaft_step_offset` |  | high | constant from the SSPG 3DP design parameters |
| 26 | `carrier_trapezoidal_support_sun_offset` | feature size | cpg_params.json → cpg_3DP_design_parameters → `carrier_trapezoidal_support_sun_offset` |  | high | constant from the SSPG 3DP design parameters |
| 27 | `carrier_trapezoidal_support_hole_PCD_offset_bearing_ID` | feature size | cpg_params.json → cpg_3DP_design_parameters → `carrier_trapezoidal_support_hole_PCD_offset_bearing_ID` |  | high | constant from the SSPG 3DP design parameters |
| 28 | `carrier_trapezoidal_support_hole_dia` | fastener size | cpg_params.json → cpg_3DP_design_parameters → `carrier_trapezoidal_support_hole_dia` |  | high | constant from the SSPG 3DP design parameters |
| 29 | `carrier_bearing_step_width` | feature size | cpg_params.json → cpg_3DP_design_parameters → `carrier_bearing_step_width` |  | high | constant from the SSPG 3DP design parameters |
| 30 | `standard_clearance_1_5mm` | clearance | cpg_params.json → cpg_3DP_design_parameters → `standard_clearance_1_5mm` |  | high | constant from the SSPG 3DP design parameters |
| 31 | `standard_fillet_1_5mm` | feature size | cpg_params.json → cpg_3DP_design_parameters → `standard_fillet_1_5mm` |  | high | constant from the SSPG 3DP design parameters |
| 32 | `sun_shaft_bearing_OD` | bearing (chosen part) | cpg_params.json → cpg_3DP_design_parameters → `sun_shaft_bearing_OD` |  | high | constant from the SSPG 3DP design parameters |
| 33 | `sun_shaft_bearing_width` | bearing (chosen part) | cpg_params.json → cpg_3DP_design_parameters → `sun_shaft_bearing_width` |  | high | constant from the SSPG 3DP design parameters |
| 34 | `standard_bearing_insertion_chamfer` | feature size | cpg_params.json → cpg_3DP_design_parameters → `standard_bearing_insertion_chamfer` |  | high | constant from the SSPG 3DP design parameters |
| 35 | `planet_bearing_OD` | bearing (chosen part) | cpg_params.json → cpg_3DP_design_parameters → `planet_bearing_OD` |  | high | constant from the SSPG 3DP design parameters |
| 36 | `planet_bearing_width` | bearing (chosen part) | cpg_params.json → cpg_3DP_design_parameters → `planet_bearing_width` |  | high | constant from the SSPG 3DP design parameters |
| 37 | `planet_bore` | planet part | cpg_params.json → cpg_3DP_design_parameters → `planet_bore` |  | high | constant planet bore from the SSPG 3DP design parameters |
| 38 | `sun_shaft_bearing_ID` | bearing (chosen part) | cpg_params.json → cpg_3DP_design_parameters → `sun_shaft_bearing_ID` |  | high | constant from the SSPG 3DP design parameters |
| 39 | `sun_central_bolt_dia` | fastener size | cpg_params.json → cpg_3DP_design_parameters → `sun_central_bolt_dia` |  | high | constant from the SSPG 3DP design parameters |
| 40 | `bearing_retainer_thickness` | wall thickness | cpg_params.json → cpg_3DP_design_parameters → `bearing_retainer_thickness` |  | high | constant from the SSPG 3DP design parameters |
| 41 | `tight_clearance_3DP` | clearance | cpg_params.json → cpg_3DP_design_parameters → `tight_clearance_3DP` |  | high | 3D-printing fit clearance from the SSPG 3DP design parameters |
| 42 | `loose_clearance_3DP` | clearance | cpg_params.json → cpg_3DP_design_parameters → `loose_clearance_3DP` |  | high | 3D-printing fit clearance from the SSPG 3DP design parameters |

## Dependent (54)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `Nr` | implicit constraint | `Ns + Np_b + Np_s` | Ns, Np_b, Np_s | high | implicitly constrained: with equal modules the coaxial constraint (Ns + Np_b) x module = (Nr - Np_s) x module_s gives Nr = Ns + Np_b + Np_s, which the code writes (the code lists it among the optimisation variables) |
| 2 | `h_a` | formula | `1 * module` | module | high | addendum, standard proportion of the module |
| 3 | `h_b` | formula | `1.25 * module` | module | high | standard proportion of the module (same value as h_f) |
| 4 | `clr_tip_root` | formula | `h_f - h_a` | h_f, h_a | high | tip-root clearance from addendum and dedendum |
| 5 | `dp_s` | formula | `module * Ns` | module, Ns | high | pitch diameter |
| 6 | `db_s` | formula | `dp_s * cos(pressure_angle_rad)` | dp_s, pressure_angle_rad | high | base-circle diameter |
| 7 | `fw_s_calc` | stress rule | two stress widths, b = FOS x Ft x qe x qk / (gear_allowable_stress x module): b1 for the sun - big planet mesh (module, Ft from serviceFactor x motor_peak_torque at the sun, qe from the sun-planet contact ratio, qk from Ns) and b2 for the small planet - ring mesh (module_s, qk from Np_s); then, if b1 + b2 < 2 x planet_bearing_width + planet_bearing_gap, each planet gear is raised to at least planet_bearing_width + planet_bearing_gap / 2 (one bearing per gear, half the gap each; mitStressAnalysisMinFacewidth); fw_s_calc = b1 | module, module_s, Ns, Np_b, Np_s, Nr, num_planet, pressure_angle, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor | high | sun face width from the tooth-stress rule of the sun - big planet mesh (b1): fixed by the optimisation variables, the motor torque, the gear material and the safety factors. The printed sun uses fw_s_used |
| 8 | `alpha_s` | formula | `(sqrt(dp_s**2 - db_s**2) / db_s) * 180 / pi - pressure_angle_rad * 180 / pi` | dp_s, db_s, pressure_angle_rad | high | involute angle used to draw the tooth |
| 9 | `beta_s` | formula | `(360 / (4 * Ns) - alpha_s) * 2` | Ns, alpha_s | high | tooth angle used to draw the tooth |
| 10 | `dp_p_b` | formula | `module * Np_b` | module, Np_b | high | big-planet pitch diameter |
| 11 | `db_p_b` | formula | `dp_p_b * cos(pressure_angle_rad)` | dp_p_b, pressure_angle_rad | high | base-circle diameter |
| 12 | `fw_p_s` | formula | `fw_r + clearance_planet` | fw_r, clearance_planet | high | small-planet width: the ring width plus a clearance (a formula, not the stress rule) |
| 13 | `alpha_p_b` | formula | `(sqrt(dp_p_b**2 - db_p_b**2) / db_p_b) * 180 / pi - pressure_angle_rad * 180 / pi` | dp_p_b, db_p_b, pressure_angle_rad | high | involute angle used to draw the tooth |
| 14 | `beta_p_b` | formula | `(360 / (4 * Np_b) - alpha_p_b) * 2` | Np_b, alpha_p_b | high | tooth angle used to draw the tooth |
| 15 | `h_f` | formula | `1.25 * module` | module | high | dedendum, standard proportion of the module |
| 16 | `dp_r` | formula | `module_s * Nr` | module_s, Nr | high | ring pitch diameter (small module) |
| 17 | `db_r` | formula | `dp_r * cos(pressure_angle_rad)` | dp_r, pressure_angle_rad | high | base-circle diameter |
| 18 | `fw_r` | stress rule | two stress widths, b = FOS x Ft x qe x qk / (gear_allowable_stress x module): b1 for the sun - big planet mesh (module, Ft from serviceFactor x motor_peak_torque at the sun, qe from the sun-planet contact ratio, qk from Ns) and b2 for the small planet - ring mesh (module_s, qk from Np_s); then, if b1 + b2 < 2 x planet_bearing_width + planet_bearing_gap, each planet gear is raised to at least planet_bearing_width + planet_bearing_gap / 2 (one bearing per gear, half the gap each; mitStressAnalysisMinFacewidth); fw_r = b2 (raised) | module, module_s, Ns, Np_b, Np_s, Nr, num_planet, pressure_angle, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor, planet_bearing_width, planet_bearing_gap | high | ring width = small-planet stress width (b2, raised to the planet-bearing minimum like fw_p_b) |
| 19 | `alpha_r` | formula | `(sqrt(dp_r**2 - db_r**2) / db_r) * 180 / pi - pressure_angle_rad * 180 / pi` | dp_r, db_r, pressure_angle_rad | high | involute angle used to draw the tooth |
| 20 | `beta_r` | formula | `(360 / (4 * Nr) + alpha_r) * 2` | Nr, alpha_r | high | tooth angle used to draw the tooth |
| 21 | `bearing_ID` | lookup | `bearings_discrete(idRequiredMM=module * (Ns + Np_b) + bearingIDClearanceMM)` → getBearingIDMM | module, Ns, Np_b, bearingIDClearanceMM | high | smallest catalogue bearing whose bore fits around the sun and big planets (bearings_discrete) |
| 22 | `bearing_OD` | lookup | `bearings_discrete(idRequiredMM=module * (Ns + Np_b) + bearingIDClearanceMM)` → getBearingODMM | module, Ns, Np_b, bearingIDClearanceMM | high | smallest catalogue bearing whose bore fits around the sun and big planets (bearings_discrete) |
| 23 | `bearing_height` | lookup | `bearings_discrete(idRequiredMM=module * (Ns + Np_b) + bearingIDClearanceMM)` → getBearingWidthMM | module, Ns, Np_b, bearingIDClearanceMM | high | smallest catalogue bearing whose bore fits around the sun and big planets (bearings_discrete) |
| 24 | `case_dist` | formula | `sec_carrier_thickness + clearance_planet * 2 + sun_coupler_hub_thickness + fw_p_b - case_mounting_surface_height` | sec_carrier_thickness, clearance_planet, sun_coupler_hub_thickness, fw_p_b, case_mounting_surface_height | high | axial gap between the motor case and the gearbox case (includes the big-planet width) |
| 25 | `Motor_case_OD_max` | formula | `case_mounting_PCD + case_mounting_hole_allen_socket_dia + clearance_case_mount_holes_shell_thickness * 2` | case_mounting_PCD, case_mounting_hole_allen_socket_dia, clearance_case_mount_holes_shell_thickness | high | widest diameter, over the case mounting ears |
| 26 | `case_mounting_PCD` | formula | `motor_case_OD_base + case_mounting_hole_shift * 2` | motor_case_OD_base, case_mounting_hole_shift | high | case bolt circle |
| 27 | `bearing_mount_thickness` | formula | `output_mounting_hole_dia * bearing_mount_wall_bolt_dia_multiple if bearing_OD + output_mounting_hole_dia * (2 * bearing_mount_wall_bolt_dia_multiple) > Nr * module_s + 2 * h_b_s else ((Nr * module_s + 2 * h_b_s) - (bearing_OD + output_mounting_hole_dia * (2 * bearing_mount_wall_bolt_dia_multiple))) / 2 + output_mounting_hole_dia * bearing_mount_wall_bolt_dia_multiple + standard_clearance_1_5mm` | output_mounting_hole_dia, bearing_mount_wall_bolt_dia_multiple, bearing_OD, Nr, module_s, h_b_s, standard_clearance_1_5mm | high | wall around the output bearing: the configured number of output-bolt diameters on each side, or wider (plus a clearance) when the ring gear's teeth reach further out (the same rule is used for the mass) |
| 28 | `output_mounting_PCD` | formula | `bearing_OD + bearing_mount_thickness` | bearing_OD, bearing_mount_thickness | high | output bolt circle |
| 29 | `motor_case_OD_base` | formula | `motor_OD + clearance_motor_and_case * 2 + Motor_case_thickness * 2` | motor_OD, clearance_motor_and_case, Motor_case_thickness | high | motor case outer diameter (body diameter) |
| 30 | `clearance_motor_and_case` | formula | `clearance_motor_and_case_min if (Ns + Np_b * 2) * module < motor_OD else ((Ns + Np_b * 2) * module - motor_OD) * 0.5 + clearance_motor_and_case_min` | Ns, Np_b, module, motor_OD, clearance_motor_and_case_min | high | radial gap between the motor and the case: the configured minimum, or more when the big planets reach wider than the motor (the same rule is used for the case mass) |
| 31 | `Motor_case_ID` | formula | `motor_OD + clearance_motor_and_case * 2` | motor_OD, clearance_motor_and_case | high | motor case inner diameter |
| 32 | `case_mounting_hole_shift` | formula | `case_mounting_hole_dia / 2 - case_mounting_hole_wall_overlap` | case_mounting_hole_dia, case_mounting_hole_wall_overlap | high | how far the case bolt circle sits outside the case wall: half the bolt hole, less the configured overlap |
| 33 | `output_mounting_nut_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=output_mounting_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | output_mounting_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 34 | `output_mounting_nut_thickness` | lookup | `nuts_and_bolts_dimensions(bolt_dia=output_mounting_hole_dia, bolt_type=socket_head)` → nut_thickness | output_mounting_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 35 | `case_mounting_hole_allen_socket_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=case_mounting_hole_dia, bolt_type=socket_head)` → bolt_head_dia | case_mounting_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 36 | `ring_radial_thickness` | formula | `ringRadialWidthMM if Nr * module_s + ringRadialWidthMM * 2 > bearing_OD else (bearing_OD + standard_clearance_1_5mm * 2 - Nr * module_s) / 2` | Nr, module_s, ringRadialWidthMM, bearing_OD, standard_clearance_1_5mm | high | ring gear wall: the configured minimum (ringRadialWidthMM), or thicker so the ring reaches the output bearing. The mass model always uses the minimum (ISSUES bug 17). In SSPG it is a fixed config value |
| 37 | `ring_OD` | formula | `Nr * module_s + ring_radial_thickness * 2` | Nr, module_s, ring_radial_thickness | high | ring gear outer diameter (small module) |
| 38 | `case_mounting_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=case_mounting_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | case_mounting_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 39 | `case_mounting_nut_thickness` | lookup | `nuts_and_bolts_dimensions(bolt_dia=case_mounting_hole_dia, bolt_type=socket_head)` → nut_thickness | case_mounting_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 40 | `planet_pin_socket_head_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=planet_pin_bolt_dia, bolt_type=socket_head)` → bolt_head_dia | planet_pin_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 41 | `carrier_PCD` | formula | `(Np_b + Ns) * module` | Np_b, Ns, module | high | planet-centre circle (twice the sun - big planet centre distance) |
| 42 | `carrier_trapezoidal_support_hole_socket_head_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=carrier_trapezoidal_support_hole_dia, bolt_type=socket_head)` → bolt_head_dia | carrier_trapezoidal_support_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 43 | `carrier_trapezoidal_support_hole_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=carrier_trapezoidal_support_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | carrier_trapezoidal_support_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 44 | `planet_pin_bolt_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=planet_pin_bolt_dia, bolt_type=socket_head)` → nut_width_across_flats | planet_pin_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 45 | `sun_hub_dia` | formula | `motor_output_hole_PCD + motor_output_hole_dia + standard_clearance_1_5mm * 4` | motor_output_hole_PCD, motor_output_hole_dia, standard_clearance_1_5mm | high | sun coupler hub, sized to the motor's output holes |
| 46 | `sun_central_bolt_socket_head_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=sun_central_bolt_dia, bolt_type=socket_head)` → bolt_head_dia | sun_central_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 47 | `fw_s_used` | formula | `fw_p_s + fw_p_b + clearance_planet + sec_carrier_thickness + standard_clearance_1_5mm` | fw_p_s, fw_p_b, clearance_planet, sec_carrier_thickness, standard_clearance_1_5mm | high | printed sun length: both planet widths plus the carrier and clearances |
| 48 | `motor_output_hole_CSK_OD` | lookup | `nuts_and_bolts_dimensions(bolt_dia=motor_output_hole_dia, bolt_type=CSK)` → bolt_head_dia | motor_output_hole_dia | high | standard countersunk fastener size for the chosen bolt diameter |
| 49 | `motor_output_hole_CSK_head_height` | lookup | `nuts_and_bolts_dimensions(bolt_dia=motor_output_hole_dia, bolt_type=CSK)` → bolt_head_height | motor_output_hole_dia | high | standard countersunk fastener size for the chosen bolt diameter |
| 50 | `fw_p_b` | stress rule | two stress widths, b = FOS x Ft x qe x qk / (gear_allowable_stress x module): b1 for the sun - big planet mesh (module, Ft from serviceFactor x motor_peak_torque at the sun, qe from the sun-planet contact ratio, qk from Ns) and b2 for the small planet - ring mesh (module_s, qk from Np_s); then, if b1 + b2 < 2 x planet_bearing_width + planet_bearing_gap, each planet gear is raised to at least planet_bearing_width + planet_bearing_gap / 2 (one bearing per gear, half the gap each; mitStressAnalysisMinFacewidth); fw_p_b = b1 (raised) | module, module_s, Ns, Np_b, Np_s, Nr, num_planet, pressure_angle, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor, planet_bearing_width, planet_bearing_gap | high | big-planet width from the tooth-stress rule (b1, raised to the planet-bearing minimum when the two planet gears together are too short for their two bearings) |
| 51 | `dp_p_s` | formula | `module_s * Np_s` | module_s, Np_s | high | small-planet pitch diameter (small module) |
| 52 | `db_p_s` | formula | `dp_p_s * cos(pressure_angle_rad)` | dp_p_s, pressure_angle_rad | high | base-circle diameter |
| 53 | `alpha_p_s` | formula | `(sqrt(dp_p_s**2 - db_p_s**2) / db_p_s) * 180 / pi - pressure_angle_rad * 180 / pi` | dp_p_s, db_p_s, pressure_angle_rad | high | involute angle used to draw the tooth |
| 54 | `beta_p_s` | formula | `(360 / (4 * Np_s) - alpha_p_s) * 2` | Np_s, alpha_p_s | high | tooth angle used to draw the tooth |

## Used by the code, not written to the CAD file (31)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `ringRadialWidthMM` | wall thickness | cpg_params.json → cpg_3DP_design_parameters → `ringRadialWidthMM` |  | high | minimum ring gear wall, shared by the CAD's ring_radial_thickness rule, the mass model and the gearbox's outer-diameter check |
| 2 | `planetMinDistanceMM` | constraint constant | cpg_params.json → cpg_3DP_design_parameters → `planetMinDistanceMM` |  | high | minimum gap between neighbouring planets; only in the old interference check, which CPG doesn't call |
| 3 | `sCarrierExtrusionDiaMM` | constraint constant | cpg_params.json → cpg_3DP_design_parameters → `sCarrierExtrusionDiaMM` |  | high | carrier extrusion diameter in the planet-interference constraint |
| 4 | `sCarrierExtrusionClearanceMM` | constraint constant | cpg_params.json → cpg_3DP_design_parameters → `sCarrierExtrusionClearanceMM` |  | high | clearance in the planet-interference constraint |
| 5 | `bearingIDClearanceMM` | constraint constant | cpg_params.json → cpg_3DP_design_parameters → `bearingIDClearanceMM` |  | high | extra bore when choosing the output bearing |
| 6 | `pressure_angle_rad` | formula | `pressure_angle * pi / 180` | pressure_angle | high | pressure angle in radians (code attribute pressure_angle) |
| 7 | `motor_peak_torque` | motor | motors.json → motors.<motor>.electrical → `peak_torque_Nm` |  | high | motor torque the gears are sized for (peak torque under the default rating setting); sets the face widths |
| 8 | `gear_allowable_stress` | material | config.json → Material_properties.<gear material> → `maxAllowableStressMPa` |  | high | allowable tooth stress of the gear material, chosen with the material mode (3dp: PLA, metal: steel); sets the face widths |
| 9 | `FOS` | safety factor | config.json → MIT_params → `FOS` |  | high | factor of safety in the tooth-stress rule |
| 10 | `serviceFactor` | safety factor | config.json → MIT_params → `serviceFactor` |  | high | service factor on the motor torque in the tooth-stress rule |
| 11 | `clearance_motor_and_case_min` | clearance | cpg_params.json → cpg_3DP_design_parameters → `clearance_motor_and_case_min` |  | high | smallest radial gap between the motor and the case; sets clearance_motor_and_case (CAD) and the case mass |
| 12 | `case_mounting_hole_wall_overlap` | clearance | cpg_params.json → cpg_3DP_design_parameters → `case_mounting_hole_wall_overlap` |  | high | how far the case mounting holes cut into the case wall (0 = the hole just touches the wall); sets case_mounting_hole_shift |
| 13 | `bearing_mount_wall_bolt_dia_multiple` | wall thickness | cpg_params.json → cpg_3DP_design_parameters → `bearing_mount_wall_bolt_dia_multiple` |  | high | bearing-mount wall per side, in output-bolt diameters; sets bearing_mount_thickness (CAD) and the bearing-holding structure mass |
| 14 | `planet_bearing_gap` | clearance | cpg_params.json → cpg_3DP_design_parameters → `planet_bearing_gap` |  | high | axial gap between the two planet bearings (one in each planet gear); with them it sets the smallest planet widths |
| 15 | `output_mounting_hole_num` | fastener size | cpg_params.json → cpg_3DP_design_parameters → `output_mounting_hole_num` |  | high | number of output mounting holes: read from the config but not used by the code or written to the CAD file |
| 16 | `module_s` | module | optimiser (`optimizationCompoundPlanetaryActuator`) |  | high | the small module (small planet, ring): searched by the optimiser loop, but not in the CAD file (which has one module; ISSUES bug 18) |
| 17 | `h_b_s` | formula | `1.25 * module_s` | module_s | high | ring tooth depth (small module), used by the bearing-mount rule |
| 18 | `maxGearboxDiameter` | formula | `(MAX_GB_DIA_MULT_FACTOR_SMALL_MOTOR if motor_OD < SMALL_MOTOR_DIA_MM else MAX_GB_DIA_MULT_FACTOR) * motor_OD` | MAX_GB_DIA_MULT_FACTOR, MAX_GB_DIA_MULT_FACTOR_SMALL_MOTOR, SMALL_MOTOR_DIA_MM, motor_OD | high | largest gearbox diameter the optimiser may use (gearbox_runner max_diameter; unlike SSPG, without subtracting the ring wall) |
| 19 | `actuator_width` | formula | `fw_r + clearance_planet + bearing_height + clearance_planet + case_dist + bearing_retainer_thickness + motor_height + case_mounting_surface_height + standard_clearance_1_5mm + base_plate_thickness` | fw_r, clearance_planet, bearing_height, case_dist, bearing_retainer_thickness, motor_height, case_mounting_surface_height, standard_clearance_1_5mm, base_plate_thickness | high | axial width without the driver mount, written to the results CSV |
| 20 | `GEAR_RATIO_MIN` | search bound | cpg_params.json → cpg_optimization_parameters → `GEAR_RATIO_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 21 | `GEAR_RATIO_MAX` | search bound | cpg_params.json → cpg_optimization_parameters → `GEAR_RATIO_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 22 | `GEAR_RATIO_STEP` | search bound | cpg_params.json → cpg_optimization_parameters → `GEAR_RATIO_STEP` |  | high | optimiser setting: limits of the search, not a part dimension |
| 23 | `MODULE_MIN` | search bound | cpg_params.json → cpg_optimization_parameters → `MODULE_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 24 | `MODULE_MAX` | search bound | cpg_params.json → cpg_optimization_parameters → `MODULE_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 25 | `NUM_PLANET_MIN` | search bound | cpg_params.json → cpg_optimization_parameters → `NUM_PLANET_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 26 | `NUM_PLANET_MAX` | search bound | cpg_params.json → cpg_optimization_parameters → `NUM_PLANET_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 27 | `NUM_TEETH_SUN_MIN` | search bound | cpg_params.json → cpg_optimization_parameters → `NUM_TEETH_SUN_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 28 | `NUM_TEETH_PLANET_MIN` | search bound | cpg_params.json → cpg_optimization_parameters → `NUM_TEETH_PLANET_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 29 | `MAX_GB_DIA_MULT_FACTOR` | search bound | cpg_params.json → cpg_optimization_parameters → `MAX_GB_DIA_MULT_FACTOR` |  | high | optimiser setting: limits of the search, not a part dimension |
| 30 | `MAX_GB_DIA_MULT_FACTOR_SMALL_MOTOR` | search bound | cpg_params.json → cpg_optimization_parameters → `MAX_GB_DIA_MULT_FACTOR_SMALL_MOTOR` |  | high | optimiser setting: limits of the search, not a part dimension |
| 31 | `SMALL_MOTOR_DIA_MM` | search bound | cpg_params.json → cpg_optimization_parameters → `SMALL_MOTOR_DIA_MM` |  | high | optimiser setting: limits of the search, not a part dimension |

## Config blocks CPG doesn't read

- cpg_params.json → `cpg_design_parameters`: older design block; CPG reads only cpg_3DP_design_parameters (gearbox_runner)

## Names in the plain equation file

`CADs/CPG/cpg_equations.txt` writes the same values; these names differ there:

- `"pressure angle"` = `pressure_angle`
