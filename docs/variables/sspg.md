# SSPG variables by category

Generated from `config_files/variables/sspg_variables.json` by `python tools/variables/render.py`; edit the JSON, not this page.

Every SSPG variable sorted into input / optimisation / fixed / dependent. 'cad_variables' are the 113 variables SSPG writes to CADs/SSPG/sspg_equations_onshape.txt, in that order; 'code_only' are values the code uses but does not write to the CAD file; 'unused_config_blocks' are config blocks SSPG never reads. tests/test_variable_categories.py checks the lists against the code, re-evaluates every formula and lookup, checks the stress-rule widths by changing what they depend on, and docs/variables/sspg.md is generated from this file (python tools/variables/render.py).

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
| Optimisation | 4 | 0 |
| Fixed | 43 | 23 |
| Dependent | 48 | 3 |
| **Total** | **113** | **28** |

CAD variables by confidence: high 113, medium 0, low 0

## Rules shared by every gearbox

From `config_files/variables/rules.json`; the test holds every gearbox's file to them.

- names matching `^Nr[0-9]*$` are **Dependent / implicit constraint**: ring-gear teeth are implicitly constrained: the coaxial geometric constraint (e.g. Nr = Ns + 2 x Np) fixes them once the sun and planet teeth are chosen, so the optimiser sets them instead of searching them
- names matching `^fw_(s_calc|p|r)$` are **Dependent / stress rule**: gear face widths follow from the tooth-stress rule: the optimisation variables, the motor torque, the gear material and the safety factors fix them, and the optimiser always takes the smallest width that passes

## Input (18)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `motor_OD` | motor | motors.json → motors.<motor>.geometry → `motorDia` |  | high | read from the chosen motor's geometry |
| 2 | `motor_height` | motor | motors.json → motors.<motor>.geometry → `motorLength` |  | high | read from the chosen motor's geometry |
| 3 | `motor_mount_hole_PCD` | motor | motors.json → motors.<motor>.geometry → `motor_mount_hole_PCD` |  | high | read from the chosen motor's geometry |
| 4 | `motor_mount_hole_dia` | motor | motors.json → motors.<motor>.geometry → `motor_mount_hole_dia` |  | high | read from the chosen motor's geometry |
| 5 | `motor_mount_hole_num` | motor | motors.json → motors.<motor>.geometry → `motor_mount_hole_num` |  | high | read from the chosen motor's geometry |
| 6 | `motor_output_hole_PCD` | motor | motors.json → motors.<motor>.geometry → `motor_output_hole_PCD` |  | high | read from the chosen motor's geometry |
| 7 | `motor_output_hole_dia` | motor | motors.json → motors.<motor>.geometry → `motor_output_hole_dia` |  | high | read from the chosen motor's geometry |
| 8 | `motor_output_hole_num` | motor | motors.json → motors.<motor>.geometry → `motor_output_hole_num` |  | high | read from the chosen motor's geometry |
| 9 | `wire_slot_dist_from_center` | motor | motors.json → motors.<motor>.geometry → `wire_slot_dist_from_center` |  | high | read from the chosen motor's geometry |
| 10 | `wire_slot_length` | motor | motors.json → motors.<motor>.geometry → `wire_slot_length` |  | high | read from the chosen motor's geometry |
| 11 | `wire_slot_radius` | motor | motors.json → motors.<motor>.geometry → `wire_slot_radius` |  | high | read from the chosen motor's geometry |
| 12 | `driver_upper_holes_dist_from_center` | driver | config.json → Motor_drivers.OdrivePro → `driver_upper_holes_dist_from_center` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 13 | `driver_lower_holes_dist_from_center` | driver | config.json → Motor_drivers.OdrivePro → `driver_lower_holes_dist_from_center` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 14 | `driver_side_holes_dist_from_center` | driver | config.json → Motor_drivers.OdrivePro → `driver_side_holes_dist_from_center` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 15 | `driver_mount_holes_dia` | driver | config.json → Motor_drivers.OdrivePro → `driver_mount_holes_dia` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 16 | `driver_mount_inserts_OD` | driver | config.json → Motor_drivers.OdrivePro → `driver_mount_inserts_OD` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 17 | `driver_mount_thickness` | driver | config.json → Motor_drivers.OdrivePro → `driver_mount_thickness` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 18 | `driver_mount_height` | driver | config.json → Motor_drivers.OdrivePro → `driver_mount_height` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |

