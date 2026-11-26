# INCPG dependent: variable classification plan

Part of [the plan for all actuators](../PLAN.md). Survey only: nothing in the code, config or CAD output changes on this branch.

## Inventory

- **CAD interface:** `incpg_dependent_equations_onshape.txt`, **134 variables**; other files: `incpg_dependent_equations.txt` (134)
- **Code:** `inrunnerCompoundPlanetaryActuator` in `ActuatorAndGearbox_INCPG_dependent.py` (lines 527-2151)
- **Config:** `incpg_dependent_params.json`, block(s) read: `incpg_3DP_design_parameters`; search bounds `incpg_optimization_parameters`; gear standard / MIT factors from `config.json`; driver: `OdrivePro`
- **Survey draft:** dependent 52, fixed 55, input 22, optimisation 5; 75 names also in SSPG / CPG; 0 alias names (same value written under a second name); 0 flagged by the survey

## Special cases (frameless inrunner, compound; "dependent" and "independent" are separate files)

| Variable(s) | What the code does | Proposed classification |
|---|---|---|
| `rotor_*`, `stator_*` | frameless inrunner geometry | Input / motor |
| `rotor_hub_*` | rotor hub sizes from the config | Fixed / config |
| `Nr` | `Ns + Np_b + Np_s` | Dependent / implicit constraint (as CPG) |
| `module` | `moduleBig`; one module in the CAD | Optimisation; **bug-18 pattern** (check, propose `module_b` / `module_s`) |
| `fw_s_calc`, `fw_p_b` | MIT stress rule (two meshes, CPG-style bearing minimum; width cap via `planet_stack_stator_heights`-style keys if present) | Dependent / stress rule |
| `fw_r` | **ring stress width + `standard_clearance_1_5mm`** (L786) | Dependent / formula on the code-only ring stress width (add a code-only `fw_r_stress` entry) |
| `fw_p_s` | `= fw_r` | Dependent / formula |
| `ring_radial_width` | config `ringRadialWidthMM` | Fixed / config |
| `sun_hub_dia` | `rotor_ID − 2 × rotor_hub_thickness` (independent: `rotor_top_bearing_ID − …`) | Dependent / formula |
| `case_mounting_hole_shift` | `case_mounting_hole_dia / 2` (no overlap) | Dependent / formula; if the shared key is introduced it would be `case_mounting_hole_wall_overlap = 0` here (review) |
| `rotor_top_bearing_*` | dependent: catalogue lookup; independent: per-motor config (`per_motor_value`, ISSUES bug 12 fix) | Dependent / lookup vs Fixed / config (per motor) |
| `rotor_bottom_bearing_*` | dependent: config; independent: per-motor config | Fixed / config |
| `output_bearing_*` | catalogue lookup | Dependent / lookup |

## Hard-coded numbers (medium)

