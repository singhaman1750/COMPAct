# DSPG: variable classification plan

Part of [the plan for all actuators](../PLAN.md). Survey only: nothing in the code, config or CAD output changes on this branch.

## Inventory

- **CAD interface:** `dspg_equations_onshape.txt`, **255 variables**; other files: `dspg_equations_stg1.txt` (129), `dspg_equations_stg2.txt` (128)
- **Code:** `doubleStagePlanetaryActuator` in `ActuatorAndGearbox.py` (lines 6620-9179)
- **Config:** `dspg_params.json`, block(s) read: `dspg_design_parameters_3DP`; search bounds `dspg_optimization_parameters`; gear standard / MIT factors from `config.json`; driver: `OdrivePro`
- **Survey draft:** dependent 115, fixed 89, input 36, optimisation 15; 0 names also in SSPG / CPG; 78 alias names (same value written under a second name); 9 flagged by the survey

## Special cases

| Variable(s) | What the code does | Proposed classification |
|---|---|---|
| `a1_*` / `a2_*` | two stages; each stage's variables have its prefix. The Onshape file (255) is the interface; the plain files `dspg_equations_stg1.txt` (129) and `_stg2.txt` (128) carry the same values under stage-local names | one spec entry per Onshape name; the stage files are checked as aliases (like `"pressure angle"`) |
| **78 alias pairs** | the same attribute is written under both prefixes (e.g. `a1_Ns` = `a2_Ns1`, `a1_module2` = `a2_module`, all motor and driver inputs under both) | both names classified identically; the spec marks the second as `alias_of` the first; the test checks they are equal |
| `a1_Nr`, `a2_Nr` | `Ns + 2·Np` per stage | Dependent / implicit constraint; extend the shared rule to `a1_Nr`, `a2_Nr` (and the alias names `a1_Nr2`, `a2_Nr1`) |
| `a1_module`, `a2_module` | one module per stage (`Stage1.module`, `Stage2.module`) | Optimisation (both); no bug-18 issue here: each stage has its own module in the CAD |
| `a1_fw_s_calc`, `a1_fw_r`, `a2_fw_s_calc`, `a2_fw_r` | MIT stress rule per stage, with an SSPG-style planet-bearing minimum | Dependent / stress rule; extend the shared pattern to the prefixed names |
| `a1_fw_p` = `fw_r1`, `a2_fw_p` = `fw_r2` | planet width is a copy of the ring width | Dependent / formula |
| `a2_clearance_motor_and_case`, `a2_motor_case_OD_base`, … | stage 2 writes the **stage-1 casing** values (one motor case) | aliases of the `a1_` values |
| `a2_sun_coupler_hub_thickness` | the writer writes `getattr(self, "sun_coupler_hub_thickness1", "N/A")`, i.e. the stage-1 value | alias of `a1_sun_coupler_hub_thickness` (Fixed); note the unusual writer expression |
| `a1_stg1_stg2_mounting_extra_width` (+ `a2_` alias) | two-case rule: 0, or extra width so the stage-2 ring + bolts fit | Dependent / formula (two-case) |
| `a1_case_dist`, `a2_case_dist` | different formulas per stage (stage 2: carrier + clearances − retainer) | Dependent / formula |
| per-stage config keys | stage-specific keys end in `1` / `2` (`planet_bearing_width1`, `output_mounting_hole_dia1`, …); shared ones don't | Fixed / config; keep DSPG's suffix convention for any new key |

## Hard-coded numbers (medium; candidates for the config)

| Where | Number | Proposed key |
|---|---|---|
| `a1_clearance_motor_and_case` (CAD L6799; mass stg1 L8725-8727) | 5 | `clearance_motor_and_case_min` |
| `a1_case_mounting_hole_shift` (L6802) | 0.5 | `case_mounting_hole_wall_overlap` |
| `a1_/a2_bearing_mount_thickness` (CAD L6807, L6991; mass stg1 L8757-8760, stg2 L9022-9025) | 2, 4 | `bearing_mount_wall_bolt_dia_multiple` (one key for both stages, or `…1` / `…2`: decide in review) |
| `a1_sun_hub_dia` (CAD L6814; mass stg1 L8828) | 4 | shared item: `sun_hub_dia` margin (also SSPG / CPG) |
| planet-bearing minimum per stage (`mitStressAnalysisMinFacewidth` L8586-8591) | 2/3 | `planet_bearing_gap` (one key, or `planet_bearing_gap1` / `2`: decide in review) |

## Config
- `dspg_design_parameters` (29 keys): **not read** → unused block (its `sCarrierExtrusion*` / `planetMinDistanceMM` names also exist in the 3DP block, which is the one read).
- Code-only keys of `dspg_design_parameters_3DP`: `sCarrierExtrusionDiaMM_Stg1/2`, `sCarrierExtrusionClearanceMM_Stg1/2`, `planetMinDistanceMM`, `bearingIDClearanceMM`, `clearance_case_mount_holes_shell_thickness2` (check: read but not written).
- Optimisation block: 16 search bounds (per-stage module and planet ranges).

## Test plan
- Tooling: **the registry must handle a gearbox with stage files** (check `_stg1` / `_stg2` names as aliases of the Onshape names) and **alias pairs** (equal values).
- Setter for both stages' Ns / Np / Nr / module / planets; 6 golden designs.
- Extra gear sets for: `stg1_stg2_mounting_extra_width` (both branches), bearing mount per stage (both branches), motor-case clearance (ring wider / narrower than motor).
- DSPG-specific: stress-rule widths per stage, each moved key.

## Risks / notes
- Largest type (255 names, 78 aliases); the alias handling is new tooling.
- Effort: ~2.5 h.

## Survey draft: every variable

Automatic first pass from the code (the special cases above take precedence). Category guesses come from the source of each value; *flags* mark hard-coded numbers, several assignments or a writer expression. The final category, sub-type, `depends_on`, confidence and reason are set during the classification itself.

