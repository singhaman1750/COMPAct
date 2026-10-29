"""Whole-actuator width and diameter of an optimised design, from the CAD variables in its Onshape
equations file (CADs/<FAMILY>/<gb_type>_equations_onshape.txt).

Definitions (the same for every gearbox type):
    width_body_mm         along the motor axis, from the bottom face of the motor casing to the top
                          of the output bearing retainer (or casing cap); motor included
    width_with_driver_mm  the same plus the motor-driver mount below the casing
    dia_body_mm           largest cylinder centred on the axis (motor casing or gearbox housing)
    dia_widest_mm         smallest circle round the axis that holds every part (casing ears, bulges)

Every formula was matched to "Assembly 1" of the Onshape models (2026-10-29): the 11 frameless and
inrunner types on 23 designs (RO100/RO80, RI100/RI80, several ratios) to within 0.01 mm; the framed
types (SSPG, CPG, WPG, DSPG) on U8_Lite, with the diameter rules read from the Onshape sketches.
The constants below are fixed sizes in those models. If a model changes, re-check its type here.

The optimiser's own `actuator_width` is not used for the frameless / inrunner types: it differs
from the CAD in most of them (ISSUES.md, bug 15). For the framed types it matches the CAD.
"""

FRAMED = ("sspg", "cpg", "wpg", "dspg")

# What the motor-driver mount adds below the casing, in mm (measured in Onshape, fixed per type)
DRIVER_MOUNT_MM = {
    "sspg": 9.0, "cpg": 9.0, "wpg": 9.0, "dspg": 9.0,
    "isspg_inside": 9.0, "isspg_compact": 4.5, "icpg": 9.0, "idspg": 6.36,
    "insspg_type_1": 8.0, "insspg_type_2": 9.0,
    "incpg_dependent": 9.0, "incpg_independent": 9.0,
    "inwpg_dependent": 9.0, "inwpg_independent": 9.0, "indspg": 6.37,
}


# ---- width ------------------------------------------------------------------------------------

def _inrunner_planet_bottom(v, independent):
    """INCPG / INWPG: bottom of the planets, from the bottom face of the motor casing."""
    below_stator = v["motor_case_thickness"] + 0.75
    rotor_top = v["stator_bottom_height"] + v["rotor_height"]
    if independent:  # the rotor top bearing sits in its own holder above the rotor
        return below_stator + rotor_top + 2 + v["rotor_top_bearing_width"] + 11
    return below_stator + rotor_top + 8.5


# INDSPG (empirical, from three designs): the stage-1 planets start at a fixed height per motor,
# keyed by stator height (RI100 24.5 mm, RI80 26.5 mm); the stage-2 carrier sits 0.8 mm above the
# stage-1 bearing with the 70x90 output bearing and 2.3 mm with the 65x85 one. Other output
# bearings were not measured: the nearest known gap is used and the width is marked approximate.
INDSPG_STAGE1_PLANET_BOTTOM_MM = {24.5: 18.38, 26.5: 19.75}
INDSPG_STAGE2_GAP_MM = {90.0: 0.8, 85.0: 2.3}


def _indspg_body(v, notes):
    planet1_bottom = INDSPG_STAGE1_PLANET_BOTTOM_MM[v["Stator_height"]]
    od = v["a2_bearing_OD"]
    if od not in INDSPG_STAGE2_GAP_MM:
        nearest = min(INDSPG_STAGE2_GAP_MM, key=lambda k: abs(k - od))
        notes.append(f"INDSPG width approximate: stage-2 gap for a {od:g} mm output bearing not measured "
                     f"(used the {nearest:g} mm one's)")
        od = nearest
    return (planet1_bottom + v["a1_fw_p"] + 3 + v["a1_bearing_height"] + INDSPG_STAGE2_GAP_MM[od] + 6.5
            + v["a2_fw_p"] + 3 + v["a2_bearing_height"] + 2)


BODY_WIDTH_MM = {
    "isspg_inside":  lambda v: 2 * v["motor_case_thickness"] + v["motor_case_height"],
    # the compact casing reaches 4.5 mm down round the driver mount
    "isspg_compact": lambda v: 2 * v["motor_case_thickness"] + v["motor_case_height"] + 4.5,
    "icpg":          lambda v: 24.3 + v["fw_p_b"] + v["fw_p_s"] + 3 + v["bearing_height"] + 2,
    "idspg":         lambda v: v["Rotor_height"] + v["a2_fw_r"] + v["a2_ring_gear_relation"] + 33.5,
    # type 1: in the designs seen, output and upper rotor bearing heights always pair (10/6, 9/7),
    # so it can't be told which of the two sets the stage offset; this form fits both
    "insspg_type_1": lambda v: (4.25 + v["stator_bottom_step_height_"] + v["Rotor_height"] + 2
                                + v["rotor_upper_support_bearing_height"] + 0.75 + v["bearing_height"]
                                + v["fw_p"] + v["bearing_height"] + 3.05 + 2),
    "insspg_type_2": lambda v: (4.3 + v["stator_bottom_step_height_"] + v["Rotor_height"] + 7.3
                                + v["fw_p"] + 3 + v["bearing_height"] + 2),
    "incpg_dependent":   lambda v: (_inrunner_planet_bottom(v, False) + v["fw_p_b"] + v["fw_p_s"]
                                    + 3.5 + v["output_bearing_width"] + 2),
    "incpg_independent": lambda v: (_inrunner_planet_bottom(v, True) + v["fw_p_b"] + v["fw_p_s"]
                                    + 3.5 + v["output_bearing_width"] + 2),
    "inwpg_dependent":   lambda v: _inrunner_planet_bottom(v, False) + v["fw_p_b"] + v["fw_p_s"] + 16.5 + 2,
    "inwpg_independent": lambda v: _inrunner_planet_bottom(v, True) + v["fw_p_b"] + v["fw_p_s"] + 16.5 + 2,
}


