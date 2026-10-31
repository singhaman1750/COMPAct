# WPG variables by category

Generated from `config_files/variables/wpg_variables.json` by `python tools/variables/render.py`; edit the JSON, not this page.

Every WPG variable sorted into input / optimisation / fixed / dependent. 'cad_variables' are the 143 variables WPG writes to CADs/WPG/wpg_equations_onshape.txt, in that order; 'code_only' are values the code uses but does not write to the CAD file (including the small module module_s: the CAD file has one module); 'unused_config_blocks' are config blocks WPG never reads. tests/test_variable_categories.py checks the lists against the code and re-evaluates every formula and lookup; docs/variables/wpg.md is generated from this file (python tools/variables/render.py).

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
| Fixed | 52 | 29 |
| Dependent | 68 | 3 |
| **Total** | **143** | **35** |

CAD variables by confidence: high 142, medium 1, low 0

## To review (not high confidence)

- `clearance_motor_and_case` (Dependent, medium): radial gap between the motor and the case: the CAD takes the configured minimum as a constant, while the mass code grows it when the big ring is wider than the motor (CAD and mass disagree, to be logged); the case is sized from maxGearboxDiameter, not from the chosen design

## Rules shared by every gearbox

From `config_files/variables/rules.json`; the test holds every gearbox's file to them.