| # | Variable | Draft category / sub-type | Conf. | Line | Code | Flags | SSPG / CPG |
|---|---|---|---|---|---|---|---|
| 1 | `a1_Ns` | optimisation / teeth | high | 6684 | `self.doubleStagePlanetaryGearbox.Stage1.Ns` |  |  |
| 2 | `a1_Np` | optimisation / teeth | high | 6685 | `self.doubleStagePlanetaryGearbox.Stage1.Np` |  |  |
| 3 | `a1_Nr` | dependent / formula | high | 6754 | `self.Ns1 + 2 * self.Np1` |  |  |
| 4 | `a1_num_planet` | optimisation / planets | high | 6686 | `self.doubleStagePlanetaryGearbox.Stage1.numPlanet` |  |  |
| 5 | `a1_module` | optimisation / module | high | 6687 | `self.doubleStagePlanetaryGearbox.Stage1.module` |  |  |
| 6 | `a1_pressure_angle` | fixed / gear standard | high | 6693 | `self.doubleStagePlanetaryGearbox.Stage1.getPressureAngleRad() * 180 / np.pi` |  |  |
| 7 | `a1_motor_mount_hole_PCD` | input / motor | high | 6722 | `self.motor.motor_mount_hole_PCD` |  |  |
| 8 | `a1_motor_mount_hole_dia` | input / motor | high | 6723 | `self.motor.motor_mount_hole_dia` |  |  |
| 9 | `a1_motor_mount_hole_num` | input / motor | high | 6724 | `self.motor.motor_mount_hole_num` |  |  |
| 10 | `a1_motor_output_hole_PCD` | input / motor | high | 6725 | `self.motor.motor_output_hole_PCD` |  |  |
| 11 | `a1_motor_output_hole_dia` | input / motor | high | 6726 | `self.motor.motor_output_hole_dia` |  |  |
| 12 | `a1_motor_output_hole_num` | input / motor | high | 6727 | `self.motor.motor_output_hole_num` |  |  |
| 13 | `a1_motor_OD` | input / motor | high | 6720 | `self.motorDiaMM` |  |  |
| 14 | `a1_motor_height` | input / motor | high | 6721 | `self.motorLengthMM` |  |  |
| 15 | `a1_wire_slot_dist_from_center` | input / motor | high | 6728 | `self.motor.wire_slot_dist_from_center` |  |  |
| 16 | `a1_wire_slot_length` | input / motor | high | 6729 | `self.motor.wire_slot_length` |  |  |
| 17 | `a1_wire_slot_radius` | input / motor | high | 6730 | `self.motor.wire_slot_radius` |  |  |
| 18 | `a1_h_a` | dependent / formula | high | 6755 | `1 * self.module1` |  |  |
| 19 | `a1_h_b` | dependent / formula | high | 6757 | `1.25 * self.module1` |  |  |
| 20 | `a1_h_f` | dependent / formula | high | 6756 | `1.25 * self.module1` |  |  |
| 21 | `a1_clr_tip_root` | dependent / formula | high | 6759 | `self.h_f1 - self.h_a1` |  |  |
| 22 | `a1_dp_s` | dependent / formula | high | 6762 | `self.module1 * self.Ns1` |  |  |
| 23 | `a1_db_s` | dependent / formula | high | 6763 | `self.dp_s1 * np.cos(np.deg2rad(self.pressure_angle))` |  |  |
| 24 | `a1_fw_s_calc` | dependent / stress rule (face width) | high | 6689 | `self.doubleStagePlanetaryGearbox.Stage1.fwSunMM` |  |  |
| 25 | `a1_alpha_s` | dependent / formula | high | 6764 | `np.sqrt(self.dp_s1 ** 2 - self.db_s1 ** 2) / self.db_s1 * 180 / np.pi - self.pressure_angle` |  |  |
| 26 | `a1_beta_s` | dependent / formula | high | 6765 | `(360 / (4 * self.Ns1) - self.alpha_s1) * 2` |  |  |
| 27 | `a1_dp_p` | dependent / formula | high | 6768 | `self.module1 * self.Np1` |  |  |
| 28 | `a1_db_p` | dependent / formula | high | 6769 | `self.dp_p1 * np.cos(np.deg2rad(self.pressure_angle))` |  |  |
| 29 | `a1_fw_p` | dependent / formula | high | 6758 | `self.fw_r1` |  |  |
| 30 | `a1_alpha_p` | dependent / formula | high | 6770 | `np.sqrt(self.dp_p1 ** 2 - self.db_p1 ** 2) / self.db_p1 * 180 / np.pi - self.pressure_angle` |  |  |
| 31 | `a1_beta_p` | dependent / formula | high | 6771 | `(360 / (4 * self.Np1) - self.alpha_p1) * 2` |  |  |
| 32 | `a1_dp_r` | dependent / formula | high | 6774 | `self.module1 * self.Nr1` |  |  |
| 33 | `a1_db_r` | dependent / formula | high | 6775 | `self.dp_r1 * np.cos(np.deg2rad(self.pressure_angle))` |  |  |
| 34 | `a1_fw_r` | dependent / stress rule (face width) | high | 6690 | `self.doubleStagePlanetaryGearbox.Stage1.fwRingMM` |  |  |
| 35 | `a1_alpha_r` | dependent / formula | high | 6776 | `np.sqrt(self.dp_r1 ** 2 - self.db_r1 ** 2) / self.db_r1 * 180 / np.pi - self.pressure_angle` |  |  |
| 36 | `a1_beta_r` | dependent / formula | high | 6777 | `(360 / (4 * self.Nr1) + self.alpha_r1) * 2` |  |  |
| 37 | `a1_bearing_ID` | dependent / lookup (bearing) | high | 6786 | `Bearing1.getBearingIDMM()` |  |  |
| 38 | `a1_bearing_OD` | dependent / lookup (bearing) | high | 6787 | `Bearing1.getBearingODMM()` |  |  |
| 39 | `a1_bearing_height` | dependent / lookup (bearing) | high | 6788 | `Bearing1.getBearingWidthMM()` |  |  |
| 40 | `a1_clearance_planet` | fixed / config | high | 6695, 6892 | `self.design_params["clearance_planet"] ‖ self.design_params["clearance_planet"]` | 2 assignments (two-case rule or reassigned) |  |
| 41 | `a1_case_dist` | dependent / formula | high | 6813 | `self.sec_carrier_thickness1 + self.clearance_planet + self.sun_coupler_hub_thickness1 - self.case_mounting_sur…` |  |  |
| 42 | `a1_Motor_case_OD_max` | dependent / formula | high | 6804 | `self.case_mounting_PCD + self.case_mounting_hole_allen_socket_dia + self.clearance_case_mount_holes_shell_thic…` |  |  |
| 43 | `a1_case_mounting_PCD` | dependent / formula | high | 6803 | `self.motor_case_OD_base + self.case_mounting_hole_shift * 2` |  |  |
| 44 | `a1_bearing_mount_thickness` | dependent / formula | medium | 6807 | `(self.output_mounting_hole_dia1 * 2 if (self.bearing1_OD + self.output_mounting_hole_dia1 * 4) > (self.Nr1 * s…` | numbers 4 |  |
| 45 | `a1_case_mounting_hole_dia` | fixed / config | high | 6708 | `self.design_params["case_mounting_hole_dia"]` |  |  |
| 46 | `a1_output_mounting_PCD` | dependent / formula | high | 6808 | `self.bearing1_OD + self.bearing_mount_thickness1` |  |  |
| 47 | `a1_output_mounting_hole_dia` | fixed / config | high | 6707 | `self.design_params["output_mounting_hole_dia1"]` |  |  |
| 48 | `a1_clearance_case_mount_holes_shell_thickness` | fixed / config | high | 6706 | `self.design_params["clearance_case_mount_holes_shell_thickness"]` |  |  |
| 49 | `a1_motor_case_OD_base` | dependent / formula | high | 6800 | `self.motor_OD + self.clearance_motor_and_case * 2 + self.Motor_case_thickness * 2` |  |  |
| 50 | `a1_sec_carrier_thickness` | fixed / config | high | 6702 | `self.design_params["sec_carrier_thickness1"]` |  |  |
| 51 | `a1_sun_coupler_hub_thickness` | fixed / config | high | 6703 | `self.design_params["sun_coupler_hub_thickness1"]` |  |  |
| 52 | `a1_clearance_sun_coupler_sec_carrier` | fixed / config | high | 6704, 6894 | `self.design_params["clearance_sun_coupler_sec_carrier"] ‖ self.design_params["clearance_sun_coupler_sec_carrie…` | 2 assignments (two-case rule or reassigned) |  |
| 53 | `a1_clearance_motor_and_case` | dependent / formula | medium | 6799 | `(5 if self.ring_OD1 < self.motor_OD else (self.ring_OD1 - self.motor_OD) / 2 + 5)` | numbers 5 |  |
| 54 | `a1_Motor_case_thickness` | fixed / config | high | 6705 | `self.design_params["Motor_case_thickness"]` |  |  |
| 55 | `a1_Motor_case_ID` | dependent / formula | high | 6801 | `self.motor_OD + self.clearance_motor_and_case * 2` |  |  |
| 56 | `a1_case_mounting_hole_shift` | dependent / formula | medium | 6802 | `self.case_mounting_hole_dia / 2 - 0.5` | numbers 0.5 |  |
| 57 | `a1_output_mounting_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 6842 | `output_mounting_bolt1.nut_width_across_flats` |  |  |
| 58 | `a1_output_mounting_nut_thickness` | dependent / lookup (bolt/nut) | high | 6843 | `output_mounting_bolt1.nut_thickness` |  |  |
| 59 | `a1_case_mounting_hole_allen_socket_dia` | dependent / lookup (bolt/nut) | high | 6793 | `case_mounting_bolt.bolt_head_dia` |  |  |
| 60 | `a1_output_mounting_nut_depth` | fixed / config | high | 6819 | `self.design_params["output_mounting_nut_depth1"]` |  |  |
| 61 | `a1_case_mounting_bolt_depth` | fixed / config | high | 6709 | `self.design_params["case_mounting_bolt_depth"]` |  |  |
| 62 | `a1_ring_radial_thickness` | fixed / config | high | 6701, 6897 | `self.design_params["ring_radial_thickness"] ‖ self.design_params["ring_radial_thickness"]` | 2 assignments (two-case rule or reassigned) |  |
| 63 | `a1_ring_OD` | dependent / formula | high | 6798 | `self.Nr1 * self.module1 + self.ring_radial_thickness * 2` |  |  |
| 64 | `a1_ring_to_chamfer_clearance` | fixed / config | high | 6820 | `self.design_params["ring_to_chamfer_clearance1"]` |  |  |
| 65 | `a1_Motor_case_OD_base_to_chamfer` | fixed / config | high | 6821 | `self.design_params["Motor_case_OD_base_to_chamfer"]` |  |  |
| 66 | `a1_pattern_offset_from_motor_case_OD_base` | fixed / config | high | 6822 | `self.design_params["pattern_offset_from_motor_case_OD_base"]` |  |  |
| 67 | `a1_pattern_bulge_dia` | fixed / config | high | 6823 | `self.design_params["pattern_bulge_dia"]` |  |  |
| 68 | `a1_pattern_num_bulge` | fixed / config | high | 6824 | `self.design_params["pattern_num_bulge"]` |  |  |
| 69 | `a1_pattern_depth` | fixed / config | high | 6825 | `self.design_params["pattern_depth"]` |  |  |
| 70 | `a1_case_mounting_wrench_size` | dependent / lookup (bolt/nut) | high | 6794 | `case_mounting_bolt.nut_width_across_flats` |  |  |
| 71 | `a1_case_mounting_nut_clearance` | fixed / config | high | 6826 | `self.design_params["case_mounting_nut_clearance"]` |  |  |
| 72 | `a1_base_plate_thickness` | fixed / config | high | 6739 | `self.design_params["base_plate_thickness"]` |  |  |
| 73 | `a1_case_mounting_nut_thickness` | dependent / lookup (bolt/nut) | high | 6795 | `case_mounting_bolt.nut_thickness` |  |  |
| 74 | `a1_case_mounting_surface_height` | fixed / config | high | 6710 | `self.design_params["case_mounting_surface_height"]` |  |  |
| 75 | `a1_central_hole_offset_from_motor_mount_PCD` | fixed / config | high | 6737 | `self.design_params["central_hole_offset_from_motor_mount_PCD"]` |  |  |
| 76 | `a1_driver_upper_holes_dist_from_center` | input / driver | high | 6743 | `self.motor_driver_params["driver_upper_holes_dist_from_center"]` |  |  |
| 77 | `a1_driver_lower_holes_dist_from_center` | input / driver | high | 6744 | `self.motor_driver_params["driver_lower_holes_dist_from_center"]` |  |  |
| 78 | `a1_driver_side_holes_dist_from_center` | input / driver | high | 6745 | `self.motor_driver_params["driver_side_holes_dist_from_center"]` |  |  |
| 79 | `a1_driver_mount_holes_dia` | input / driver | high | 6746 | `self.motor_driver_params["driver_mount_holes_dia"]` |  |  |
| 80 | `a1_driver_mount_inserts_OD` | input / driver | high | 6747 | `self.motor_driver_params["driver_mount_inserts_OD"]` |  |  |
| 81 | `a1_driver_mount_thickness` | input / driver | high | 6748 | `self.motor_driver_params["driver_mount_thickness"]` |  |  |
| 82 | `a1_driver_mount_height` | input / driver | high | 6749 | `self.motor_driver_params["driver_mount_height"]` |  |  |
| 83 | `a1_air_flow_hole_offset` | fixed / config | high | 6740 | `self.design_params["air_flow_hole_offset"]` |  |  |
| 84 | `a1_planet_pin_bolt_dia` | fixed / config | high | 6836 | `self.design_params["planet_pin_bolt_dia1"]` |  |  |
| 85 | `a1_planet_pin_socket_head_dia` | dependent / lookup (bolt/nut) | high | 6847 | `planet_pin_bolt1.bolt_head_dia` |  |  |
| 86 | `a1_carrier_PCD` | dependent / formula | high | 6811 | `(self.Np1 + self.Ns1) * self.module1` |  |  |
| 87 | `a1_planet_shaft_dia` | fixed / config | high | 6827 | `self.design_params["planet_shaft_dia1"]` |  |  |
| 88 | `a1_planet_shaft_step_offset` | fixed / config | high | 6712 | `self.design_params["planet_shaft_step_offset"]` |  |  |
| 89 | `a1_carrier_trapezoidal_support_sun_offset` | fixed / config | high | 6828 | `self.design_params["carrier_trapezoidal_support_sun_offset1"]` |  |  |
| 90 | `a1_carrier_trapezoidal_support_hole_PCD_offset_bearing_ID` | fixed / config | high | 6829 | `self.design_params["carrier_trapezoidal_support_hole_PCD_offset_bearing_ID1"]` |  |  |
| 91 | `a1_carrier_trapezoidal_support_hole_dia` | fixed / config | high | 6837 | `self.design_params["carrier_trapezoidal_support_hole_dia1"]` |  |  |
| 92 | `a1_carrier_trapezoidal_support_hole_socket_head_dia` | dependent / lookup (bolt/nut) | high | 6852 | `carrier_trapezoidal_support_hole_bolt1.bolt_head_dia` |  |  |
| 93 | `a1_carrier_bearing_step_width` | fixed / config | high | 6711 | `self.design_params["carrier_bearing_step_width"]` |  |  |
| 94 | `a1_standard_clearance_1_5mm` | fixed / config | high | 6698, 6895 | `self.design_params["standard_clearance_1_5mm"] ‖ self.design_params["standard_clearance_1_5mm"]` | 2 assignments (two-case rule or reassigned) |  |
| 95 | `a1_standard_fillet_1_5mm` | fixed / config | high | 6699, 6896 | `self.design_params["standard_fillet_1_5mm"] ‖ self.design_params["standard_fillet_1_5mm"]` | 2 assignments (two-case rule or reassigned) |  |
| 96 | `a1_sun_shaft_bearing_OD` | fixed / config | high | 6830 | `self.design_params["sun_shaft_bearing_OD1"]` |  |  |
| 97 | `a1_sun_shaft_bearing_width` | fixed / config | high | 6831 | `self.design_params["sun_shaft_bearing_width1"]` |  |  |
| 98 | `a1_standard_bearing_insertion_chamfer` | fixed / config | high | 6700 | `self.design_params["standard_bearing_insertion_chamfer"]` |  |  |
| 99 | `a1_carrier_trapezoidal_support_hole_wrench_size` | dependent / lookup (bolt/nut) | high | 6853 | `carrier_trapezoidal_support_hole_bolt1.nut_width_across_flats` |  |  |
| 100 | `a1_planet_pin_bolt_wrench_size` | dependent / lookup (bolt/nut) | high | 6848 | `planet_pin_bolt1.nut_width_across_flats` |  |  |
| 101 | `a1_planet_bearing_OD` | fixed / config | high | 6832 | `self.design_params["planet_bearing_OD1"]` |  |  |
| 102 | `a1_planet_bearing_width` | fixed / config | high | 6833 | `self.design_params["planet_bearing_width1"]` |  |  |
| 103 | `a1_planet_bore` | fixed / config | high | 6834 | `self.design_params["planet_bore1"]` |  |  |
| 104 | `a1_sun_shaft_bearing_ID` | fixed / config | high | 6835 | `self.design_params["sun_shaft_bearing_ID1"]` |  |  |
| 105 | `a1_sun_hub_dia` | dependent / formula | medium | 6814 | `self.motor_output_hole_PCD + self.motor_output_hole_dia + self.standard_clearance_1_5mm * 4` | numbers 4 |  |
| 106 | `a1_sun_central_bolt_dia` | fixed / config | high | 6838 | `self.design_params["sun_central_bolt_dia1"]` |  |  |
| 107 | `a1_sun_central_bolt_socket_head_dia` | dependent / lookup (bolt/nut) | high | 6857 | `sun_central_bolt1.bolt_head_dia` |  |  |
| 108 | `a1_fw_s_used` | dependent / formula | high | 6812 | `self.fw_p1 + self.clearance_planet + self.sec_carrier_thickness1 + self.standard_clearance_1_5mm` |  |  |
| 109 | `a1_motor_output_hole_CSK_OD` | dependent / lookup (bolt/nut) | high | 6734 | `motor_output_hole_bolt.bolt_head_dia` |  |  |
| 110 | `a1_motor_output_hole_CSK_head_height` | dependent / lookup (bolt/nut) | high | 6735 | `motor_output_hole_bolt.bolt_head_height` |  |  |
| 111 | `a1_bearing_retainer_thickness` | fixed / config | high | 6713 | `self.design_params["bearing_retainer_thickness1"]` |  |  |
| 112 | `a1_stg1_stg2_mounting_pattern_width` | fixed / config | high | 6918 | `self.design_params["stg1_stg2_mounting_pattern_width"]` |  |  |
| 113 | `a1_stg1_stg2_allen_socket_head_dia` | dependent / lookup (bolt/nut) | high | 6983 | `stg1_stg2_mounting_hole.bolt_head_dia` |  |  |
| 114 | `a1_stg1_stg2_mounting_hole_dia` | fixed / config | high | 6917 | `self.design_params["stg1_stg2_mounting_hole_dia"]` |  |  |
| 115 | `a1_Ns2` | optimisation / teeth | high | 6882 | `self.doubleStagePlanetaryGearbox.Stage2.Ns` |  |  |
| 116 | `a1_Np2` | optimisation / teeth | high | 6883 | `self.doubleStagePlanetaryGearbox.Stage2.Np` |  |  |
| 117 | `a1_Nr2` | dependent / formula | high | 6925 | `self.Ns2 + 2 * self.Np2` |  |  |
| 118 | `a1_module2` | optimisation / module | high | 6884 | `self.doubleStagePlanetaryGearbox.Stage2.module` |  |  |
| 119 | `a1_stg1_stg2_mounting_extra_width` | dependent / formula | high | 6998 | `(0) if ((self.Nr2 * self.module2 + self.ring_radial_thickness * 2 + self.stg1_stg2_allen_socket_head_dia) / 2 …` |  |  |
| 120 | `a1_dp_s2` | dependent / formula | high | 6935 | `self.module2 * self.Ns2` |  |  |
| 121 | `a1_db_s2` | dependent / formula | high | 6939 | `self.dp_s2 * np.cos(np.deg2rad(self.pressure_angle))` |  |  |
| 122 | `a1_fw_s_calc2` | dependent / stress rule (face width) | high | 6888 | `self.doubleStagePlanetaryGearbox.Stage2.fwSunMM` |  |  |
| 123 | `a1_alpha_s2` | dependent / formula | high | 6944 | `np.sqrt(self.dp_s2**2 - self.db_s2**2) / self.db_s2 * 180 / np.pi - self.pressure_angle` |  |  |
| 124 | `a1_beta_s2` | dependent / formula | high | 6947 | `(360 / (4 * self.Ns2) - self.alpha_s2) * 2` |  |  |
| 125 | `a1_fw_s_used2` | dependent / formula | high | 6990 | `self.fw_p2 + self.clearance_planet + self.sec_carrier_thickness2 + self.standard_clearance_1_5mm` |  |  |
| 126 | `a1_fw_p2` | dependent / formula | high | 6926 | `self.fw_r2` |  |  |
| 127 | `a1_tight_clearance_3DP` | fixed / config | high | 6696 | `self.design_params["tight_clearance_3DP"]` |  |  |
| 128 | `a1_loose_clearance_3DP` | fixed / config | high | 6697 | `self.design_params["loose_clearance_3DP"]` |  |  |
| 129 | `a2_Ns` | optimisation / teeth | high | 6882 | `self.doubleStagePlanetaryGearbox.Stage2.Ns` |  |  |
| 130 | `a2_Np` | optimisation / teeth | high | 6883 | `self.doubleStagePlanetaryGearbox.Stage2.Np` |  |  |
| 131 | `a2_Nr` | dependent / formula | high | 6925 | `self.Ns2 + 2 * self.Np2` |  |  |
| 132 | `a2_module` | optimisation / module | high | 6884 | `self.doubleStagePlanetaryGearbox.Stage2.module` |  |  |
| 133 | `a2_pressure_angle` | fixed / gear standard | high | 6693 | `self.doubleStagePlanetaryGearbox.Stage1.getPressureAngleRad() * 180 / np.pi` |  |  |
| 134 | `a2_h_a` | dependent / formula | high | 6927 | `1 * self.module2` |  |  |
| 135 | `a2_h_f` | dependent / formula | high | 6928 | `1.25 * self.module2` |  |  |
| 136 | `a2_clr_tip_root` | dependent / formula | high | 6930 | `self.h_f2 - self.h_a2` |  |  |
| 137 | `a2_dp_r` | dependent / formula | high | 6934 | `self.module2 * self.Nr2` |  |  |
| 138 | `a2_db_r` | dependent / formula | high | 6941 | `self.dp_r2 * np.cos(np.deg2rad(self.pressure_angle))` |  |  |
| 139 | `a2_fw_r` | dependent / stress rule (face width) | high | 6889 | `self.doubleStagePlanetaryGearbox.Stage2.fwRingMM` |  |  |
| 140 | `a2_alpha_r` | dependent / formula | high | 6946 | `np.sqrt(self.dp_r2**2 - self.db_r2**2) / self.db_r2 * 180 / np.pi - self.pressure_angle` |  |  |
| 141 | `a2_beta_r` | dependent / formula | high | 6949 | `(360 / (4 * self.Nr2) + self.alpha_r2) * 2` |  |  |
| 142 | `a2_bearing_ID` | dependent / lookup (bearing) | high | 6958 | `Bearing2.getBearingIDMM()` |  |  |
| 143 | `a2_bearing_OD` | dependent / lookup (bearing) | high | 6959 | `Bearing2.getBearingODMM()` |  |  |
| 144 | `a2_bearing_height` | dependent / lookup (bearing) | high | 6960 | `Bearing2.getBearingWidthMM()` |  |  |
| 145 | `a2_clearance_planet` | fixed / config | high | 6695, 6892 | `self.design_params["clearance_planet"] ‖ self.design_params["clearance_planet"]` | 2 assignments (two-case rule or reassigned) |  |
| 146 | `a2_case_dist` | dependent / formula | high | 6993 | `self.sec_carrier_thickness2 + self.clearance_planet + self.standard_clearance_1_5mm - self.bearing_retainer_th…` |  |  |
| 147 | `a2_Motor_case_OD_max` | dependent / formula | high | 6804 | `self.case_mounting_PCD + self.case_mounting_hole_allen_socket_dia + self.clearance_case_mount_holes_shell_thic…` |  |  |
| 148 | `a2_case_mounting_PCD` | dependent / formula | high | 6803 | `self.motor_case_OD_base + self.case_mounting_hole_shift * 2` |  |  |
| 149 | `a2_bearing_mount_thickness` | dependent / formula | medium | 6991 | `(self.output_mounting_hole_dia2 * 2) if ((self.bearing2_OD + self.output_mounting_hole_dia2 * 4) > (self.Nr2 *…` | numbers 4 |  |
| 150 | `a2_case_mounting_hole_dia` | fixed / config | high | 6708 | `self.design_params["case_mounting_hole_dia"]` |  |  |
| 151 | `a2_output_mounting_PCD` | dependent / formula | high | 6992 | `self.bearing2_OD + self.bearing_mount_thickness2` |  |  |
| 152 | `a2_output_mounting_hole_dia` | fixed / config | high | 6913 | `self.design_params["output_mounting_hole_dia2"]` |  |  |
| 153 | `a2_clearance_case_mount_holes_shell_thickness` | fixed / config | high | 6706 | `self.design_params["clearance_case_mount_holes_shell_thickness"]` |  |  |
| 154 | `a2_motor_case_OD_base` | dependent / formula | high | 6800 | `self.motor_OD + self.clearance_motor_and_case * 2 + self.Motor_case_thickness * 2` |  |  |
| 155 | `a2_sec_carrier_thickness` | fixed / config | high | 6898 | `self.design_params["sec_carrier_thickness2"]` |  |  |
| 156 | `a2_sun_coupler_hub_thickness` | dependent / formula | high | 7995 | `writer: getattr(self, "sun_coupler_hub_thickness1", "N/A")` | writer writes an expression, not one attribute |  |
| 157 | `a2_clearance_sun_coupler_sec_carrier` | fixed / config | high | 6704, 6894 | `self.design_params["clearance_sun_coupler_sec_carrier"] ‖ self.design_params["clearance_sun_coupler_sec_carrie…` | 2 assignments (two-case rule or reassigned) |  |
| 158 | `a2_clearance_motor_and_case` | dependent / formula | medium | 6799 | `(5 if self.ring_OD1 < self.motor_OD else (self.ring_OD1 - self.motor_OD) / 2 + 5)` | numbers 5 |  |
| 159 | `a2_motor_OD` | input / motor | high | 6720 | `self.motorDiaMM` |  |  |
| 160 | `a2_Motor_case_thickness` | fixed / config | high | 6705 | `self.design_params["Motor_case_thickness"]` |  |  |
| 161 | `a2_Motor_case_ID` | dependent / formula | high | 6801 | `self.motor_OD + self.clearance_motor_and_case * 2` |  |  |
| 162 | `a2_case_mounting_hole_shift` | dependent / formula | medium | 6802 | `self.case_mounting_hole_dia / 2 - 0.5` | numbers 0.5 |  |
| 163 | `a2_output_mounting_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 6964 | `output_mounting_hole2.nut_width_across_flats` |  |  |
| 164 | `a2_output_mounting_nut_thickness` | dependent / lookup (bolt/nut) | high | 6965 | `output_mounting_hole2.nut_thickness` |  |  |
| 165 | `a2_case_mounting_hole_allen_socket_dia` | dependent / lookup (bolt/nut) | high | 6793 | `case_mounting_bolt.bolt_head_dia` |  |  |
| 166 | `a2_output_mounting_nut_depth` | fixed / config | high | 6919 | `self.design_params["output_mounting_nut_depth2"]` |  |  |
| 167 | `a2_case_mounting_bolt_depth` | fixed / config | high | 6709 | `self.design_params["case_mounting_bolt_depth"]` |  |  |
| 168 | `a2_ring_radial_thickness` | fixed / config | high | 6701, 6897 | `self.design_params["ring_radial_thickness"] ‖ self.design_params["ring_radial_thickness"]` | 2 assignments (two-case rule or reassigned) |  |
| 169 | `a2_ring_OD` | dependent / formula | high | 6989 | `self.Nr2 * self.module2 + self.ring_radial_thickness * 2` |  |  |
| 170 | `a2_ring_to_chamfer_clearance` | fixed / config | high | 6899 | `self.design_params["ring_to_chamfer_clearance2"]` |  |  |
| 171 | `a2_Motor_case_OD_base_to_chamfer` | fixed / config | high | 6821 | `self.design_params["Motor_case_OD_base_to_chamfer"]` |  |  |
| 172 | `a2_pattern_offset_from_motor_case_OD_base` | fixed / config | high | 6822 | `self.design_params["pattern_offset_from_motor_case_OD_base"]` |  |  |
| 173 | `a2_pattern_bulge_dia` | fixed / config | high | 6823 | `self.design_params["pattern_bulge_dia"]` |  |  |
| 174 | `a2_pattern_num_bulge` | fixed / config | high | 6824 | `self.design_params["pattern_num_bulge"]` |  |  |
| 175 | `a2_pattern_depth` | fixed / config | high | 6825 | `self.design_params["pattern_depth"]` |  |  |
| 176 | `a2_motor_height` | input / motor | high | 6721 | `self.motorLengthMM` |  |  |
| 177 | `a2_case_mounting_wrench_size` | dependent / lookup (bolt/nut) | high | 6794 | `case_mounting_bolt.nut_width_across_flats` |  |  |
| 178 | `a2_case_mounting_nut_clearance` | fixed / config | high | 6826 | `self.design_params["case_mounting_nut_clearance"]` |  |  |
| 179 | `a2_base_plate_thickness` | fixed / config | high | 6739 | `self.design_params["base_plate_thickness"]` |  |  |
| 180 | `a2_case_mounting_nut_thickness` | dependent / lookup (bolt/nut) | high | 6795 | `case_mounting_bolt.nut_thickness` |  |  |
| 181 | `a2_case_mounting_surface_height` | fixed / config | high | 6710 | `self.design_params["case_mounting_surface_height"]` |  |  |
| 182 | `a2_motor_mount_hole_PCD` | input / motor | high | 6722 | `self.motor.motor_mount_hole_PCD` |  |  |
| 183 | `a2_motor_mount_hole_dia` | input / motor | high | 6723 | `self.motor.motor_mount_hole_dia` |  |  |
| 184 | `a2_motor_mount_hole_num` | input / motor | high | 6724 | `self.motor.motor_mount_hole_num` |  |  |
| 185 | `a2_central_hole_offset_from_motor_mount_PCD` | fixed / config | high | 6737 | `self.design_params["central_hole_offset_from_motor_mount_PCD"]` |  |  |
| 186 | `a2_wire_slot_dist_from_center` | input / motor | high | 6728 | `self.motor.wire_slot_dist_from_center` |  |  |
| 187 | `a2_wire_slot_length` | input / motor | high | 6729 | `self.motor.wire_slot_length` |  |  |
| 188 | `a2_wire_slot_radius` | input / motor | high | 6730 | `self.motor.wire_slot_radius` |  |  |
| 189 | `a2_driver_upper_holes_dist_from_center` | input / driver | high | 6743 | `self.motor_driver_params["driver_upper_holes_dist_from_center"]` |  |  |
| 190 | `a2_driver_lower_holes_dist_from_center` | input / driver | high | 6744 | `self.motor_driver_params["driver_lower_holes_dist_from_center"]` |  |  |
| 191 | `a2_driver_side_holes_dist_from_center` | input / driver | high | 6745 | `self.motor_driver_params["driver_side_holes_dist_from_center"]` |  |  |
| 192 | `a2_driver_mount_holes_dia` | input / driver | high | 6746 | `self.motor_driver_params["driver_mount_holes_dia"]` |  |  |
| 193 | `a2_driver_mount_inserts_OD` | input / driver | high | 6747 | `self.motor_driver_params["driver_mount_inserts_OD"]` |  |  |
| 194 | `a2_driver_mount_thickness` | input / driver | high | 6748 | `self.motor_driver_params["driver_mount_thickness"]` |  |  |
| 195 | `a2_driver_mount_height` | input / driver | high | 6749 | `self.motor_driver_params["driver_mount_height"]` |  |  |
| 196 | `a2_air_flow_hole_offset` | fixed / config | high | 6740 | `self.design_params["air_flow_hole_offset"]` |  |  |
| 197 | `a2_num_planet` | optimisation / planets | high | 6885 | `self.doubleStagePlanetaryGearbox.Stage2.numPlanet` |  |  |
| 198 | `a2_planet_pin_bolt_dia` | fixed / config | high | 6914 | `self.design_params["planet_pin_bolt_dia2"]` |  |  |
| 199 | `a2_planet_pin_socket_head_dia` | dependent / lookup (bolt/nut) | high | 6969 | `planet_bolt2.bolt_head_dia` |  |  |
| 200 | `a2_carrier_PCD` | dependent / formula | high | 6936 | `(self.Np2 + self.Ns2) * self.module2` |  |  |
| 201 | `a2_planet_shaft_dia` | fixed / config | high | 6900 | `self.design_params["planet_shaft_dia2"]` |  |  |
| 202 | `a2_fw_p` | dependent / formula | high | 6926 | `self.fw_r2` |  |  |
| 203 | `a2_planet_shaft_step_offset` | fixed / config | high | 6901 | `self.design_params["planet_shaft_step_offset2"]` |  |  |
| 204 | `a2_carrier_trapezoidal_support_sun_offset` | fixed / config | high | 6902 | `self.design_params["carrier_trapezoidal_support_sun_offset2"]` |  |  |
| 205 | `a2_carrier_trapezoidal_support_hole_PCD_offset_bearing_ID` | fixed / config | high | 6903 | `self.design_params["carrier_trapezoidal_support_hole_PCD_offset_bearing_ID2"]` |  |  |
| 206 | `a2_carrier_trapezoidal_support_hole_dia` | fixed / config | high | 6915 | `self.design_params["carrier_trapezoidal_support_hole_dia2"]` |  |  |
| 207 | `a2_carrier_trapezoidal_support_hole_socket_head_dia` | dependent / lookup (bolt/nut) | high | 6974 | `carrier_trapezoidal_support_hole2.bolt_head_dia` |  |  |
| 208 | `a2_carrier_bearing_step_width` | fixed / config | high | 6904 | `self.design_params["carrier_bearing_step_width2"]` |  |  |
| 209 | `a2_standard_clearance_1_5mm` | fixed / config | high | 6698, 6895 | `self.design_params["standard_clearance_1_5mm"] ‖ self.design_params["standard_clearance_1_5mm"]` | 2 assignments (two-case rule or reassigned) |  |
| 210 | `a2_standard_fillet_1_5mm` | fixed / config | high | 6699, 6896 | `self.design_params["standard_fillet_1_5mm"] ‖ self.design_params["standard_fillet_1_5mm"]` | 2 assignments (two-case rule or reassigned) |  |
| 211 | `a2_sun_shaft_bearing_OD` | fixed / config | high | 6905 | `self.design_params["sun_shaft_bearing_OD2"]` |  |  |
| 212 | `a2_sun_shaft_bearing_width` | fixed / config | high | 6906 | `self.design_params["sun_shaft_bearing_width2"]` |  |  |
| 213 | `a2_standard_bearing_insertion_chamfer` | fixed / config | high | 6700 | `self.design_params["standard_bearing_insertion_chamfer"]` |  |  |
| 214 | `a2_carrier_trapezoidal_support_hole_wrench_size` | dependent / lookup (bolt/nut) | high | 6975 | `carrier_trapezoidal_support_hole2.nut_width_across_flats` |  |  |
| 215 | `a2_planet_pin_bolt_wrench_size` | dependent / lookup (bolt/nut) | high | 6970 | `planet_bolt2.nut_width_across_flats` |  |  |
| 216 | `a2_motor_output_hole_PCD` | input / motor | high | 6725 | `self.motor.motor_output_hole_PCD` |  |  |
| 217 | `a2_motor_output_hole_dia` | input / motor | high | 6726 | `self.motor.motor_output_hole_dia` |  |  |
| 218 | `a2_motor_output_hole_num` | input / motor | high | 6727 | `self.motor.motor_output_hole_num` |  |  |
| 219 | `a2_h_b` | dependent / formula | high | 6929 | `1.25 * self.module2` |  |  |
| 220 | `a2_dp_s` | dependent / formula | high | 6935 | `self.module2 * self.Ns2` |  |  |
| 221 | `a2_db_s` | dependent / formula | high | 6939 | `self.dp_s2 * np.cos(np.deg2rad(self.pressure_angle))` |  |  |
| 222 | `a2_fw_s_calc` | dependent / stress rule (face width) | high | 6888 | `self.doubleStagePlanetaryGearbox.Stage2.fwSunMM` |  |  |
| 223 | `a2_alpha_s` | dependent / formula | high | 6944 | `np.sqrt(self.dp_s2**2 - self.db_s2**2) / self.db_s2 * 180 / np.pi - self.pressure_angle` |  |  |
| 224 | `a2_beta_s` | dependent / formula | high | 6947 | `(360 / (4 * self.Ns2) - self.alpha_s2) * 2` |  |  |
| 225 | `a2_dp_p` | dependent / formula | high | 6933 | `self.module2 * self.Np2` |  |  |
| 226 | `a2_db_p` | dependent / formula | high | 6940 | `self.dp_p2 * np.cos(np.deg2rad(self.pressure_angle))` |  |  |
| 227 | `a2_alpha_p` | dependent / formula | high | 6945 | `np.sqrt(self.dp_p2**2 - self.db_p2**2) / self.db_p2 * 180 / np.pi - self.pressure_angle` |  |  |
| 228 | `a2_beta_p` | dependent / formula | high | 6948 | `(360 / (4 * self.Np2) - self.alpha_p2) * 2` |  |  |
| 229 | `a2_planet_bearing_OD` | fixed / config | high | 6907 | `self.design_params["planet_bearing_OD2"]` |  |  |
| 230 | `a2_planet_bearing_width` | fixed / config | high | 6908 | `self.design_params["planet_bearing_width2"]` |  |  |
| 231 | `a2_planet_bore` | fixed / config | high | 6909 | `self.design_params["planet_bore2"]` |  |  |
| 232 | `a2_sun_shaft_bearing_ID` | fixed / config | high | 6910 | `self.design_params["sun_shaft_bearing_ID2"]` |  |  |
| 233 | `a2_sun_hub_dia` | dependent / formula | medium | 6814 | `self.motor_output_hole_PCD + self.motor_output_hole_dia + self.standard_clearance_1_5mm * 4` | numbers 4 |  |
| 234 | `a2_sun_central_bolt_dia` | fixed / config | high | 6916 | `self.design_params["sun_central_bolt_dia2"]` |  |  |
| 235 | `a2_sun_central_bolt_socket_head_dia` | dependent / lookup (bolt/nut) | high | 6979 | `sun_central_bolt2.bolt_head_dia` |  |  |
| 236 | `a2_fw_s_used` | dependent / formula | high | 6990 | `self.fw_p2 + self.clearance_planet + self.sec_carrier_thickness2 + self.standard_clearance_1_5mm` |  |  |
| 237 | `a2_motor_output_hole_CSK_OD` | dependent / lookup (bolt/nut) | high | 6734 | `motor_output_hole_bolt.bolt_head_dia` |  |  |
| 238 | `a2_motor_output_hole_CSK_head_height` | dependent / lookup (bolt/nut) | high | 6735 | `motor_output_hole_bolt.bolt_head_height` |  |  |
| 239 | `a2_bearing_retainer_thickness` | fixed / config | high | 6911 | `self.design_params["bearing_retainer_thickness2"]` |  |  |
| 240 | `a2_Ns1` | optimisation / teeth | high | 6684 | `self.doubleStagePlanetaryGearbox.Stage1.Ns` |  |  |
| 241 | `a2_Np1` | optimisation / teeth | high | 6685 | `self.doubleStagePlanetaryGearbox.Stage1.Np` |  |  |
| 242 | `a2_Nr1` | dependent / formula | high | 6754 | `self.Ns1 + 2 * self.Np1` |  |  |
| 243 | `a2_module1` | optimisation / module | high | 6687 | `self.doubleStagePlanetaryGearbox.Stage1.module` |  |  |
| 244 | `a2_bearing1_ID` | dependent / lookup (bearing) | high | 6786 | `Bearing1.getBearingIDMM()` |  |  |
| 245 | `a2_bearing1_OD` | dependent / lookup (bearing) | high | 6787 | `Bearing1.getBearingODMM()` |  |  |
| 246 | `a2_bearing1_height1` | dependent / lookup (bearing) | high | 6788 | `Bearing1.getBearingWidthMM()` |  |  |
| 247 | `a2_bearing_mount_thickness1` | dependent / formula | medium | 6807 | `(self.output_mounting_hole_dia1 * 2 if (self.bearing1_OD + self.output_mounting_hole_dia1 * 4) > (self.Nr1 * s…` | numbers 4 |  |
| 248 | `a2_output_mounting_PCD1` | dependent / formula | high | 6808 | `self.bearing1_OD + self.bearing_mount_thickness1` |  |  |
| 249 | `a2_num_planet1` | optimisation / planets | high | 6686 | `self.doubleStagePlanetaryGearbox.Stage1.numPlanet` |  |  |
| 250 | `a2_stg1_stg2_mounting_pattern_width` | fixed / config | high | 6918 | `self.design_params["stg1_stg2_mounting_pattern_width"]` |  |  |
| 251 | `a2_stg1_stg2_allen_socket_head_dia` | dependent / lookup (bolt/nut) | high | 6983 | `stg1_stg2_mounting_hole.bolt_head_dia` |  |  |
| 252 | `a2_stg1_stg2_mounting_hole_dia` | fixed / config | high | 6917 | `self.design_params["stg1_stg2_mounting_hole_dia"]` |  |  |
| 253 | `a2_stg1_stg2_mounting_extra_width` | dependent / formula | high | 6998 | `(0) if ((self.Nr2 * self.module2 + self.ring_radial_thickness * 2 + self.stg1_stg2_allen_socket_head_dia) / 2 …` |  |  |
| 254 | `a2_tight_clearance_3DP` | fixed / config | high | 6696 | `self.design_params["tight_clearance_3DP"]` |  |  |
| 255 | `a2_loose_clearance_3DP` | fixed / config | high | 6697 | `self.design_params["loose_clearance_3DP"]` |  |  |

## Config accounting

| Block | Keys | Read by this type | Read but not written to the CAD | Never used |
|---|---|---|---|---|
| `dspg_design_parameters` | 29 | **no** | sCarrierExtrusionDiaMM_Stg1, sCarrierExtrusionClearanceMM_Stg1, sCarrierExtrusionDiaMM_Stg2, sCarrierExtrusionClearanceMM_Stg2, planetMinDistanceMM | Ring1RadialWidthMM, Ring2RadialWidthMM, carrier1ShaftHeightMM, mainCase2AttachmentHeightMM, baseThicknessMM, sCarrierThicknessMM, mainCoverThicknessMM, planetBoreMM, sunBoreMM, couplerRadiusMM, couplerThicknessMM, couplerShaftHeightMM, CarrierRadialThicknessClearance1, CarrierRadialThicknessClearance2, carrierInnerDiaClearanceMM1, sCarrierInnerDiaClearanceMM1, carrierInnerDiaClearanceMM2, sCarrier… |
| `dspg_optimization_parameters` | 16 | yes | GEAR_RATIO_MIN, GEAR_RATIO_MAX, GEAR_RATIO_STEP, MODULE_STAGE1_MIN, MODULE_STAGE1_MAX, MODULE_STAGE2_MIN, MODULE_STAGE2_MAX, NUM_PLANET_STAGE1_MIN, NUM_PLANET_STAGE1_MAX, NUM_PLANET_STAGE2_MIN, NUM_PLANET_STAGE2_MAX, NUM_TEETH_SUN_MIN, NUM_TEETH_PLANET_MIN, MAX_GB_DIA_MULT_FACTOR, MAX_GB_DIA_MULT_FACTOR_SMALL_MOTOR, SMALL_MOTOR_DIA_MM | — |
| `dspg_design_parameters_3DP` | 70 | yes | sCarrierExtrusionDiaMM_Stg1, sCarrierExtrusionClearanceMM_Stg1, sCarrierExtrusionDiaMM_Stg2, sCarrierExtrusionClearanceMM_Stg2, planetMinDistanceMM, bearingIDClearanceMM, clearance_case_mount_holes_shell_thickness2 | — |


## Result (classification done)

Spec: [`config_files/variables/dspg_variables.json`](../../../config_files/variables/dspg_variables.json), page [`docs/variables/dspg.md`](../dspg.md) (generated). Tests: the generic `tests/test_variable_categories.py` (DSPG registered in `tests/variable_helpers.py`) and `tests/test_variable_categories_dspg.py`.

**Counts (CAD variables, 255):** input 36, optimisation 15, fixed 90, dependent 114 (70 formula, 35 lookup, 5 stress rule, 4 implicit constraint). 79 names are aliases of another name (the plan said 78: the extra one is `a2_sun_coupler_hub_thickness`, whose writer is `getattr(self, "sun_coupler_hub_thickness1", "N/A")`, i.e. the stage-1 value; it is an alias of `a1_sun_coupler_hub_thickness`, Fixed, so fixed is 90 and dependent 114 against the draft's 89 / 115). **Code-only values: 33** (fixed 29, input 2, dependent 2: `maxGearboxDiameter`, `actuator_width`). Confidence: 284 high, 4 medium, 0 low.

**Medium-confidence entries**
- `a1_sun_hub_dia`, `a2_sun_hub_dia` (Dependent / formula): `sun_hub_dia = motor_output_hole_PCD + motor_output_hole_dia + standard_clearance_1_5mm * 4`; the 4 is still hard-coded in the CAD code and in the stage-1 mass code. Left as it is: the plan's shared-key decision (finding 2, `sun_hub_clearance_multiple`) is still open.
- `bearing_mount_wall_bolt_dia_multiple` (code-only, Fixed): one key for both stages and both the CAD and the mass code; the plan leaves open whether it should be one per stage.
- `planet_bearing_gap` (code-only, Fixed): the same single-key choice for both stages.

**Config keys added** to `dspg_design_parameters_3DP` (shared names, values that keep every output bit-identical): `clearance_motor_and_case_min` = 5, `case_mounting_hole_wall_overlap` = 0.5, `bearing_mount_wall_bolt_dia_multiple` = 2, `planet_bearing_gap` = 1.0 (was `standard_clearance_1_5mm * 2 / 3` in both stages; 1.5 * 2 / 3 is exactly 1.0). They replace the hard-coded numbers in `setVariables_stg1` / `_stg2`, `mitStressAnalysisMinFacewidth`, and the stage-1 / stage-2 mass functions (`getMassKG_3DP_stg1`: case clearance and bearing mount; `getMassKG_3DP_stg2`: bearing mount). Each has a test that it drives exactly its CAD variables (and the mass where it should).

**Shared tooling changed:** `rules.json` (`Nr` pattern accepts the `a1_` / `a2_` prefix; a new stress-rule pattern for `a[12]_fw_(s_calc|r)[12]?`, while `a1_fw_p` / `a2_fw_p` stay formulas), `tests/variable_helpers.py` (DSPG entry, two-stage gear setter, plain files read per stage from the spec's `plain_files`), `tools/variables/render.py` (names the two stage files); `docs/variables/sspg.md` and `cpg.md` regenerated (only the shared-rules list changed).

**Results:** `python tests/golden/golden.py check`: All 58 cases match the baseline. `python -m pytest -q`: 782 passed. No `CADs/` file, no golden baseline touched.

**Open questions**
1. One key per stage (`planet_bearing_gap1` / `2`, `bearing_mount_wall_bolt_dia_multiple1` / `2`) or the single shared key used here? (plan decision 1)
2. `sun_hub_dia` margin: shared key, and apply to SSPG / CPG too? (plan decision 2) **Done (2026-10-31):** the margin is now the config key `sun_hub_clearance_multiple` (4 in every type with this rule, SSPG and CPG included; 5 in IDSPG, its CAD value), read by the CAD code and the mass code; value-identical; `tests/test_sun_hub_clearance.py`.
3. `clearance_motor_and_case_min` and `case_mounting_hole_wall_overlap` exist once: stage 2 writes the stage-1 case values, so there is no second copy to key.
4. `clearance_case_mount_holes_shell_thickness2` is read in stage 2 but never written or used (the CAD writes the stage-1 value under both prefixes): kept as a code-only Fixed value, not removed.
5. Stage 2's stress widths depend on stage 1 too (the stage-1 gear ratio sets the torque on stage 2); the spec lists `a1_Ns` and `a1_Nr` among the dependencies of `a2_fw_s_calc` / `a2_fw_r`.
6. `dspg_design_parameters` (29 keys) is never read; listed as an unused block. `planetMinDistanceMM` and the `sCarrierExtrusion*` keys are read by the gearbox class only for its interference check; they are code-only, not written to the CAD.