| Where | Number | Proposed key |
|---|---|---|
| planet-bearing minimum (L1619-1623) | 2/3, 1/3 | `planet_bearing_gap` |
| mass code: `RingOuterRadiusMM … + 1.25 × module2 + ringRadialWidthMM`, fillet factor **0.2146**, `1.5 × 3`, `1.5 / 3` margins, sun-shaft bearing 4 g | various | mass-only list (0.2146 = 1 − π/4, the fillet's area factor: geometry) |

## Config (`incpg_dependent_params.json`)
- Code-only keys: `planetMinDistanceMM`, `sCarrierExtrusion*`, `min_rotor_top_bearing_ID`.
- Optimisation block: 10 search bounds.

## Test plan
- Registry: compound setter; RI100 / RI80; 3 golden designs.
- Specific: stress-rule widths (`fw_r` = stress + clearance), the planet-bearing gap.

## Risks / notes
- The fewest flags of all types: the CAD values are mostly config or clean formulas. Effort: ~1 h.

## Survey draft: every variable

Automatic first pass from the code (the special cases above take precedence). Category guesses come from the source of each value; *flags* mark hard-coded numbers, several assignments or a writer expression. The final category, sub-type, `depends_on`, confidence and reason are set during the classification itself.

| # | Variable | Draft category / sub-type | Conf. | Line | Code | Flags | SSPG / CPG |
|---|---|---|---|---|---|---|---|
| 1 | `Ns` | optimisation / teeth | high | 639 | `self.inrunnerCompoundPlanetaryGearbox.Ns` |  | sspg: optimisation, cpg: optimisation |
| 2 | `Np_b` | optimisation / teeth | high | 640 | `self.inrunnerCompoundPlanetaryGearbox.NpBig` |  | cpg: optimisation |
| 3 | `Np_s` | optimisation / teeth | high | 641 | `self.inrunnerCompoundPlanetaryGearbox.NpSmall` |  | cpg: optimisation |
| 4 | `Nr` | dependent / formula | high | 642 | `self.Ns + self.Np_b + self.Np_s` |  | sspg: dependent, cpg: dependent |
| 5 | `num_planet` | optimisation / planets | high | 643 | `self.inrunnerCompoundPlanetaryGearbox.numPlanet` |  | sspg: optimisation, cpg: optimisation |
| 6 | `module` | optimisation / module | high | 644 | `self.inrunnerCompoundPlanetaryGearbox.moduleBig` |  | sspg: optimisation, cpg: optimisation |
| 7 | `pressure_angle` | fixed / gear standard | high | 650 | `self.inrunnerCompoundPlanetaryGearbox.getPressureAngleRad()` |  | sspg: fixed, cpg: fixed |
| 8 | `pressure_angle_deg` | fixed / gear standard | high | 651 | `self.inrunnerCompoundPlanetaryGearbox.getPressureAngleRad() * 180 / np.pi` |  |  |
| 9 | `clearance_planet` | fixed / config | high | 654 | `self.design_params["clearance_planet"]` |  | sspg: fixed, cpg: fixed |
| 10 | `clearance_case_mount_holes_shell_thickness` | fixed / config | high | 655 | `self.design_params["clearance_case_mount_holes_shell_thickness"]` |  | sspg: fixed, cpg: fixed |
| 11 | `standard_clearance_1_5mm` | fixed / config | high | 656 | `self.design_params["standard_clearance_1_5mm"]` |  | sspg: fixed, cpg: fixed |
| 12 | `standard_clearance_2_mm` | fixed / config | high | 657 | `self.design_params["standard_clearance_2_mm"]` |  |  |
| 13 | `standard_fillet_1_5mm` | fixed / config | high | 659 | `self.design_params["standard_fillet_1_5mm"]` |  | sspg: fixed, cpg: fixed |
| 14 | `standard_fillet_3_mm` | fixed / config | high | 660 | `self.design_params["standard_fillet_3_mm"]` |  |  |
| 15 | `standard_bearing_insertion_chamfer` | fixed / config | high | 661 | `self.design_params["standard_bearing_insertion_chamfer"]` |  | sspg: fixed, cpg: fixed |
| 16 | `bearingIDClearanceMM` | fixed / config | high | 662 | `self.design_params["bearingIDClearanceMM"]` |  | sspg: fixed, cpg: fixed |
| 17 | `tight_clearance_3DP` | fixed / config | high | 663 | `self.design_params["tight_clearance_3DP"]` |  | sspg: fixed, cpg: fixed |
| 18 | `loose_clearance_3DP` | fixed / config | high | 664 | `self.design_params["loose_clearance_3DP"]` |  | sspg: fixed, cpg: fixed |
| 19 | `bearing_step_width` | fixed / config | high | 665 | `self.design_params["bearing_step_width"]` |  |  |
| 20 | `motor_OD` | input / motor | high | 668 | `self.motorDiaMM` |  | sspg: input, cpg: input |
| 21 | `motor_height` | input / motor | high | 669 | `self.motorLengthMM` |  | sspg: input, cpg: input |
| 22 | `rotor_OD` | input / motor | high | 670 | `self.motor.rotor_OD` |  |  |
| 23 | `stator_ID` | input / motor | high | 671 | `self.motor.stator_ID` |  |  |
| 24 | `rotor_height` | input / motor | high | 672 | `self.motor.rotor_height` |  |  |
| 25 | `rotor_ID` | input / motor | high | 673 | `self.motor.rotor_ID` |  |  |
| 26 | `stator_height` | input / motor | high | 674 | `self.motor.stator_height` |  |  |
| 27 | `stator_OD` | input / motor | high | 675 | `self.motor.stator_OD` |  |  |
| 28 | `stator_hole_dia` | input / motor | high | 676 | `self.motor.stator_hole_dia` |  |  |
| 29 | `stator_top_height` | input / motor | high | 677 | `self.motor.stator_wire_top_height` |  |  |
| 30 | `stator_mid_height` | input / motor | high | 678 | `self.motor.stator_mid_height` |  |  |
| 31 | `stator_bottom_height` | input / motor | high | 679 | `self.motor.stator_wire_bottom_height` |  |  |
| 32 | `stator_inside_OD` | input / motor | high | 680 | `self.motor.stator_wire_OD` |  |  |
| 33 | `stator_hole_num` | input / motor | high | 681 | `self.motor.stator_hole_num` |  |  |
| 34 | `stator_inside_ID` | input / motor | high | 682 | `self.motor.stator_wire_ID` |  |  |
| 35 | `driver_upper_holes_dist_from_center` | input / driver | high | 685 | `self.motor_driver_params["driver_upper_holes_dist_from_center"]` |  | sspg: input, cpg: input |
| 36 | `driver_lower_holes_dist_from_center` | input / driver | high | 686 | `self.motor_driver_params["driver_lower_holes_dist_from_center"]` |  | sspg: input, cpg: input |
| 37 | `driver_side_holes_dist_from_center` | input / driver | high | 687 | `self.motor_driver_params["driver_side_holes_dist_from_center"]` |  | sspg: input, cpg: input |
| 38 | `driver_mount_holes_dia` | input / driver | high | 688 | `self.motor_driver_params["driver_mount_holes_dia"]` |  | sspg: input, cpg: input |
| 39 | `driver_mount_inserts_OD` | input / driver | high | 689 | `self.motor_driver_params["driver_mount_inserts_OD"]` |  | sspg: input, cpg: input |
| 40 | `driver_mount_thickness` | input / driver | high | 690 | `self.motor_driver_params["driver_mount_thickness"]` |  | sspg: input, cpg: input |
| 41 | `driver_mount_height` | input / driver | high | 691 | `self.motor_driver_params["driver_mount_height"]` |  | sspg: input, cpg: input |
| 42 | `motor_mount_driver_hole_dia` | fixed / config | high | 692 | `self.design_params["motor_mount_driver_hole_dia"]` |  |  |
| 43 | `motor_mount_driver_hole_num` | fixed / config | high | 693 | `self.design_params["motor_mount_driver_hole_num"]` |  |  |
| 44 | `rotor_hub_thickness` | fixed / config | high | 696 | `self.design_params["rotor_hub_thickness"]` |  |  |
| 45 | `rotor_hub_height` | fixed / config | high | 697 | `self.design_params["rotor_hub_height"]` |  |  |
| 46 | `rotor_hub_sun_hole_dia` | fixed / config | high | 698 | `self.design_params["rotor_hub_sun_hole_dia"]` |  |  |
| 47 | `rotor_hub_sun_hole_num` | fixed / config | high | 699 | `self.design_params["rotor_hub_sun_hole_num"]` |  |  |
| 48 | `rotor_top_bearing_ID` | dependent / lookup (bearing) | high | 829 | `RotorTopBearings.getBearingIDMM()` |  |  |
| 49 | `rotor_top_bearing_OD` | dependent / lookup (bearing) | high | 830 | `RotorTopBearings.getBearingODMM()` |  |  |
| 50 | `rotor_top_bearing_width` | dependent / lookup (bearing) | high | 831 | `RotorTopBearings.getBearingWidthMM()` |  |  |
| 51 | `rotor_bottom_bearing_ID` | fixed / config | high | 701 | `self.design_params["rotor_bottom_bearing_ID"]` |  |  |
| 52 | `rotor_bottom_bearing_OD` | fixed / config | high | 702 | `self.design_params["rotor_bottom_bearing_OD"]` |  |  |
| 53 | `rotor_bottom_bearing_width` | fixed / config | high | 703 | `self.design_params["rotor_bottom_bearing_width"]` |  |  |
| 54 | `planet_pin_bolt_dia` | fixed / config | high | 707 | `self.design_params["planet_pin_bolt_dia"]` |  | sspg: fixed, cpg: fixed |
| 55 | `planet_shaft_step_offset` | fixed / config | high | 709 | `self.design_params["planet_shaft_step_offset"]` |  | sspg: fixed, cpg: fixed |
| 56 | `planet_bearing_OD` | fixed / config | high | 710 | `self.design_params["planet_bearing_OD"]` |  | sspg: fixed, cpg: fixed |
| 57 | `planet_bearing_width` | fixed / config | high | 711 | `self.design_params["planet_bearing_width"]` |  | sspg: fixed, cpg: fixed |
| 58 | `planet_bearing_ID` | fixed / config | high | 712 | `self.design_params["planet_bearing_ID"]` |  |  |
| 59 | `sun_coupler_hub_thickness` | fixed / config | high | 715 | `self.design_params["sun_coupler_hub_thickness"]` |  | sspg: fixed, cpg: fixed |
| 60 | `sun_shaft_bearing_ID` | fixed / config | high | 716 | `self.design_params["sun_shaft_bearing_ID"]` |  | sspg: fixed, cpg: fixed |
| 61 | `sun_shaft_bearing_OD` | fixed / config | high | 717 | `self.design_params["sun_shaft_bearing_OD"]` |  | sspg: fixed, cpg: fixed |
| 62 | `sun_shaft_bearing_width` | fixed / config | high | 718 | `self.design_params["sun_shaft_bearing_width"]` |  | sspg: fixed, cpg: fixed |
| 63 | `sun_central_bolt_dia` | fixed / config | high | 719 | `self.design_params["sun_central_bolt_dia"]` |  | sspg: fixed, cpg: fixed |
| 64 | `sec_carrier_thickness` | fixed / config | high | 722 | `self.design_params["sec_carrier_thickness"]` |  | sspg: fixed, cpg: fixed |
| 65 | `carrier_trapezoidal_support_sun_offset` | fixed / config | high | 724 | `self.design_params["carrier_trapezoidal_support_sun_offset"]` |  | sspg: fixed, cpg: fixed |
| 66 | `carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID` | fixed / config | high | 725 | `self.design_params["carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID"]` |  |  |
| 67 | `carrier_trapezoidal_support_hole_dia` | fixed / config | high | 726 | `self.design_params["carrier_trapezoidal_support_hole_dia"]` |  | sspg: fixed, cpg: fixed |
| 68 | `case_mounting_surface_height` | fixed / config | high | 729 | `self.design_params["case_mounting_surface_height"]` |  | sspg: fixed, cpg: fixed |
| 69 | `case_mounting_hole_dia` | fixed / config | high | 730 | `self.design_params["case_mounting_hole_dia"]` |  | sspg: fixed, cpg: fixed |
| 70 | `motor_case_thickness` | fixed / config | high | 732 | `self.design_params["motor_case_thickness"]` |  |  |
| 71 | `output_mount_hole_dia` | fixed / config | high | 734 | `self.design_params["output_mount_hole_dia"]` |  |  |
| 72 | `actuactor_mount_hole_dia` | fixed / config | high | 736 | `self.design_params["actuactor_mount_hole_dia"]` |  |  |
| 73 | `motor_case_OD_base_to_chamfer` | fixed / config | high | 738 | `self.design_params["motor_case_OD_base_to_chamfer"]` |  |  |
| 74 | `pattern_offset_from_motor_case_OD_base` | fixed / config | high | 739 | `self.design_params["pattern_offset_from_motor_case_OD_base"]` |  | sspg: fixed, cpg: fixed |
| 75 | `pattern_bulge_dia` | fixed / config | high | 740 | `self.design_params["pattern_bulge_dia"]` |  | sspg: fixed, cpg: fixed |
| 76 | `pattern_num_bulge` | fixed / config | high | 741 | `self.design_params["pattern_num_bulge"]` |  | sspg: fixed, cpg: fixed |
| 77 | `pattern_depth` | fixed / config | high | 742 | `self.design_params["pattern_depth"]` |  | sspg: fixed, cpg: fixed |
| 78 | `magnet_mount_hole_dia` | fixed / config | high | 747 | `self.design_params["magnet_mount_hole_dia"]` |  |  |
| 79 | `magnet_thickness` | fixed / config | high | 748 | `self.design_params["magnet_thickness"]` |  |  |
| 80 | `magnet_dia` | fixed / config | high | 749 | `self.design_params["magnet_dia"]` |  |  |
| 81 | `magnet_mount_thickness` | fixed / config | high | 750 | `self.design_params["magnet_mount_thickness"]` |  |  |
| 82 | `magnet_pattern_bulge_dia` | fixed / config | high | 751 | `self.design_params["magnet_pattern_bulge_dia"]` |  |  |
| 83 | `magnet_pattern_bulge_number` | fixed / config | high | 752 | `self.design_params["magnet_pattern_bulge_number"]` |  |  |
| 84 | `magnet_mount_height` | fixed / config | high | 753 | `self.design_params["magnet_mount_height"]` |  |  |
| 85 | `ring_radial_width` | fixed / config | high | 756 | `self.design_params["ringRadialWidthMM"]` |  |  |
| 86 | `ring_gearbox_casing_thickness` | fixed / config | high | 744 | `self.design_params["ring_gearbox_casing_thickness"]` |  |  |
| 87 | `h_a` | dependent / formula | high | 765 | `1 * self.module` |  | sspg: dependent, cpg: dependent |
| 88 | `h_b` | dependent / formula | high | 766 | `1.25 * self.module` |  | sspg: dependent, cpg: dependent |
| 89 | `h_f` | dependent / formula | high | 767 | `1.25 * self.module` |  | sspg: dependent, cpg: dependent |
| 90 | `clr_tip_root` | dependent / formula | high | 768 | `self.h_f - self.h_a` |  | sspg: dependent, cpg: dependent |
| 91 | `dp_s` | dependent / formula | high | 770 | `self.module * self.Ns` |  | sspg: dependent, cpg: dependent |
| 92 | `db_s` | dependent / formula | high | 771 | `self.dp_s * np.cos((self.pressure_angle))` |  | sspg: dependent, cpg: dependent |
| 93 | `alpha_s` | dependent / formula | high | 772 | `(np.sqrt(self.dp_s ** 2 - self.db_s ** 2) / self.db_s) * 180 / np.pi - self.pressure_angle_deg` |  | sspg: dependent, cpg: dependent |
| 94 | `beta_s` | dependent / formula | high | 773 | `(360 / (4 * self.Ns) - self.alpha_s) * 2` |  | sspg: dependent, cpg: dependent |
| 95 | `fw_s_calc` | dependent / stress rule (face width) | high | 774 | `self.inrunnerCompoundPlanetaryGearbox.fwSunMM` |  | sspg: dependent, cpg: dependent |
| 96 | `dp_p_b` | dependent / formula | high | 776 | `self.module * self.Np_b` |  | cpg: dependent |
| 97 | `db_p_b` | dependent / formula | high | 777 | `self.dp_p_b * np.cos((self.pressure_angle))` |  | cpg: dependent |
| 98 | `alpha_p_b` | dependent / formula | high | 778 | `(np.sqrt(self.dp_p_b ** 2 - self.db_p_b ** 2) / self.db_p_b) * 180 / np.pi - self.pressure_angle_deg` |  | cpg: dependent |
| 99 | `beta_p_b` | dependent / formula | high | 779 | `(360 / (4 * self.Np_b) - self.alpha_p_b) * 2` |  | cpg: dependent |
| 100 | `fw_p_b` | dependent / stress rule (face width) | high | 780 | `self.inrunnerCompoundPlanetaryGearbox.fwPlanetBigMM` |  | cpg: dependent |
| 101 | `dp_r` | dependent / formula | high | 782 | `self.module * self.Nr` |  | sspg: dependent, cpg: dependent |
| 102 | `db_r` | dependent / formula | high | 783 | `self.dp_r * np.cos((self.pressure_angle))` |  | sspg: dependent, cpg: dependent |
| 103 | `alpha_r` | dependent / formula | high | 784 | `(np.sqrt(self.dp_r ** 2 - self.db_r ** 2) / self.db_r) * 180 / np.pi - self.pressure_angle_deg` |  | sspg: dependent, cpg: dependent |
| 104 | `beta_r` | dependent / formula | high | 785 | `(360 / (4 * self.Nr) + self.alpha_r) * 2` |  | sspg: dependent, cpg: dependent |
| 105 | `fw_r` | dependent / stress rule (face width) | high | 786 | `self.inrunnerCompoundPlanetaryGearbox.fwRingMM + self.standard_clearance_1_5mm` |  | sspg: dependent, cpg: dependent |
| 106 | `dp_p_s` | dependent / formula | high | 788 | `self.module * self.Np_s` |  | cpg: dependent |
| 107 | `db_p_s` | dependent / formula | high | 789 | `self.dp_p_s * np.cos((self.pressure_angle))` |  | cpg: dependent |
| 108 | `alpha_p_s` | dependent / formula | high | 790 | `(np.sqrt(self.dp_p_s ** 2 - self.db_p_s ** 2) / self.db_p_s) * 180 / np.pi - self.pressure_angle_deg` |  | cpg: dependent |
| 109 | `beta_p_s` | dependent / formula | high | 791 | `(360 / (4 * self.Np_s) - self.alpha_p_s) * 2` |  | cpg: dependent |
| 110 | `fw_p_s` | dependent / formula | high | 792 | `self.fw_r` |  | cpg: dependent |
| 111 | `motor_mount_driver_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 796 | `motor_mount_driver_bolt.nut_width_across_flats` |  |  |
| 112 | `motor_mount_driver_nut_depth` | dependent / lookup (bolt/nut) | high | 797 | `motor_mount_driver_bolt.nut_thickness` |  |  |
| 113 | `planet_pin_socket_head_dia` | dependent / lookup (bolt/nut) | high | 802 | `planet_pin_bolt.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 114 | `planet_pin_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 803 | `planet_pin_bolt.nut_width_across_flats` |  |  |
| 115 | `planet_pin_nut_depth` | dependent / lookup (bolt/nut) | high | 804 | `planet_pin_bolt.nut_thickness` |  |  |
| 116 | `sun_central_bolt_socket_head_dia` | dependent / lookup (bolt/nut) | high | 808 | `sun_central_bolt.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 117 | `rotor_hub_sun_hole_CSK_OD` | dependent / lookup (bolt/nut) | high | 812 | `rotor_hub_sun_bolt.bolt_head_dia` |  |  |
| 118 | `rotor_hub_sun_hole_CSK_head_height` | dependent / lookup (bolt/nut) | high | 813 | `rotor_hub_sun_bolt.bolt_head_height` |  |  |
| 119 | `sun_hub_dia` | dependent / formula | high | 815 | `self.rotor_ID - 2*self.rotor_hub_thickness` |  | sspg: dependent, cpg: dependent |
| 120 | `output_bearing_ID` | dependent / lookup (bearing) | high | 820 | `OutputBearings.getBearingIDMM()` |  |  |
| 121 | `output_bearing_OD` | dependent / lookup (bearing) | high | 821 | `OutputBearings.getBearingODMM()` |  |  |
| 122 | `output_bearing_width` | dependent / lookup (bearing) | high | 822 | `OutputBearings.getBearingWidthMM()` |  |  |
| 123 | `carrier_trapezoidal_support_hole_socket_head_dia` | dependent / lookup (bolt/nut) | high | 836 | `carrier_trapezoidal_support_hole.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 124 | `carrier_trapezoidal_support_hole_wrench_size` | dependent / lookup (bolt/nut) | high | 837 | `carrier_trapezoidal_support_hole.nut_width_across_flats` |  | sspg: dependent, cpg: dependent |
| 125 | `carrier_trapezoidal_support_nut_depth` | dependent / lookup (bolt/nut) | high | 838 | `carrier_trapezoidal_support_hole.nut_thickness` |  |  |
| 126 | `case_mounting_hole_allen_socket_dia` | dependent / lookup (bolt/nut) | high | 850 | `case_mounting_hole_bolt.bolt_head_dia` |  | sspg: dependent, cpg: dependent |
| 127 | `case_mounting_wrench_size` | dependent / lookup (bolt/nut) | high | 851 | `case_mounting_hole_bolt.nut_width_across_flats` |  | sspg: dependent, cpg: dependent |
| 128 | `case_mounting_nut_depth` | dependent / lookup (bolt/nut) | high | 852 | `case_mounting_hole_bolt.nut_thickness` |  |  |
| 129 | `output_mount_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 856 | `output_mount_hole_bolt.nut_width_across_flats` |  |  |
| 130 | `output_mount_hole_nut_depth` | dependent / lookup (bolt/nut) | high | 857 | `output_mount_hole_bolt.nut_thickness` |  |  |
| 131 | `actuactor_mount_nut_wrench_size` | dependent / lookup (bolt/nut) | high | 861 | `actuactor_mount_hole_bolt.nut_width_across_flats` |  |  |
| 132 | `actuactor_mount_nut_depth` | dependent / lookup (bolt/nut) | high | 862 | `actuactor_mount_hole_bolt.nut_thickness` |  |  |
| 133 | `case_mounting_hole_shift` | dependent / formula | high | 864 | `self.case_mounting_hole_dia / 2` |  | sspg: dependent, cpg: dependent |
| 134 | `fw_s_used` | dependent / formula | high | 868 | `self.bearing_step_width + self.sec_carrier_thickness +self.clearance_planet +self.fw_p_b+self.fw_p_s` |  | sspg: dependent, cpg: dependent |

## Config accounting

| Block | Keys | Read by this type | Read but not written to the CAD | Never used |
|---|---|---|---|---|
| `incpg_optimization_parameters` | 10 | yes | GEAR_RATIO_MIN, GEAR_RATIO_MAX, GEAR_RATIO_STEP, MODULE_MIN, MODULE_MAX, NUM_PLANET_MIN, NUM_PLANET_MAX, NUM_TEETH_SUN_MIN, NUM_TEETH_PLANET_MIN, MAX_GB_DIA_MULT_FACTOR | — |
| `incpg_3DP_design_parameters` | 57 | yes | planetMinDistanceMM, sCarrierExtrusionDiaMM, sCarrierExtrusionClearanceMM, min_rotor_top_bearing_ID | — |


## Result (classification done)

Spec: [`config_files/variables/incpg_dependent_variables.json`](../../../config_files/variables/incpg_dependent_variables.json), page [`docs/variables/incpg_dependent.md`](../incpg_dependent.md) (generated). Tests: the generic `tests/test_variable_categories.py` (INCPG dependent registered in `tests/variable_helpers.py`) and `tests/test_variable_categories_incpg.py` (parametrized over the INCPG variants that have a spec; the independent variant follows in its own commit).

**Counts (CAD variables, 134):** input 21, optimisation 5, fixed 54, dependent 54 (27 formula, 24 lookup, 2 stress rule, 1 implicit constraint). The draft said input 22 / fixed 55 / dependent 52: `motor_height` is the sum of three motor heights (Dependent / formula), and `pressure_angle` (radians) is a formula of `pressure_angle_deg`, which is the Fixed gear standard (the CAD file carries both). **Code-only values: 23** (fixed 17, input 2, dependent 3: `fw_r_stress`, `maxGearboxDiameter`, `actuator_width`; optimisation 1: `module_s`). Confidence: 157 high, 0 medium, 0 low.

**No medium-confidence entries.** `fw_r` is written as the small planet - ring stress width plus `standard_clearance_1_5mm`, as the plan proposed: a code-only `fw_r_stress` (Dependent / stress rule, attribute `fwRingMM`) and `fw_r` as Dependent / formula on it (`fw_r_stress + standard_clearance_1_5mm`); `rules.json` lists `fw_r` as an exception to the shared face-width name rule for the INCPG gearboxes. `fw_p_s` is a copy of `fw_r` (Dependent / formula).

**Config key added** to `incpg_3DP_design_parameters` in `incpg_dependent_params.json` (shared name, value that keeps every output bit-identical): `planet_bearing_gap` = 1.0 (was `standard_clearance_1_5mm * 2 / 3` for the pair and `* 1 / 3` per gear; 1.5 * 2 / 3 is exactly 1.0 and 1.5 * 1 / 3 exactly 0.5, so the code reads `planet_bearing_gap` and `planet_bearing_gap / 2`), in `mitStressAnalysisMinFacewidth`. The other shared keys have no counterpart: there is no motor-case clearance rule, `bearing_mount_thickness` does not exist, and `case_mounting_hole_shift = case_mounting_hole_dia / 2` has no overlap (it would be `case_mounting_hole_wall_overlap = 0`; not introduced). One internal attribute was added without changing any value: `min_rotor_top_bearing_ID` (the per-motor minimum bore, read once and used in the rotor top bearing request), so the spec and its test can name it. A test shows `planet_bearing_gap` and `min_rotor_top_bearing_ID` each drive exactly their CAD variables.

**Shared tooling changed:** `rules.json` (the exception for `fw_r`, added with the INWPG commit), `tests/variable_helpers.py` (INCPG dependent entry and a branch rule), `tests/test_variable_categories.py` (a config value can be per motor: `per_motor` sources are read for the motor in use).

**Results:** `python tests/golden/golden.py check`: All 58 cases match the baseline. `python -m pytest -q`: 907 passed. No `CADs/` file, no golden baseline touched.

**Open questions**
1. **Bug-18 pattern: fixed (option A, 2026-10-31).** The class now has `module_b` and `module_s`; the small-side gears use `module_s` (spec: `module` has attr `module_b`, `module_s` attr `module_s`; the small-side formulas name `module_s`). The CAD file still writes one `module` (= `module_b`); option B (a second module in the CAD) stays open (ISSUES bug 18).
2. The shared face-width rule is still name-based, with a per-gearbox exception list (`fw_r` here) instead of the source-based check the plan proposed.
3. The CAD file carries `pressure_angle` in radians and `pressure_angle_deg` in degrees (every other gearbox writes only the degrees under `pressure_angle`).
4. `min_rotor_top_bearing_ID` (per motor: RI100 25 mm, RI80 0) is a Fixed code-only value; the top bearing itself is a catalogue lookup (Dependent) in this variant.
5. `ring_radial_width` (the CAD name) is the config's `ringRadialWidthMM` (Fixed), also read by the gearbox class and the mass code.
6. `planetMinDistanceMM` and `sCarrierExtrusion*` are read by the gearbox class without effect; they are code-only. The mass-only hard-coded numbers (fillet factor 0.2146, `1.5 x 3` margins, a 4 g sun-shaft bearing) stay out of scope.
