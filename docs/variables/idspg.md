# IDSPG variables by category

Generated from `config_files/variables/idspg_variables.json` by `python tools/variables/render.py`; edit the JSON, not this page.

Every IDSPG variable sorted into input / optimisation / fixed / dependent. 'cad_variables' are the 198 variables IDSPG writes to CADs/IDSPG/idspg_equations_onshape.txt (and the same names to idspg_equations.txt), in that order, under the stage prefixes a1_ / a2_; 36 of them are written twice under both prefixes, and the second name is marked 'alias_of' the first (same value, same classification). 'code_only' are values the code uses but does not write to the CAD file, plus every config key the CAD does not use; 'unused_config_blocks' are config blocks IDSPG never reads. tests/test_variable_categories.py checks the lists against the code and re-evaluates every formula and lookup; docs/variables/idspg.md is generated from this file (python tools/variables/render.py).

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
| Input | 20 | 4 |
| Optimisation | 15 | 0 |
| Fixed | 79 | 45 |
| Dependent | 84 | 2 |
| **Total** | **198** | **51** |

CAD variables by confidence: high 191, medium 7, low 0

## To review (not high confidence)

- `a1_sun_hub_dia` (Dependent, medium): sun hub: the rotor's mount-hole circle plus hole diameter plus a hard-coded 5 x standard_clearance_1_5mm; the mass code uses 4 (CAD and mass disagree, to be logged); the shared sun-hub margin item the plan still has to decide
- `a1_fw_s_used` (Dependent, medium): stage-1 sun length: the rotor height and offsets, less the stage-1 bearing, clearances and retainer (an axial-fill rule that makes the stages fill the rotor height)
- `a1_fw_s_used2` (Dependent, medium): stage-2 sun length: retainer, clearances, carrier, planet width and the always-zero shortfall (an axial-fill rule)
- `a2_sun_hub_dia` (Dependent, medium): same value as a1_sun_hub_dia (the CAD writes it under both stage prefixes); sun hub: the rotor's mount-hole circle plus hole diameter plus a hard-coded 5 x standard_clearance_1_5mm; the mass code uses 4 (CAD and mass disagree, to be logged); the shared sun-hub margin item the plan still has to decide
- `a2_fw_s_used` (Dependent, medium): same value as a1_fw_s_used2 (the CAD writes it under both stage prefixes); stage-2 sun length: retainer, clearances, carrier, planet width and the always-zero shortfall (an axial-fill rule)
- `a1_ring_gear_relation` (Dependent, medium): axial-fill check for stage 1: the stator height and mounting casing less the stage-1 stack (a value written for the CAD, not used by the code)
- `a2_ring_gear_relation` (Dependent, medium): axial-fill check for stage 2: the two stage lengths less the stator, rotor base and extrusion (a value written for the CAD, not used by the code)
- `planet_bearing_gap` (Fixed, medium): axial gap between the two planet bearings (one in each planet gear); with the bearing width it sets the smallest planet and ring width of both stages; one key for both stages, the plan leaves open whether it should be one per stage (planet_bearing_gap1 / 2)
- `shortfall` (Fixed, medium): always 0: the code sets it only in a disabled axial-fill case (the stage-2 sun length adds it)

## Rules shared by every gearbox

From `config_files/variables/rules.json`; the test holds every gearbox's file to them.