def widths(gb_type, cad_vars, code_actuator_width=None, notes=None):
    """Body width and width with the driver mount, in mm. The framed types use the optimiser's
    `actuator_width` (it matches their CAD); pass it as code_actuator_width. Approximations are
    appended to `notes`."""
    notes = [] if notes is None else notes
    if gb_type in FRAMED:
        if code_actuator_width is None:
            raise ValueError(f"{gb_type}: the framed types need the optimiser's actuator_width")
        body = float(code_actuator_width)
    elif gb_type == "indspg":
        body = _indspg_body(cad_vars, notes)
    else:
        body = BODY_WIDTH_MM[gb_type](cad_vars)
    return {"width_body_mm": body, "width_with_driver_mm": body + DRIVER_MOUNT_MM[gb_type]}


# ---- diameter ---------------------------------------------------------------------------------

# Frameless / inrunner motor casing: (body diameter, how much the ears / bulges add)
MOTOR_CASING_MM = {
    "isspg_inside":  lambda v: (v["motor_OD"] + 2 * v["clearance_motor_and_case"] + 2 * v["motor_case_thickness"], 12.62),
    "isspg_compact": lambda v: (v["motor_OD"] + 2 * v["clearance_motor_and_case"] + 2 * v["motor_case_thickness"], 12.62),
    "icpg":          lambda v: (v["Rotor_OD"] + 2 * v["motor_casing_thickness"] + 6, 13.1),
    "idspg":         lambda v: (v["Rotor_OD"] + 2 * v["motor_casing_thickness"] + 6, 20.0),
    "insspg_type_1": lambda v: (v["Stator_OD"] + 2 * v["stator_casing_thickness"], 12.0),
    "insspg_type_2": lambda v: (v["Stator_OD"] + 2 * v["stator_casing_thickness"], 12.0),
    "indspg":        lambda v: (v["Stator_OD"] + 2 * v["stator_casing_thickness"], 12.0),
    "incpg_dependent":   lambda v: (v["stator_OD"] + 2 * v["motor_case_thickness"], 12.0),
    "incpg_independent": lambda v: (v["stator_OD"] + 2 * v["motor_case_thickness"], 12.0),
    "inwpg_dependent":   lambda v: (v["stator_OD"] + 2 * v["motor_case_thickness"], 12.0),
    "inwpg_independent": lambda v: (v["stator_OD"] + 2 * v["motor_case_thickness"], 12.0),
}

# Frameless / inrunner gearbox housing round the output bearing: bearing OD + 17 mm (INDSPG + 14)
OUTPUT_BEARING_OD = {
    "isspg_inside": "output_bearing_OD", "isspg_compact": "output_bearing_OD", "icpg": "bearing_OD",
    "idspg": "a2_bearing_OD", "insspg_type_1": "bearing_OD", "insspg_type_2": "bearing_OD",
    "indspg": "a2_bearing_OD", "incpg_dependent": "output_bearing_OD", "incpg_independent": "output_bearing_OD",
    "inwpg_dependent": "output_bearing_OD", "inwpg_independent": "output_bearing_OD",
}


def _framed_diameters(gb_type, v):
    """From the Onshape sketches: motor casing motor_case_OD_base; gearbox housing
    R = bearing_OD/2 + bearing_mount_thickness (DSPG stage 1: the bearing seat, bearing OD + 0.8,
    plus a1_stg1_stg2_mounting_extra_width); ears R = case_mounting_PCD/2 + wrench/2 + nut clearance."""
    p = "a1_" if gb_type == "dspg" else ""
    casing = v[p + "motor_case_OD_base"]
    if gb_type == "dspg":
        housings = [v["a1_bearing_OD"] + v["a1_loose_clearance_3DP"]
                    + 2 * (v["a1_bearing_mount_thickness"] + v["a1_stg1_stg2_mounting_extra_width"]),
                    v["a2_bearing_OD"] + 2 * v["a2_bearing_mount_thickness"]]
    else:
        housings = [v["bearing_OD"] + 2 * v["bearing_mount_thickness"]]
    ears = v[p + "case_mounting_PCD"] + v[p + "case_mounting_wrench_size"] + 2 * v[p + "case_mounting_nut_clearance"]
    body = max([casing] + housings)
    return {"dia_body_mm": body, "dia_widest_mm": max(body, ears)}


def diameters(gb_type, cad_vars):
    """Body and widest diameter, in mm."""
    v = cad_vars
    if gb_type in FRAMED:
        return _framed_diameters(gb_type, v)
    casing, ears = MOTOR_CASING_MM[gb_type](v)
    housing = v[OUTPUT_BEARING_OD[gb_type]] + (14 if gb_type == "indspg" else 17)
    return {"dia_body_mm": max(casing, housing), "dia_widest_mm": max(casing + ears, housing)}


def geometry(gb_type, cad_vars, code_actuator_width=None):
    """Widths and diameters in mm, plus `geometry_notes` (empty unless something is approximate)."""
    notes = []
    return {**widths(gb_type, cad_vars, code_actuator_width, notes), **diameters(gb_type, cad_vars),
            "geometry_notes": notes}