## Optimisation (4)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `Ns` | teeth | optimiser (`optimizationSingleStageActuator`) |  | high | sun teeth: searched by the optimiser loop |
| 2 | `Np` | teeth | optimiser (`optimizationSingleStageActuator`) |  | high | planet teeth: searched by the optimiser loop |
| 3 | `module` | module | optimiser (`optimizationSingleStageActuator`) |  | high | searched by the optimiser loop (MODULE_MIN..MODULE_MAX, step 0.1) |
| 4 | `num_planet` | planets | optimiser (`optimizationSingleStageActuator`) |  | high | searched by the optimiser loop (NUM_PLANET_MIN..MAX) |

## Fixed (43)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `pressure_angle` | gear standard | config.json → Gear_standard_parameters → `pressureAngleDEG` |  | high | gear standard, the same for every gearbox type |
| 2 | `planet_bore` | planet part | sspg_params.json → sspg_3DP_design_parameters → `planet_bore` |  | high | constant planet bore from the SSPG 3DP design parameters |
| 3 | `clearance_planet` | clearance | sspg_params.json → sspg_3DP_design_parameters → `clearance_planet` |  | high | constant from the SSPG 3DP design parameters |
| 4 | `sec_carrier_thickness` | wall thickness | sspg_params.json → sspg_3DP_design_parameters → `sec_carrier_thickness` |  | high | constant from the SSPG 3DP design parameters |
| 5 | `sun_coupler_hub_thickness` | wall thickness | sspg_params.json → sspg_3DP_design_parameters → `sun_coupler_hub_thickness` |  | high | constant from the SSPG 3DP design parameters |
| 6 | `clearance_sun_coupler_sec_carrier` | clearance | sspg_params.json → sspg_3DP_design_parameters → `clearance_sun_coupler_sec_carrier` |  | high | constant from the SSPG 3DP design parameters |
| 7 | `case_mounting_surface_height` | wall thickness | sspg_params.json → sspg_3DP_design_parameters → `case_mounting_surface_height` |  | high | constant from the SSPG 3DP design parameters |
| 8 | `Motor_case_thickness` | wall thickness | sspg_params.json → sspg_3DP_design_parameters → `Motor_case_thickness` |  | high | constant from the SSPG 3DP design parameters |
| 9 | `case_mounting_hole_dia` | fastener size | sspg_params.json → sspg_3DP_design_parameters → `case_mounting_hole_dia` |  | high | constant from the SSPG 3DP design parameters |
| 10 | `clearance_case_mount_holes_shell_thickness` | clearance | sspg_params.json → sspg_3DP_design_parameters → `clearance_case_mount_holes_shell_thickness` |  | high | constant from the SSPG 3DP design parameters |
| 11 | `base_plate_thickness` | wall thickness | sspg_params.json → sspg_3DP_design_parameters → `base_plate_thickness` |  | high | constant from the SSPG 3DP design parameters |
| 12 | `output_mounting_nut_depth` | fastener size | sspg_params.json → sspg_3DP_design_parameters → `output_mounting_nut_depth` |  | high | constant from the SSPG 3DP design parameters |
| 13 | `output_mounting_hole_dia` | fastener size | sspg_params.json → sspg_3DP_design_parameters → `output_mounting_hole_dia` |  | high | constant from the SSPG 3DP design parameters |
| 14 | `case_mounting_bolt_depth` | fastener size | sspg_params.json → sspg_3DP_design_parameters → `case_mounting_bolt_depth` |  | high | constant from the SSPG 3DP design parameters |
| 15 | `case_mounting_nut_clearance` | clearance | sspg_params.json → sspg_3DP_design_parameters → `case_mounting_nut_clearance` |  | high | constant from the SSPG 3DP design parameters |
| 16 | `central_hole_offset_from_motor_mount_PCD` | feature size | sspg_params.json → sspg_3DP_design_parameters → `central_hole_offset_from_motor_mount_PCD` |  | high | constant from the SSPG 3DP design parameters |
| 17 | `air_flow_hole_offset` | feature size | sspg_params.json → sspg_3DP_design_parameters → `air_flow_hole_offset` |  | high | constant from the SSPG 3DP design parameters |
| 18 | `ring_radial_thickness` | wall thickness | sspg_params.json → sspg_3DP_design_parameters → `ringRadialWidthMM` |  | high | ring gear wall, a copy of ringRadialWidthMM (also used by the gearbox class and the max-diameter rule) |
| 19 | `ring_to_chamfer_clearance` | clearance | sspg_params.json → sspg_3DP_design_parameters → `ring_to_chamfer_clearance` |  | high | constant from the SSPG 3DP design parameters |
| 20 | `Motor_case_OD_base_to_chamfer` | feature size | sspg_params.json → sspg_3DP_design_parameters → `Motor_case_OD_base_to_chamfer` |  | high | constant from the SSPG 3DP design parameters |
| 21 | `pattern_offset_from_motor_case_OD_base` | feature size | sspg_params.json → sspg_3DP_design_parameters → `pattern_offset_from_motor_case_OD_base` |  | high | constant for the decorative/grip pattern on the case |
| 22 | `pattern_bulge_dia` | feature size | sspg_params.json → sspg_3DP_design_parameters → `pattern_bulge_dia` |  | high | constant for the decorative/grip pattern on the case |
| 23 | `pattern_num_bulge` | feature size | sspg_params.json → sspg_3DP_design_parameters → `pattern_num_bulge` |  | high | constant for the decorative/grip pattern on the case |
| 24 | `pattern_depth` | feature size | sspg_params.json → sspg_3DP_design_parameters → `pattern_depth` |  | high | constant for the decorative/grip pattern on the case |
| 25 | `planet_pin_bolt_dia` | fastener size | sspg_params.json → sspg_3DP_design_parameters → `planet_pin_bolt_dia` |  | high | constant from the SSPG 3DP design parameters |
| 26 | `planet_shaft_dia` | planet part | sspg_params.json → sspg_3DP_design_parameters → `planet_shaft_dia` |  | high | constant from the SSPG 3DP design parameters |
| 27 | `planet_shaft_step_offset` | planet part | sspg_params.json → sspg_3DP_design_parameters → `planet_shaft_step_offset` |  | high | constant from the SSPG 3DP design parameters |
| 28 | `planet_bearing_OD` | bearing (chosen part) | sspg_params.json → sspg_3DP_design_parameters → `planet_bearing_OD` |  | high | constant from the SSPG 3DP design parameters |
| 29 | `planet_bearing_width` | bearing (chosen part) | sspg_params.json → sspg_3DP_design_parameters → `planet_bearing_width` |  | high | constant from the SSPG 3DP design parameters |
| 30 | `carrier_trapezoidal_support_sun_offset` | feature size | sspg_params.json → sspg_3DP_design_parameters → `carrier_trapezoidal_support_sun_offset` |  | high | constant from the SSPG 3DP design parameters |
| 31 | `carrier_trapezoidal_support_hole_PCD_offset_bearing_ID` | feature size | sspg_params.json → sspg_3DP_design_parameters → `carrier_trapezoidal_support_hole_PCD_offset_bearing_ID` |  | high | constant from the SSPG 3DP design parameters |
| 32 | `carrier_trapezoidal_support_hole_dia` | fastener size | sspg_params.json → sspg_3DP_design_parameters → `carrier_trapezoidal_support_hole_dia` |  | high | constant from the SSPG 3DP design parameters |
| 33 | `carrier_bearing_step_width` | feature size | sspg_params.json → sspg_3DP_design_parameters → `carrier_bearing_step_width` |  | high | constant from the SSPG 3DP design parameters |
| 34 | `standard_clearance_1_5mm` | clearance | sspg_params.json → sspg_3DP_design_parameters → `standard_clearance_1_5mm` |  | high | constant from the SSPG 3DP design parameters |
| 35 | `standard_fillet_1_5mm` | feature size | sspg_params.json → sspg_3DP_design_parameters → `standard_fillet_1_5mm` |  | high | constant from the SSPG 3DP design parameters |
| 36 | `sun_shaft_bearing_OD` | bearing (chosen part) | sspg_params.json → sspg_3DP_design_parameters → `sun_shaft_bearing_OD` |  | high | constant from the SSPG 3DP design parameters |
| 37 | `sun_shaft_bearing_width` | bearing (chosen part) | sspg_params.json → sspg_3DP_design_parameters → `sun_shaft_bearing_width` |  | high | constant from the SSPG 3DP design parameters |
| 38 | `sun_shaft_bearing_ID` | bearing (chosen part) | sspg_params.json → sspg_3DP_design_parameters → `sun_shaft_bearing_ID` |  | high | constant from the SSPG 3DP design parameters |
| 39 | `standard_bearing_insertion_chamfer` | feature size | sspg_params.json → sspg_3DP_design_parameters → `standard_bearing_insertion_chamfer` |  | high | constant from the SSPG 3DP design parameters |
| 40 | `sun_central_bolt_dia` | fastener size | sspg_params.json → sspg_3DP_design_parameters → `sun_central_bolt_dia` |  | high | constant from the SSPG 3DP design parameters |
| 41 | `bearing_retainer_thickness` | wall thickness | sspg_params.json → sspg_3DP_design_parameters → `bearing_retainer_thickness` |  | high | constant from the SSPG 3DP design parameters |
| 42 | `tight_clearance_3DP` | clearance | sspg_params.json → sspg_3DP_design_parameters → `tight_clearance_3DP` |  | high | 3D-printing fit clearance from the SSPG 3DP design parameters |
| 43 | `loose_clearance_3DP` | clearance | sspg_params.json → sspg_3DP_design_parameters → `loose_clearance_3DP` |  | high | 3D-printing fit clearance from the SSPG 3DP design parameters |

