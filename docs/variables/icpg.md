# ICPG variables by category

Generated from `config_files/variables/icpg_variables.json` by `python tools/variables/render.py`; edit the JSON, not this page.

Every ISSPG icpg variable sorted into input / optimisation / fixed / dependent. 'cad_variables' are the 117 variables ISSPG icpg writes to CADs/ISSPG/isspg_icpg_equations_onshape.txt, in that order (this gearbox has no other equation file); 'code_only' are values the code uses but does not write to the CAD file, plus every config key the CAD does not use; 'unused_config_blocks' are config blocks ISSPG never reads. tests/test_variable_categories.py checks the lists against the code and re-evaluates every formula and lookup; docs/variables/icpg.md is generated from this file (python tools/variables/render.py).

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
| Input | 25 | 2 |
| Optimisation | 5 | 1 |
| Fixed | 48 | 22 |
| Dependent | 39 | 4 |
| **Total** | **117** | **29** |

CAD variables by confidence: high 106, medium 11, low 0

## To review (not high confidence)

- `sun_hub_dia` (Dependent, medium): sun hub: sized to the rotor's mount holes plus a hard-coded x 4 clearance margin, capped at the rotor's outer diameter less two clearances (the shared sun-hub margin item the plan still has to decide)
- `fw_s_used` (Dependent, medium): printed sun length: the stack of bearings, hub, carrier and planet widths, but at least the motor height when the stator's radial clearance around the output bearing is below a hard-coded 2 x standard_clearance_1_5mm (a two-case floor rule; the plan asks whether the 2 is geometry or tuning)
- `sun_bottom_casing_bearing_ID` (Dependent, medium): catalogue bearing chosen by bearings_discrete (smallest one that fits) (the request has a hard-coded number: x 4 clearance margin); this is its bore
- `sun_bottom_casing_bearing_OD` (Dependent, medium): catalogue bearing chosen by bearings_discrete (smallest one that fits) (the request has a hard-coded number: x 4 clearance margin); this is its outer diameter
- `sun_bottom_casing_bearing_height` (Dependent, medium): catalogue bearing chosen by bearings_discrete (smallest one that fits) (the request has a hard-coded number: x 4 clearance margin); this is its width
- `driver_mount_thickness` (Input, medium): motor-driver mount dimension: the runner passes no driver here, so the value comes from this gearbox's own config rather than from the chosen driver (Input / driver for consistency with the other types; the plan asks whether it should be Fixed)
- `driver_mount_inserts_OD` (Input, medium): motor-driver mount dimension: the runner passes no driver here, so the value comes from this gearbox's own config rather than from the chosen driver (Input / driver for consistency with the other types; the plan asks whether it should be Fixed)
- `driver_upper_holes_dist_from_center` (Input, medium): motor-driver mount dimension: the runner passes no driver here, so the value comes from this gearbox's own config rather than from the chosen driver (Input / driver for consistency with the other types; the plan asks whether it should be Fixed)
- `driver_lower_holes_dist_from_center` (Input, medium): motor-driver mount dimension: the runner passes no driver here, so the value comes from this gearbox's own config rather than from the chosen driver (Input / driver for consistency with the other types; the plan asks whether it should be Fixed)
- `driver_mount_height` (Input, medium): motor-driver mount dimension: the runner passes no driver here, so the value comes from this gearbox's own config rather than from the chosen driver (Input / driver for consistency with the other types; the plan asks whether it should be Fixed)
- `driver_side_holes_dist_from_center` (Input, medium): motor-driver mount dimension: the runner passes no driver here, so the value comes from this gearbox's own config rather than from the chosen driver (Input / driver for consistency with the other types; the plan asks whether it should be Fixed)

## Rules shared by every gearbox

From `config_files/variables/rules.json`; the test holds every gearbox's file to them.