- names matching `^(a[12]_)?Nr(_[bs]|[0-9]*)$` are **Dependent / implicit constraint**: ring-gear teeth are implicitly constrained: the coaxial geometric constraint (e.g. Nr = Ns + 2 x Np) fixes them once the sun and planet teeth are chosen, so the optimiser sets them instead of searching them
- names matching `^fw_(s_calc|p|p_b|r|r_s)$` are **Dependent / stress rule**: gear face widths follow from the tooth-stress rule: the optimisation variables, the motor torque, the gear material and the safety factors fix them, and the optimiser always takes the smallest width that passes (widths that are a formula of another width, e.g. CPG's fw_p_s = fw_r + clearance_planet, are dependent / formula)
- names matching `^a[12]_fw_(s_calc|r)[12]?$` are **Dependent / stress rule**: the same stress-rule face widths in a two-stage gearbox, under the stage prefixes a1_ / a2_ (the planet width a1_fw_p / a2_fw_p is a copy of the ring width, so it is dependent / formula and not in this rule)

## Input (18)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `driver_lower_holes_dist_from_center` | driver | config.json → Motor_drivers.OdrivePro → `driver_lower_holes_dist_from_center` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 2 | `driver_mount_height` | driver | config.json → Motor_drivers.OdrivePro → `driver_mount_height` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 3 | `driver_mount_holes_dia` | driver | config.json → Motor_drivers.OdrivePro → `driver_mount_holes_dia` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 4 | `driver_mount_inserts_OD` | driver | config.json → Motor_drivers.OdrivePro → `driver_mount_inserts_OD` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 5 | `driver_mount_thickness` | driver | config.json → Motor_drivers.OdrivePro → `driver_mount_thickness` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 6 | `driver_side_holes_dist_from_center` | driver | config.json → Motor_drivers.OdrivePro → `driver_side_holes_dist_from_center` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 7 | `driver_upper_holes_dist_from_center` | driver | config.json → Motor_drivers.OdrivePro → `driver_upper_holes_dist_from_center` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 8 | `motor_OD` | motor | motors.json → motors.<motor>.geometry → `motorDia` |  | high | read from the chosen motor's geometry |
| 9 | `motor_height` | motor | motors.json → motors.<motor>.geometry → `motorLength` |  | high | read from the chosen motor's geometry |
| 10 | `motor_mount_hole_PCD` | motor | motors.json → motors.<motor>.geometry → `motor_mount_hole_PCD` |  | high | read from the chosen motor's geometry |
| 11 | `motor_mount_hole_dia` | motor | motors.json → motors.<motor>.geometry → `motor_mount_hole_dia` |  | high | read from the chosen motor's geometry |
| 12 | `motor_mount_hole_num` | motor | motors.json → motors.<motor>.geometry → `motor_mount_hole_num` |  | high | read from the chosen motor's geometry |
| 13 | `motor_output_hole_PCD` | motor | motors.json → motors.<motor>.geometry → `motor_output_hole_PCD` |  | high | read from the chosen motor's geometry |
| 14 | `motor_output_hole_dia` | motor | motors.json → motors.<motor>.geometry → `motor_output_hole_dia` |  | high | read from the chosen motor's geometry |
| 15 | `motor_output_hole_num` | motor | motors.json → motors.<motor>.geometry → `motor_output_hole_num` |  | high | read from the chosen motor's geometry |
| 16 | `wire_slot_dist_from_center` | motor | motors.json → motors.<motor>.geometry → `wire_slot_dist_from_center` |  | high | read from the chosen motor's geometry |
| 17 | `wire_slot_length` | motor | motors.json → motors.<motor>.geometry → `wire_slot_length` |  | high | read from the chosen motor's geometry |
| 18 | `wire_slot_radius` | motor | motors.json → motors.<motor>.geometry → `wire_slot_radius` |  | high | read from the chosen motor's geometry |

## Optimisation (5)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `Np_b` | teeth | optimiser (`optimizationWolfromPlanetaryActuator`) |  | high | big planet teeth: searched by the optimiser loop |
| 2 | `Np_s` | teeth | optimiser (`optimizationWolfromPlanetaryActuator`) |  | high | small planet teeth: searched by the optimiser loop |
| 3 | `Ns` | teeth | optimiser (`optimizationWolfromPlanetaryActuator`) |  | high | sun teeth: searched by the optimiser loop |
| 4 | `module` | module | optimiser (`optimizationWolfromPlanetaryActuator`) |  | high | the big module (sun, big planet, big ring): searched by the optimiser loop; the CAD file has this one module although the small ring and small planet use the small module module_s (code-only; same pattern as CPG bug 18) |
| 5 | `num_planet` | planets | optimiser (`optimizationWolfromPlanetaryActuator`) |  | high | number of planets: searched by the optimiser loop |

## Fixed (52)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `Motor_case_OD_base_to_chamfer` | feature size | wpg_params.json → wpg_3DP_design_parameters → `Motor_case_OD_base_to_chamfer` |  | high | constant from the WPG 3DP design parameters |
| 2 | `Motor_case_thickness` | wall thickness | wpg_params.json → wpg_3DP_design_parameters → `Motor_case_thickness` |  | high | constant from the WPG 3DP design parameters |
| 3 | `air_flow_hole_offset` | feature size | wpg_params.json → wpg_3DP_design_parameters → `air_flow_hole_offset` |  | high | constant from the WPG 3DP design parameters |
| 4 | `standard_bearing_insertion_chamfer` | feature size | wpg_params.json → wpg_3DP_design_parameters → `standard_bearing_insertion_chamfer` |  | high | constant from the WPG 3DP design parameters |
| 5 | `base_plate_thickness` | wall thickness | wpg_params.json → wpg_3DP_design_parameters → `base_plate_thickness` |  | high | constant from the WPG 3DP design parameters |
| 6 | `bearing_retainer_thickness` | wall thickness | wpg_params.json → wpg_3DP_design_parameters → `bearing_retainer_thickness` |  | high | constant from the WPG 3DP design parameters |
| 7 | `carrier_bearing_step_width` | feature size | wpg_params.json → wpg_3DP_design_parameters → `carrier_bearing_step_width` |  | high | constant from the WPG 3DP design parameters |
| 8 | `carrier_small_ring_inner_bearing_ID` | bearing (chosen part) | wpg_params.json → wpg_3DP_design_parameters → `carrier_small_ring_inner_bearing_ID` |  | high | constant from the WPG 3DP design parameters |
| 9 | `carrier_small_ring_inner_bearing_flap` | bearing (chosen part) | wpg_params.json → wpg_3DP_design_parameters → `carrier_small_ring_inner_bearing_flap` |  | high | constant from the WPG 3DP design parameters |
| 10 | `carrier_thickness` | wall thickness | wpg_params.json → wpg_3DP_design_parameters → `carrier_thickness` |  | high | constant from the WPG 3DP design parameters |
| 11 | `carrier_trapezoidal_support_hole_PCD_offset_bearing_ID` | feature size | wpg_params.json → wpg_3DP_design_parameters → `carrier_trapezoidal_support_hole_PCD_offset_bearing_ID` |  | high | constant from the WPG 3DP design parameters |
| 12 | `carrier_trapezoidal_support_hole_dia` | fastener size | wpg_params.json → wpg_3DP_design_parameters → `carrier_trapezoidal_support_hole_dia` |  | high | constant from the WPG 3DP design parameters |
| 13 | `carrier_trapezoidal_support_sun_offset` | feature size | wpg_params.json → wpg_3DP_design_parameters → `carrier_trapezoidal_support_sun_offset` |  | high | constant from the WPG 3DP design parameters |
| 14 | `case_mounting_bolt_depth` | fastener size | wpg_params.json → wpg_3DP_design_parameters → `case_mounting_bolt_depth` |  | high | constant from the WPG 3DP design parameters |
| 15 | `case_mounting_hole_dia` | fastener size | wpg_params.json → wpg_3DP_design_parameters → `case_mounting_hole_dia` |  | high | constant from the WPG 3DP design parameters |
| 16 | `case_mounting_nut_clearance` | clearance | wpg_params.json → wpg_3DP_design_parameters → `case_mounting_nut_clearance` |  | high | constant from the WPG 3DP design parameters |
| 17 | `case_mounting_surface_height` | wall thickness | wpg_params.json → wpg_3DP_design_parameters → `case_mounting_surface_height` |  | high | constant from the WPG 3DP design parameters |
| 18 | `central_hole_offset_from_motor_mount_PCD` | feature size | wpg_params.json → wpg_3DP_design_parameters → `central_hole_offset_from_motor_mount_PCD` |  | high | constant from the WPG 3DP design parameters |
| 19 | `clearance_case_mount_holes_shell_thickness` | clearance | wpg_params.json → wpg_3DP_design_parameters → `clearance_case_mount_holes_shell_thickness` |  | high | constant from the WPG 3DP design parameters |
| 20 | `clearance_planet` | clearance | wpg_params.json → wpg_3DP_design_parameters → `clearance_planet` |  | high | constant from the WPG 3DP design parameters |
| 21 | `clearance_sun_coupler_sec_carrier` | clearance | wpg_params.json → wpg_3DP_design_parameters → `clearance_sun_coupler_sec_carrier` |  | high | constant from the WPG 3DP design parameters |
| 22 | `gear_casing_thickness` | wall thickness | wpg_params.json → wpg_3DP_design_parameters → `gear_casing_thickness` |  | high | constant from the WPG 3DP design parameters |
| 23 | `output_mounting_hole_dia` | fastener size | wpg_params.json → wpg_3DP_design_parameters → `output_mounting_hole_dia` |  | high | constant from the WPG 3DP design parameters |
| 24 | `output_mounting_nut_depth` | fastener size | wpg_params.json → wpg_3DP_design_parameters → `output_mounting_nut_depth` |  | high | constant from the WPG 3DP design parameters |
| 25 | `pattern_bulge_dia` | feature size | wpg_params.json → wpg_3DP_design_parameters → `pattern_bulge_dia` |  | high | constant from the WPG 3DP design parameters |
| 26 | `pattern_depth` | feature size | wpg_params.json → wpg_3DP_design_parameters → `pattern_depth` |  | high | constant from the WPG 3DP design parameters |
| 27 | `pattern_num_bulge` | feature size | wpg_params.json → wpg_3DP_design_parameters → `pattern_num_bulge` |  | high | constant from the WPG 3DP design parameters |
| 28 | `pattern_offset_from_motor_case_OD_base` | feature size | wpg_params.json → wpg_3DP_design_parameters → `pattern_offset_from_motor_case_OD_base` |  | high | constant from the WPG 3DP design parameters |
| 29 | `planet_bearing_OD` | bearing (chosen part) | wpg_params.json → wpg_3DP_design_parameters → `planet_bearing_OD` |  | high | constant from the WPG 3DP design parameters |
| 30 | `planet_bearing_width` | bearing (chosen part) | wpg_params.json → wpg_3DP_design_parameters → `planet_bearing_width` |  | high | constant from the WPG 3DP design parameters |
| 31 | `planet_bore` | planet part | wpg_params.json → wpg_3DP_design_parameters → `planet_bore` |  | high | constant from the WPG 3DP design parameters |
| 32 | `planet_pin_bolt_dia` | fastener size | wpg_params.json → wpg_3DP_design_parameters → `planet_pin_bolt_dia` |  | high | constant from the WPG 3DP design parameters |
| 33 | `planet_shaft_dia` | planet part | wpg_params.json → wpg_3DP_design_parameters → `planet_shaft_dia` |  | high | constant from the WPG 3DP design parameters |
| 34 | `planet_shaft_step_offset` | planet part | wpg_params.json → wpg_3DP_design_parameters → `planet_shaft_step_offset` |  | high | constant from the WPG 3DP design parameters |
| 35 | `pressure_angle` | gear standard | config.json → Gear_standard_parameters → `pressureAngleDEG` |  | high | gear standard, the same for every gearbox type |
| 36 | `ring_radial_thickness` | wall thickness | wpg_params.json → wpg_3DP_design_parameters → `ring_radial_thickness` |  | high | constant from the WPG 3DP design parameters |
| 37 | `sec_carrier_thickness` | wall thickness | wpg_params.json → wpg_3DP_design_parameters → `sec_carrier_thickness` |  | high | constant from the WPG 3DP design parameters |
| 38 | `small_ring_case_thickness` | wall thickness | wpg_params.json → wpg_3DP_design_parameters → `small_ring_case_thickness` |  | high | constant from the WPG 3DP design parameters |
| 39 | `small_ring_output_wall_thickness` | wall thickness | wpg_params.json → wpg_3DP_design_parameters → `small_ring_output_wall_thickness` |  | high | constant from the WPG 3DP design parameters |
| 40 | `small_ring_output_wall_to_bearing_shaft_attachement_hole_depth` | fastener size | wpg_params.json → wpg_3DP_design_parameters → `small_ring_output_wall_to_bearing_shaft_attachement_hole_depth` |  | high | constant from the WPG 3DP design parameters |
| 41 | `small_ring_output_wall_to_bearing_shaft_attachement_hole_dia` | fastener size | wpg_params.json → wpg_3DP_design_parameters → `small_ring_output_wall_to_bearing_shaft_attachement_hole_dia` |  | high | constant from the WPG 3DP design parameters |
| 42 | `small_ring_output_wall_to_bearing_shaft_attachement_hole_num` | fastener size | wpg_params.json → wpg_3DP_design_parameters → `small_ring_output_wall_to_bearing_shaft_attachement_hole_num` |  | high | constant from the WPG 3DP design parameters |
| 43 | `small_ring_output_wall_to_bearing_shaft_attachement_hole_pcd` | fastener size | wpg_params.json → wpg_3DP_design_parameters → `small_ring_output_wall_to_bearing_shaft_attachement_hole_pcd` |  | high | constant from the WPG 3DP design parameters |
| 44 | `standard_clearance_1_5mm` | clearance | wpg_params.json → wpg_3DP_design_parameters → `standard_clearance_1_5mm` |  | high | constant from the WPG 3DP design parameters |
| 45 | `standard_fillet_1_5mm` | feature size | wpg_params.json → wpg_3DP_design_parameters → `standard_fillet_1_5mm` |  | high | constant from the WPG 3DP design parameters |
| 46 | `sun_central_bolt_dia` | fastener size | wpg_params.json → wpg_3DP_design_parameters → `sun_central_bolt_dia` |  | high | constant from the WPG 3DP design parameters |
| 47 | `sun_coupler_hub_thickness` | wall thickness | wpg_params.json → wpg_3DP_design_parameters → `sun_coupler_hub_thickness` |  | high | constant from the WPG 3DP design parameters |
| 48 | `sun_shaft_bearing_ID` | bearing (chosen part) | wpg_params.json → wpg_3DP_design_parameters → `sun_shaft_bearing_ID` |  | high | constant from the WPG 3DP design parameters |
| 49 | `sun_shaft_bearing_OD` | bearing (chosen part) | wpg_params.json → wpg_3DP_design_parameters → `sun_shaft_bearing_OD` |  | high | constant from the WPG 3DP design parameters |
| 50 | `sun_shaft_bearing_width` | bearing (chosen part) | wpg_params.json → wpg_3DP_design_parameters → `sun_shaft_bearing_width` |  | high | constant from the WPG 3DP design parameters |
| 51 | `tight_clearance_3DP` | clearance | wpg_params.json → wpg_3DP_design_parameters → `tight_clearance_3DP` |  | high | constant from the WPG 3DP design parameters |
| 52 | `loose_clearance_3DP` | clearance | wpg_params.json → wpg_3DP_design_parameters → `loose_clearance_3DP` |  | high | constant from the WPG 3DP design parameters |

## Dependent (68)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `Nr_b` | implicit constraint | `Ns + Np_b * 2` | Ns, Np_b | high | implicitly constrained: the geometric constraints fix the ring teeth once the sun and planet teeth are chosen (Ns + 2 x Np_b: the big ring), and the optimiser sets them instead of searching them (the code lists them among the optimisation variables) |
| 2 | `Nr_s` | implicit constraint | `Ns + Np_b + Np_s` | Np_s, Ns, Np_b | high | implicitly constrained: the geometric constraints fix the ring teeth once the sun and planet teeth are chosen (Ns + Np_b + Np_s: the small ring), and the optimiser sets them instead of searching them (the code lists them among the optimisation variables) |
| 3 | `Motor_case_ID` | formula | `maxGearboxDiameter + clearance_motor_and_case * 2 + 2 * ring_radial_thickness` | maxGearboxDiameter, ring_radial_thickness, clearance_motor_and_case | high | motor case inner diameter |
| 4 | `Motor_case_OD_max` | formula | `case_mounting_PCD + case_mounting_hole_allen_socket_dia + clearance_case_mount_holes_shell_thickness * 2` | case_mounting_PCD, case_mounting_hole_allen_socket_dia, clearance_case_mount_holes_shell_thickness | high | widest diameter, over the case mounting ears |
| 5 | `alpha_p_b` | formula | `(dp_p_b ** 2 - db_p_b ** 2) ** 0.5 / db_p_b * 180 / pi - pressure_angle` | pressure_angle, db_p_b, dp_p_b | high | involute angle used to draw the tooth |
| 6 | `alpha_p_s` | formula | `(dp_p_s ** 2 - db_p_s ** 2) ** 0.5 / db_p_s * 180 / pi - pressure_angle` | pressure_angle, db_p_s, dp_p_s | high | involute angle used to draw the tooth |
| 7 | `alpha_r_b` | formula | `(dp_r_b ** 2 - db_r_b ** 2) ** 0.5 / db_r_b * 180 / pi - pressure_angle` | pressure_angle, db_r_b, dp_r_b | high | computed by the code: (dp_r_b ** 2 - db_r_b ** 2) ** 0.5 / db_r_b * 180 / pi - pressure_angle |
| 8 | `alpha_r_s` | formula | `(dp_r_s ** 2 - db_r_s ** 2) ** 0.5 / db_r_s * 180 / pi - pressure_angle` | pressure_angle, db_r_s, dp_r_s | high | computed by the code: (dp_r_s ** 2 - db_r_s ** 2) ** 0.5 / db_r_s * 180 / pi - pressure_angle |
| 9 | `alpha_s` | formula | `(dp_s ** 2 - db_s ** 2) ** 0.5 / db_s * 180 / pi - pressure_angle` | pressure_angle, db_s, dp_s | high | involute angle used to draw the tooth |
| 10 | `bearing_ID` | lookup | `bearings_discrete(idRequiredMM=module * Nr_s + 2 * module + 2 * small_ring_case_thickness)` → getBearingIDMM | small_ring_case_thickness, module, Nr_s | high | catalogue bearing chosen by bearings_discrete for the bore the design needs (smallest one that fits); this is its bore |
| 11 | `bearing_OD` | lookup | `bearings_discrete(idRequiredMM=module * Nr_s + 2 * module + 2 * small_ring_case_thickness)` → getBearingODMM | small_ring_case_thickness, module, Nr_s | high | catalogue bearing chosen by bearings_discrete for the bore the design needs (smallest one that fits); this is its outer diameter |
| 12 | `bearing_height` | lookup | `bearings_discrete(idRequiredMM=module * Nr_s + 2 * module + 2 * small_ring_case_thickness)` → getBearingWidthMM | small_ring_case_thickness, module, Nr_s | high | catalogue bearing chosen by bearings_discrete for the bore the design needs (smallest one that fits); this is its width |
| 13 | `bearing_mount_thickness` | formula | `output_mounting_hole_dia * bearing_mount_wall_bolt_dia_multiple if bearing_OD + output_mounting_hole_dia * (2 * bearing_mount_wall_bolt_dia_multiple) > Nr_s * module + 2 * h_b else (Nr_s * module + 2 * h_b - (bearing_OD + output_mounting_hole_dia * (2 * bearing_mount_wall_bolt_dia_multiple))) / 2 + output_mounting_hole_dia * bearing_mount_wall_bolt_dia_multiple + standard_clearance_1_5mm` | output_mounting_hole_dia, bearing_mount_wall_bolt_dia_multiple, standard_clearance_1_5mm, bearing_OD, Nr_s, module, h_b | high | wall around the output bearing: the configured number of output-bolt diameters on each side, or wider (plus a clearance) when the ring gear's teeth reach further out (the same rule is used for the mass) |
| 14 | `beta_p_b` | formula | `(360 / (4 * Np_b) - alpha_p_b) * 2` | alpha_p_b, Np_b | high | tooth angle used to draw the tooth |
| 15 | `beta_p_s` | formula | `(360 / (4 * Np_s) - alpha_p_s) * 2` | alpha_p_s, Np_s | high | tooth angle used to draw the tooth |
| 16 | `beta_r_b` | formula | `(360 / (4 * Nr_b) + alpha_r_b) * 2` | alpha_r_b, Nr_b | high | computed by the code: (360 / (4 * Nr_b) + alpha_r_b) * 2 |
| 17 | `beta_r_s` | formula | `(360 / (4 * Nr_s) + alpha_r_s) * 2` | alpha_r_s, Nr_s | high | computed by the code: (360 / (4 * Nr_s) + alpha_r_s) * 2 |
| 18 | `beta_s` | formula | `(360 / (4 * Ns) - alpha_s) * 2` | alpha_s, Ns | high | tooth angle used to draw the tooth |
| 19 | `carrier_PCD` | formula | `(Np_b + Ns) * module` | module, Np_b, Ns | high | planet-centre circle (twice the centre distance) |
| 20 | `carrier_small_ring_inner_bearing_OD` | lookup | `bearings_discrete(idRequiredMM=carrier_small_ring_inner_bearing_ID)` → getBearingODMM | carrier_small_ring_inner_bearing_ID | high | catalogue bearing chosen by bearings_discrete for the bore the design needs (smallest one that fits); this is its outer diameter |
| 21 | `carrier_small_ring_inner_bearing_height` | lookup | `bearings_discrete(idRequiredMM=carrier_small_ring_inner_bearing_ID)` → getBearingWidthMM | carrier_small_ring_inner_bearing_ID | high | catalogue bearing chosen by bearings_discrete for the bore the design needs (smallest one that fits); this is its width |
| 22 | `carrier_trapezoidal_support_hole_socket_head_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=carrier_trapezoidal_support_hole_dia, bolt_type=socket_head)` → bolt_head_dia | carrier_trapezoidal_support_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 23 | `carrier_trapezoidal_support_hole_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=carrier_trapezoidal_support_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | carrier_trapezoidal_support_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 24 | `case_dist` | formula | `sec_carrier_thickness + clearance_planet + sun_coupler_hub_thickness - case_mounting_surface_height` | case_mounting_surface_height, sun_coupler_hub_thickness, sec_carrier_thickness, clearance_planet | high | axial gap between the motor case and the gearbox case |
| 25 | `case_mounting_PCD` | formula | `motor_case_OD_base + case_mounting_hole_shift * 2` | motor_case_OD_base, case_mounting_hole_shift | high | case bolt circle |
| 26 | `case_mounting_hole_allen_socket_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=case_mounting_hole_dia, bolt_type=socket_head)` → bolt_head_dia | case_mounting_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 27 | `case_mounting_hole_shift` | formula | `case_mounting_hole_dia / 2 - case_mounting_hole_wall_overlap` | case_mounting_hole_wall_overlap, case_mounting_hole_dia | high | how far the case bolt circle sits outside the case wall: half the bolt hole, less the configured overlap |
| 28 | `case_mounting_nut_thickness` | lookup | `nuts_and_bolts_dimensions(bolt_dia=case_mounting_hole_dia, bolt_type=socket_head)` → nut_thickness | case_mounting_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 29 | `case_mounting_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=case_mounting_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | case_mounting_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 30 | `clearance_motor_and_case` | formula | `clearance_motor_and_case_min` | clearance_motor_and_case_min | medium | radial gap between the motor and the case: the CAD takes the configured minimum as a constant, while the mass code grows it when the big ring is wider than the motor (CAD and mass disagree, to be logged); the case is sized from maxGearboxDiameter, not from the chosen design |
| 31 | `clr_tip_root` | formula | `h_f - h_a` | h_f, h_a | high | tip-root clearance from addendum and dedendum |
| 32 | `clr_tip_root_s` | formula | `h_f - h_a` | h_f, h_a | high | computed by the code: h_f - h_a |
| 33 | `db_p_b` | formula | `dp_p_b * cos(pressure_angle_rad)` | dp_p_b, pressure_angle_rad | high | base-circle diameter |
| 34 | `db_p_s` | formula | `dp_p_s * cos(pressure_angle_rad)` | dp_p_s, pressure_angle_rad | high | base-circle diameter |
| 35 | `db_r_b` | formula | `dp_r_b * cos(pressure_angle_rad)` | dp_r_b, pressure_angle_rad | high | computed by the code: dp_r_b * cos(pressure_angle_rad) |
| 36 | `db_r_s` | formula | `dp_r_s * cos(pressure_angle_rad)` | dp_r_s, pressure_angle_rad | high | computed by the code: dp_r_s * cos(pressure_angle_rad) |
| 37 | `db_s` | formula | `dp_s * cos(pressure_angle_rad)` | dp_s, pressure_angle_rad | high | base-circle diameter |
| 38 | `dp_p_b` | formula | `module * Np_b` | module, Np_b | high | big-planet pitch diameter |
| 39 | `dp_p_s` | formula | `module * Np_s` | module, Np_s | high | small-planet pitch diameter (small module) |
| 40 | `dp_r_b` | formula | `module * Nr_b` | module, Nr_b | high | computed by the code: module * Nr_b |
| 41 | `dp_r_s` | formula | `module * Nr_s` | module, Nr_s | high | computed by the code: module * Nr_s |
| 42 | `dp_s` | formula | `module * Ns` | module, Ns | high | pitch diameter |
| 43 | `fw_p_b` | stress rule | b1 = FOS x Ft_sp_big x qe x qk / (gear_allowable_stress x module) (sun - big planet), b2 = the same with Ft_rp_big on the big planet - big ring mesh; big-planet width = max(b1, b2); small-planet width b3 = FOS x Ft_rp_small x qe x qk / (gear_allowable_stress x module_s) (small planet - small ring); if b_big + b_small < 2 x planet_bearing_width + planet_bearing_gap, each is raised to at least planet_bearing_width + planet_bearing_gap / 2; Ft_sp_big, Ft_rp_big, Ft_rp_small = serviceFactor x motor_peak_torque / (num_planet x pitch radius) with the Wolfrom force ratios; qe = 1 / contact ratio of the mesh, qk = curve fit in the tooth count of the mesh; fw_p_b = the big-planet width | module, module_s, Ns, Np_b, Np_s, Nr_b, Nr_s, num_planet, pressure_angle_rad, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor, planet_bearing_width, planet_bearing_gap | high | big-planet width from the tooth-stress rule (the larger of its two meshes), raised to hold its bearing; the big ring width fw_r_b is a copy |
| 44 | `fw_p_s` | formula | `fw_r_s + clearance_planet` | fw_r_s, clearance_planet | high | small-planet width: the ring width plus a clearance (a formula, not the stress rule) |
| 45 | `fw_r_b` | formula | `fw_p_b` | fw_p_b | high | computed by the code: fw_p_b |
| 46 | `fw_r_s` | stress rule | b3 = FOS x Ft_rp_small x qe x qk / (gear_allowable_stress x module_s) on the small planet - small ring mesh, with the same planet-bearing minimum as the planets (each gear at least planet_bearing_width + planet_bearing_gap / 2 when the two together are below 2 x planet_bearing_width + planet_bearing_gap); Ft_sp_big, Ft_rp_big, Ft_rp_small = serviceFactor x motor_peak_torque / (num_planet x pitch radius) with the Wolfrom force ratios; qe = 1 / contact ratio of the mesh, qk = curve fit in the tooth count of the mesh; fw_r_s = the small width | module, module_s, Ns, Np_b, Np_s, Nr_b, Nr_s, num_planet, pressure_angle_rad, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor, planet_bearing_width, planet_bearing_gap | high | small-ring width from the tooth-stress rule (the small planet's width is this plus clearance_planet), raised to hold the planet bearing; it uses the small module, which the CAD file does not carry |
| 47 | `fw_s_calc` | stress rule | b = FOS x Ft_sp_big x qe x qk / (gear_allowable_stress x module) on the sun - big planet mesh (mitStressAnalysisMinFacewidth); Ft_sp_big, Ft_rp_big, Ft_rp_small = serviceFactor x motor_peak_torque / (num_planet x pitch radius) with the Wolfrom force ratios; qe = 1 / contact ratio of the mesh, qk = curve fit in the tooth count of the mesh; fw_s_calc = b | module, Ns, Np_b, Nr_b, num_planet, pressure_angle_rad, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor | high | sun face width from the tooth-stress rule: fixed by the optimisation variables, the motor torque, the gear material and the safety factors, so the optimiser has no freedom over it (it takes the smallest width that passes) |
| 48 | `fw_s_used` | formula | `fw_p_s + fw_p_b + clearance_planet + sec_carrier_thickness + standard_clearance_1_5mm` | standard_clearance_1_5mm, sec_carrier_thickness, clearance_planet, fw_p_s, fw_p_b | high | printed sun length: planet width plus the carrier and clearances |
| 49 | `gear_casing_big_ring_to_bearing_dist` | formula | `fw_p_s + clearance_planet + carrier_thickness + carrier_bearing_step_width + carrier_small_ring_inner_bearing_height - bearing_height - carrier_bearing_step_width` | carrier_bearing_step_width, bearing_height, carrier_small_ring_inner_bearing_height, carrier_thickness, fw_p_s, clearance_planet | high | computed by the code: fw_p_s + clearance_planet + carrier_thickness + carrier_bearing_step_width + carrier_small_ring_inner_bearing_height - bearing_height - carrier_bearing_step_width |
| 50 | `h_a` | formula | `1 * module` | module | high | addendum, standard proportion of the module |
| 51 | `h_b` | formula | `1.25 * module` | module | high | standard proportion of the module (same value as h_f) |
| 52 | `h_f` | formula | `1.25 * module` | module | high | dedendum, standard proportion of the module |
| 53 | `motor_case_OD_base` | formula | `maxGearboxDiameter + 2 * ring_radial_thickness + clearance_motor_and_case * 2 + Motor_case_thickness * 2` | Motor_case_thickness, maxGearboxDiameter, clearance_motor_and_case, ring_radial_thickness | high | motor case outer diameter (body diameter) |
| 54 | `motor_output_hole_CSK_OD` | lookup | `nuts_and_bolts_dimensions(bolt_dia=motor_output_hole_dia, bolt_type=CSK)` → bolt_head_dia | motor_output_hole_dia | high | standard countersunk fastener size for the chosen bolt diameter |
| 55 | `motor_output_hole_CSK_head_height` | lookup | `nuts_and_bolts_dimensions(bolt_dia=motor_output_hole_dia, bolt_type=CSK)` → bolt_head_height | motor_output_hole_dia | high | standard countersunk fastener size for the chosen bolt diameter |
| 56 | `output_mounting_PCD` | formula | `bearing_OD + bearing_mount_thickness` | bearing_OD, bearing_mount_thickness | high | output bolt circle |
| 57 | `output_mounting_nut_thickness` | lookup | `nuts_and_bolts_dimensions(bolt_dia=output_mounting_hole_dia, bolt_type=socket_head)` → nut_thickness | output_mounting_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 58 | `output_mounting_nut_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=output_mounting_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | output_mounting_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 59 | `planet_pin_bolt_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=planet_pin_bolt_dia, bolt_type=socket_head)` → nut_width_across_flats | planet_pin_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 60 | `planet_pin_socket_head_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=planet_pin_bolt_dia, bolt_type=socket_head)` → bolt_head_dia | planet_pin_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 61 | `ring_OD_b` | formula | `Nr_b * module + ring_radial_thickness * 2` | Nr_b, module, ring_radial_thickness | high | computed by the code: Nr_b * module + ring_radial_thickness * 2 |
| 62 | `ring_to_chamfer_clearance` | formula | `clearance_planet` | clearance_planet | high | computed by the code: clearance_planet |
| 63 | `small_ring_output_wall_to_bearing_shaft_attachement_hole_CSK_OD` | lookup | `nuts_and_bolts_dimensions(bolt_dia=small_ring_output_wall_to_bearing_shaft_attachement_hole_dia, bolt_type=CSK)` → bolt_head_dia | small_ring_output_wall_to_bearing_shaft_attachement_hole_dia | high | standard countersunk fastener size for the chosen bolt diameter |
| 64 | `small_ring_output_wall_to_bearing_shaft_attachement_hole_CSK_head_height` | lookup | `nuts_and_bolts_dimensions(bolt_dia=small_ring_output_wall_to_bearing_shaft_attachement_hole_dia, bolt_type=CSK)` → bolt_head_height | small_ring_output_wall_to_bearing_shaft_attachement_hole_dia | high | standard countersunk fastener size for the chosen bolt diameter |
| 65 | `small_ring_output_wall_to_bearing_shaft_attachement_nut_thickness` | lookup | `nuts_and_bolts_dimensions(bolt_dia=small_ring_output_wall_to_bearing_shaft_attachement_hole_dia, bolt_type=CSK)` → nut_thickness | small_ring_output_wall_to_bearing_shaft_attachement_hole_dia | high | standard countersunk fastener size for the chosen bolt diameter |
| 66 | `small_ring_output_wall_to_bearing_shaft_attachement_nut_wrench` | lookup | `nuts_and_bolts_dimensions(bolt_dia=small_ring_output_wall_to_bearing_shaft_attachement_hole_dia, bolt_type=CSK)` → nut_width_across_flats | small_ring_output_wall_to_bearing_shaft_attachement_hole_dia | high | standard countersunk fastener size for the chosen bolt diameter |
| 67 | `sun_central_bolt_socket_head_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=sun_central_bolt_dia, bolt_type=socket_head)` → bolt_head_dia | sun_central_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 68 | `sun_hub_dia` | formula | `motor_output_hole_PCD + motor_output_hole_CSK_OD + standard_clearance_1_5mm * 2 if motor_output_hole_PCD + motor_output_hole_CSK_OD + standard_clearance_1_5mm * 2 > module * Ns + 2 * module else module * Ns + 2 * module` | motor_output_hole_PCD, motor_output_hole_CSK_OD, standard_clearance_1_5mm, module, Ns | high | sun coupler hub: sized to the motor's output holes (plus a margin), or to the sun's tip circle when that is larger |

## Used by the code, not written to the CAD file (35)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `pressure_angle_rad` | formula | `pressure_angle * pi / 180` | pressure_angle | high | pressure angle in radians (code attribute pressure_angle) |
| 2 | `module_s` | module | optimiser (`optimizationWolfromPlanetaryActuator`) |  | high | the small module (small planet, small ring): searched by the optimiser loop (MODULE_SMALL_MIN..MAX) and used by the stress rule and the gearbox constraints, but not in the CAD file, which has one module and draws the small ring and planet with it (same pattern as CPG bug 18) |
| 3 | `motor_peak_torque` | motor | motors.json → motors.<motor>.electrical → `peak_torque_Nm` |  | high | motor torque the gears are sized for (peak torque under the default rating setting); sets the face widths |
| 4 | `gear_allowable_stress` | material | config.json → Material_properties.<gear material> → `maxAllowableStressMPa` |  | high | allowable tooth stress of the gear material, chosen with the material mode (3dp: PLA, metal: steel); sets the face widths |
| 5 | `FOS` | safety factor | config.json → MIT_params → `FOS` |  | high | factor of safety in the tooth-stress rule |
| 6 | `serviceFactor` | safety factor | config.json → MIT_params → `serviceFactor` |  | high | service factor on the motor torque in the tooth-stress rule |
| 7 | `clearance_motor_and_case_min` | clearance | wpg_params.json → wpg_3DP_design_parameters → `clearance_motor_and_case_min` |  | high | the configured motor-to-case gap: the CAD uses it as a constant (clearance_motor_and_case), the mass code grows it with the big ring |
| 8 | `case_mounting_hole_wall_overlap` | clearance | wpg_params.json → wpg_3DP_design_parameters → `case_mounting_hole_wall_overlap` |  | high | how far the case bolt holes overlap the case wall; sets case_mounting_hole_shift |
| 9 | `bearing_mount_wall_bolt_dia_multiple` | wall thickness | wpg_params.json → wpg_3DP_design_parameters → `bearing_mount_wall_bolt_dia_multiple` |  | high | wall around the output bearing, in output-bolt diameters on each side (CAD and mass code; the two use different ring terms in the comparison, to be logged) |
| 10 | `planet_bearing_gap` | clearance | wpg_params.json → wpg_3DP_design_parameters → `planet_bearing_gap` |  | high | axial gap between the two planet bearings (one in each planet gear); with the bearing width it sets the smallest planet and ring widths |
| 11 | `bearingIDClearanceMM` | constraint constant | wpg_params.json → wpg_3DP_design_parameters → `bearingIDClearanceMM` |  | high | extra bore when choosing the output bearing |
| 12 | `maxGearboxDiameter` | formula | `(MAX_GB_DIA_MULT_FACTOR_SMALL_MOTOR if motor_OD < SMALL_MOTOR_DIA_MM else MAX_GB_DIA_MULT_FACTOR) * motor_OD - 2 * ringRadialWidthMMBig` | MAX_GB_DIA_MULT_FACTOR_SMALL_MOTOR, SMALL_MOTOR_DIA_MM, MAX_GB_DIA_MULT_FACTOR, motor_OD, ringRadialWidthMMBig | high | largest gearbox diameter the optimiser may use (gearbox_runner max_diameter); it also sizes the motor case (Motor_case_ID, motor_case_OD_base), which therefore does not follow the chosen design |
| 13 | `actuator_width` | formula | `fw_r_b + clearance_planet + gear_casing_big_ring_to_bearing_dist + carrier_bearing_step_width + bearing_height + case_dist + bearing_retainer_thickness + motor_height + case_mounting_surface_height + standard_clearance_1_5mm + base_plate_thickness` | fw_r_b, clearance_planet, gear_casing_big_ring_to_bearing_dist, carrier_bearing_step_width, bearing_height, case_dist, bearing_retainer_thickness, motor_height, case_mounting_surface_height, standard_clearance_1_5mm, base_plate_thickness | high | axial width without the driver mount, written to the results CSV |
| 14 | `planetMinDistanceMM` | constraint constant | wpg_params.json → wpg_3DP_design_parameters → `planetMinDistanceMM` |  | high | minimum gap between neighbouring planets; only in the old interference check, which WPG doesn't call |
| 15 | `ringRadialWidthMMSmall` | wall thickness | wpg_params.json → wpg_3DP_design_parameters → `ringRadialWidthMMSmall` |  | high | minimum wall of the small ring gear, read by the gearbox class (ring2RadialWidthMM); not written to the CAD file (the CAD ring wall is ring_radial_thickness) |
| 16 | `ringRadialWidthMMBig` | wall thickness | wpg_params.json → wpg_3DP_design_parameters → `ringRadialWidthMMBig` |  | high | minimum wall of the big ring gear, read by the gearbox class (ring1RadialWidthMM); also sets maxGearboxDiameter; not written to the CAD file (the CAD ring wall is ring_radial_thickness) |
| 17 | `sCarrierExtrusionDiaMM` | constraint constant | wpg_params.json → wpg_3DP_design_parameters → `sCarrierExtrusionDiaMM` |  | high | carrier extrusion diameter in the planet-interference constraint |
| 18 | `sCarrierExtrusionClearanceMM` | constraint constant | wpg_params.json → wpg_3DP_design_parameters → `sCarrierExtrusionClearanceMM` |  | high | carrier extrusion clearance in the planet-interference constraint |
| 19 | `gearbox_casing_thickness` | wall thickness | wpg_params.json → wpg_3DP_design_parameters → `gearbox_casing_thickness` |  | high | gearbox casing wall, read by the actuator class; used by the mass model, not written to the CAD file |
| 20 | `small_ring_gear_casing_thickness` | wall thickness | wpg_params.json → wpg_3DP_design_parameters → `small_ring_gear_casing_thickness` |  | high | small-ring casing wall, read by the actuator class; used by the mass model, not written to the CAD file |
| 21 | `GEAR_RATIO_MIN` | search bound | wpg_params.json → wpg_optimization_parameters → `GEAR_RATIO_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 22 | `GEAR_RATIO_MAX` | search bound | wpg_params.json → wpg_optimization_parameters → `GEAR_RATIO_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 23 | `GEAR_RATIO_STEP` | search bound | wpg_params.json → wpg_optimization_parameters → `GEAR_RATIO_STEP` |  | high | optimiser setting: limits of the search, not a part dimension |
| 24 | `MODULE_BIG_MIN` | search bound | wpg_params.json → wpg_optimization_parameters → `MODULE_BIG_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 25 | `MODULE_BIG_MAX` | search bound | wpg_params.json → wpg_optimization_parameters → `MODULE_BIG_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 26 | `MODULE_SMALL_MIN` | search bound | wpg_params.json → wpg_optimization_parameters → `MODULE_SMALL_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 27 | `MODULE_SMALL_MAX` | search bound | wpg_params.json → wpg_optimization_parameters → `MODULE_SMALL_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 28 | `NUM_PLANET_MIN` | search bound | wpg_params.json → wpg_optimization_parameters → `NUM_PLANET_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 29 | `NUM_PLANET_MAX` | search bound | wpg_params.json → wpg_optimization_parameters → `NUM_PLANET_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 30 | `NUM_TEETH_SUN_MIN` | search bound | wpg_params.json → wpg_optimization_parameters → `NUM_TEETH_SUN_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 31 | `NUM_TEETH_PLANET_BIG_MIN` | search bound | wpg_params.json → wpg_optimization_parameters → `NUM_TEETH_PLANET_BIG_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 32 | `NUM_TEETH_PLANET_SMALL_MIN` | search bound | wpg_params.json → wpg_optimization_parameters → `NUM_TEETH_PLANET_SMALL_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 33 | `MAX_GB_DIA_MULT_FACTOR` | search bound | wpg_params.json → wpg_optimization_parameters → `MAX_GB_DIA_MULT_FACTOR` |  | high | optimiser setting: limits of the search, not a part dimension |
| 34 | `MAX_GB_DIA_MULT_FACTOR_SMALL_MOTOR` | search bound | wpg_params.json → wpg_optimization_parameters → `MAX_GB_DIA_MULT_FACTOR_SMALL_MOTOR` |  | high | optimiser setting: limits of the search, not a part dimension |
| 35 | `SMALL_MOTOR_DIA_MM` | search bound | wpg_params.json → wpg_optimization_parameters → `SMALL_MOTOR_DIA_MM` |  | high | optimiser setting: limits of the search, not a part dimension |

## Config blocks WPG doesn't read

- wpg_params.json → `wpg_design_parameters`: older design block; WPG reads only wpg_3DP_design_parameters (gearbox_runner)

## Names in the plain equation file

`CADs/WPG/wpg_equations.txt` writes the same values; these names differ there:

- `"bearing mount thickness"` = `bearing_mount_thickness`
- `"pressure angle"` = `pressure_angle`