## Dependent (48)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `Nr` | implicit constraint | `Ns + 2 * Np` | Ns, Np | high | implicitly constrained: the geometric (coaxial) constraint Ns + 2 x Np = Nr fixes it, and the optimiser sets it from Ns and Np instead of searching it (the code lists it among the optimisation variables) |
| 2 | `h_a` | formula | `1 * module` | module | high | addendum, standard proportion of the module |
| 3 | `h_b` | formula | `1.25 * module` | module | high | standard proportion of the module (same value as h_f) |
| 4 | `clr_tip_root` | formula | `h_f - h_a` | h_f, h_a | high | tip-root clearance from addendum and dedendum |
| 5 | `h_f` | formula | `1.25 * module` | module | high | dedendum, standard proportion of the module |
| 6 | `bearing_ID` | lookup | `bearings_discrete(idRequiredMM=module * (Ns + Np) + bearingIDClearanceMM)` → getBearingIDMM | module, Ns, Np, bearingIDClearanceMM | high | smallest catalogue bearing whose bore fits around the gears (bearings_discrete) |
| 7 | `bearing_OD` | lookup | `bearings_discrete(idRequiredMM=module * (Ns + Np) + bearingIDClearanceMM)` → getBearingODMM | module, Ns, Np, bearingIDClearanceMM | high | smallest catalogue bearing whose bore fits around the gears (bearings_discrete) |
| 8 | `bearing_height` | lookup | `bearings_discrete(idRequiredMM=module * (Ns + Np) + bearingIDClearanceMM)` → getBearingWidthMM | module, Ns, Np, bearingIDClearanceMM | high | smallest catalogue bearing whose bore fits around the gears (bearings_discrete) |
| 9 | `clearance_motor_and_case` | formula | `clearance_motor_and_case_min if ring_OD < motor_OD else (ring_OD - motor_OD) / 2 + clearance_motor_and_case_min` | ring_OD, motor_OD, clearance_motor_and_case_min | high | radial gap between the motor and the case: the configured minimum, or more when the ring gear is wider than the motor (the same rule is used for the case mass) |
| 10 | `Motor_case_ID` | formula | `motor_OD + clearance_motor_and_case * 2` | motor_OD, clearance_motor_and_case | high | motor case inner diameter |
| 11 | `motor_case_OD_base` | formula | `motor_OD + clearance_motor_and_case * 2 + Motor_case_thickness * 2` | motor_OD, clearance_motor_and_case, Motor_case_thickness | high | motor case outer diameter (body diameter) |
| 12 | `case_mounting_hole_shift` | formula | `case_mounting_hole_dia / 2 - case_mounting_hole_wall_overlap` | case_mounting_hole_dia, case_mounting_hole_wall_overlap | high | how far the case bolt circle sits outside the case wall: half the bolt hole, less the configured overlap |
| 13 | `case_mounting_PCD` | formula | `motor_case_OD_base + case_mounting_hole_shift * 2` | motor_case_OD_base, case_mounting_hole_shift | high | case bolt circle |
| 14 | `case_mounting_hole_allen_socket_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=case_mounting_hole_dia, bolt_type=socket_head)` → bolt_head_dia | case_mounting_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 15 | `Motor_case_OD_max` | formula | `case_mounting_PCD + case_mounting_hole_allen_socket_dia + clearance_case_mount_holes_shell_thickness * 2` | case_mounting_PCD, case_mounting_hole_allen_socket_dia, clearance_case_mount_holes_shell_thickness | high | widest diameter, over the case mounting ears |
| 16 | `dp_s` | formula | `module * Ns` | module, Ns | high | pitch diameter |
| 17 | `db_s` | formula | `dp_s * cos(pressure_angle_rad)` | dp_s, pressure_angle_rad | high | base-circle diameter |
| 18 | `fw_s_calc` | stress rule | b = FOS x Ft x qe x qk / (gear_allowable_stress x module), with Ft = serviceFactor x motor_peak_torque / (num_planet x sun pitch radius), qe = 1 / sun-planet contact ratio, qk = curve fit in Ns (mitStressAnalysisMinFacewidth); fw_s_calc = b | module, Ns, Np, Nr, num_planet, pressure_angle, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor | high | sun face width from the tooth-stress rule: fixed by the optimisation variables, the motor torque, the gear material and the safety factors, so the optimiser has no freedom over it (it takes the smallest width that passes, which is always optimal since width only adds mass). The printed sun uses fw_s_used |
| 19 | `alpha_s` | formula | `(sqrt(dp_s**2 - db_s**2) / db_s) * 180 / pi - pressure_angle_rad * 180 / pi` | dp_s, db_s, pressure_angle_rad | high | involute angle used to draw the tooth |
| 20 | `beta_s` | formula | `(360 / (4 * Ns) - alpha_s) * 2` | Ns, alpha_s | high | tooth angle used to draw the tooth |
| 21 | `dp_p` | formula | `module * Np` | module, Np | high | pitch diameter |
| 22 | `db_p` | formula | `dp_p * cos(pressure_angle_rad)` | dp_p, pressure_angle_rad | high | base-circle diameter |
| 23 | `fw_p` | stress rule | b = FOS x Ft x qe x qk / (gear_allowable_stress x module), with Ft = serviceFactor x motor_peak_torque / (num_planet x sun pitch radius), qe = 1 / sun-planet contact ratio, qk = curve fit in Ns (mitStressAnalysisMinFacewidth); fw = max(b, 2 x planet_bearing_width + planet_bearing_gap) | module, Ns, Np, Nr, num_planet, pressure_angle, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor, planet_bearing_width, planet_bearing_gap | high | planet face width from the tooth-stress rule, at least room for the two planet bearings: fixed by the optimisation variables, the motor torque, the gear material and the safety factors |
| 24 | `alpha_p` | formula | `(sqrt(dp_p**2 - db_p**2) / db_p) * 180 / pi - pressure_angle_rad * 180 / pi` | dp_p, db_p, pressure_angle_rad | high | involute angle used to draw the tooth |
| 25 | `beta_p` | formula | `(360 / (4 * Np) - alpha_p) * 2` | Np, alpha_p | high | tooth angle used to draw the tooth |
| 26 | `dp_r` | formula | `module * Nr` | module, Nr | high | pitch diameter |
| 27 | `db_r` | formula | `dp_r * cos(pressure_angle_rad)` | dp_r, pressure_angle_rad | high | base-circle diameter |
| 28 | `fw_r` | stress rule | b = FOS x Ft x qe x qk / (gear_allowable_stress x module), with Ft = serviceFactor x motor_peak_torque / (num_planet x sun pitch radius), qe = 1 / sun-planet contact ratio, qk = curve fit in Ns (mitStressAnalysisMinFacewidth); fw = max(b, 2 x planet_bearing_width + planet_bearing_gap) | module, Ns, Np, Nr, num_planet, pressure_angle, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor, planet_bearing_width, planet_bearing_gap | high | ring (= planet) face width from the tooth-stress rule, at least room for the two planet bearings: fixed by the optimisation variables, the motor torque, the gear material and the safety factors |
| 29 | `alpha_r` | formula | `(sqrt(dp_r**2 - db_r**2) / db_r) * 180 / pi - pressure_angle_rad * 180 / pi` | dp_r, db_r, pressure_angle_rad | high | involute angle used to draw the tooth |
| 30 | `beta_r` | formula | `(360 / (4 * Nr) + alpha_r) * 2` | Nr, alpha_r | high | tooth angle used to draw the tooth |
| 31 | `case_dist` | formula | `sec_carrier_thickness + clearance_planet + sun_coupler_hub_thickness - case_mounting_surface_height` | sec_carrier_thickness, clearance_planet, sun_coupler_hub_thickness, case_mounting_surface_height | high | axial gap between the motor case and the gearbox case |
| 32 | `bearing_mount_thickness` | formula | `output_mounting_hole_dia * bearing_mount_wall_bolt_dia_multiple if bearing_OD + output_mounting_hole_dia * (2 * bearing_mount_wall_bolt_dia_multiple) > Nr * module + 2 * h_b else ((Nr * module + 2 * h_b) - (bearing_OD + output_mounting_hole_dia * (2 * bearing_mount_wall_bolt_dia_multiple))) / 2 + output_mounting_hole_dia * bearing_mount_wall_bolt_dia_multiple + standard_clearance_1_5mm` | bearing_OD, output_mounting_hole_dia, bearing_mount_wall_bolt_dia_multiple, Nr, module, h_b, standard_clearance_1_5mm | high | wall around the output bearing: the configured number of output-bolt diameters on each side, or wider (plus a clearance) when the ring gear's teeth reach further out (the same rule is used for the mass) |
| 33 | `output_mounting_PCD` | formula | `bearing_OD + bearing_mount_thickness` | bearing_OD, bearing_mount_thickness | high | output bolt circle |
| 34 | `carrier_PCD` | formula | `(Np + Ns) * module` | Np, Ns, module | high | planet-centre circle (twice the centre distance) |
| 35 | `motor_output_hole_CSK_OD` | lookup | `nuts_and_bolts_dimensions(bolt_dia=motor_output_hole_dia, bolt_type=CSK)` → bolt_head_dia | motor_output_hole_dia | high | standard countersunk fastener size for the chosen bolt diameter |
| 36 | `motor_output_hole_CSK_head_height` | lookup | `nuts_and_bolts_dimensions(bolt_dia=motor_output_hole_dia, bolt_type=CSK)` → bolt_head_height | motor_output_hole_dia | high | standard countersunk fastener size for the chosen bolt diameter |
| 37 | `output_mounting_nut_thickness` | lookup | `nuts_and_bolts_dimensions(bolt_dia=output_mounting_hole_dia, bolt_type=socket_head)` → nut_thickness | output_mounting_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 38 | `output_mounting_nut_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=output_mounting_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | output_mounting_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 39 | `case_mounting_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=case_mounting_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | case_mounting_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 40 | `case_mounting_nut_thickness` | lookup | `nuts_and_bolts_dimensions(bolt_dia=case_mounting_hole_dia, bolt_type=socket_head)` → nut_thickness | case_mounting_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 41 | `ring_OD` | formula | `dp_r + 2 * ring_radial_thickness` | dp_r, ring_radial_thickness | high | ring gear outer diameter |
| 42 | `planet_pin_socket_head_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=planet_pin_bolt_dia, bolt_type=socket_head)` → bolt_head_dia | planet_pin_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 43 | `planet_pin_bolt_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=planet_pin_bolt_dia, bolt_type=socket_head)` → nut_width_across_flats | planet_pin_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 44 | `carrier_trapezoidal_support_hole_socket_head_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=carrier_trapezoidal_support_hole_dia, bolt_type=socket_head)` → bolt_head_dia | carrier_trapezoidal_support_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 45 | `carrier_trapezoidal_support_hole_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=carrier_trapezoidal_support_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | carrier_trapezoidal_support_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 46 | `sun_hub_dia` | formula | `motor_output_hole_PCD + motor_output_hole_dia + standard_clearance_1_5mm * 4` | motor_output_hole_PCD, motor_output_hole_dia, standard_clearance_1_5mm | high | sun coupler hub, sized to the motor's output holes |
| 47 | `sun_central_bolt_socket_head_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=sun_central_bolt_dia, bolt_type=socket_head)` → bolt_head_dia | sun_central_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 48 | `fw_s_used` | formula | `fw_p + clearance_planet + sec_carrier_thickness + standard_clearance_1_5mm` | fw_p, clearance_planet, sec_carrier_thickness, standard_clearance_1_5mm | high | printed sun length: planet width plus the carrier and clearances |

## Used by the code, not written to the CAD file (28)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `ringRadialWidthMM` | constraint constant | sspg_params.json → sspg_3DP_design_parameters → `ringRadialWidthMM` |  | high | ring wall used by the max-diameter rule; written to the CAD as ring_radial_thickness |
| 2 | `planetMinDistanceMM` | constraint constant | sspg_params.json → sspg_3DP_design_parameters → `planetMinDistanceMM` |  | high | minimum gap between neighbouring planets (old interference check) |
| 3 | `sCarrierExtrusionDiaMM` | constraint constant | sspg_params.json → sspg_3DP_design_parameters → `sCarrierExtrusionDiaMM` |  | high | carrier extrusion diameter in the planet-interference constraint |
| 4 | `sCarrierExtrusionClearanceMM` | constraint constant | sspg_params.json → sspg_3DP_design_parameters → `sCarrierExtrusionClearanceMM` |  | high | clearance in the planet-interference constraint |
| 5 | `bearingIDClearanceMM` | constraint constant | sspg_params.json → sspg_3DP_design_parameters → `bearingIDClearanceMM` |  | high | extra bore when choosing the output bearing |
| 6 | `clearance_motor_and_case_min` | constraint constant | sspg_params.json → sspg_3DP_design_parameters → `clearance_motor_and_case_min` |  | high | smallest radial gap between the motor and the case; sets clearance_motor_and_case (CAD) and the case mass |
| 7 | `case_mounting_hole_wall_overlap` | constraint constant | sspg_params.json → sspg_3DP_design_parameters → `case_mounting_hole_wall_overlap` |  | high | how far the case mounting holes cut into the case wall (0 = the hole just touches the wall); sets case_mounting_hole_shift |
| 8 | `bearing_mount_wall_bolt_dia_multiple` | constraint constant | sspg_params.json → sspg_3DP_design_parameters → `bearing_mount_wall_bolt_dia_multiple` |  | high | bearing-mount wall per side, in output-bolt diameters; sets bearing_mount_thickness (CAD) and the bearing-holding structure mass |
| 9 | `planet_bearing_gap` | constraint constant | sspg_params.json → sspg_3DP_design_parameters → `planet_bearing_gap` |  | high | axial gap between the two bearings inside a planet; with them it sets the smallest planet (and ring) face width |
| 10 | `pressure_angle_rad` | formula | `pressure_angle * pi / 180` | pressure_angle | high | pressure angle in radians (code attribute pressure_angle) |
| 11 | `maxGearboxDiameter` | formula | `(MAX_GB_DIA_MULT_FACTOR_SMALL_MOTOR if motor_OD < SMALL_MOTOR_DIA_MM else MAX_GB_DIA_MULT_FACTOR) * motor_OD - 2 * ringRadialWidthMM` | MAX_GB_DIA_MULT_FACTOR, MAX_GB_DIA_MULT_FACTOR_SMALL_MOTOR, SMALL_MOTOR_DIA_MM, motor_OD, ringRadialWidthMM | high | largest gear diameter the optimiser may use (gearbox_runner max_diameter) |
| 12 | `actuator_width` | formula | `motor_height + case_mounting_surface_height + standard_clearance_1_5mm + base_plate_thickness + case_dist + bearing_height + standard_clearance_1_5mm + fw_r + clearance_planet + bearing_retainer_thickness` | motor_height, case_mounting_surface_height, standard_clearance_1_5mm, base_plate_thickness, case_dist, bearing_height, fw_r, clearance_planet, bearing_retainer_thickness | high | axial width without the driver mount, written to the results CSV |
| 13 | `motor_peak_torque` | motor | motors.json → motors.<motor>.electrical → `peak_torque_Nm` |  | high | motor torque the gears are sized for (peak torque under the default rating setting); sets the face widths |
| 14 | `gear_allowable_stress` | material | config.json → Material_properties.<gear material> → `maxAllowableStressMPa` |  | high | allowable tooth stress of the gear material, chosen with the material mode (3dp: PLA, metal: steel); sets the face widths |
| 15 | `FOS` | safety factor | config.json → MIT_params → `FOS` |  | high | factor of safety in the tooth-stress rule |
| 16 | `serviceFactor` | safety factor | config.json → MIT_params → `serviceFactor` |  | high | service factor on the motor torque in the tooth-stress rule |
| 17 | `GEAR_RATIO_MIN` | search bound | sspg_params.json → sspg_optimization_parameters → `GEAR_RATIO_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 18 | `GEAR_RATIO_MAX` | search bound | sspg_params.json → sspg_optimization_parameters → `GEAR_RATIO_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 19 | `GEAR_RATIO_STEP` | search bound | sspg_params.json → sspg_optimization_parameters → `GEAR_RATIO_STEP` |  | high | optimiser setting: limits of the search, not a part dimension |
| 20 | `MODULE_MIN` | search bound | sspg_params.json → sspg_optimization_parameters → `MODULE_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 21 | `MODULE_MAX` | search bound | sspg_params.json → sspg_optimization_parameters → `MODULE_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 22 | `NUM_PLANET_MIN` | search bound | sspg_params.json → sspg_optimization_parameters → `NUM_PLANET_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 23 | `NUM_PLANET_MAX` | search bound | sspg_params.json → sspg_optimization_parameters → `NUM_PLANET_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 24 | `NUM_TEETH_SUN_MIN` | search bound | sspg_params.json → sspg_optimization_parameters → `NUM_TEETH_SUN_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 25 | `NUM_TEETH_PLANET_MIN` | search bound | sspg_params.json → sspg_optimization_parameters → `NUM_TEETH_PLANET_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 26 | `MAX_GB_DIA_MULT_FACTOR` | search bound | sspg_params.json → sspg_optimization_parameters → `MAX_GB_DIA_MULT_FACTOR` |  | high | optimiser setting: limits of the search, not a part dimension |
| 27 | `MAX_GB_DIA_MULT_FACTOR_SMALL_MOTOR` | search bound | sspg_params.json → sspg_optimization_parameters → `MAX_GB_DIA_MULT_FACTOR_SMALL_MOTOR` |  | high | optimiser setting: limits of the search, not a part dimension |
| 28 | `SMALL_MOTOR_DIA_MM` | search bound | sspg_params.json → sspg_optimization_parameters → `SMALL_MOTOR_DIA_MM` |  | high | optimiser setting: limits of the search, not a part dimension |

## Config blocks SSPG doesn't read

- sspg_params.json → `sspg_design_parameters`: older design block; SSPG reads only sspg_3DP_design_parameters (gearbox_runner)
- sspg_params.json → `sspg_3DP_design_parameters_old`: superseded by sspg_3DP_design_parameters; nothing reads it

## Names in the plain equation file

`CADs/SSPG/sspg_equations.txt` writes the same values; these names differ there:

- `"pressure angle"` = `pressure_angle`
- `"bearing mount thickness"` = `bearing_mount_thickness`