- names matching `^(a[12]_)?Nr(_[bs]|[0-9]*)$` are **Dependent / implicit constraint**: ring-gear teeth are implicitly constrained: the coaxial geometric constraint (e.g. Nr = Ns + 2 x Np) fixes them once the sun and planet teeth are chosen, so the optimiser sets them instead of searching them
- names matching `^fw_(s_calc|p|p_b|r|r_s)$` are **Dependent / stress rule**: gear face widths follow from the tooth-stress rule: the optimisation variables, the motor torque, the gear material and the safety factors fix them, and the optimiser always takes the smallest width that passes (widths that are a formula of another width, e.g. CPG's fw_p_s = fw_r + clearance_planet, are dependent / formula) Exceptions: inwpg_dependent: `fw_p_b`; inwpg_independent: `fw_p_b`; incpg_dependent: `fw_r`; incpg_independent: `fw_r`.
- names matching `^a[12]_fw_(s_calc|r)[12]?$` are **Dependent / stress rule**: the same stress-rule face widths in a two-stage gearbox, under the stage prefixes a1_ / a2_ (the planet width a1_fw_p / a2_fw_p is a copy of the ring width, so it is dependent / formula and not in this rule)

## Input (20)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `Rotor_ID` | motor | motors.json → motors.<motor>.geometry → `rotor_ID` |  | high | read from the chosen motor's geometry |
| 2 | `Rotor_OD` | motor | motors.json → motors.<motor>.geometry → `motor_OD` |  | high | read from the chosen motor's geometry |
| 3 | `Rotor_bottom_ID` | motor | motors.json → motors.<motor>.geometry → `motor_rotor_base_ID` |  | high | read from the chosen motor's geometry |
| 4 | `Rotor_csk_head_height` | motor | motors.json → motors.<motor>.geometry → `rotorCSKHeadHeightMM` |  | high | read from the chosen motor's geometry |
| 5 | `Rotor_csk_head_upper_dia` | motor | motors.json → motors.<motor>.geometry → `rotorCSKHeadUpperDiaMM` |  | high | read from the chosen motor's geometry |
| 6 | `Rotor_height` | motor | motors.json → motors.<motor>.geometry → `rotor_height` |  | high | read from the chosen motor's geometry |
| 7 | `Stator_ID` | motor | motors.json → motors.<motor>.geometry → `stator_ID` |  | high | read from the chosen motor's geometry |
| 8 | `Stator_OD` | motor | motors.json → motors.<motor>.geometry → `stator_OD` |  | high | read from the chosen motor's geometry |
| 9 | `Stator_height` | motor | motors.json → motors.<motor>.geometry → `stator_height` |  | high | read from the chosen motor's geometry |
| 10 | `Stator_mounting_holes_PCD` | motor | motors.json → motors.<motor>.geometry → `stator_hole_PCD` |  | high | read from the chosen motor's geometry |
| 11 | `rotor_mount_hole_PCD` | motor | motors.json → motors.<motor>.geometry → `motor_rotor_hole_PCD` |  | high | read from the chosen motor's geometry |
| 12 | `rotor_mount_hole_dia` | motor | motors.json → motors.<motor>.geometry → `motor_rotor_hole_dia` |  | high | read from the chosen motor's geometry |
| 13 | `rotor_mount_hole_num` | motor | motors.json → motors.<motor>.geometry → `motor_rotor_hole_num` |  | high | read from the chosen motor's geometry |
| 14 | `rotor_bottom_thickness` | motor | motors.json → motors.<motor>.geometry → `motor_rotor_base_thickness` |  | high | read from the chosen motor's geometry |
| 15 | `stator_mounitng_holes_head_socket_dia` | motor | motors.json → motors.<motor>.geometry → `stator_mounitng_holes_head_socket_dia` |  | high | read from the chosen motor's geometry |
| 16 | `stator_mounting_hole_num` | motor | motors.json → motors.<motor>.geometry → `stator_hole_num` |  | high | read from the chosen motor's geometry |
| 17 | `stator_mounting_holes_dia` | motor | motors.json → motors.<motor>.geometry → `stator_hole_dia` |  | high | read from the chosen motor's geometry |
| 18 | `stator_mounting_plate_OD` | motor | motors.json → motors.<motor>.geometry → `motor_stator_extrusion_dia` |  | high | read from the chosen motor's geometry |
| 19 | `stator_rotor_top_offset` | motor | motors.json → motors.<motor>.geometry → `stator_top_rotor_top_offset` |  | high | read from the chosen motor's geometry |
| 20 | `motor_stator_extrusion_depth` | motor | motors.json → motors.<motor>.geometry → `motor_stator_extrusion_depth` |  | high | read from the chosen motor's geometry |

## Optimisation (15)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `a1_Ns` | teeth | optimiser (`optimizationinternalDoubleStagePlanetaryActuator`) |  | high | stage-1 sun teeth: searched by the optimiser loop |
| 2 | `a1_Np` | teeth | optimiser (`optimizationinternalDoubleStagePlanetaryActuator`) |  | high | stage-1 planet teeth: searched by the optimiser loop |
| 3 | `a1_num_planet` | planets | optimiser (`optimizationinternalDoubleStagePlanetaryActuator`) |  | high | stage-1 number of planets: searched by the optimiser loop |
| 4 | `a1_module` | module | optimiser (`optimizationinternalDoubleStagePlanetaryActuator`) |  | high | stage-1 module: searched by the optimiser loop |
| 5 | `a1_Ns2` | teeth | optimiser (`optimizationinternalDoubleStagePlanetaryActuator`) |  | high | same value as a2_Ns (the CAD writes it under both stage prefixes); stage-2 sun teeth: searched by the optimiser loop |
| 6 | `a1_Np2` | teeth | optimiser (`optimizationinternalDoubleStagePlanetaryActuator`) |  | high | same value as a2_Np (the CAD writes it under both stage prefixes); stage-2 planet teeth: searched by the optimiser loop |
| 7 | `a1_module2` | module | optimiser (`optimizationinternalDoubleStagePlanetaryActuator`) |  | high | same value as a2_module (the CAD writes it under both stage prefixes); stage-2 module: searched by the optimiser loop |
| 8 | `a2_Ns` | teeth | optimiser (`optimizationinternalDoubleStagePlanetaryActuator`) |  | high | stage-2 sun teeth: searched by the optimiser loop |
| 9 | `a2_Np` | teeth | optimiser (`optimizationinternalDoubleStagePlanetaryActuator`) |  | high | stage-2 planet teeth: searched by the optimiser loop |
| 10 | `a2_module` | module | optimiser (`optimizationinternalDoubleStagePlanetaryActuator`) |  | high | stage-2 module: searched by the optimiser loop |
| 11 | `a2_num_planet` | planets | optimiser (`optimizationinternalDoubleStagePlanetaryActuator`) |  | high | stage-2 number of planets: searched by the optimiser loop |
| 12 | `a2_Ns1` | teeth | optimiser (`optimizationinternalDoubleStagePlanetaryActuator`) |  | high | same value as a1_Ns (the CAD writes it under both stage prefixes); stage-1 sun teeth: searched by the optimiser loop |
| 13 | `a2_Np1` | teeth | optimiser (`optimizationinternalDoubleStagePlanetaryActuator`) |  | high | same value as a1_Np (the CAD writes it under both stage prefixes); stage-1 planet teeth: searched by the optimiser loop |
| 14 | `a2_module1` | module | optimiser (`optimizationinternalDoubleStagePlanetaryActuator`) |  | high | same value as a1_module (the CAD writes it under both stage prefixes); stage-1 module: searched by the optimiser loop |
| 15 | `a2_num_planet1` | planets | optimiser (`optimizationinternalDoubleStagePlanetaryActuator`) |  | high | same value as a1_num_planet (the CAD writes it under both stage prefixes); stage-1 number of planets: searched by the optimiser loop |

## Fixed (79)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `a1_pressure_angle` | gear standard | idspg_motor_config.json → Gear_standard_parameters → `pressureAngleDEG` |  | high | gear standard, the same for every gearbox type |
| 2 | `a1_clearance_planet` | clearance | idspg_params.json → idspg_design_parameters_3DP → `clearance_planet` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 3 | `a1_sec_carrier_thickness` | wall thickness | idspg_params.json → idspg_design_parameters_3DP → `sec_carrier_thickness1` |  | high | constant from the IDSPG 3DP design parameters |
| 4 | `a1_sun_coupler_hub_thickness` | wall thickness | idspg_params.json → idspg_design_parameters_3DP → `sun_coupler_hub_thickness1` |  | high | constant from the IDSPG 3DP design parameters |
| 5 | `a1_clearance_sun_coupler_sec_carrier` | clearance | idspg_params.json → idspg_design_parameters_3DP → `clearance_sun_coupler_sec_carrier` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 6 | `a1_ring_radial_thickness` | wall thickness | idspg_params.json → idspg_design_parameters_3DP → `ring_radial_thickness` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 7 | `a1_pattern_offset_from_motor_case_OD_base` | feature size | idspg_params.json → idspg_design_parameters_3DP → `pattern_offset_from_motor_case_OD_base` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 8 | `a1_pattern_bulge_dia` | feature size | idspg_params.json → idspg_design_parameters_3DP → `pattern_bulge_dia` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 9 | `a1_pattern_num_bulge` | feature size | idspg_params.json → idspg_design_parameters_3DP → `pattern_num_bulge` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 10 | `a1_pattern_depth` | feature size | idspg_params.json → idspg_design_parameters_3DP → `pattern_depth` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 11 | `a1_planet_pin_bolt_dia` | fastener size | idspg_params.json → idspg_design_parameters_3DP → `planet_pin_bolt_dia1` |  | high | constant from the IDSPG 3DP design parameters |
| 12 | `a1_planet_shaft_dia` | planet part | idspg_params.json → idspg_design_parameters_3DP → `planet_shaft_dia1` |  | high | constant from the IDSPG 3DP design parameters |
| 13 | `a1_planet_shaft_step_offset` | planet part | idspg_params.json → idspg_design_parameters_3DP → `planet_shaft_step_offset` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 14 | `a1_carrier_trapezoidal_support_sun_offset` | feature size | idspg_params.json → idspg_design_parameters_3DP → `carrier_trapezoidal_support_sun_offset1` |  | high | constant from the IDSPG 3DP design parameters |
| 15 | `a1_carrier_trapezoidal_support_hole_PCD_offset_bearing_ID` | feature size | idspg_params.json → idspg_design_parameters_3DP → `carrier_trapezoidal_support_hole_PCD_offset_bearing_ID1` |  | high | constant from the IDSPG 3DP design parameters |
| 16 | `a1_carrier_trapezoidal_support_hole_dia` | fastener size | idspg_params.json → idspg_design_parameters_3DP → `carrier_trapezoidal_support_hole_dia1` |  | high | constant from the IDSPG 3DP design parameters |
| 17 | `a1_carrier_bearing_step_width` | feature size | idspg_params.json → idspg_design_parameters_3DP → `carrier_bearing_step_width` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 18 | `a1_standard_clearance_1_5mm` | clearance | idspg_params.json → idspg_design_parameters_3DP → `standard_clearance_1_5mm` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 19 | `a1_standard_fillet_1_5mm` | feature size | idspg_params.json → idspg_design_parameters_3DP → `standard_fillet_1_5mm` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 20 | `a1_sun_shaft_bearing_OD` | bearing (chosen part) | idspg_params.json → idspg_design_parameters_3DP → `sun_shaft_bearing_OD1` |  | high | constant from the IDSPG 3DP design parameters |
| 21 | `a1_sun_shaft_bearing_width` | bearing (chosen part) | idspg_params.json → idspg_design_parameters_3DP → `sun_shaft_bearing_width1` |  | high | constant from the IDSPG 3DP design parameters |
| 22 | `a1_standard_bearing_insertion_chamfer` | feature size | idspg_params.json → idspg_design_parameters_3DP → `standard_bearing_insertion_chamfer` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 23 | `a1_planet_bearing_OD` | bearing (chosen part) | idspg_params.json → idspg_design_parameters_3DP → `planet_bearing_OD1` |  | high | constant from the IDSPG 3DP design parameters |
| 24 | `a1_planet_bearing_width` | bearing (chosen part) | idspg_params.json → idspg_design_parameters_3DP → `planet_bearing_width1` |  | high | constant from the IDSPG 3DP design parameters |
| 25 | `a1_planet_bore` | planet part | idspg_params.json → idspg_design_parameters_3DP → `planet_bore1` |  | high | constant from the IDSPG 3DP design parameters |
| 26 | `a1_sun_shaft_bearing_ID` | bearing (chosen part) | idspg_params.json → idspg_design_parameters_3DP → `sun_shaft_bearing_ID1` |  | high | constant from the IDSPG 3DP design parameters |
| 27 | `a1_sun_central_bolt_dia` | fastener size | idspg_params.json → idspg_design_parameters_3DP → `sun_central_bolt_dia1` |  | high | constant from the IDSPG 3DP design parameters |
| 28 | `a1_tight_clearance_3DP` | clearance | idspg_params.json → idspg_design_parameters_3DP → `tight_clearance_3DP` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 29 | `a1_loose_clearance_3DP` | clearance | idspg_params.json → idspg_design_parameters_3DP → `loose_clearance_3DP` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 30 | `a2_pressure_angle` | gear standard | idspg_motor_config.json → Gear_standard_parameters → `pressureAngleDEG` |  | high | same value as a1_pressure_angle (the CAD writes it under both stage prefixes); gear standard, the same for every gearbox type |
| 31 | `a2_clearance_planet` | clearance | idspg_params.json → idspg_design_parameters_3DP → `clearance_planet` |  | high | same value as a1_clearance_planet (the CAD writes it under both stage prefixes); constant from the IDSPG 3DP design parameters (one value for both stages) |
| 32 | `a2_output_mounting_hole_dia` | fastener size | idspg_params.json → idspg_design_parameters_3DP → `output_mounting_hole_dia2` |  | high | constant from the IDSPG 3DP design parameters |
| 33 | `a2_sec_carrier_thickness` | wall thickness | idspg_params.json → idspg_design_parameters_3DP → `sec_carrier_thickness2` |  | high | constant from the IDSPG 3DP design parameters |
| 34 | `a2_sun_coupler_hub_thickness` | wall thickness | idspg_params.json → idspg_design_parameters_3DP → `sun_coupler_hub_thickness1` |  | high | same value as a1_sun_coupler_hub_thickness (the CAD writes it under both stage prefixes); constant from the IDSPG 3DP design parameters |
| 35 | `a2_clearance_sun_coupler_sec_carrier` | clearance | idspg_params.json → idspg_design_parameters_3DP → `clearance_sun_coupler_sec_carrier` |  | high | same value as a1_clearance_sun_coupler_sec_carrier (the CAD writes it under both stage prefixes); constant from the IDSPG 3DP design parameters (one value for both stages) |
| 36 | `a2_output_mounting_nut_depth` | fastener size | idspg_params.json → idspg_design_parameters_3DP → `output_mounting_nut_depth2` |  | high | constant from the IDSPG 3DP design parameters |
| 37 | `a2_ring_radial_thickness` | wall thickness | idspg_params.json → idspg_design_parameters_3DP → `ring_radial_thickness` |  | high | same value as a1_ring_radial_thickness (the CAD writes it under both stage prefixes); constant from the IDSPG 3DP design parameters (one value for both stages) |
| 38 | `a2_pattern_offset_from_motor_case_OD_base` | feature size | idspg_params.json → idspg_design_parameters_3DP → `pattern_offset_from_motor_case_OD_base` |  | high | same value as a1_pattern_offset_from_motor_case_OD_base (the CAD writes it under both stage prefixes); constant from the IDSPG 3DP design parameters (one value for both stages) |
| 39 | `a2_pattern_bulge_dia` | feature size | idspg_params.json → idspg_design_parameters_3DP → `pattern_bulge_dia` |  | high | same value as a1_pattern_bulge_dia (the CAD writes it under both stage prefixes); constant from the IDSPG 3DP design parameters (one value for both stages) |
| 40 | `a2_pattern_num_bulge` | feature size | idspg_params.json → idspg_design_parameters_3DP → `pattern_num_bulge` |  | high | same value as a1_pattern_num_bulge (the CAD writes it under both stage prefixes); constant from the IDSPG 3DP design parameters (one value for both stages) |
| 41 | `a2_pattern_depth` | feature size | idspg_params.json → idspg_design_parameters_3DP → `pattern_depth` |  | high | same value as a1_pattern_depth (the CAD writes it under both stage prefixes); constant from the IDSPG 3DP design parameters (one value for both stages) |
| 42 | `a2_planet_pin_bolt_dia` | fastener size | idspg_params.json → idspg_design_parameters_3DP → `planet_pin_bolt_dia2` |  | high | constant from the IDSPG 3DP design parameters |
| 43 | `a2_planet_shaft_dia` | planet part | idspg_params.json → idspg_design_parameters_3DP → `planet_shaft_dia2` |  | high | constant from the IDSPG 3DP design parameters |
| 44 | `a2_planet_shaft_step_offset` | planet part | idspg_params.json → idspg_design_parameters_3DP → `planet_shaft_step_offset2` |  | high | constant from the IDSPG 3DP design parameters |
| 45 | `a2_carrier_trapezoidal_support_sun_offset` | feature size | idspg_params.json → idspg_design_parameters_3DP → `carrier_trapezoidal_support_sun_offset2` |  | high | constant from the IDSPG 3DP design parameters |
| 46 | `a2_carrier_trapezoidal_support_hole_PCD_offset_bearing_ID` | feature size | idspg_params.json → idspg_design_parameters_3DP → `carrier_trapezoidal_support_hole_PCD_offset_bearing_ID2` |  | high | constant from the IDSPG 3DP design parameters |
| 47 | `a2_carrier_trapezoidal_support_hole_dia` | fastener size | idspg_params.json → idspg_design_parameters_3DP → `carrier_trapezoidal_support_hole_dia2` |  | high | constant from the IDSPG 3DP design parameters |
| 48 | `a2_carrier_bearing_step_width` | feature size | idspg_params.json → idspg_design_parameters_3DP → `carrier_bearing_step_width2` |  | high | constant from the IDSPG 3DP design parameters |
| 49 | `a2_standard_clearance_1_5mm` | clearance | idspg_params.json → idspg_design_parameters_3DP → `standard_clearance_1_5mm` |  | high | same value as a1_standard_clearance_1_5mm (the CAD writes it under both stage prefixes); constant from the IDSPG 3DP design parameters (one value for both stages) |
| 50 | `a2_standard_fillet_1_5mm` | feature size | idspg_params.json → idspg_design_parameters_3DP → `standard_fillet_1_5mm` |  | high | same value as a1_standard_fillet_1_5mm (the CAD writes it under both stage prefixes); constant from the IDSPG 3DP design parameters (one value for both stages) |
| 51 | `a2_sun_shaft_bearing_OD` | bearing (chosen part) | idspg_params.json → idspg_design_parameters_3DP → `sun_shaft_bearing_OD2` |  | high | constant from the IDSPG 3DP design parameters |
| 52 | `a2_sun_shaft_bearing_width` | bearing (chosen part) | idspg_params.json → idspg_design_parameters_3DP → `sun_shaft_bearing_width2` |  | high | constant from the IDSPG 3DP design parameters |
| 53 | `a2_standard_bearing_insertion_chamfer` | feature size | idspg_params.json → idspg_design_parameters_3DP → `standard_bearing_insertion_chamfer` |  | high | same value as a1_standard_bearing_insertion_chamfer (the CAD writes it under both stage prefixes); constant from the IDSPG 3DP design parameters (one value for both stages) |
| 54 | `a2_planet_bearing_OD` | bearing (chosen part) | idspg_params.json → idspg_design_parameters_3DP → `planet_bearing_OD2` |  | high | constant from the IDSPG 3DP design parameters |
| 55 | `a2_planet_bearing_width` | bearing (chosen part) | idspg_params.json → idspg_design_parameters_3DP → `planet_bearing_width2` |  | high | constant from the IDSPG 3DP design parameters |
| 56 | `a2_planet_bore` | planet part | idspg_params.json → idspg_design_parameters_3DP → `planet_bore2` |  | high | constant from the IDSPG 3DP design parameters |
| 57 | `a2_sun_shaft_bearing_ID` | bearing (chosen part) | idspg_params.json → idspg_design_parameters_3DP → `sun_shaft_bearing_ID2` |  | high | constant from the IDSPG 3DP design parameters |
| 58 | `a2_sun_central_bolt_dia` | fastener size | idspg_params.json → idspg_design_parameters_3DP → `sun_central_bolt_dia2` |  | high | constant from the IDSPG 3DP design parameters |
| 59 | `a2_tight_clearance_3DP` | clearance | idspg_params.json → idspg_design_parameters_3DP → `tight_clearance_3DP` |  | high | same value as a1_tight_clearance_3DP (the CAD writes it under both stage prefixes); constant from the IDSPG 3DP design parameters (one value for both stages) |
| 60 | `a2_loose_clearance_3DP` | clearance | idspg_params.json → idspg_design_parameters_3DP → `loose_clearance_3DP` |  | high | same value as a1_loose_clearance_3DP (the CAD writes it under both stage prefixes); constant from the IDSPG 3DP design parameters (one value for both stages) |
| 61 | `a1_sun_bottom_casing_bearing_ID` | bearing (chosen part) | idspg_params.json → idspg_design_parameters_3DP → `a1_sun_bottom_casing_bearing_ID` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 62 | `a1_sun_bottom_casing_bearing_OD` | bearing (chosen part) | idspg_params.json → idspg_design_parameters_3DP → `a1_sun_bottom_casing_bearing_OD` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 63 | `a1_sun_bottom_casing_bearing_height` | bearing (chosen part) | idspg_params.json → idspg_design_parameters_3DP → `a1_sun_bottom_casing_bearing_height` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 64 | `a1_sun_carrier_bearing_ID` | bearing (chosen part) | idspg_params.json → idspg_design_parameters_3DP → `a1_sun_carrier_bearing_ID` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 65 | `a1_sun_carrier_bearing_OD` | bearing (chosen part) | idspg_params.json → idspg_design_parameters_3DP → `a1_sun_carrier_bearing_OD` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 66 | `a1_sun_carrier_bearing_height` | bearing (chosen part) | idspg_params.json → idspg_design_parameters_3DP → `a1_sun_carrier_bearing_height` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 67 | `bearing_retainer_hole_dia` | fastener size | idspg_params.json → idspg_design_parameters_3DP → `bearing_retainer_hole_dia` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 68 | `bearing_retainer_hole_num` | fastener size | idspg_params.json → idspg_design_parameters_3DP → `bearing_retainer_hole_num` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 69 | `bearing_retainer_hole_wrench_nut_size` | fastener size | idspg_params.json → idspg_design_parameters_3DP → `bearing_retainer_hole_wrench_nut_size` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 70 | `a2_bearing_retainer_hole_dia` | fastener size | idspg_params.json → idspg_design_parameters_3DP → `a2_bearing_retainer_hole_dia` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 71 | `a2_bearing_retainer_hole_num` | fastener size | idspg_params.json → idspg_design_parameters_3DP → `a2_bearing_retainer_hole_num` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 72 | `a2_bearing_retainer_nut_wrench_size` | fastener size | idspg_params.json → idspg_design_parameters_3DP → `a2_bearing_retainer_nut_wrench_size` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 73 | `a2_bearing_retainer_wrench_height` | fastener size | idspg_params.json → idspg_design_parameters_3DP → `a2_bearing_retainer_wrench_height` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 74 | `bearing_retainer_thickness` | wall thickness | idspg_params.json → idspg_design_parameters_3DP → `bearing_retainer_thickness` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 75 | `motor_casing_thickness` | wall thickness | idspg_params.json → idspg_design_parameters_3DP → `motor_casing_thickness` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 76 | `a1_ring_gear_thickness_mounting_casing` | wall thickness | idspg_params.json → idspg_design_parameters_3DP → `a1_ring_gear_thickness_mounting_casing` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 77 | `a2_ring_gear_thickness_mounting_casing` | wall thickness | idspg_params.json → idspg_design_parameters_3DP → `a2_ring_gear_thickness_mounting_casing` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 78 | `a1_sun_gear_rotor_nut_depth` | fastener size | idspg_params.json → idspg_design_parameters_3DP → `a1_sun_gear_rotor_nut_depth` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 79 | `a1_sun_gear_rotor_nut_wrench_size` | fastener size | idspg_params.json → idspg_design_parameters_3DP → `a1_sun_gear_rotor_nut_wrench_size` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |

## Dependent (84)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `a1_Nr` | implicit constraint | `a1_Ns + 2 * a1_Np` | a1_Ns, a1_Np | high | implicitly constrained: the coaxial constraint Ns + 2 x Np = Nr fixes it, and the optimiser sets it from Ns and Np instead of searching it (the code lists it among the optimisation variables) |
| 2 | `a1_motor_OD` | formula | `motorDiaMM` | motorDiaMM | high | computed by the code: motorDiaMM |
| 3 | `a1_motor_height` | formula | `motorLengthMM` | motorLengthMM | high | computed by the code: motorLengthMM |
| 4 | `a1_h_a` | formula | `1 * a1_module` | a1_module | high | addendum, standard proportion of the module |
| 5 | `a1_h_b` | formula | `1.25 * a1_module` | a1_module | high | standard proportion of the module (same value as h_f) |
| 6 | `a1_h_f` | formula | `1.25 * a1_module` | a1_module | high | dedendum, standard proportion of the module |
| 7 | `a1_clr_tip_root` | formula | `a1_h_f - a1_h_a` | a1_h_f, a1_h_a | high | tip-root clearance from addendum and dedendum |
| 8 | `a1_dp_s` | formula | `a1_module * a1_Ns` | a1_module, a1_Ns | high | pitch diameter |
| 9 | `a1_db_s` | formula | `a1_dp_s * cos(a1_pressure_angle * pi / 180)` | a1_dp_s, a1_pressure_angle | high | base-circle diameter |
| 10 | `a1_fw_s_calc` | stress rule | b = FOS x Ft x qe x qk / (gear_allowable_stress x module) (mitStressAnalysisMinFacewidth), with Ft = serviceFactor x motor_peak_torque / (num_planet x sun pitch radius), qe = 1 / sun-planet contact ratio, qk = curve fit in Ns; a1_fw_s_calc = b | a1_module, a1_Ns, a1_Np, a1_Nr, a1_num_planet, a1_pressure_angle, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor | high | stage-1 sun face width from the tooth-stress rule: fixed by the optimisation variables, the motor torque, the gear material and the safety factors, so the optimiser has no freedom over it |
| 11 | `a1_alpha_s` | formula | `sqrt(a1_dp_s ** 2 - a1_db_s ** 2) / a1_db_s * 180 / pi - a1_pressure_angle` | a1_pressure_angle, a1_db_s, a1_dp_s | high | involute angle used to draw the tooth |
| 12 | `a1_beta_s` | formula | `(360 / (4 * a1_Ns) - a1_alpha_s) * 2` | a1_alpha_s, a1_Ns | high | tooth angle used to draw the tooth |
| 13 | `a1_dp_p` | formula | `a1_module * a1_Np` | a1_module, a1_Np | high | pitch diameter |
| 14 | `a1_db_p` | formula | `a1_dp_p * cos(a1_pressure_angle * pi / 180)` | a1_dp_p, a1_pressure_angle | high | base-circle diameter |
| 15 | `a1_fw_p` | formula | `a1_fw_r` | a1_fw_r | high | computed by the code: a1_fw_r |
| 16 | `a1_alpha_p` | formula | `sqrt(a1_dp_p ** 2 - a1_db_p ** 2) / a1_db_p * 180 / pi - a1_pressure_angle` | a1_pressure_angle, a1_db_p, a1_dp_p | high | involute angle used to draw the tooth |
| 17 | `a1_beta_p` | formula | `(360 / (4 * a1_Np) - a1_alpha_p) * 2` | a1_alpha_p, a1_Np | high | tooth angle used to draw the tooth |
| 18 | `a1_dp_r` | formula | `a1_module * a1_Nr` | a1_module, a1_Nr | high | pitch diameter |
| 19 | `a1_db_r` | formula | `a1_dp_r * cos(a1_pressure_angle * pi / 180)` | a1_dp_r, a1_pressure_angle | high | base-circle diameter |
| 20 | `a1_fw_r` | stress rule | b = FOS x Ft x qe x qk / (gear_allowable_stress x module) (mitStressAnalysisMinFacewidth), with Ft = serviceFactor x motor_peak_torque / (num_planet x sun pitch radius), qe = 1 / sun-planet contact ratio, qk = curve fit in Ns; if b < 2 x planet_bearing_width + planet_bearing_gap, b is raised to that value; a1_fw_r = b (the planet width is a copy) | a1_module, a1_Ns, a1_Np, a1_Nr, a1_num_planet, a1_pressure_angle, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor, a1_planet_bearing_width, planet_bearing_gap | high | stage-1 ring face width from the tooth-stress rule, raised to hold the planet's two bearings; the planet width is a copy (ISSUES bug 14, wide 3D-printed stage-1 gears, is still open) |
| 21 | `a1_alpha_r` | formula | `sqrt(a1_dp_r ** 2 - a1_db_r ** 2) / a1_db_r * 180 / pi - a1_pressure_angle` | a1_pressure_angle, a1_db_r, a1_dp_r | high | involute angle used to draw the tooth |
| 22 | `a1_beta_r` | formula | `(360 / (4 * a1_Nr) + a1_alpha_r) * 2` | a1_alpha_r, a1_Nr | high | tooth angle used to draw the tooth |
| 23 | `a1_bearing_ID` | lookup | `bearings_discrete(idRequiredMM=a1_module * (a1_Ns + a1_Np) + bearingIDClearanceMM)` → getBearingIDMM | bearingIDClearanceMM, a1_module, a1_Ns, a1_Np | high | catalogue bearing chosen by bearings_discrete for the bore the stage needs (smallest one that fits); this is its bore |
| 24 | `a1_bearing_OD` | lookup | `bearings_discrete(idRequiredMM=a1_module * (a1_Ns + a1_Np) + bearingIDClearanceMM)` → getBearingODMM | bearingIDClearanceMM, a1_module, a1_Ns, a1_Np | high | catalogue bearing chosen by bearings_discrete for the bore the stage needs (smallest one that fits); this is its outer diameter |
| 25 | `a1_bearing_height` | lookup | `bearings_discrete(idRequiredMM=a1_module * (a1_Ns + a1_Np) + bearingIDClearanceMM)` → getBearingWidthMM | bearingIDClearanceMM, a1_module, a1_Ns, a1_Np | high | catalogue bearing chosen by bearings_discrete for the bore the stage needs (smallest one that fits); this is its width |
| 26 | `a1_ring_OD` | formula | `Stator_ID` | Stator_ID | high | stage-1 ring outer diameter: the ring fits the stator bore, a copy of Stator_ID (an input) |
| 27 | `a1_planet_pin_socket_head_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=a1_planet_pin_bolt_dia, bolt_type=socket_head)` → bolt_head_dia | a1_planet_pin_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 28 | `a1_carrier_PCD` | formula | `(a1_Np + a1_Ns) * a1_module` | a1_module, a1_Np, a1_Ns | high | planet-centre circle (twice the centre distance) |
| 29 | `a1_carrier_trapezoidal_support_hole_socket_head_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=a1_carrier_trapezoidal_support_hole_dia, bolt_type=socket_head)` → bolt_head_dia | a1_carrier_trapezoidal_support_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 30 | `a1_carrier_trapezoidal_support_hole_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=a1_carrier_trapezoidal_support_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | a1_carrier_trapezoidal_support_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 31 | `a1_planet_pin_bolt_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=a1_planet_pin_bolt_dia, bolt_type=socket_head)` → nut_width_across_flats | a1_planet_pin_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 32 | `a1_sun_hub_dia` | formula | `rotor_mount_hole_PCD + rotor_mount_hole_dia + a1_standard_clearance_1_5mm * 5` | rotor_mount_hole_PCD, rotor_mount_hole_dia, a1_standard_clearance_1_5mm | medium | sun hub: the rotor's mount-hole circle plus hole diameter plus a hard-coded 5 x standard_clearance_1_5mm; the mass code uses 4 (CAD and mass disagree, to be logged); the shared sun-hub margin item the plan still has to decide |
| 33 | `a1_sun_central_bolt_socket_head_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=a1_sun_central_bolt_dia, bolt_type=socket_head)` → bolt_head_dia | a1_sun_central_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 34 | `a1_fw_s_used` | formula | `Rotor_height + stator_rotor_top_offset + a1_ring_gear_thickness_mounting_casing - a1_bearing_height - a1_clearance_planet - a1_carrier_bearing_step_width - bearing_retainer_thickness` | bearing_retainer_thickness, a1_carrier_bearing_step_width, a1_clearance_planet, a1_bearing_height, a1_ring_gear_thickness_mounting_casing, Rotor_height, stator_rotor_top_offset | medium | stage-1 sun length: the rotor height and offsets, less the stage-1 bearing, clearances and retainer (an axial-fill rule that makes the stages fill the rotor height) |
| 35 | `a1_Nr2` | implicit constraint | `a2_Ns + 2 * a2_Np` | a2_Ns, a2_Np | high | same value as a2_Nr (the CAD writes it under both stage prefixes); implicitly constrained: the coaxial constraint Ns + 2 x Np = Nr fixes it, and the optimiser sets it from Ns and Np instead of searching it (the code lists it among the optimisation variables) |
| 36 | `a1_dp_s2` | formula | `a2_module * a2_Ns` | a2_module, a2_Ns | high | same value as a2_dp_s (the CAD writes it under both stage prefixes); pitch diameter |
| 37 | `a1_db_s2` | formula | `a2_dp_s * cos(a1_pressure_angle * pi / 180)` | a2_dp_s, a1_pressure_angle | high | same value as a2_db_s (the CAD writes it under both stage prefixes); base-circle diameter |
| 38 | `a1_fw_s_calc2` | stress rule | b = FOS x Ft x qe x qk / (gear_allowable_stress x module) (mitStressAnalysisMinFacewidth), with Ft = serviceFactor x motor_peak_torque x stage-1 gear ratio / (num_planet x sun pitch radius), qe = 1 / sun-planet contact ratio, qk = curve fit in Ns; a2_fw_s_calc = b | a2_module, a2_Ns, a2_Np, a2_Nr, a2_num_planet, a1_pressure_angle, a1_Ns, a1_Nr, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor | high | stage-2 sun face width from the tooth-stress rule: fixed by the optimisation variables, the motor torque, the gear material and the safety factors, so the optimiser has no freedom over it |
| 39 | `a1_alpha_s2` | formula | `sqrt(a2_dp_s ** 2 - a2_db_s ** 2) / a2_db_s * 180 / pi - a1_pressure_angle` | a1_pressure_angle, a2_db_s, a2_dp_s | high | same value as a2_alpha_s (the CAD writes it under both stage prefixes); involute angle used to draw the tooth |
| 40 | `a1_beta_s2` | formula | `(360 / (4 * a2_Ns) - a2_alpha_s) * 2` | a2_alpha_s, a2_Ns | high | same value as a2_beta_s (the CAD writes it under both stage prefixes); tooth angle used to draw the tooth |
| 41 | `a1_fw_s_used2` | formula | `bearing_retainer_thickness + a1_standard_clearance_1_5mm + a2_sec_carrier_thickness + a1_clearance_planet + a2_fw_p + shortfall` | shortfall, a2_fw_p, a1_clearance_planet, a2_sec_carrier_thickness, bearing_retainer_thickness, a1_standard_clearance_1_5mm | medium | stage-2 sun length: retainer, clearances, carrier, planet width and the always-zero shortfall (an axial-fill rule) |
| 42 | `a1_fw_p2` | formula | `a2_fw_r` | a2_fw_r | high | same value as a2_fw_p (the CAD writes it under both stage prefixes); computed by the code: a2_fw_r |
| 43 | `a2_Nr` | implicit constraint | `a2_Ns + 2 * a2_Np` | a2_Ns, a2_Np | high | implicitly constrained: the coaxial constraint Ns + 2 x Np = Nr fixes it, and the optimiser sets it from Ns and Np instead of searching it (the code lists it among the optimisation variables) |
| 44 | `a2_h_a` | formula | `1 * a2_module` | a2_module | high | addendum, standard proportion of the module |
| 45 | `a2_h_f` | formula | `1.25 * a2_module` | a2_module | high | dedendum, standard proportion of the module |
| 46 | `a2_clr_tip_root` | formula | `a2_h_f - a2_h_a` | a2_h_f, a2_h_a | high | tip-root clearance from addendum and dedendum |
| 47 | `a2_dp_r` | formula | `a2_module * a2_Nr` | a2_module, a2_Nr | high | pitch diameter |
| 48 | `a2_db_r` | formula | `a2_dp_r * cos(a1_pressure_angle * pi / 180)` | a2_dp_r, a1_pressure_angle | high | base-circle diameter |
| 49 | `a2_fw_r` | stress rule | b = FOS x Ft x qe x qk / (gear_allowable_stress x module) (mitStressAnalysisMinFacewidth), with Ft = serviceFactor x motor_peak_torque x stage-1 gear ratio / (num_planet x sun pitch radius), qe = 1 / sun-planet contact ratio, qk = curve fit in Ns; if b < 2 x planet_bearing_width + planet_bearing_gap, b is raised to that value; a2_fw_r = b (the planet width is a copy) | a2_module, a2_Ns, a2_Np, a2_Nr, a2_num_planet, a1_pressure_angle, a1_Ns, a1_Nr, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor, a2_planet_bearing_width, planet_bearing_gap | high | stage-2 ring face width from the tooth-stress rule, raised to hold the planet's two bearings; the planet width is a copy |
| 50 | `a2_alpha_r` | formula | `sqrt(a2_dp_r ** 2 - a2_db_r ** 2) / a2_db_r * 180 / pi - a1_pressure_angle` | a1_pressure_angle, a2_db_r, a2_dp_r | high | involute angle used to draw the tooth |
| 51 | `a2_beta_r` | formula | `(360 / (4 * a2_Nr) + a2_alpha_r) * 2` | a2_alpha_r, a2_Nr | high | tooth angle used to draw the tooth |
| 52 | `a2_bearing_ID` | lookup | `bearings_discrete(idRequiredMM=a2_module * (a2_Ns + a2_Np) + bearingIDClearanceMM)` → getBearingIDMM | bearingIDClearanceMM, a2_module, a2_Ns, a2_Np | high | catalogue bearing chosen by bearings_discrete for the bore the stage needs (smallest one that fits); this is its bore |
| 53 | `a2_bearing_OD` | lookup | `bearings_discrete(idRequiredMM=a2_module * (a2_Ns + a2_Np) + bearingIDClearanceMM)` → getBearingODMM | bearingIDClearanceMM, a2_module, a2_Ns, a2_Np | high | catalogue bearing chosen by bearings_discrete for the bore the stage needs (smallest one that fits); this is its outer diameter |
| 54 | `a2_bearing_height` | lookup | `bearings_discrete(idRequiredMM=a2_module * (a2_Ns + a2_Np) + bearingIDClearanceMM)` → getBearingWidthMM | bearingIDClearanceMM, a2_module, a2_Ns, a2_Np | high | catalogue bearing chosen by bearings_discrete for the bore the stage needs (smallest one that fits); this is its width |
| 55 | `a2_motor_OD` | formula | `motorDiaMM` | motorDiaMM | high | same value as a1_motor_OD (the CAD writes it under both stage prefixes); computed by the code: motorDiaMM |
| 56 | `a2_output_mounting_nut_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=a2_output_mounting_hole_dia)` → nut_width_across_flats | a2_output_mounting_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 57 | `a2_output_mounting_nut_thickness` | lookup | `nuts_and_bolts_dimensions(bolt_dia=a2_output_mounting_hole_dia)` → nut_thickness | a2_output_mounting_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 58 | `a2_ring_OD` | formula | `a2_Nr * a2_module + a1_ring_radial_thickness * 2` | a2_Nr, a2_module, a1_ring_radial_thickness | high | stage-2 ring outer diameter: the ring's pitch diameter plus two ring walls |
| 59 | `a2_motor_height` | formula | `motorLengthMM` | motorLengthMM | high | same value as a1_motor_height (the CAD writes it under both stage prefixes); computed by the code: motorLengthMM |
| 60 | `a2_planet_pin_socket_head_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=a2_planet_pin_bolt_dia, bolt_type=socket_head)` → bolt_head_dia | a2_planet_pin_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 61 | `a2_carrier_PCD` | formula | `(a2_Np + a2_Ns) * a2_module` | a2_module, a2_Np, a2_Ns | high | planet-centre circle (twice the centre distance) |
| 62 | `a2_fw_p` | formula | `a2_fw_r` | a2_fw_r | high | computed by the code: a2_fw_r |
| 63 | `a2_carrier_trapezoidal_support_hole_socket_head_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=a2_carrier_trapezoidal_support_hole_dia, bolt_type=socket_head)` → bolt_head_dia | a2_carrier_trapezoidal_support_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 64 | `a2_carrier_trapezoidal_support_hole_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=a2_carrier_trapezoidal_support_hole_dia, bolt_type=socket_head)` → nut_width_across_flats | a2_carrier_trapezoidal_support_hole_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 65 | `a2_planet_pin_bolt_wrench_size` | lookup | `nuts_and_bolts_dimensions(bolt_dia=a2_planet_pin_bolt_dia, bolt_type=socket_head)` → nut_width_across_flats | a2_planet_pin_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 66 | `a2_h_b` | formula | `1.25 * a2_module` | a2_module | high | standard proportion of the module (same value as h_f) |
| 67 | `a2_dp_s` | formula | `a2_module * a2_Ns` | a2_module, a2_Ns | high | pitch diameter |
| 68 | `a2_db_s` | formula | `a2_dp_s * cos(a1_pressure_angle * pi / 180)` | a2_dp_s, a1_pressure_angle | high | base-circle diameter |
| 69 | `a2_fw_s_calc` | stress rule | b = FOS x Ft x qe x qk / (gear_allowable_stress x module) (mitStressAnalysisMinFacewidth), with Ft = serviceFactor x motor_peak_torque x stage-1 gear ratio / (num_planet x sun pitch radius), qe = 1 / sun-planet contact ratio, qk = curve fit in Ns; a2_fw_s_calc = b | a2_module, a2_Ns, a2_Np, a2_Nr, a2_num_planet, a1_pressure_angle, a1_Ns, a1_Nr, motor_peak_torque, gear_allowable_stress, FOS, serviceFactor | high | same value as a1_fw_s_calc2 (the CAD writes it under both stage prefixes); stage-2 sun face width from the tooth-stress rule: fixed by the optimisation variables, the motor torque, the gear material and the safety factors, so the optimiser has no freedom over it |
| 70 | `a2_alpha_s` | formula | `sqrt(a2_dp_s ** 2 - a2_db_s ** 2) / a2_db_s * 180 / pi - a1_pressure_angle` | a1_pressure_angle, a2_db_s, a2_dp_s | high | involute angle used to draw the tooth |
| 71 | `a2_beta_s` | formula | `(360 / (4 * a2_Ns) - a2_alpha_s) * 2` | a2_alpha_s, a2_Ns | high | tooth angle used to draw the tooth |
| 72 | `a2_dp_p` | formula | `a2_module * a2_Np` | a2_module, a2_Np | high | pitch diameter |
| 73 | `a2_db_p` | formula | `a2_dp_p * cos(a1_pressure_angle * pi / 180)` | a2_dp_p, a1_pressure_angle | high | base-circle diameter |
| 74 | `a2_alpha_p` | formula | `sqrt(a2_dp_p ** 2 - a2_db_p ** 2) / a2_db_p * 180 / pi - a1_pressure_angle` | a1_pressure_angle, a2_db_p, a2_dp_p | high | involute angle used to draw the tooth |
| 75 | `a2_beta_p` | formula | `(360 / (4 * a2_Np) - a2_alpha_p) * 2` | a2_alpha_p, a2_Np | high | tooth angle used to draw the tooth |
| 76 | `a2_sun_hub_dia` | formula | `rotor_mount_hole_PCD + rotor_mount_hole_dia + a1_standard_clearance_1_5mm * 5` | rotor_mount_hole_PCD, rotor_mount_hole_dia, a1_standard_clearance_1_5mm | medium | same value as a1_sun_hub_dia (the CAD writes it under both stage prefixes); sun hub: the rotor's mount-hole circle plus hole diameter plus a hard-coded 5 x standard_clearance_1_5mm; the mass code uses 4 (CAD and mass disagree, to be logged); the shared sun-hub margin item the plan still has to decide |
| 77 | `a2_sun_central_bolt_socket_head_dia` | lookup | `nuts_and_bolts_dimensions(bolt_dia=a2_sun_central_bolt_dia)` → bolt_head_dia | a2_sun_central_bolt_dia | high | standard socket-head fastener size for the chosen bolt diameter |
| 78 | `a2_fw_s_used` | formula | `bearing_retainer_thickness + a1_standard_clearance_1_5mm + a2_sec_carrier_thickness + a1_clearance_planet + a2_fw_p + shortfall` | shortfall, a2_fw_p, a1_clearance_planet, a2_sec_carrier_thickness, bearing_retainer_thickness, a1_standard_clearance_1_5mm | medium | same value as a1_fw_s_used2 (the CAD writes it under both stage prefixes); stage-2 sun length: retainer, clearances, carrier, planet width and the always-zero shortfall (an axial-fill rule) |
| 79 | `a2_Nr1` | implicit constraint | `a1_Ns + 2 * a1_Np` | a1_Ns, a1_Np | high | same value as a1_Nr (the CAD writes it under both stage prefixes); implicitly constrained: the coaxial constraint Ns + 2 x Np = Nr fixes it, and the optimiser sets it from Ns and Np instead of searching it (the code lists it among the optimisation variables) |
| 80 | `a2_bearing1_ID` | lookup | `bearings_discrete(idRequiredMM=a1_module * (a1_Ns + a1_Np) + bearingIDClearanceMM)` → getBearingIDMM | bearingIDClearanceMM, a1_module, a1_Ns, a1_Np | high | same value as a1_bearing_ID (the CAD writes it under both stage prefixes); catalogue bearing chosen by bearings_discrete for the bore the stage needs (smallest one that fits); this is its bore |
| 81 | `a2_bearing1_OD` | lookup | `bearings_discrete(idRequiredMM=a1_module * (a1_Ns + a1_Np) + bearingIDClearanceMM)` → getBearingODMM | bearingIDClearanceMM, a1_module, a1_Ns, a1_Np | high | same value as a1_bearing_OD (the CAD writes it under both stage prefixes); catalogue bearing chosen by bearings_discrete for the bore the stage needs (smallest one that fits); this is its outer diameter |
| 82 | `a2_bearing1_height1` | lookup | `bearings_discrete(idRequiredMM=a1_module * (a1_Ns + a1_Np) + bearingIDClearanceMM)` → getBearingWidthMM | bearingIDClearanceMM, a1_module, a1_Ns, a1_Np | high | same value as a1_bearing_height (the CAD writes it under both stage prefixes); catalogue bearing chosen by bearings_discrete for the bore the stage needs (smallest one that fits); this is its width |
| 83 | `a1_ring_gear_relation` | formula | `Stator_height + a1_ring_gear_thickness_mounting_casing - bearing_retainer_thickness - a1_bearing_height - a1_carrier_bearing_step_width - a1_clearance_planet - a1_fw_r - a1_clearance_planet * 0.5` | a1_fw_r, a1_clearance_planet, a1_carrier_bearing_step_width, a1_bearing_height, bearing_retainer_thickness, Stator_height, a1_ring_gear_thickness_mounting_casing | medium | axial-fill check for stage 1: the stator height and mounting casing less the stage-1 stack (a value written for the CAD, not used by the code) |
| 84 | `a2_ring_gear_relation` | formula | `a1_fw_s_used + a1_standard_clearance_1_5mm + a1_carrier_bearing_step_width + a1_bearing_height + a1_fw_s_used2 - a2_fw_p - Stator_height - a1_ring_gear_thickness_mounting_casing - rotor_bottom_thickness - motor_stator_extrusion_depth` | motor_stator_extrusion_depth, rotor_bottom_thickness, a1_ring_gear_thickness_mounting_casing, Stator_height, a2_fw_p, a1_fw_s_used2, a1_bearing_height, a1_carrier_bearing_step_width, a1_fw_s_used, a1_standard_clearance_1_5mm | medium | axial-fill check for stage 2: the two stage lengths less the stator, rotor base and extrusion (a value written for the CAD, not used by the code) |

## Used by the code, not written to the CAD file (51)

| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |
|---|---|---|---|---|---|---|
| 1 | `motor_peak_torque` | motor | motors.json → motors.<motor>.electrical → `peak_torque_Nm` |  | high | motor torque the gears are sized for (peak torque under the default rating setting); sets the face widths |
| 2 | `gear_allowable_stress` | material | config.json → Material_properties.<gear material> → `maxAllowableStressMPa` |  | high | allowable tooth stress of the gear material, chosen with the material mode (3dp: PLA, metal: steel); sets the face widths |
| 3 | `FOS` | safety factor | idspg_motor_config.json → MIT_params → `FOS` |  | high | factor of safety in the tooth-stress rule |
| 4 | `serviceFactor` | safety factor | idspg_motor_config.json → MIT_params → `serviceFactor` |  | high | service factor on the motor torque in the tooth-stress rule |
| 5 | `planet_bearing_gap` | clearance | idspg_params.json → idspg_design_parameters_3DP → `planet_bearing_gap` |  | medium | axial gap between the two planet bearings (one in each planet gear); with the bearing width it sets the smallest planet and ring width of both stages; one key for both stages, the plan leaves open whether it should be one per stage (planet_bearing_gap1 / 2) |
| 6 | `maxGearboxDiameter` | formula | `MAX_GB_DIA_MULT_FACTOR * (a1_motor_OD + a1_standard_clearance_1_5mm * 2)` | MAX_GB_DIA_MULT_FACTOR, a1_motor_OD, a1_standard_clearance_1_5mm | high | largest gearbox diameter the optimiser may use (gearbox_runner max_diameter): the motor's outer diameter plus two clearances, times a factor |
| 7 | `maxGearboxDiameter_Stg1` | formula | `Stator_ID - ring1RadialWidthMM * 2` | Stator_ID, ring1RadialWidthMM | high | largest stage-1 diameter the optimiser may use (gearbox_runner max_diameter_stage1): the stator bore less two ring walls |
| 8 | `motorDiaMM` | motor | motors.json → motors.<motor>.geometry → `motor_OD` |  | high | read from the chosen motor's geometry |
| 9 | `motorLengthMM` | motor | motors.json → motors.<motor>.geometry → `motor_height` |  | high | read from the chosen motor's geometry |
| 10 | `bearingIDClearanceMM` | constraint constant | idspg_params.json → idspg_design_parameters_3DP → `bearingIDClearanceMM` |  | high | constant from the IDSPG 3DP design parameters (one value for both stages) |
| 11 | `shortfall` | constraint constant | constant `0` in the code |  | medium | always 0: the code sets it only in a disabled axial-fill case (the stage-2 sun length adds it) |
| 12 | `sCarrierExtrusionDiaMM_Stg1` | feature size | idspg_params.json → idspg_design_parameters_3DP → `sCarrierExtrusionDiaMM_Stg1` |  | high | read by the code but not written to the CAD file |
| 13 | `sCarrierExtrusionClearanceMM_Stg1` | clearance | idspg_params.json → idspg_design_parameters_3DP → `sCarrierExtrusionClearanceMM_Stg1` |  | high | read by the code but not written to the CAD file |
| 14 | `sCarrierExtrusionDiaMM_Stg2` | feature size | idspg_params.json → idspg_design_parameters_3DP → `sCarrierExtrusionDiaMM_Stg2` |  | high | read by the code but not written to the CAD file |
| 15 | `sCarrierExtrusionClearanceMM_Stg2` | clearance | idspg_params.json → idspg_design_parameters_3DP → `sCarrierExtrusionClearanceMM_Stg2` |  | high | read by the code but not written to the CAD file |
| 16 | `planetMinDistanceMM` | constraint constant | idspg_params.json → idspg_design_parameters_3DP → `planetMinDistanceMM` |  | high | read by the code but not written to the CAD file |
| 17 | `Motor_case_thickness` | wall thickness | idspg_params.json → idspg_design_parameters_3DP → `Motor_case_thickness` |  | high | read by the code but not written to the CAD file |
| 18 | `clearance_case_mount_holes_shell_thickness` | clearance | idspg_params.json → idspg_design_parameters_3DP → `clearance_case_mount_holes_shell_thickness` |  | high | read by the code but not written to the CAD file |
| 19 | `output_mounting_hole_dia1` | fastener size | idspg_params.json → idspg_design_parameters_3DP → `output_mounting_hole_dia1` |  | high | read by the code but not written to the CAD file |
| 20 | `case_mounting_hole_dia` | fastener size | idspg_params.json → idspg_design_parameters_3DP → `case_mounting_hole_dia` |  | high | read by the code but not written to the CAD file |
| 21 | `case_mounting_bolt_depth` | fastener size | idspg_params.json → idspg_design_parameters_3DP → `case_mounting_bolt_depth` |  | high | read by the code but not written to the CAD file |
| 22 | `case_mounting_surface_height` | wall thickness | idspg_params.json → idspg_design_parameters_3DP → `case_mounting_surface_height` |  | high | read by the code but not written to the CAD file |
| 23 | `bearing_retainer_thickness1` | wall thickness | idspg_params.json → idspg_design_parameters_3DP → `bearing_retainer_thickness1` |  | high | in the config but never read |
| 24 | `central_hole_offset_from_motor_mount_PCD` | feature size | idspg_params.json → idspg_design_parameters_3DP → `central_hole_offset_from_motor_mount_PCD` |  | high | read by the code but not written to the CAD file |
| 25 | `base_plate_thickness` | wall thickness | idspg_params.json → idspg_design_parameters_3DP → `base_plate_thickness` |  | high | read by the code but not written to the CAD file |
| 26 | `air_flow_hole_offset` | feature size | idspg_params.json → idspg_design_parameters_3DP → `air_flow_hole_offset` |  | high | read by the code but not written to the CAD file |
| 27 | `output_mounting_nut_depth1` | fastener size | idspg_params.json → idspg_design_parameters_3DP → `output_mounting_nut_depth1` |  | high | read by the code but not written to the CAD file |
| 28 | `ring_to_chamfer_clearance1` | clearance | idspg_params.json → idspg_design_parameters_3DP → `ring_to_chamfer_clearance1` |  | high | read by the code but not written to the CAD file |
| 29 | `Motor_case_OD_base_to_chamfer` | feature size | idspg_params.json → idspg_design_parameters_3DP → `Motor_case_OD_base_to_chamfer` |  | high | read by the code but not written to the CAD file |
| 30 | `case_mounting_nut_clearance` | clearance | idspg_params.json → idspg_design_parameters_3DP → `case_mounting_nut_clearance` |  | high | read by the code but not written to the CAD file |
| 31 | `clearance_case_mount_holes_shell_thickness2` | clearance | idspg_params.json → idspg_design_parameters_3DP → `clearance_case_mount_holes_shell_thickness2` |  | high | read by the code but not written to the CAD file |
| 32 | `ring_to_chamfer_clearance2` | clearance | idspg_params.json → idspg_design_parameters_3DP → `ring_to_chamfer_clearance2` |  | high | read by the code but not written to the CAD file |
| 33 | `bearing_retainer_thickness2` | wall thickness | idspg_params.json → idspg_design_parameters_3DP → `bearing_retainer_thickness2` |  | high | in the config but never read |
| 34 | `stg1_stg2_mounting_hole_dia` | fastener size | idspg_params.json → idspg_design_parameters_3DP → `stg1_stg2_mounting_hole_dia` |  | high | read by the code but not written to the CAD file |
| 35 | `stg1_stg2_mounting_pattern_width` | wall thickness | idspg_params.json → idspg_design_parameters_3DP → `stg1_stg2_mounting_pattern_width` |  | high | read by the code but not written to the CAD file |
| 36 | `ring1RadialWidthMM` | wall thickness | idspg_params.json → idspg_design_parameters_3DP → `ring1RadialWidthMM` |  | high | read by the code but not written to the CAD file |
| 37 | `ring2RadialWidthMM` | wall thickness | idspg_params.json → idspg_design_parameters_3DP → `ring2RadialWidthMM` |  | high | read by the code but not written to the CAD file |
| 38 | `GEAR_RATIO_MIN` | search bound | idspg_params.json → idspg_optimization_parameters → `GEAR_RATIO_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 39 | `GEAR_RATIO_MAX` | search bound | idspg_params.json → idspg_optimization_parameters → `GEAR_RATIO_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 40 | `GEAR_RATIO_STEP` | search bound | idspg_params.json → idspg_optimization_parameters → `GEAR_RATIO_STEP` |  | high | optimiser setting: limits of the search, not a part dimension |
| 41 | `MODULE_STAGE1_MIN` | search bound | idspg_params.json → idspg_optimization_parameters → `MODULE_STAGE1_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 42 | `MODULE_STAGE1_MAX` | search bound | idspg_params.json → idspg_optimization_parameters → `MODULE_STAGE1_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 43 | `MODULE_STAGE2_MIN` | search bound | idspg_params.json → idspg_optimization_parameters → `MODULE_STAGE2_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 44 | `MODULE_STAGE2_MAX` | search bound | idspg_params.json → idspg_optimization_parameters → `MODULE_STAGE2_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 45 | `NUM_PLANET_STAGE1_MIN` | search bound | idspg_params.json → idspg_optimization_parameters → `NUM_PLANET_STAGE1_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 46 | `NUM_PLANET_STAGE1_MAX` | search bound | idspg_params.json → idspg_optimization_parameters → `NUM_PLANET_STAGE1_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 47 | `NUM_PLANET_STAGE2_MIN` | search bound | idspg_params.json → idspg_optimization_parameters → `NUM_PLANET_STAGE2_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 48 | `NUM_PLANET_STAGE2_MAX` | search bound | idspg_params.json → idspg_optimization_parameters → `NUM_PLANET_STAGE2_MAX` |  | high | optimiser setting: limits of the search, not a part dimension |
| 49 | `NUM_TEETH_SUN_MIN` | search bound | idspg_params.json → idspg_optimization_parameters → `NUM_TEETH_SUN_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 50 | `NUM_TEETH_PLANET_MIN` | search bound | idspg_params.json → idspg_optimization_parameters → `NUM_TEETH_PLANET_MIN` |  | high | optimiser setting: limits of the search, not a part dimension |
| 51 | `MAX_GB_DIA_MULT_FACTOR` | search bound | idspg_params.json → idspg_optimization_parameters → `MAX_GB_DIA_MULT_FACTOR` |  | high | optimiser setting: limits of the search, not a part dimension |

## Config blocks IDSPG doesn't read

- idspg_params.json → `idspg_design_parameters`: older design block (29 keys); IDSPG reads only idspg_design_parameters_3DP (gearbox_runner)
