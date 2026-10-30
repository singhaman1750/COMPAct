"""CPG-only variable checks: the stress-rule face widths follow what they depend on, fw_p_s
follows fw_r, and the shared rules reach CPG's names. The checks every gearbox gets are in
test_variable_categories.py."""
import pytest

from variable_helpers import GEARBOXES, SPECS, downstream_of, equation_lines, golden_design, write_design

CAD = SPECS["cpg"]["cad_variables"]


def test_shared_rules_reach_cpg():
    by_name = {e["name"]: e for e in CAD}
    assert {"Nr", "fw_s_calc", "fw_p_b", "fw_r"} <= set(by_name)
    assert (by_name["fw_p_s"]["category"], by_name["fw_p_s"]["subtype"]) == ("dependent", "formula")


def test_optimisation_variables_are_the_gearbox_values(monkeypatch, tmp_path):
    _, motor, material, gears, _ = golden_design(GEARBOXES["cpg"].golden()[0])
    actuator, _, _, onshape = write_design(monkeypatch, tmp_path, "cpg", motor, material, gears)
    v = {n: float(x) for n, x in onshape}
    gb = actuator.compoundPlanetaryGearbox
    assert (v["Ns"], v["Np_b"], v["Np_s"], v["num_planet"], v["module"]) == \
        (gb.Ns, gb.NpBig, gb.NpSmall, gb.numPlanet, gb.moduleBig)
    assert actuator.module_s == gb.moduleSmall
    assert (v["fw_s_calc"], v["fw_p_b"], v["fw_r"]) == pytest.approx((gb.fwSunMM, gb.fwPlanetBigMM, gb.fwRingMM))


@pytest.mark.parametrize("what", ["FOS", "serviceFactor", "motor_peak_torque", "gear_allowable_stress"])
def test_stress_rule_widths_follow_what_they_depend_on(monkeypatch, tmp_path, what):
    """The face widths have no closed formula in the spec, so their dependencies are checked by
    changing them: doubling FOS, the service factor or the motor torque, or halving the allowable
    stress, doubles both stress widths (b1: sun - big planet, b2: small planet - ring). On a design
    whose planets are above the planet-bearing minimum, fw_s_calc, fw_p_b and fw_r all double,
    fw_p_s = fw_r + clearance_planet follows, and nothing outside the downstream chain changes."""
    _, motor, material, gears, _ = golden_design("cpg__MN8014__10")

    def run(folder, change):
        folder.mkdir()
        actuator, _, _, onshape = write_design(monkeypatch, folder, "cpg", motor, material, gears)
        if change:
            if what == "FOS":
                actuator.FOS *= 2
            elif what == "serviceFactor":
                actuator.serviceFactor *= 2
            elif what == "motor_peak_torque":
                actuator.motor.maxMotorTorque *= 2
            else:
                actuator.compoundPlanetaryGearbox.maxGearAllowableStressPa /= 2
            actuator.updateFacewidth()
            actuator.genEquationFile_editCADdirectly()
            text = (folder / "CPG" / "cpg_equations_onshape.txt").read_text()
            onshape = equation_lines(text)
        return {n: float(x) for n, x in onshape}, actuator

    base, act = run(tmp_path / "a", False)
    more, _ = run(tmp_path / "b", True)
    each_min = act.planet_bearing_width + act.standard_clearance_1_5mm * 1 / 3
    assert base["fw_p_b"] == base["fw_s_calc"] and base["fw_p_b"] > each_min and base["fw_r"] > each_min  # not raised
    for fw in ("fw_s_calc", "fw_p_b", "fw_r"):
        assert more[fw] == pytest.approx(2 * base[fw], rel=1e-12), fw
    assert more["fw_p_s"] == pytest.approx(more["fw_r"] + more["clearance_planet"], rel=1e-12)
    changed = {k for k in base if base[k] != more[k]}
    assert {"fw_s_calc", "fw_p_b", "fw_r", "fw_p_s", "fw_s_used", "case_dist"} <= changed <= downstream_of("cpg", what)