- names matching `^(a[12]_)?Nr(_[bs]|[0-9]*)$` are **Dependent / implicit constraint**: ring-gear teeth are implicitly constrained: the coaxial geometric constraint (e.g. Nr = Ns + 2 x Np) fixes them once the sun and planet teeth are chosen, so the optimiser sets them instead of searching them
- names matching `^fw_(s_calc|p|p_b|r|r_s)$` are **Dependent / stress rule**: gear face widths follow from the tooth-stress rule: the optimisation variables, the motor torque, the gear material and the safety factors fix them, and the optimiser always takes the smallest width that passes (widths that are a formula of another width, e.g. CPG's fw_p_s = fw_r + clearance_planet, are dependent / formula) Exceptions: inwpg_dependent: `fw_p_b`; inwpg_independent: `fw_p_b`; incpg_dependent: `fw_r`; incpg_independent: `fw_r`.
- names matching `^a[12]_fw_(s_calc|r)[12]?$` are **Dependent / stress rule**: the same stress-rule face widths in a two-stage gearbox, under the stage prefixes a1_ / a2_ (the planet width a1_fw_p / a2_fw_p is a copy of the ring width, so it is dependent / formula and not in this rule)

## Input (25)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `rotor_mount_hole_PCD` | motor | motors.json → motors.<motor>.geometry → `motor_rotor_hole_PCD` |  | high | read from the chosen motor's geometry |
| 2 | `rotor_mount_hole_dia` | motor | motors.json → motors.<motor>.geometry → `motor_rotor_hole_dia` |  | high | read from the chosen motor's geometry |
| 3 | `rotor_mount_hole_num` | motor | motors.json → motors.<motor>.geometry → `motor_rotor_hole_num` |  | high | read from the chosen motor's geometry |
| 4 | `stator_OD` | motor | motors.json → motors.<motor>.geometry → `stator_OD` |  | high | read from the chosen motor's geometry |
| 5 | `stator_ID` | motor | motors.json → motors.<motor>.geometry → `stator_ID` |  | high | read from the chosen motor's geometry |
| 6 | `stator_height` | motor | motors.json → motors.<motor>.geometry → `stator_height` |  | high | read from the chosen motor's geometry |
| 7 | `stator_mounting_holes_PCD` | motor | motors.json → motors.<motor>.geometry → `stator_hole_PCD` |  | high | read from the chosen motor's geometry |
| 8 | `stator_top_rotor_top_offset` | motor | motors.json → motors.<motor>.geometry → `stator_top_rotor_top_offset` |  | high | read from the chosen motor's geometry |
| 9 | `stator_hole_dia` | motor | motors.json → motors.<motor>.geometry → `stator_hole_dia` |  | high | read from the chosen motor's geometry |
| 10 | `Rotor_ID` | motor | motors.json → motors.<motor>.geometry → `rotor_ID` |  | high | read from the chosen motor's geometry |
| 11 | `Rotor_OD` | motor | motors.json → motors.<motor>.geometry → `motor_OD` |  | high | read from the chosen motor's geometry |
| 12 | `Rotor_height` | motor | motors.json → motors.<motor>.geometry → `rotor_height` |  | high | read from the chosen motor's geometry |
| 13 | `Rotor_bottom_ID` | motor | motors.json → motors.<motor>.geometry → `motor_rotor_base_ID` |  | high | read from the chosen motor's geometry |
| 14 | `rotor_bottom_thickness` | motor | motors.json → motors.<motor>.geometry → `motor_rotor_base_thickness` |  | high | read from the chosen motor's geometry |
| 15 | `Rotor_csk_head_upper_dia` | motor | motors.json → motors.<motor>.geometry → `rotorCSKHeadUpperDiaMM` |  | high | read from the chosen motor's geometry |
| 16 | `Rotor_csk_head_height` | motor | motors.json → motors.<motor>.geometry → `rotorCSKHeadHeightMM` |  | high | read from the chosen motor's geometry |
| 17 | `motor_height` | motor | motors.json → motors.<motor>.geometry → `motor_height` |  | high | read from the chosen motor's geometry |
| 18 | `motor_stator_extrusion_dia` | motor | motors.json → motors.<motor>.geometry → `motor_stator_extrusion_dia` |  | high | read from the chosen motor's geometry |
| 19 | `motor_stator_extrusion_depth` | motor | motors.json → motors.<motor>.geometry → `motor_stator_extrusion_depth` |  | high | read from the chosen motor's geometry |
| 20 | `driver_mount_thickness` | driver | icpg_params.json → cpg_3DP_design_parameters → `driver_mount_thickness` |  | medium | motor-driver mount dimension: the runner passes no driver here, so the value comes from this gearbox's own config rather than from the chosen driver (Input / driver for consistency with the other types; the plan asks whether it should be Fixed) |
| 21 | `driver_mount_inserts_OD` | driver | icpg_params.json → cpg_3DP_design_parameters → `driver_mount_inserts_OD` |  | medium | motor-driver mount dimension: the runner passes no driver here, so the value comes from this gearbox's own config rather than from the chosen driver (Input / driver for consistency with the other types; the plan asks whether it should be Fixed) |
| 22 | `driver_upper_holes_dist_from_center` | driver | icpg_params.json → cpg_3DP_design_parameters → `driver_upper_holes_dist_from_center` |  | medium | motor-driver mount dimension: the runner passes no driver here, so the value comes from this gearbox's own config rather than from the chosen driver (Input / driver for consistency with the other types; the plan asks whether it should be Fixed) |
| 23 | `driver_lower_holes_dist_from_center` | driver | icpg_params.json → cpg_3DP_design_parameters → `driver_lower_holes_dist_from_center` |  | medium | motor-driver mount dimension: the runner passes no driver here, so the value comes from this gearbox's own config rather than from the chosen driver (Input / driver for consistency with the other types; the plan asks whether it should be Fixed) |
| 24 | `driver_mount_height` | driver | icpg_params.json → cpg_3DP_design_parameters → `driver_mount_height` |  | medium | motor-driver mount dimension: the runner passes no driver here, so the value comes from this gearbox's own config rather than from the chosen driver (Input / driver for consistency with the other types; the plan asks whether it should be Fixed) |
| 25 | `driver_side_holes_dist_from_center` | driver | icpg_params.json → cpg_3DP_design_parameters → `driver_side_holes_dist_from_center` |  | medium | motor-driver mount dimension: the runner passes no driver here, so the value comes from this gearbox's own config rather than from the chosen driver (Input / driver for consistency with the other types; the plan asks whether it should be Fixed) |

## Optimisation (5)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `Ns` | teeth | optimiser (`optimizationInternalCompoundPlanetaryActuator`) |  | high | sun teeth: searched by the optimiser loop |
| 2 | `Np_b` | teeth | optimiser (`optimizationInternalCompoundPlanetaryActuator`) |  | high | big planet teeth: searched by the optimiser loop |
| 3 | `Np_s` | teeth | optimiser (`optimizationInternalCompoundPlanetaryActuator`) |  | high | small planet teeth: searched by the optimiser loop |
| 4 | `num_planet` | planets | optimiser (`optimizationInternalCompoundPlanetaryActuator`) |  | high | number of planets: searched by the optimiser loop |
| 5 | `module` | module | optimiser (`optimizationInternalCompoundPlanetaryActuator`) |  | high | the big module (sun, big planet): searched by the optimiser loop; the CAD file has this one module although the small planet and the ring use the small module module_s (code-only; same pattern as CPG bug 18) |

## Fixed (48)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `pressure_angle` | gear standard | motor_config.json → Gear_standard_parameters → `pressureAngleDEG` |  | high | gear standard, the same for every gearbox type |
| 2 | `clearance_planet` | clearance | icpg_params.json → cpg_3DP_design_parameters → `clearance_planet` |  | high | constant from the ICPG 3DP design parameters |
| 3 | `sec_carrier_thickness` | wall thickness | icpg_params.json → cpg_3DP_design_parameters → `sec_carrier_thickness` |  | high | constant from the ICPG 3DP design parameters |
| 4 | `sun_coupler_hub_thickness` | wall thickness | icpg_params.json → cpg_3DP_design_parameters → `sun_coupler_hub_thickness` |  | high | constant from the ICPG 3DP design parameters |
| 5 | `planet_pin_bolt_dia` | fastener size | icpg_params.json → cpg_3DP_design_parameters → `planet_pin_bolt_dia` |  | high | constant from the ICPG 3DP design parameters |
| 6 | `planet_shaft_dia` | planet part | icpg_params.json → cpg_3DP_design_parameters → `planet_shaft_dia` |  | high | constant from the ICPG 3DP design parameters |
| 7 | `planet_shaft_step_offset` | planet part | icpg_params.json → cpg_3DP_design_parameters → `planet_shaft_step_offset` |  | high | constant from the ICPG 3DP design parameters |
| 8 | `carrier_trapezoidal_support_sun_offset` | feature size | icpg_params.json → cpg_3DP_design_parameters → `carrier_trapezoidal_support_sun_offset` |  | high | constant from the ICPG 3DP design parameters |
| 9 | `carrier_trapezoidal_support_hole_PCD_offset_bearing_ID` | feature size | icpg_params.json → cpg_3DP_design_parameters → `carrier_trapezoidal_support_hole_PCD_offset_bearing_ID` |  | high | constant from the ICPG 3DP design parameters |
| 10 | `carrier_trapezoidal_support_hole_dia` | fastener size | icpg_params.json → cpg_3DP_design_parameters → `carrier_trapezoidal_support_hole_dia` |  | high | constant from the ICPG 3DP design parameters |
| 11 | `carrier_bearing_step_width` | feature size | icpg_params.json → cpg_3DP_design_parameters → `carrier_bearing_step_width` |  | high | constant from the ICPG 3DP design parameters |
| 12 | `standard_clearance_1_5mm` | clearance | icpg_params.json → cpg_3DP_design_parameters → `standard_clearance_1_5mm` |  | high | constant from the ICPG 3DP design parameters |
| 13 | `standard_fillet_1_5mm` | feature size | icpg_params.json → cpg_3DP_design_parameters → `standard_fillet_1_5mm` |  | high | constant from the ICPG 3DP design parameters |
| 14 | `sun_shaft_bearing_OD` | bearing (chosen part) | icpg_params.json → cpg_3DP_design_parameters → `sun_shaft_bearing_OD` |  | high | constant from the ICPG 3DP design parameters |
| 15 | `sun_shaft_bearing_width` | bearing (chosen part) | icpg_params.json → cpg_3DP_design_parameters → `sun_shaft_bearing_width` |  | high | constant from the ICPG 3DP design parameters |
| 16 | `sun_shaft_bearing_ID` | bearing (chosen part) | icpg_params.json → cpg_3DP_design_parameters → `sun_shaft_bearing_ID` |  | high | constant from the ICPG 3DP design parameters |
| 17 | `standard_bearing_insertion_chamfer` | feature size | icpg_params.json → cpg_3DP_design_parameters → `standard_bearing_insertion_chamfer` |  | high | constant from the ICPG 3DP design parameters |
| 18 | `planet_bearing_OD` | bearing (chosen part) | icpg_params.json → cpg_3DP_design_parameters → `planet_bearing_OD` |  | high | constant from the ICPG 3DP design parameters |
| 19 | `planet_bearing_width` | bearing (chosen part) | icpg_params.json → cpg_3DP_design_parameters → `planet_bearing_width` |  | high | constant from the ICPG 3DP design parameters |
| 20 | `planet_bore` | planet part | icpg_params.json → cpg_3DP_design_parameters → `planet_bore` |  | high | constant from the ICPG 3DP design parameters |
| 21 | `sun_central_bolt_dia` | fastener size | icpg_params.json → cpg_3DP_design_parameters → `sun_central_bolt_dia` |  | high | constant from the ICPG 3DP design parameters |
| 22 | `bearing_retainer_thickness` | wall thickness | icpg_params.json → cpg_3DP_design_parameters → `bearing_retainer_thickness` |  | high | constant from the ICPG 3DP design parameters |
| 23 | `tight_clearance_3DP` | clearance | icpg_params.json → cpg_3DP_design_parameters → `tight_clearance_3DP` |  | high | constant from the ICPG 3DP design parameters |
| 24 | `loose_clearance_3DP` | clearance | icpg_params.json → cpg_3DP_design_parameters → `loose_clearance_3DP` |  | high | constant from the ICPG 3DP design parameters |
| 25 | `sun_gear_rotor_nut_wrench_size` | fastener size | icpg_params.json → cpg_3DP_design_parameters → `sun_gear_rotor_nut_wrench_size` |  | high | constant from the ICPG 3DP design parameters |
| 26 | `sun_gear_rotor_nut_height` | feature size | icpg_params.json → cpg_3DP_design_parameters → `sun_gear_rotor_nut_height` |  | high | constant from the ICPG 3DP design parameters |
| 27 | `stator_mounting_hole_allen_socket_head_dia` | feature size | icpg_params.json → cpg_3DP_design_parameters → `stator_mounting_hole_allen_socket_head_dia` |  | high | constant from the ICPG 3DP design parameters |
| 28 | `bearing_retainer_hole_dia` | fastener size | icpg_params.json → cpg_3DP_design_parameters → `bearing_retainer_hole_dia` |  | high | constant from the ICPG 3DP design parameters |
| 29 | `bearing_retainer_hole_num` | fastener size | icpg_params.json → cpg_3DP_design_parameters → `bearing_retainer_hole_num` |  | high | constant from the ICPG 3DP design parameters |
| 30 | `ring_gear_thickness_mounting_casing` | wall thickness | icpg_params.json → cpg_3DP_design_parameters → `ring_gear_thickness_mounting_casing` |  | high | constant from the ICPG 3DP design parameters |
| 31 | `motor_casing_thickness` | wall thickness | icpg_params.json → cpg_3DP_design_parameters → `Motor_case_thickness` |  | high | constant from the ICPG 3DP design parameters |
| 32 | `sun_sec_carrier_bearing_height` | bearing (chosen part) | icpg_params.json → cpg_3DP_design_parameters → `sun_sec_carrier_bearing_height` |  | high | constant from the ICPG 3DP design parameters |
| 33 | `sun_sec_carrier_bearing_ID` | bearing (chosen part) | icpg_params.json → cpg_3DP_design_parameters → `sun_sec_carrier_bearing_ID` |  | high | constant from the ICPG 3DP design parameters |
| 34 | `sun_sec_carrier_bearing_OD` | bearing (chosen part) | icpg_params.json → cpg_3DP_design_parameters → `sun_sec_carrier_bearing_OD` |  | high | constant from the ICPG 3DP design parameters |
| 35 | `case_mounting_hole_dia` | fastener size | icpg_params.json → cpg_3DP_design_parameters → `case_mounting_hole_dia` |  | high | constant from the ICPG 3DP design parameters |
| 36 | `case_mounting_hole_wrench_size` | fastener size | icpg_params.json → cpg_3DP_design_parameters → `case_mounting_hole_wrench_size` |  | high | constant from the ICPG 3DP design parameters |
| 37 | `case_mounting_hole_wrench_thickness` | fastener size | icpg_params.json → cpg_3DP_design_parameters → `case_mounting_hole_wrench_thickness` |  | high | constant from the ICPG 3DP design parameters |
| 38 | `driver_mount_PCD` | feature size | icpg_params.json → cpg_3DP_design_parameters → `driver_mount_PCD` |  | high | constant from the ICPG 3DP design parameters |
| 39 | `driver_mount_hole_dia` | fastener size | icpg_params.json → cpg_3DP_design_parameters → `driver_mount_hole_dia` |  | high | constant from the ICPG 3DP design parameters |
| 40 | `driver_mount_wrench_size` | fastener size | icpg_params.json → cpg_3DP_design_parameters → `driver_mount_wrench_size` |  | high | constant from the ICPG 3DP design parameters |
| 41 | `driver_mount_wrench_thickness` | fastener size | icpg_params.json → cpg_3DP_design_parameters → `driver_mount_wrench_thickness` |  | high | constant from the ICPG 3DP design parameters |
| 42 | `case_mounting_wrench_size` | fastener size | icpg_params.json → cpg_3DP_design_parameters → `case_mounting_wrench_size` |  | high | constant from the ICPG 3DP design parameters: a config value here, where the other types look the size up from the bolt table |
| 43 | `case_mounting_hole_allen_socket_dia` | feature size | icpg_params.json → cpg_3DP_design_parameters → `case_mounting_hole_allen_socket_dia` |  | high | constant from the ICPG 3DP design parameters: a config value here, where the other types look the size up from the bolt table |
| 44 | `clearance_case_mount_holes_shell_thickness` | clearance | icpg_params.json → cpg_3DP_design_parameters → `clearance_case_mount_holes_shell_thickness` |  | high | constant from the ICPG 3DP design parameters |
| 45 | `motor_case_mounting_hole_dia` | fastener size | icpg_params.json → cpg_3DP_design_parameters → `motor_case_mounting_hole_dia` |  | high | constant from the ICPG 3DP design parameters |
| 46 | `motor_case_wrench_size` | fastener size | icpg_params.json → cpg_3DP_design_parameters → `motor_case_wrench_size` |  | high | constant from the ICPG 3DP design parameters |
| 47 | `central_hole_offset_from_motor_mount_PCD` | feature size | icpg_params.json → cpg_3DP_design_parameters → `central_hole_offset_from_motor_mount_PCD` |  | high | constant from the ICPG 3DP design parameters |
| 48 | `motor_mount_driver_hole_num` | fastener size | icpg_params.json → cpg_3DP_design_parameters → `motor_mount_driver_hole_num` |  | high | constant from the ICPG 3DP design parameters |

## Dependent (39)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `Nr` | implicit constraint | `Ns + Np_b + Np_s` | Ns, Np_b, Np_s | high | implicitly constrained: the coaxial constraint gives Nr = Ns + Np_b + Np_s (with equal modules), which the optimiser sets on the gearbox; the code lists it among the optimisation variables |
| 2 | `h_a` | formula | `1 * module` | module | high | addendum, standard proportion of the module |
| 3 | `h_b` | formula | `1.25 * module` | module | high | standard proportion of the module (same value as h_f) |
| 4 | `clr_tip_root` | formula | `h_f - h_a` | h_f, h_a | high | tip-root clearance from addendum and dedendum |
| 5 | `dp_s` | formula | `module * Ns` | module, Ns | high | pitch diameter |
| 6 | `db_s` | formula | `dp_s * cos(pressure_angle_rad)` | dp_s, pressure_angle_rad | high | base-circle diameter |
| 7 | `fw_s_calc` | stress rule | two stress widths, b = FOS x Ft x qe x qk / (gear_allowable_stress x module): b1 for the sun - big planet mesh (module, Ft from serviceFactor x motor_peak_torque at the sun, qe from the sun-planet contact ratio, qk from Ns) and b2 for the small planet - ring mesh (module_s, qk from Np_s); then, if b1 + b2 < 2 x planet_bearing_width + planet_bearing_gap, each planet gear is raised to at least planet_bearing_width + planet_bearing_gap / 2 (one bearing per gear, half the gap each; mitStressAnalysisMinFacewidth); fw_s_calc = b1; then the two planet steps (big + small + planet_step_gap_mm) must fit the stator height less gear_axial_margin_mm: when they are longer, all four widths are scaled by (stator_height - gear_axial_margin_mm - planet_step_gap_mm) / (big + small), so the capped gears carry the same fraction of the torque | module, module_s, Ns, Np_b, Np_s, Nr, num_planet, pressure_angle, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor, stator_height, gear_axial_margin_mm, planet_step_gap_mm | high | sun face width from the tooth-stress rule, scaled by the stator-height cap when it applies: fixed by the optimisation variables, the motor torque, the gear material, the safety factors and the cap |
| 8 | `alpha_s` | formula | `sqrt(dp_s ** 2 - db_s ** 2) / db_s * 180 / pi - pressure_angle` | pressure_angle, db_s, dp_s | high | involute angle used to draw the tooth |
| 9 | `beta_s` | formula | `(360 / (4 * Ns) - alpha_s) * 2` | alpha_s, Ns | high | tooth angle used to draw the tooth |
| 10 | `dp_p_b` | formula | `module * Np_b` | module, Np_b | high | big-planet pitch diameter |
| 11 | `db_p_b` | formula | `dp_p_b * cos(pressure_angle_rad)` | dp_p_b, pressure_angle_rad | high | base-circle diameter |
| 12 | `fw_p_s` | formula | `fw_r + clearance_planet` | fw_r, clearance_planet | high | small-planet width: the ring width plus a clearance (a formula, not the stress rule) |
| 13 | `alpha_p_b` | formula | `sqrt(dp_p_b ** 2 - db_p_b ** 2) / db_p_b * 180 / pi - pressure_angle` | pressure_angle, db_p_b, dp_p_b | high | involute angle used to draw the tooth |
| 14 | `beta_p_b` | formula | `(360 / (4 * Np_b) - alpha_p_b) * 2` | alpha_p_b, Np_b | high | tooth angle used to draw the tooth |
| 15 | `h_f` | formula | `1.25 * module` | module | high | dedendum, standard proportion of the module |
| 16 | `dp_r` | formula | `module * Nr` | module, Nr | high | pitch diameter |
| 17 | `db_r` | formula | `dp_r * cos(pressure_angle_rad)` | dp_r, pressure_angle_rad | high | base-circle diameter |
| 18 | `fw_r` | stress rule | two stress widths, b = FOS x Ft x qe x qk / (gear_allowable_stress x module): b1 for the sun - big planet mesh (module, Ft from serviceFactor x motor_peak_torque at the sun, qe from the sun-planet contact ratio, qk from Ns) and b2 for the small planet - ring mesh (module_s, qk from Np_s); then, if b1 + b2 < 2 x planet_bearing_width + planet_bearing_gap, each planet gear is raised to at least planet_bearing_width + planet_bearing_gap / 2 (one bearing per gear, half the gap each; mitStressAnalysisMinFacewidth); fw_r = b2 (raised); then the two planet steps (big + small + planet_step_gap_mm) must fit the stator height less gear_axial_margin_mm: when they are longer, all four widths are scaled by (stator_height - gear_axial_margin_mm - planet_step_gap_mm) / (big + small), so the capped gears carry the same fraction of the torque | module, module_s, Ns, Np_b, Np_s, Nr, num_planet, pressure_angle, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor, stator_height, gear_axial_margin_mm, planet_step_gap_mm, planet_bearing_width, planet_bearing_gap | high | ring face width from the tooth-stress rule (the small planet - ring mesh), raised to hold the planet bearing and scaled by the stator-height cap; the small planet's width fw_p_s is this plus clearance_planet |
| 19 | `alpha_r` | formula | `sqrt(dp_r ** 2 - db_r ** 2) / db_r * 180 / pi - pressure_angle` | pressure_angle, db_r, dp_r | high | involute angle used to draw the tooth |
| 20 | `beta_r` | formula | `(360 / (4 * Nr) + alpha_r) * 2` | alpha_r, Nr | high | tooth angle used to draw the tooth |
| 21 | `bearing_ID` | lookup | `bearings_discrete(idRequiredMM=carrier_PCD + bearingIDClearance_3DP)` → getBearingIDMM | carrier_PCD, bearingIDClearance_3DP | high | catalogue bearing chosen by bearings_discrete (smallest one that fits); this is its bore |
| 22 | `bearing_OD` | lookup | `bearings_discrete(idRequiredMM=carrier_PCD + bearingIDClearance_3DP)` → getBearingODMM | carrier_PCD, bearingIDClearance_3DP | high | catalogue bearing chosen by bearings_discrete (smallest one that fits); this is its outer diameter |
| 23 | `bearing_height` | lookup | `bearings_discrete(idRequiredMM=carrier_PCD + bearingIDClearance_3DP)` → getBearingWidthMM | carrier_PCD, bearingIDClearance_3DP | high | catalogue bearing chosen by bearings_discrete (smallest one that fits); this is its width |
| 24 | `planet_pin_socket_head_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=planet_pin_bolt_dia, bolt_type=socket_head)` → bolt_head_dia | planet_pin_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 25 | `carrier_PCD` | formula | `module * (Ns + Np_b)` | module, Ns, Np_b | high | planet-centre circle (twice the centre distance) |
| 26 | `carrier_trapezoidal_support_hole_socket_head_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=carrier_trapezoidal_support_hole_dia, bolt_type=socket_head)` → bolt_head_dia | carrier_trapezoidal_support_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 27 | `carrier_trapezoidal_support_hole_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=carrier_trapezoidal_support_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | carrier_trapezoidal_support_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 28 | `planet_pin_bolt_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=planet_pin_bolt_dia, bolt_type=socket_head)` → nut_width_across_flats | planet_pin_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 29 | `sun_hub_dia` | formula | `(Rotor_OD - standard_clearance_1_5mm * 2) if (rotor_mount_hole_PCD + rotor_mount_hole_dia + standard_clearance_1_5mm * 4) > Rotor_OD else (rotor_mount_hole_PCD + rotor_mount_hole_dia + standard_clearance_1_5mm * 4)` | Rotor_OD, standard_clearance_1_5mm, rotor_mount_hole_PCD, rotor_mount_hole_dia | medium | sun hub: sized to the rotor's mount holes plus a hard-coded x 4 clearance margin, capped at the rotor's outer diameter less two clearances (the shared sun-hub margin item the plan still has to decide) |
| 30 | `sun_central_bolt_socket_head_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=sun_central_bolt_dia, bolt_type=socket_head)` → bolt_head_dia | sun_central_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 31 | `fw_p_b` | stress rule | two stress widths, b = FOS x Ft x qe x qk / (gear_allowable_stress x module): b1 for the sun - big planet mesh (module, Ft from serviceFactor x motor_peak_torque at the sun, qe from the sun-planet contact ratio, qk from Ns) and b2 for the small planet - ring mesh (module_s, qk from Np_s); then, if b1 + b2 < 2 x planet_bearing_width + planet_bearing_gap, each planet gear is raised to at least planet_bearing_width + planet_bearing_gap / 2 (one bearing per gear, half the gap each; mitStressAnalysisMinFacewidth); fw_p_b = b1 (raised); then the two planet steps (big + small + planet_step_gap_mm) must fit the stator height less gear_axial_margin_mm: when they are longer, all four widths are scaled by (stator_height - gear_axial_margin_mm - planet_step_gap_mm) / (big + small), so the capped gears carry the same fraction of the torque | module, module_s, Ns, Np_b, Np_s, Nr, num_planet, pressure_angle, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor, stator_height, gear_axial_margin_mm, planet_step_gap_mm, planet_bearing_width, planet_bearing_gap | high | big-planet face width from the tooth-stress rule, raised to hold its bearing and scaled by the stator-height cap |
| 32 | `fw_s_used` | formula | `motor_height if ((stator_ID - bearing_OD) / 2 < standard_clearance_1_5mm * 2 and (standard_clearance_1_5mm * 2 + sun_sec_carrier_bearing_height - (sun_bottom_casing_bearing_height + standard_clearance_1_5mm - sun_coupler_hub_thickness) + sec_carrier_thickness + clearance_planet + fw_p_s + fw_p_b) < motor_height) else (standard_clearance_1_5mm * 2 + sun_sec_carrier_bearing_height - (sun_bottom_casing_bearing_height + standard_clearance_1_5mm - sun_coupler_hub_thickness) + sec_carrier_thickness + clearance_planet + fw_p_s + fw_p_b)` | motor_height, fw_p_b, fw_p_s, standard_clearance_1_5mm, clearance_planet, stator_ID, bearing_OD, sec_carrier_thickness, sun_sec_carrier_bearing_height, sun_coupler_hub_thickness, sun_bottom_casing_bearing_height | medium | printed sun length: the stack of bearings, hub, carrier and planet widths, but at least the motor height when the stator's radial clearance around the output bearing is below a hard-coded 2 x standard_clearance_1_5mm (a two-case floor rule; the plan asks whether the 2 is geometry or tuning) |
| 33 | `dp_p_s` | formula | `module * Np_s` | module, Np_s | high | small-planet pitch diameter (small module) |
| 34 | `db_p_s` | formula | `dp_p_s * cos(pressure_angle_rad)` | dp_p_s, pressure_angle_rad | high | base-circle diameter |
| 35 | `alpha_p_s` | formula | `sqrt(dp_p_s ** 2 - db_p_s ** 2) / db_p_s * 180 / pi - pressure_angle` | pressure_angle, db_p_s, dp_p_s | high | involute angle used to draw the tooth |
| 36 | `beta_p_s` | formula | `(360 / (4 * Np_s) - alpha_p_s) * 2` | alpha_p_s, Np_s | high | tooth angle used to draw the tooth |
| 37 | `sun_bottom_casing_bearing_ID` | lookup | `bearings_discrete(idRequiredMM=rotor_mount_hole_PCD + sun_gear_rotor_nut_wrench_size + standard_clearance_1_5mm * 4)` → getBearingIDMM | rotor_mount_hole_PCD, sun_gear_rotor_nut_wrench_size, standard_clearance_1_5mm | medium | catalogue bearing chosen by bearings_discrete (smallest one that fits) (the request has a hard-coded number: x 4 clearance margin); this is its bore |
| 38 | `sun_bottom_casing_bearing_OD` | lookup | `bearings_discrete(idRequiredMM=rotor_mount_hole_PCD + sun_gear_rotor_nut_wrench_size + standard_clearance_1_5mm * 4)` → getBearingODMM | rotor_mount_hole_PCD, sun_gear_rotor_nut_wrench_size, standard_clearance_1_5mm | medium | catalogue bearing chosen by bearings_discrete (smallest one that fits) (the request has a hard-coded number: x 4 clearance margin); this is its outer diameter |
| 39 | `sun_bottom_casing_bearing_height` | lookup | `bearings_discrete(idRequiredMM=rotor_mount_hole_PCD + sun_gear_rotor_nut_wrench_size + standard_clearance_1_5mm * 4)` → getBearingWidthMM | rotor_mount_hole_PCD, sun_gear_rotor_nut_wrench_size, standard_clearance_1_5mm | medium | catalogue bearing chosen by bearings_discrete (smallest one that fits) (the request has a hard-coded number: x 4 clearance margin); this is its width |

## Used by the code, not written to the CAD file (29)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `pressure_angle_rad` | formula | `pressure_angle * pi / 180` | pressure_angle | high | pressure angle in radians (code attribute pressure_angle) |
| 2 | `motor_peak_torque` | motor | motors.json → motors.<motor>.electrical → `peak_torque_Nm` |  | high | motor torque the gears are sized for (peak torque under the default rating setting); sets the face widths |
| 3 | `gear_allowable_stress` | material | config.json → Material_properties.<gear material> → `maxAllowableStressMPa` |  | high | allowable tooth stress of the gear material, chosen with the material mode (3dp: PLA, metal: steel); sets the face widths |
| 4 | `FOS` | safety factor | motor_config.json → MIT_params → `FOS` |  | high | factor of safety in the tooth-stress rule (the ISSPG default is 1.2) |
| 5 | `serviceFactor` | safety factor | motor_config.json → MIT_params → `serviceFactor` |  | high | service factor on the motor torque in the tooth-stress rule |
| 6 | `planet_bearing_gap` | clearance | icpg_params.json → cpg_3DP_design_parameters → `planet_bearing_gap` |  | high | axial gap between the two planet bearings (one in each planet gear); with the bearing width it sets the smallest planet and ring width |
| 7 | `maxGearboxDiameter` | formula | `MAX_GB_DIA_MULT_FACTOR * stator_ID` | MAX_GB_DIA_MULT_FACTOR, stator_ID | high | largest gearbox diameter the optimiser may use (gearbox_runner max_diameter): the stator's inner diameter times a factor (the gears sit inside the frameless outrunner) |
| 8 | `module_s` | module | optimiser (`optimizationInternalCompoundPlanetaryActuator`) |  | high | the small module (small planet, ring): searched by the optimiser loop and used by the stress rule and the gearbox constraints, but not in the CAD file, which has one module (same pattern as CPG bug 18) |
| 9 | `bearingIDClearance_3DP` | constraint constant | icpg_params.json → cpg_3DP_design_parameters → `bearingIDClearanceMM` |  | high | constant from the ICPG 3DP design parameters |
| 10 | `actuator_width` | formula | `fw_s_used + bearing_height + sun_coupler_hub_thickness + standard_clearance_1_5mm * 3.5 + sun_bottom_casing_bearing_height + bearing_retainer_thickness` | bearing_retainer_thickness, sun_bottom_casing_bearing_height, sun_coupler_hub_thickness, standard_clearance_1_5mm, fw_s_used, bearing_height | high | axial width: both motor-case walls plus the motor case height, written to the results CSV |
| 11 | `fw_limit_mm` | formula | `stator_height - gear_axial_margin_mm` | stator_height, gear_axial_margin_mm | high | the widest gear the stator height allows: the stator height less gear_axial_margin_mm (the width cap of the stress rule) |
| 12 | `ringRadialWidthMM` | constraint constant | icpg_params.json → cpg_3DP_design_parameters → `ringRadialWidthMM` |  | high | read by the code but not written to the CAD file |
| 13 | `planetMinDistanceMM` | constraint constant | icpg_params.json → cpg_3DP_design_parameters → `planetMinDistanceMM` |  | high | read by the code but not written to the CAD file |
| 14 | `sCarrierExtrusionDiaMM` | constraint constant | icpg_params.json → cpg_3DP_design_parameters → `sCarrierExtrusionDiaMM` |  | high | read by the code but not written to the CAD file |
| 15 | `sCarrierExtrusionClearanceMM` | constraint constant | icpg_params.json → cpg_3DP_design_parameters → `sCarrierExtrusionClearanceMM` |  | high | read by the code but not written to the CAD file |
| 16 | `carrier_trapezoidal_support_hole_wrench_size_config` | fastener size | icpg_params.json → cpg_3DP_design_parameters → `carrier_trapezoidal_support_hole_wrench_size` |  | high | config value carrier_trapezoidal_support_hole_wrench_size (the CAD variable of the same name is not read from it): in the config but never read |
| 17 | `sun_sec_carrier_bearing_massKG` | bearing (chosen part) | icpg_params.json → cpg_3DP_design_parameters → `sun_sec_carrier_bearing_massKG` |  | high | in the config but never read |
| 18 | `gear_axial_margin_mm` | feature size | icpg_params.json → cpg_3DP_design_parameters → `gear_axial_margin_mm` |  | high | read by the code but not written to the CAD file |
| 19 | `planet_step_gap_mm` | planet part | icpg_params.json → cpg_3DP_design_parameters → `planet_step_gap_mm` |  | high | read by the code but not written to the CAD file |
| 20 | `GEAR_RATIO_MIN` | search bound | icpg_params.json → cpg_optimization_parameters → `GEAR_RATIO_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 21 | `GEAR_RATIO_MAX` | search bound | icpg_params.json → cpg_optimization_parameters → `GEAR_RATIO_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 22 | `GEAR_RATIO_STEP` | search bound | icpg_params.json → cpg_optimization_parameters → `GEAR_RATIO_STEP` |  | high | optimiser setting: limits of the search, not a part dimension |
| 23 | `MODULE_MIN` | search bound | icpg_params.json → cpg_optimization_parameters → `MODULE_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 24 | `MODULE_MAX` | search bound | icpg_params.json → cpg_optimization_parameters → `MODULE_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 25 | `NUM_PLANET_MIN` | search bound | icpg_params.json → cpg_optimization_parameters → `NUM_PLANET_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 26 | `NUM_PLANET_MAX` | search bound | icpg_params.json → cpg_optimization_parameters → `NUM_PLANET_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 27 | `NUM_TEETH_SUN_MIN` | search bound | icpg_params.json → cpg_optimization_parameters → `NUM_TEETH_SUN_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 28 | `NUM_TEETH_PLANET_MIN` | search bound | icpg_params.json → cpg_optimization_parameters → `NUM_TEETH_PLANET_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 29 | `MAX_GB_DIA_MULT_FACTOR` | search bound | icpg_params.json → cpg_optimization_parameters → `MAX_GB_DIA_MULT_FACTOR` |  | high | optimiser setting: limits of the search, not a part dimension |

## Config blocks ICPG doesn't read

- icpg_params.json → `cpg_design_parameters`: older design block (19 keys); ICPG reads only cpg_3DP_design_parameters (gearbox_runner)
