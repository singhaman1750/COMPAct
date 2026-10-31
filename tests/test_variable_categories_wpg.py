"""WPG-only variable checks: the shared rules reach WPG's names (two rings, three stress widths), the
stress-rule face widths follow what they depend on, and every number moved to the config drives exactly
its CAD variables (and the mass where it should). The checks every gearbox gets are in
test_variable_categories.py."""
import pytest

from variable_helpers import GEARBOXES, SPECS, downstream_of, equation_lines, golden_design, write_design

SPEC = SPECS["wpg"]
CAD = SPEC["cad_variables"]
BY_NAME = {e["name"]: e for e in CAD}
FOLDER, ONSHAPE = "WPG", "wpg_equations_onshape.txt"


def design(monkeypatch, tmp_path, name):
    _, motor, material, gears, _ = golden_design(name)
    return write_design(monkeypatch, tmp_path, "wpg", motor, material, gears)


def rerun(actuator, folder, **params):
    """Change config values on a built actuator, redo its variables and face widths, and return its
    Onshape file as name -> value."""
    actuator.design_params.update(params)
    actuator.setVariables()
    actuator.updateFacewidth()
    actuator.setVariables()
    actuator.genEquationFile_editCADdirectly()
    return {n: float(x) for n, x in equation_lines((folder / FOLDER / ONSHAPE).read_text())}


def test_shared_rules_reach_wpg():
    for n in ("Nr_b", "Nr_s"):
        assert (BY_NAME[n]["category"], BY_NAME[n]["subtype"]) == ("dependent", "implicit constraint"), n
    for n in ("fw_s_calc", "fw_p_b", "fw_r_s"):
        assert (BY_NAME[n]["category"], BY_NAME[n]["subtype"]) == ("dependent", "stress rule"), n
    for n in ("fw_r_b", "fw_p_s"):                  # a copy of fw_p_b, and fw_r_s + clearance_planet
        assert (BY_NAME[n]["category"], BY_NAME[n]["subtype"]) == ("dependent", "formula"), n
    assert BY_NAME["clearance_motor_and_case"]["confidence"] == "medium"


def test_optimisation_variables_are_the_gearbox_values(monkeypatch, tmp_path):
    actuator, _, _, onshape = design(monkeypatch, tmp_path, GEARBOXES["wpg"].golden()[0])
    v = {n: float(x) for n, x in onshape}
    gb = actuator.wolfromPlanetaryGearbox
    assert (v["Ns"], v["Np_b"], v["Np_s"], v["num_planet"], v["module"]) == (gb.Ns, gb.NpBig, gb.NpSmall, gb.numPlanet, gb.moduleBig)
    assert (v["Nr_b"], v["Nr_s"]) == (gb.Ns + 2 * gb.NpBig, gb.Ns + gb.NpBig + gb.NpSmall)    # the implicit ring constraints
    module_s = next(e for e in SPEC["code_only"] if e["name"] == "module_s")           # the small module: searched, not in the CAD
    assert (module_s["category"], module_s["attr"]) == ("optimisation", "module_s") and actuator.module_s == gb.moduleSmall > 0
    assert (v["fw_s_calc"], v["fw_p_b"], v["fw_r_s"]) == pytest.approx((gb.fwSunMM, gb.fwPlanetBigMM, gb.fwRingSmallMM))
    assert v["fw_r_b"] == v["fw_p_b"] and v["fw_p_s"] == pytest.approx(v["fw_r_s"] + v["clearance_planet"])


@pytest.mark.parametrize("what", ["FOS", "serviceFactor", "motor_peak_torque", "gear_allowable_stress"])
def test_stress_rule_widths_follow_what_they_depend_on(monkeypatch, tmp_path, what):
    """The face widths have no closed formula in the spec, so their dependencies are checked by changing
    them: doubling FOS, the service factor or the motor torque, or halving the allowable stress, doubles
    the three stress widths (sun - big planet, big planet, small ring) on a design whose planets are above
    the planet-bearing minimum; the copies follow and nothing outside the downstream chain changes."""
    def run(folder, change):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, "wpg__VT8020_PRO__20")
        if change:
            if what == "FOS":
                actuator.FOS *= 2
            elif what == "serviceFactor":
                actuator.serviceFactor *= 2
            elif what == "motor_peak_torque":
                actuator.motor.maxMotorTorque *= 2
            else:
                actuator.wolfromPlanetaryGearbox.maxGearAllowableStressPa /= 2
            actuator.updateFacewidth()
            actuator.genEquationFile_editCADdirectly()
            onshape = equation_lines((folder / FOLDER / ONSHAPE).read_text())
        return {n: float(x) for n, x in onshape}, actuator

    base, act = run(tmp_path / "a", False)
    more, _ = run(tmp_path / "b", True)
    assert base["fw_p_b"] + base["fw_r_s"] > 2 * act.planet_bearing_width + act.planet_bearing_gap     # not raised
    for fw in ("fw_s_calc", "fw_p_b", "fw_r_s"):
        assert more[fw] == pytest.approx(2 * base[fw], rel=1e-12), fw
    assert more["fw_r_b"] == more["fw_p_b"]
    changed = {k for k in base if base[k] != more[k]}
    assert {"fw_s_calc", "fw_p_b", "fw_r_b", "fw_r_s", "fw_p_s", "fw_s_used"} <= changed <= downstream_of("wpg", what)


