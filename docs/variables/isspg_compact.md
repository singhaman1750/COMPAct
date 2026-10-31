# ISSPG_COMPACT variables by category

Generated from `config_files/variables/isspg_compact_variables.json` by `python tools/variables/render.py`; edit the JSON, not this page.

Every ISSPG compact variable sorted into input / optimisation / fixed / dependent. 'cad_variables' are the 145 variables ISSPG compact writes to CADs/ISSPG/isspg_compact_equations_onshape.txt, in that order (this gearbox has no other equation file); 'code_only' are values the code uses but does not write to the CAD file, plus every config key the CAD does not use; 'unused_config_blocks' are config blocks ISSPG never reads. tests/test_variable_categories.py checks the lists against the code and re-evaluates every formula and lookup; docs/variables/isspg_compact.md is generated from this file (python tools/variables/render.py).

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
| Input | 24 | 2 |
| Optimisation | 4 | 0 |
| Fixed | 57 | 24 |
| Dependent | 60 | 4 |
| **Total** | **145** | **30** |

CAD variables by confidence: high 134, medium 11, low 0

## To review (not high confidence)

- `sun_coupler_hub_thickness` (Dependent, medium): computed by the code: 3 + bearing_step_width / 2 + sun2_bearing_width; the 3 mm term is hard-coded (the config's sun_coupler_hub_thickness is not read)
- `output_bearing_ID` (Dependent, medium): catalogue bearing chosen by bearings_discrete (smallest one that fits) (the request has a hard-coded number: 20 mm clearance); this is its bore
- `output_bearing_OD` (Dependent, medium): catalogue bearing chosen by bearings_discrete (smallest one that fits) (the request has a hard-coded number: 20 mm clearance); this is its outer diameter
- `output_bearing_width` (Dependent, medium): catalogue bearing chosen by bearings_discrete (smallest one that fits) (the request has a hard-coded number: 20 mm clearance); this is its width
- `sun2_bearing_ID` (Dependent, medium): catalogue bearing chosen by bearings_discrete (smallest one that fits) (requested by outer diameter: bearings_discrete returns the first bearing with OD >= the request, which can exceed it, ISSUES bug 5); this is its bore
- `sun2_bearing_OD` (Dependent, medium): catalogue bearing chosen by bearings_discrete (smallest one that fits) (requested by outer diameter: bearings_discrete returns the first bearing with OD >= the request, which can exceed it, ISSUES bug 5); this is its outer diameter
- `sun2_bearing_width` (Dependent, medium): catalogue bearing chosen by bearings_discrete (smallest one that fits) (requested by outer diameter: bearings_discrete returns the first bearing with OD >= the request, which can exceed it, ISSUES bug 5); this is its width
- `sun_hub_dia` (Dependent, medium): sun coupler hub, sized to the motor's output holes; the x 4 clearance margin is hard-coded (the config's sun_hub_dia is not read); the plan still has to decide a shared key
- `carrier_thickness_mid` (Dependent, medium): middle carrier plate: a hard-coded 6 mm, or, when the ring hub would be thinner than a hard-coded 3 mm, what remains of the carrier after the top; an iterative two-case rule with two hard-coded numbers
- `carrier_thickness` (Dependent, medium): carrier thickness: the hard-coded 6 mm middle plate plus the top, or, when the ring hub would be thinner than a hard-coded 3 mm, whatever closes the stack; an iterative two-case rule with two hard-coded numbers
- `ring_hub_thickness` (Dependent, medium): ring hub thickness: whatever lets the stack reach the motor, but at least a hard-coded 3 mm (the config's ring_hub_thickness is not read); an iterative two-case rule with two hard-coded numbers

## Rules shared by every gearbox

From `config_files/variables/rules.json`; the test holds every gearbox's file to them.

- names matching `^(a[12]_)?Nr(_[bs]|[0-9]*)$` are **Dependent / implicit constraint**: ring-gear teeth are implicitly constrained: the coaxial geometric constraint (e.g. Nr = Ns + 2 x Np) fixes them once the sun and planet teeth are chosen, so the optimiser sets them instead of searching them
- names matching `^fw_(s_calc|p|p_b|r|r_s)$` are **Dependent / stress rule**: gear face widths follow from the tooth-stress rule: the optimisation variables, the motor torque, the gear material and the safety factors fix them, and the optimiser always takes the smallest width that passes (widths that are a formula of another width, e.g. CPG's fw_p_s = fw_r + clearance_planet, are dependent / formula) Exceptions: inwpg_dependent: `fw_p_b`; inwpg_independent: `fw_p_b`; incpg_dependent: `fw_r`; incpg_independent: `fw_r`.
- names matching `^a[12]_fw_(s_calc|r)[12]?$` are **Dependent / stress rule**: the same stress-rule face widths in a two-stage gearbox, under the stage prefixes a1_ / a2_ (the planet width a1_fw_p / a2_fw_p is a copy of the ring width, so it is dependent / formula and not in this rule)

## Input (24)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `driver_upper_holes_dist_from_center` | driver | config.json → Motor_drivers.OdrivePro → `driver_upper_holes_dist_from_center` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 2 | `driver_lower_holes_dist_from_center` | driver | config.json → Motor_drivers.OdrivePro → `driver_lower_holes_dist_from_center` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 3 | `driver_side_holes_dist_from_center` | driver | config.json → Motor_drivers.OdrivePro → `driver_side_holes_dist_from_center` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 4 | `driver_mount_holes_dia` | driver | config.json → Motor_drivers.OdrivePro → `driver_mount_holes_dia` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 5 | `driver_mount_inserts_OD` | driver | config.json → Motor_drivers.OdrivePro → `driver_mount_inserts_OD` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 6 | `driver_mount_thickness` | driver | config.json → Motor_drivers.OdrivePro → `driver_mount_thickness` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 7 | `driver_mount_height` | driver | config.json → Motor_drivers.OdrivePro → `driver_mount_height` |  | high | read from the chosen motor driver (OdrivePro); like the motor, it changes with the chosen part |
| 8 | `motor_OD` | motor | motors.json → motors.<motor>.geometry → `motor_OD` |  | high | read from the chosen motor's geometry |
| 9 | `motor_height` | motor | motors.json → motors.<motor>.geometry → `motor_height` |  | high | read from the chosen motor's geometry |
| 10 | `stator_ID` | motor | motors.json → motors.<motor>.geometry → `stator_ID` |  | high | read from the chosen motor's geometry |
| 11 | `motor_rotor_base_thickness` | motor | motors.json → motors.<motor>.geometry → `motor_rotor_base_thickness` |  | high | read from the chosen motor's geometry |
| 12 | `motor_rotor_base_ID` | motor | motors.json → motors.<motor>.geometry → `motor_rotor_base_ID` |  | high | read from the chosen motor's geometry |
| 13 | `rotor_height` | motor | motors.json → motors.<motor>.geometry → `rotor_height` |  | high | read from the chosen motor's geometry |
| 14 | `rotor_ID` | motor | motors.json → motors.<motor>.geometry → `rotor_ID` |  | high | read from the chosen motor's geometry |
| 15 | `motor_stator_extrusion_depth` | motor | motors.json → motors.<motor>.geometry → `motor_stator_extrusion_depth` |  | high | read from the chosen motor's geometry |
| 16 | `motor_stator_extrusion_dia` | motor | motors.json → motors.<motor>.geometry → `motor_stator_extrusion_dia` |  | high | read from the chosen motor's geometry |
| 17 | `stator_height` | motor | motors.json → motors.<motor>.geometry → `stator_height` |  | high | read from the chosen motor's geometry |
| 18 | `stator_OD` | motor | motors.json → motors.<motor>.geometry → `stator_OD` |  | high | read from the chosen motor's geometry |
| 19 | `stator_top_rotor_top_offset` | motor | motors.json → motors.<motor>.geometry → `stator_top_rotor_top_offset` |  | high | read from the chosen motor's geometry |
| 20 | `stator_hole_dia` | motor | motors.json → motors.<motor>.geometry → `stator_hole_dia` |  | high | read from the chosen motor's geometry |
| 21 | `stator_hole_PCD` | motor | motors.json → motors.<motor>.geometry → `stator_hole_PCD` |  | high | read from the chosen motor's geometry |
| 22 | `motor_rotor_hole_num` | motor | motors.json → motors.<motor>.geometry → `motor_rotor_hole_num` |  | high | read from the chosen motor's geometry |
| 23 | `motor_rotor_hole_dia` | motor | motors.json → motors.<motor>.geometry → `motor_rotor_hole_dia` |  | high | read from the chosen motor's geometry |
| 24 | `motor_rotor_hole_PCD` | motor | motors.json → motors.<motor>.geometry → `motor_rotor_hole_PCD` |  | high | read from the chosen motor's geometry |

## Optimisation (4)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `Ns` | teeth | optimiser (`optimizationInternalSingleStageActuator`) |  | high | sun teeth: searched by the optimiser loop |
| 2 | `Np` | teeth | optimiser (`optimizationInternalSingleStageActuator`) |  | high | planet teeth: searched by the optimiser loop |
| 3 | `module` | module | optimiser (`optimizationInternalSingleStageActuator`) |  | high | module: searched by the optimiser loop |
| 4 | `num_planet` | planets | optimiser (`optimizationInternalSingleStageActuator`) |  | high | number of planets: searched by the optimiser loop |

## Fixed (57)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `pressure_angle_deg` | gear standard | config.json → Gear_standard_parameters → `pressureAngleDEG` |  | high | gear standard, the same for every gearbox type |
| 2 | `clearance_planet` | clearance | isspg_params.json → isspg_3DP_design_parameters → `clearance_planet` |  | high | constant from the ISSPG 3DP design parameters |
| 3 | `clearance_case_mount_holes_shell_thickness` | clearance | isspg_params.json → isspg_3DP_design_parameters → `clearance_case_mount_holes_shell_thickness` |  | high | constant from the ISSPG 3DP design parameters |
| 4 | `standard_clearance_1_5mm` | clearance | isspg_params.json → isspg_3DP_design_parameters → `standard_clearance_1_5mm` |  | high | constant from the ISSPG 3DP design parameters |
| 5 | `standard_clearance_2_mm` | clearance | isspg_params.json → isspg_3DP_design_parameters → `standard_clearance_2_mm` |  | high | constant from the ISSPG 3DP design parameters |
| 6 | `standard_fillet_1_5mm` | feature size | isspg_params.json → isspg_3DP_design_parameters → `standard_fillet_1_5mm` |  | high | constant from the ISSPG 3DP design parameters |
| 7 | `standard_fillet_3_mm` | feature size | isspg_params.json → isspg_3DP_design_parameters → `standard_fillet_3_mm` |  | high | constant from the ISSPG 3DP design parameters |
| 8 | `standard_bearing_insertion_chamfer` | feature size | isspg_params.json → isspg_3DP_design_parameters → `standard_bearing_insertion_chamfer` |  | high | constant from the ISSPG 3DP design parameters |
| 9 | `bearingIDClearanceMM` | constraint constant | isspg_params.json → isspg_3DP_design_parameters → `bearingIDClearanceMM` |  | high | constant from the ISSPG 3DP design parameters |
| 10 | `tight_clearance_3DP` | clearance | isspg_params.json → isspg_3DP_design_parameters → `tight_clearance_3DP` |  | high | constant from the ISSPG 3DP design parameters |
| 11 | `loose_clearance_3DP` | clearance | isspg_params.json → isspg_3DP_design_parameters → `loose_clearance_3DP` |  | high | constant from the ISSPG 3DP design parameters |
| 12 | `bearing_step_width` | bearing (chosen part) | isspg_params.json → isspg_3DP_design_parameters → `bearing_step_width` |  | high | constant from the ISSPG 3DP design parameters |
| 13 | `sun1_bearing_ID` | bearing (chosen part) | isspg_params.json → isspg_3DP_design_parameters → `sun1_bearing_ID` |  | high | constant from the ISSPG 3DP design parameters |
| 14 | `sun1_bearing_OD` | bearing (chosen part) | isspg_params.json → isspg_3DP_design_parameters → `sun1_bearing_OD` |  | high | constant from the ISSPG 3DP design parameters |
| 15 | `sun1_bearing_width` | bearing (chosen part) | isspg_params.json → isspg_3DP_design_parameters → `sun1_bearing_width` |  | high | constant from the ISSPG 3DP design parameters |
| 16 | `sun_central_bolt_dia` | fastener size | isspg_params.json → isspg_3DP_design_parameters → `sun_central_bolt_dia` |  | high | constant from the ISSPG 3DP design parameters |
| 17 | `case_mounting_surface_height` | wall thickness | isspg_params.json → isspg_3DP_design_parameters → `case_mounting_surface_height` |  | high | constant from the ISSPG 3DP design parameters |
| 18 | `case_mounting_hole_dia` | fastener size | isspg_params.json → isspg_3DP_design_parameters → `case_mounting_hole_dia` |  | high | constant from the ISSPG 3DP design parameters |
| 19 | `motor_case_thickness` | wall thickness | isspg_params.json → isspg_3DP_design_parameters → `motor_case_thickness` |  | high | constant from the ISSPG 3DP design parameters |
| 20 | `output_mount_hole_dia` | fastener size | isspg_params.json → isspg_3DP_design_parameters → `output_mount_hole_dia` |  | high | constant from the ISSPG 3DP design parameters |
| 21 | `motor_case_OD_base_to_chamfer` | feature size | isspg_params.json → isspg_3DP_design_parameters → `motor_case_OD_base_to_chamfer` |  | high | constant from the ISSPG 3DP design parameters |
| 22 | `pattern_offset_from_motor_case_OD_base` | feature size | isspg_params.json → isspg_3DP_design_parameters → `pattern_offset_from_motor_case_OD_base` |  | high | constant from the ISSPG 3DP design parameters |
| 23 | `pattern_bulge_dia` | feature size | isspg_params.json → isspg_3DP_design_parameters → `pattern_bulge_dia` |  | high | constant from the ISSPG 3DP design parameters |
| 24 | `pattern_num_bulge` | feature size | isspg_params.json → isspg_3DP_design_parameters → `pattern_num_bulge` |  | high | constant from the ISSPG 3DP design parameters |
| 25 | `pattern_depth` | feature size | isspg_params.json → isspg_3DP_design_parameters → `pattern_depth` |  | high | constant from the ISSPG 3DP design parameters |
| 26 | `clearance_motor_and_case` | clearance | isspg_params.json → isspg_3DP_design_parameters → `clearance_motor_and_case` |  | high | motor-to-case gap: a config value here (SSPG and CPG compute it from the gear size) |
| 27 | `ring_hub_to_case_hole_num` | fastener size | isspg_params.json → isspg_3DP_design_parameters → `ring_hub_to_case_hole_num` |  | high | constant from the ISSPG 3DP design parameters |
| 28 | `ring_hub_to_case_hole_dia` | fastener size | isspg_params.json → isspg_3DP_design_parameters → `ring_hub_to_case_hole_dia` |  | high | constant from the ISSPG 3DP design parameters |
| 29 | `planet_pin_bolt_dia` | fastener size | isspg_params.json → isspg_3DP_design_parameters → `planet_pin_bolt_dia` |  | high | constant from the ISSPG 3DP design parameters |
| 30 | `planet_shaft_step_offset` | planet part | isspg_params.json → isspg_3DP_design_parameters → `planet_shaft_step_offset` |  | high | constant from the ISSPG 3DP design parameters |
| 31 | `planet_bearing_OD` | bearing (chosen part) | isspg_params.json → isspg_3DP_design_parameters → `planet_bearing_OD` |  | high | constant from the ISSPG 3DP design parameters |
| 32 | `planet_bearing_width` | bearing (chosen part) | isspg_params.json → isspg_3DP_design_parameters → `planet_bearing_width` |  | high | constant from the ISSPG 3DP design parameters |
| 33 | `planet_bearing_ID` | bearing (chosen part) | isspg_params.json → isspg_3DP_design_parameters → `planet_bearing_ID` |  | high | constant from the ISSPG 3DP design parameters |
| 34 | `carrier_trapezoidal_support_sun_offset` | feature size | isspg_params.json → isspg_3DP_design_parameters → `carrier_trapezoidal_support_sun_offset` |  | high | constant from the ISSPG 3DP design parameters |
| 35 | `carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID` | bearing (chosen part) | isspg_params.json → isspg_3DP_design_parameters → `carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID` |  | high | constant from the ISSPG 3DP design parameters |
| 36 | `carrier_trapezoidal_support_hole_dia` | fastener size | isspg_params.json → isspg_3DP_design_parameters → `carrier_trapezoidal_support_hole_dia` |  | high | constant from the ISSPG 3DP design parameters |
| 37 | `motor_mount_driver_hole_dia` | fastener size | isspg_params.json → isspg_3DP_design_parameters → `motor_mount_driver_hole_dia` |  | high | constant from the ISSPG 3DP design parameters |
| 38 | `central_hole_offset_from_motor_mount_PCD` | feature size | isspg_params.json → isspg_3DP_design_parameters → `central_hole_offset_from_motor_mount_PCD` |  | high | constant from the ISSPG 3DP design parameters |
| 39 | `motor_mount_driver_hole_num` | fastener size | isspg_params.json → isspg_3DP_design_parameters → `motor_mount_driver_hole_num` |  | high | constant from the ISSPG 3DP design parameters |
| 40 | `magnet_mount_hole_dia` | fastener size | isspg_params.json → isspg_3DP_design_parameters → `magnet_mount_hole_dia` |  | high | constant from the ISSPG 3DP design parameters |
| 41 | `magnet_thickness` | wall thickness | isspg_params.json → isspg_3DP_design_parameters → `magnet_thickness` |  | high | constant from the ISSPG 3DP design parameters |
| 42 | `magnet_dia` | feature size | isspg_params.json → isspg_3DP_design_parameters → `magnet_dia` |  | high | constant from the ISSPG 3DP design parameters |
| 43 | `magnet_mount_thickness` | wall thickness | isspg_params.json → isspg_3DP_design_parameters → `magnet_mount_thickness` |  | high | constant from the ISSPG 3DP design parameters |
| 44 | `magnet_pattern_bulge_dia` | feature size | isspg_params.json → isspg_3DP_design_parameters → `magnet_pattern_bulge_dia` |  | high | constant from the ISSPG 3DP design parameters |
| 45 | `magnet_pattern_bulge_number` | feature size | isspg_params.json → isspg_3DP_design_parameters → `magnet_pattern_bulge_number` |  | high | constant from the ISSPG 3DP design parameters |
| 46 | `magnet_mount_height` | feature size | isspg_params.json → isspg_3DP_design_parameters → `magnet_mount_height` |  | high | constant from the ISSPG 3DP design parameters |
| 47 | `input_bearing_ID` | bearing (chosen part) | isspg_params.json → isspg_3DP_design_parameters → `input_bearing_ID` |  | high | constant from the ISSPG 3DP design parameters |
| 48 | `input_bearing_OD` | bearing (chosen part) | isspg_params.json → isspg_3DP_design_parameters → `input_bearing_OD` |  | high | constant from the ISSPG 3DP design parameters |
| 49 | `input_bearing_width` | bearing (chosen part) | isspg_params.json → isspg_3DP_design_parameters → `input_bearing_width` |  | high | constant from the ISSPG 3DP design parameters |
| 50 | `sec_carrier_thickness` | wall thickness | isspg_params.json → isspg_3DP_design_parameters → `sec_carrier_thickness` |  | high | constant from the ISSPG 3DP design parameters |
| 51 | `carrier_top_to_mid_hole_dia` | fastener size | isspg_params.json → isspg_3DP_design_parameters → `carrier_top_to_mid_hole_dia` |  | high | constant from the ISSPG 3DP design parameters |
| 52 | `ring_stator_case_thickness` | wall thickness | isspg_params.json → isspg_3DP_design_parameters → `ring_stator_case_thickness` |  | high | constant from the ISSPG 3DP design parameters |
| 53 | `ring_hub_offset_stator_hole_PCD` | feature size | isspg_params.json → isspg_3DP_design_parameters → `ring_hub_offset_stator_hole_PCD` |  | high | constant from the ISSPG 3DP design parameters |
| 54 | `stator_ring_hub_hole_num` | fastener size | isspg_params.json → isspg_3DP_design_parameters → `stator_ring_hub_hole_num` |  | high | constant from the ISSPG 3DP design parameters |
| 55 | `wire_slot_length` | feature size | isspg_params.json → isspg_3DP_design_parameters → `wire_slot_length` |  | high | wire slot size: a config value here (a frameless motor has no wire-slot data; SSPG and CPG read it from the motor) |
| 56 | `wire_slot_radius` | feature size | isspg_params.json → isspg_3DP_design_parameters → `wire_slot_radius` |  | high | wire slot size: a config value here (a frameless motor has no wire-slot data; SSPG and CPG read it from the motor) |
| 57 | `actuactor_mount_hole_dia` | fastener size | isspg_params.json → isspg_3DP_design_parameters → `actuactor_mount_hole_dia` |  | high | constant from the ISSPG 3DP design parameters |

## Dependent (60)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `Nr` | implicit constraint | `Ns + 2 * Np` | Ns, Np | high | implicitly constrained: the geometric (coaxial) constraint Ns + 2 x Np = Nr fixes it, and the optimiser sets it from Ns and Np instead of searching it (the code lists it among the optimisation variables) |
| 2 | `sun_coupler_hub_thickness` | formula | `3 + bearing_step_width / 2 + sun2_bearing_width` | sun2_bearing_width, bearing_step_width | medium | computed by the code: 3 + bearing_step_width / 2 + sun2_bearing_width; the 3 mm term is hard-coded (the config's sun_coupler_hub_thickness is not read) |
| 3 | `case_mounting_hole_shift` | formula | `case_mounting_hole_dia / 2` | case_mounting_hole_dia | high | how far the case bolt circle sits outside the case wall: half the bolt hole, less the configured overlap |
| 4 | `case_mounting_hole_allen_socket_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=case_mounting_hole_dia, bolt_type=socket_head)` → bolt_head_dia | case_mounting_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 5 | `case_mounting_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=case_mounting_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | case_mounting_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 6 | `case_mounting_nut_depth` | lookup | `nuts_and_bolts_dimensions(bolt_dia=case_mounting_hole_dia, bolt_type=socket_head)` → nut_thickness | case_mounting_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 7 | `output_mount_nut_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=output_mount_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | output_mount_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 8 | `output_mount_hole_nut_depth` | lookup | `nuts_and_bolts_dimensions(bolt_dia=output_mount_hole_dia, bolt_type=socket_head)` → nut_thickness | output_mount_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 9 | `ring_hub_to_case_hole_nut_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=ring_hub_to_case_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | ring_hub_to_case_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 10 | `ring_hub_to_case_hole_nut_depth` | lookup | `nuts_and_bolts_dimensions(bolt_dia=ring_hub_to_case_hole_dia, bolt_type=socket_head)` → nut_thickness | ring_hub_to_case_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 11 | `carrier_trapezoidal_support_hole_socket_head_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=carrier_trapezoidal_support_hole_dia, bolt_type=socket_head)` → bolt_head_dia | carrier_trapezoidal_support_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 12 | `carrier_trapezoidal_support_hole_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=carrier_trapezoidal_support_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | carrier_trapezoidal_support_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 13 | `carrier_trapezoidal_support_nut_depth` | lookup | `nuts_and_bolts_dimensions(bolt_dia=carrier_trapezoidal_support_hole_dia, bolt_type=socket_head)` → nut_thickness | carrier_trapezoidal_support_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 14 | `planet_pin_socket_head_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=planet_pin_bolt_dia, bolt_type=socket_head)` → bolt_head_dia | planet_pin_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 15 | `planet_pin_nut_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=planet_pin_bolt_dia, bolt_type=socket_head)` → nut_width_across_flats | planet_pin_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 16 | `planet_pin_nut_depth` | lookup | `nuts_and_bolts_dimensions(bolt_dia=planet_pin_bolt_dia, bolt_type=socket_head)` → nut_thickness | planet_pin_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 17 | `motor_mount_driver_nut_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=motor_mount_driver_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | motor_mount_driver_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 18 | `motor_mount_driver_nut_depth` | lookup | `nuts_and_bolts_dimensions(bolt_dia=motor_mount_driver_hole_dia, bolt_type=socket_head)` → nut_thickness | motor_mount_driver_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 19 | `h_a` | formula | `1 * module` | module | high | addendum, standard proportion of the module |
| 20 | `h_b` | formula | `1.25 * module` | module | high | standard proportion of the module (same value as h_f) |
| 21 | `h_f` | formula | `1.25 * module` | module | high | dedendum, standard proportion of the module |
| 22 | `clr_tip_root` | formula | `h_f - h_a` | h_f, h_a | high | tip-root clearance from addendum and dedendum |
| 23 | `dp_s` | formula | `module * Ns` | module, Ns | high | pitch diameter |
| 24 | `db_s` | formula | `dp_s * cos(pressure_angle_rad)` | dp_s, pressure_angle_rad | high | base-circle diameter |
| 25 | `fw_s_calc` | stress rule | b = FOS x Ft x qe x qk / (gear_allowable_stress x module) (mitStressAnalysisMinFacewidth), with Ft = serviceFactor x motor_peak_torque / (num_planet x sun pitch radius), qe = 1 / sun-planet contact ratio, qk = curve fit in Ns; if b < 2 x planet_bearing_width + planet_bearing_gap, the planet and ring width is raised to that value; then the gears must fit the stator height less gear_axial_margin_mm: when the ring is wider than that, all three widths are scaled by (stator_height - gear_axial_margin_mm) / ring width, so the capped gears carry the same fraction of the torque; fw_s_calc = b (scaled) | module, Ns, Np, Nr, num_planet, pressure_angle_deg, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor, stator_height, gear_axial_margin_mm, planet_bearing_width, planet_bearing_gap | high | sun face width from the tooth-stress rule, scaled by the stator-height cap when it applies: fixed by the optimisation variables, the motor torque, the gear material, the safety factors and the cap |
| 26 | `alpha_s` | formula | `sqrt(dp_s ** 2 - db_s ** 2) / db_s * 180 / pi - pressure_angle_rad * 180 / pi` | pressure_angle_rad, db_s, dp_s | high | involute angle used to draw the tooth |
| 27 | `beta_s` | formula | `(360 / (4 * Ns) - alpha_s) * 2` | alpha_s, Ns | high | tooth angle used to draw the tooth |
| 28 | `dp_p` | formula | `module * Np` | module, Np | high | pitch diameter |
| 29 | `db_p` | formula | `dp_p * cos(pressure_angle_rad)` | dp_p, pressure_angle_rad | high | base-circle diameter |
| 30 | `fw_p` | stress rule | b = FOS x Ft x qe x qk / (gear_allowable_stress x module) (mitStressAnalysisMinFacewidth), with Ft = serviceFactor x motor_peak_torque / (num_planet x sun pitch radius), qe = 1 / sun-planet contact ratio, qk = curve fit in Ns; if b < 2 x planet_bearing_width + planet_bearing_gap, the planet and ring width is raised to that value; then the gears must fit the stator height less gear_axial_margin_mm: when the ring is wider than that, all three widths are scaled by (stator_height - gear_axial_margin_mm) / ring width, so the capped gears carry the same fraction of the torque; fw_p = b (scaled) | module, Ns, Np, Nr, num_planet, pressure_angle_deg, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor, planet_bearing_width, planet_bearing_gap, stator_height, gear_axial_margin_mm | high | planet face width from the tooth-stress rule, raised to hold its two bearings and scaled by the stator-height cap (the ring width is the same value) |
| 31 | `alpha_p` | formula | `sqrt(dp_p ** 2 - db_p ** 2) / db_p * 180 / pi - pressure_angle_rad * 180 / pi` | pressure_angle_rad, db_p, dp_p | high | involute angle used to draw the tooth |
| 32 | `beta_p` | formula | `(360 / (4 * Np) - alpha_p) * 2` | alpha_p, Np | high | tooth angle used to draw the tooth |
| 33 | `dp_r` | formula | `module * Nr` | module, Nr | high | pitch diameter |
| 34 | `db_r` | formula | `dp_r * cos(pressure_angle_rad)` | dp_r, pressure_angle_rad | high | base-circle diameter |
| 35 | `fw_r` | stress rule | b = FOS x Ft x qe x qk / (gear_allowable_stress x module) (mitStressAnalysisMinFacewidth), with Ft = serviceFactor x motor_peak_torque / (num_planet x sun pitch radius), qe = 1 / sun-planet contact ratio, qk = curve fit in Ns; if b < 2 x planet_bearing_width + planet_bearing_gap, the planet and ring width is raised to that value; then the gears must fit the stator height less gear_axial_margin_mm: when the ring is wider than that, all three widths are scaled by (stator_height - gear_axial_margin_mm) / ring width, so the capped gears carry the same fraction of the torque; fw_r = b (scaled) | module, Ns, Np, Nr, num_planet, pressure_angle_deg, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor, planet_bearing_width, planet_bearing_gap, stator_height, gear_axial_margin_mm | high | ring face width from the tooth-stress rule, raised to the planet-bearing minimum and scaled by the stator-height cap (the planet width is the same value) |
| 36 | `alpha_r` | formula | `sqrt(dp_r ** 2 - db_r ** 2) / db_r * 180 / pi - pressure_angle_rad * 180 / pi` | pressure_angle_rad, db_r, dp_r | high | involute angle used to draw the tooth |
| 37 | `beta_r` | formula | `(360 / (4 * Nr) + alpha_r) * 2` | alpha_r, Nr | high | tooth angle used to draw the tooth |
| 38 | `output_bearing_ID` | lookup | `bearings_discrete(idRequiredMM=tight_clearance_3DP + carrier_top_to_mid_nut_wrench_size * 0.5 + sun1_bearing_OD + 20)` → getBearingIDMM | sun1_bearing_OD, tight_clearance_3DP, carrier_top_to_mid_nut_wrench_size | medium | catalogue bearing chosen by bearings_discrete (smallest one that fits) (the request has a hard-coded number: 20 mm clearance); this is its bore |
| 39 | `output_bearing_OD` | lookup | `bearings_discrete(idRequiredMM=tight_clearance_3DP + carrier_top_to_mid_nut_wrench_size * 0.5 + sun1_bearing_OD + 20)` → getBearingODMM | sun1_bearing_OD, tight_clearance_3DP, carrier_top_to_mid_nut_wrench_size | medium | catalogue bearing chosen by bearings_discrete (smallest one that fits) (the request has a hard-coded number: 20 mm clearance); this is its outer diameter |
| 40 | `output_bearing_width` | lookup | `bearings_discrete(idRequiredMM=tight_clearance_3DP + carrier_top_to_mid_nut_wrench_size * 0.5 + sun1_bearing_OD + 20)` → getBearingWidthMM | sun1_bearing_OD, tight_clearance_3DP, carrier_top_to_mid_nut_wrench_size | medium | catalogue bearing chosen by bearings_discrete (smallest one that fits) (the request has a hard-coded number: 20 mm clearance); this is its width |
| 41 | `sun2_bearing_ID` | lookup | `bearings_discrete(idRequiredMM=0, odRequiredMM=motor_rotor_base_ID)` → getBearingIDMM | motor_rotor_base_ID | medium | catalogue bearing chosen by bearings_discrete (smallest one that fits) (requested by outer diameter: bearings_discrete returns the first bearing with OD >= the request, which can exceed it, ISSUES bug 5); this is its bore |
| 42 | `sun2_bearing_OD` | lookup | `bearings_discrete(idRequiredMM=0, odRequiredMM=motor_rotor_base_ID)` → getBearingODMM | motor_rotor_base_ID | medium | catalogue bearing chosen by bearings_discrete (smallest one that fits) (requested by outer diameter: bearings_discrete returns the first bearing with OD >= the request, which can exceed it, ISSUES bug 5); this is its outer diameter |
| 43 | `sun2_bearing_width` | lookup | `bearings_discrete(idRequiredMM=0, odRequiredMM=motor_rotor_base_ID)` → getBearingWidthMM | motor_rotor_base_ID | medium | catalogue bearing chosen by bearings_discrete (smallest one that fits) (requested by outer diameter: bearings_discrete returns the first bearing with OD >= the request, which can exceed it, ISSUES bug 5); this is its width |
| 44 | `sun_hub_nut_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=motor_rotor_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | motor_rotor_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 45 | `sun_hub_nut_depth` | lookup | `nuts_and_bolts_dimensions(bolt_dia=motor_rotor_hole_dia, bolt_type=socket_head)` → nut_thickness | motor_rotor_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 46 | `sun_hub_dia` | formula | `motor_rotor_hole_PCD + sun_hub_nut_wrench_size + standard_clearance_1_5mm * 4` | motor_rotor_hole_PCD, sun_hub_nut_wrench_size, standard_clearance_1_5mm | medium | sun coupler hub, sized to the motor's output holes; the x 4 clearance margin is hard-coded (the config's sun_hub_dia is not read); the plan still has to decide a shared key |
| 47 | `sun_central_bolt_socket_head_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=sun_central_bolt_dia, bolt_type=socket_head)` → bolt_head_dia | sun_central_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 48 | `sun_central_nut_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=sun_central_bolt_dia, bolt_type=socket_head)` → nut_width_across_flats | sun_central_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 49 | `sun_central_nut_depth` | lookup | `nuts_and_bolts_dimensions(bolt_dia=sun_central_bolt_dia, bolt_type=socket_head)` → nut_thickness | sun_central_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 50 | `fw_s_used` | formula | `sec_carrier_thickness + clearance_planet + fw_p` | fw_p, sec_carrier_thickness, clearance_planet | high | printed sun length: planet width plus the carrier and clearances |
| 51 | `carrier_thickness_top` | formula | `output_bearing_width + bearing_step_width + standard_clearance_1_5mm` | standard_clearance_1_5mm, output_bearing_width, bearing_step_width | high | computed by the code: output_bearing_width + bearing_step_width + standard_clearance_1_5mm |
| 52 | `carrier_top_to_mid_bolt_socket_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=carrier_top_to_mid_hole_dia, bolt_type=socket_head)` → bolt_head_dia | carrier_top_to_mid_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 53 | `carrier_top_to_mid_nut_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=carrier_top_to_mid_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | carrier_top_to_mid_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 54 | `carrier_top_to_mid_nut_depth` | lookup | `nuts_and_bolts_dimensions(bolt_dia=carrier_top_to_mid_hole_dia, bolt_type=socket_head)` → nut_thickness | carrier_top_to_mid_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 55 | `carrier_thickness_mid` | formula | `6 if (fw_s_used + clearance_planet + (6 + carrier_thickness_top) - (motor_case_thickness - bearing_step_width) - motor_height) >= 3 else (motor_height + 3 + motor_case_thickness - bearing_step_width - fw_s_used - clearance_planet) - carrier_thickness_top` | carrier_thickness_top, motor_height, clearance_planet, fw_s_used, motor_case_thickness, bearing_step_width | medium | middle carrier plate: a hard-coded 6 mm, or, when the ring hub would be thinner than a hard-coded 3 mm, what remains of the carrier after the top; an iterative two-case rule with two hard-coded numbers |
| 56 | `carrier_thickness` | formula | `(6 + carrier_thickness_top) if (fw_s_used + clearance_planet + (6 + carrier_thickness_top) - (motor_case_thickness - bearing_step_width) - motor_height) >= 3 else (motor_height + 3 + motor_case_thickness - bearing_step_width - fw_s_used - clearance_planet)` | carrier_thickness_top, clearance_planet, motor_height, fw_s_used, bearing_step_width, motor_case_thickness | medium | carrier thickness: the hard-coded 6 mm middle plate plus the top, or, when the ring hub would be thinner than a hard-coded 3 mm, whatever closes the stack; an iterative two-case rule with two hard-coded numbers |
| 57 | `ring_hub_thickness` | formula | `(fw_s_used + clearance_planet + (6 + carrier_thickness_top) - (motor_case_thickness - bearing_step_width) - motor_height) if (fw_s_used + clearance_planet + (6 + carrier_thickness_top) - (motor_case_thickness - bearing_step_width) - motor_height) >= 3 else 3` | motor_height, motor_case_thickness, bearing_step_width, fw_s_used, clearance_planet, carrier_thickness_top | medium | ring hub thickness: whatever lets the stack reach the motor, but at least a hard-coded 3 mm (the config's ring_hub_thickness is not read); an iterative two-case rule with two hard-coded numbers |
| 58 | `motor_case_height` | formula | `motor_height + ring_hub_thickness + sun_coupler_hub_thickness + bearing_step_width` | bearing_step_width, sun_coupler_hub_thickness, motor_height, ring_hub_thickness | high | computed by the code: motor_height + ring_hub_thickness + sun_coupler_hub_thickness + bearing_step_width |
| 59 | `actuactor_mount_nut_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=actuactor_mount_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | actuactor_mount_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 60 | `actuactor_mount_nut_depth` | lookup | `nuts_and_bolts_dimensions(bolt_dia=actuactor_mount_hole_dia, bolt_type=socket_head)` → nut_thickness | actuactor_mount_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |

## Used by the code, not written to the CAD file (30)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `pressure_angle_rad` | formula | `pressure_angle_deg * pi / 180` | pressure_angle_deg | high | pressure angle in radians (code attribute pressure_angle) |
| 2 | `motor_peak_torque` | motor | motors.json → motors.<motor>.electrical → `peak_torque_Nm` |  | high | motor torque the gears are sized for (peak torque under the default rating setting); sets the face widths |
| 3 | `gear_allowable_stress` | material | config.json → Material_properties.<gear material> → `maxAllowableStressMPa` |  | high | allowable tooth stress of the gear material, chosen with the material mode (3dp: PLA, metal: steel); sets the face widths |
| 4 | `FOS` | safety factor | config.json → MIT_params → `FOS` |  | high | factor of safety in the tooth-stress rule (the ISSPG default is 1.2) |
| 5 | `serviceFactor` | safety factor | config.json → MIT_params → `serviceFactor` |  | high | service factor on the motor torque in the tooth-stress rule |
| 6 | `planet_bearing_gap` | clearance | isspg_params.json → isspg_3DP_design_parameters → `planet_bearing_gap` |  | high | axial gap between the two planet bearings (one in each planet gear); with the bearing width it sets the smallest planet and ring width |
| 7 | `maxGearboxDiameter` | formula | `stator_ID` | stator_ID | high | largest gearbox diameter the optimiser may use: the stator's inner diameter (the gears sit inside the frameless outrunner) |
| 8 | `actuator_width` | formula | `motor_case_thickness + motor_case_thickness + motor_case_height` | motor_case_height, motor_case_thickness | high | axial width: both motor-case walls plus the motor case height, written to the results CSV |
| 9 | `fw_limit_mm` | formula | `stator_height - gear_axial_margin_mm` | stator_height, gear_axial_margin_mm | high | the widest gear the stator height allows: the stator height less gear_axial_margin_mm (the width cap of the stress rule) |
| 10 | `planetMinDistanceMM` | constraint constant | isspg_params.json → isspg_3DP_design_parameters → `planetMinDistanceMM` |  | high | read by the code but not written to the CAD file |
| 11 | `sCarrierExtrusionDiaMM` | constraint constant | isspg_params.json → isspg_3DP_design_parameters → `sCarrierExtrusionDiaMM` |  | high | read by the code but not written to the CAD file |
| 12 | `sCarrierExtrusionClearanceMM` | constraint constant | isspg_params.json → isspg_3DP_design_parameters → `sCarrierExtrusionClearanceMM` |  | high | read by the code but not written to the CAD file |
| 13 | `ring_hub_thickness_config` | wall thickness | isspg_params.json → isspg_3DP_design_parameters → `ring_hub_thickness` |  | high | config value ring_hub_thickness (the CAD variable of the same name is not read from it): in the config but never read |
| 14 | `ring_hub_to_case_hole_nut_wrench_size_config` | fastener size | isspg_params.json → isspg_3DP_design_parameters → `ring_hub_to_case_hole_nut_wrench_size` |  | high | config value ring_hub_to_case_hole_nut_wrench_size (the CAD variable of the same name is not read from it): in the config but never read |
| 15 | `ring_hub_to_case_hole_nut_depth_config` | fastener size | isspg_params.json → isspg_3DP_design_parameters → `ring_hub_to_case_hole_nut_depth` |  | high | config value ring_hub_to_case_hole_nut_depth (the CAD variable of the same name is not read from it): in the config but never read |
| 16 | `stator_hole_PCD_config` | feature size | isspg_params.json → isspg_3DP_design_parameters → `stator_hole_PCD` |  | high | config value stator_hole_PCD (the CAD variable of the same name is not read from it): in the config but never read |
| 17 | `stator_hole_dia_config` | fastener size | isspg_params.json → isspg_3DP_design_parameters → `stator_hole_dia` |  | high | config value stator_hole_dia (the CAD variable of the same name is not read from it): in the config but never read |
| 18 | `sun_hub_dia_config` | feature size | isspg_params.json → isspg_3DP_design_parameters → `sun_hub_dia` |  | high | config value sun_hub_dia (the CAD variable of the same name is not read from it): in the config but never read |
| 19 | `sun_coupler_hub_thickness_config` | wall thickness | isspg_params.json → isspg_3DP_design_parameters → `sun_coupler_hub_thickness` |  | high | config value sun_coupler_hub_thickness (the CAD variable of the same name is not read from it): in the config but never read |
| 20 | `case_mounting_hole_shift_config` | feature size | isspg_params.json → isspg_3DP_design_parameters → `case_mounting_hole_shift` |  | high | config value case_mounting_hole_shift (the CAD variable of the same name is not read from it): in the config but never read |
| 21 | `gear_axial_margin_mm` | feature size | isspg_params.json → isspg_3DP_design_parameters → `gear_axial_margin_mm` |  | high | read by the code but not written to the CAD file |
| 22 | `GEAR_RATIO_MIN` | search bound | isspg_params.json → isspg_optimization_parameters → `GEAR_RATIO_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 23 | `GEAR_RATIO_MAX` | search bound | isspg_params.json → isspg_optimization_parameters → `GEAR_RATIO_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 24 | `GEAR_RATIO_STEP` | search bound | isspg_params.json → isspg_optimization_parameters → `GEAR_RATIO_STEP` |  | high | optimiser setting: limits of the search, not a part dimension |
| 25 | `MODULE_MIN` | search bound | isspg_params.json → isspg_optimization_parameters → `MODULE_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 26 | `MODULE_MAX` | search bound | isspg_params.json → isspg_optimization_parameters → `MODULE_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 27 | `NUM_PLANET_MIN` | search bound | isspg_params.json → isspg_optimization_parameters → `NUM_PLANET_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 28 | `NUM_PLANET_MAX` | search bound | isspg_params.json → isspg_optimization_parameters → `NUM_PLANET_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 29 | `NUM_TEETH_SUN_MIN` | search bound | isspg_params.json → isspg_optimization_parameters → `NUM_TEETH_SUN_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 30 | `NUM_TEETH_PLANET_MIN` | search bound | isspg_params.json → isspg_optimization_parameters → `NUM_TEETH_PLANET_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |

## Config blocks ISSPG_COMPACT doesn't read