def test_motor_case_clearance_comes_from_the_config(monkeypatch, tmp_path):
    """clearance_motor_and_case_min (config) is the CAD's motor-to-case gap (a constant there) and the
    minimum in the case mass: raising it from 5 to 7 changes clearance_motor_and_case and exactly the CAD
    variables downstream of it, and the mass (on a design whose big ring is narrower than the motor)."""
    def run(minimum, folder):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, "wpg__U8_Lite__20")
        if minimum is not None:
            onshape = rerun(actuator, folder, clearance_motor_and_case_min=minimum).items()
        return {n: float(x) for n, x in onshape}, actuator.getMassKG_3DP()

    base, base_mass = run(None, tmp_path / "a")
    more, more_mass = run(7, tmp_path / "b")
    assert base["clearance_motor_and_case"] == 5 and more["clearance_motor_and_case"] == 7
    changed = {k for k in base if base[k] != more[k]}
    assert changed == downstream_of("wpg", "clearance_motor_and_case_min") & set(base)
    assert {"clearance_motor_and_case", "Motor_case_ID", "motor_case_OD_base", "case_mounting_PCD", "Motor_case_OD_max"} <= changed
    assert more_mass > base_mass


def test_case_mounting_hole_overlap_comes_from_the_config(monkeypatch, tmp_path):
    """case_mounting_hole_wall_overlap (config) sets case_mounting_hole_shift: raising it by 0.5 lowers the
    shift by 0.5 and changes exactly the CAD variables downstream of it. The mass follows through Motor_case_OD_max
    (the case-mounting ring's outer diameter), so a larger overlap gives a lighter case."""
    def run(overlap, folder):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, "wpg__U8_Lite__20")
        if overlap is not None:
            onshape = rerun(actuator, folder, case_mounting_hole_wall_overlap=overlap).items()
        return {n: float(x) for n, x in onshape}, actuator.getMassKG_3DP()

    base, base_mass = run(None, tmp_path / "a")
    more, more_mass = run(1.0, tmp_path / "b")
    assert more["case_mounting_hole_shift"] == pytest.approx(base["case_mounting_hole_shift"] - 0.5)
    changed = {k for k in base if base[k] != more[k]}
    assert changed == downstream_of("wpg", "case_mounting_hole_wall_overlap") & set(base) \
        == {"case_mounting_hole_shift", "case_mounting_PCD", "Motor_case_OD_max"}
    assert more_mass < base_mass


def test_bearing_mount_wall_multiple_comes_from_the_config(monkeypatch, tmp_path):
    """bearing_mount_wall_bolt_dia_multiple (config) drives the CAD value and the mass: raising it from 2 to 3
    turns the wall from 2 to 3 output-bolt diameters and changes exactly the CAD variables downstream of it."""
    def run(multiple, folder):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, "wpg__U8_Lite__20")
        if multiple is not None:
            onshape = rerun(actuator, folder, bearing_mount_wall_bolt_dia_multiple=multiple).items()
        return {n: float(x) for n, x in onshape}, actuator.getMassKG_3DP()

    base, base_mass = run(None, tmp_path / "a")
    more, more_mass = run(3, tmp_path / "b")
    d = base["output_mounting_hole_dia"]
    assert (base["bearing_mount_thickness"], more["bearing_mount_thickness"]) == (2 * d, 3 * d)
    changed = {k for k in base if base[k] != more[k]}
    assert changed == downstream_of("wpg", "bearing_mount_wall_bolt_dia_multiple") & set(base) \
        == {"bearing_mount_thickness", "output_mounting_PCD"}
    assert more_mass > base_mass


def test_planet_bearing_gap_comes_from_the_config(monkeypatch, tmp_path):
    """planet_bearing_gap (config) sets the smallest planet widths: the two planets together hold two bearings
    and the gap, each gear at least one bearing and half the gap. On the metal golden design the planets sum to
    8.4 mm; a 6.0 mm gap (minimum 13.0 mm, each at least 3.5 + 3.0 = 6.5 mm) raises the big planet and the small
    ring to 6.5, leaves fw_s_calc alone and changes nothing outside the downstream chain."""
    def run(gap, folder):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, "wpg__U8_Lite__20__metal")
        if gap is not None:
            onshape = rerun(actuator, folder, planet_bearing_gap=gap).items()
        return {n: float(x) for n, x in onshape}

    base, more = run(None, tmp_path / "a"), run(6.0, tmp_path / "b")
    assert base["fw_p_b"] + base["fw_r_s"] >= 8.0 and base["fw_p_b"] < 6.5 and base["fw_r_s"] < 6.5     # below the new minimum
    assert more["fw_p_b"] == more["fw_r_b"] == more["fw_r_s"] == 6.5 and more["fw_p_s"] == 6.5 + more["clearance_planet"]
    assert more["fw_s_calc"] == base["fw_s_calc"]
    changed = {k for k in base if base[k] != more[k]}
    assert {"fw_p_b", "fw_r_b", "fw_r_s", "fw_p_s", "fw_s_used"} <= changed <= downstream_of("wpg", "planet_bearing_gap")
