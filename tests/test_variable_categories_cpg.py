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


def test_motor_case_clearance_comes_from_the_config(monkeypatch, tmp_path):
    """clearance_motor_and_case_min (config) drives both the CAD value and the case mass: raising it
    changes clearance_motor_and_case and exactly the CAD variables downstream of it, and the mass."""
    _, motor, material, gears, _ = golden_design("cpg__U8_Lite__10")

    def run(clearance_min, folder):
        folder.mkdir()
        actuator, _, _, onshape = write_design(monkeypatch, folder, "cpg", motor, material, gears)
        if clearance_min is not None:
            actuator.design_params["clearance_motor_and_case_min"] = clearance_min
            actuator.setVariables()
            actuator.genEquationFile_editCADdirectly()
            onshape = equation_lines((folder / "CPG" / "cpg_equations_onshape.txt").read_text())
        return {n: float(x) for n, x in onshape}, actuator.getMassKG_3DP()

    base, base_mass = run(None, tmp_path / "a")
    more, more_mass = run(7, tmp_path / "b")
    assert base["clearance_motor_and_case"] == 5 and more["clearance_motor_and_case"] == 7   # planets < motor here
    changed = {k for k in base if base[k] != more[k]}
    assert changed == downstream_of("cpg", "clearance_motor_and_case") & set(base)
    assert changed == {"clearance_motor_and_case", "Motor_case_ID", "motor_case_OD_base", "case_mounting_PCD",
                       "Motor_case_OD_max"}
    assert more_mass > base_mass


def test_case_mounting_hole_overlap_comes_from_the_config(monkeypatch, tmp_path):
    """case_mounting_hole_wall_overlap (config) sets case_mounting_hole_shift: raising it by 0.5 lowers
    the shift by 0.5 and changes exactly the CAD variables downstream of it; the mass doesn't use it."""
    _, motor, material, gears, _ = golden_design("cpg__U8_Lite__10")

    def run(overlap, folder):
        folder.mkdir()
        actuator, _, _, onshape = write_design(monkeypatch, folder, "cpg", motor, material, gears)
        if overlap is not None:
            actuator.design_params["case_mounting_hole_wall_overlap"] = overlap
            actuator.setVariables()
            actuator.genEquationFile_editCADdirectly()
            onshape = equation_lines((folder / "CPG" / "cpg_equations_onshape.txt").read_text())
        return {n: float(x) for n, x in onshape}, actuator.getMassKG_3DP()

    base, base_mass = run(None, tmp_path / "a")
    more, more_mass = run(1.0, tmp_path / "b")
    assert more["case_mounting_hole_shift"] == pytest.approx(base["case_mounting_hole_shift"] - 0.5)
    changed = {k for k in base if base[k] != more[k]}
    assert changed == downstream_of("cpg", "case_mounting_hole_shift") & set(base) \
        == {"case_mounting_hole_shift", "case_mounting_PCD", "Motor_case_OD_max"}
    assert more_mass == base_mass


def test_bearing_mount_wall_multiple_comes_from_the_config(monkeypatch, tmp_path):
    """bearing_mount_wall_bolt_dia_multiple (config) drives both the CAD value and the mass. On a
    design where the bearing plus its bolts is wider than the ring gear, raising it from 2 to 3 turns
    the wall from 2 to 3 output-bolt diameters and changes exactly the CAD variables downstream of it."""
    for name in GEARBOXES["cpg"].golden():   # a 3dp design in the first branch of the rule
        _, motor, material, gears, _ = golden_design(name)
        if material != "3dp":
            continue
        (tmp_path / name).mkdir()
        actuator, *_ = write_design(monkeypatch, tmp_path / name, "cpg", motor, material, gears)
        if actuator.bearing_mount_thickness == actuator.output_mounting_hole_dia * 2:
            break
    else:
        pytest.fail("no golden CPG design in the first branch of the bearing-mount rule")

    def run(multiple, folder):
        folder.mkdir()
        actuator, _, _, onshape = write_design(monkeypatch, folder, "cpg", motor, material, gears)
        if multiple is not None:
            actuator.design_params["bearing_mount_wall_bolt_dia_multiple"] = multiple
            actuator.setVariables()
            actuator.genEquationFile_editCADdirectly()
            onshape = equation_lines((folder / "CPG" / "cpg_equations_onshape.txt").read_text())
        return {n: float(x) for n, x in onshape}, actuator.getMassKG_3DP()

    base, base_mass = run(None, tmp_path / "a")
    more, more_mass = run(3, tmp_path / "b")
    d = base["output_mounting_hole_dia"]
    assert (base["bearing_mount_thickness"], more["bearing_mount_thickness"]) == (2 * d, 3 * d)
    changed = {k for k in base if base[k] != more[k]}
    assert changed == downstream_of("cpg", "bearing_mount_thickness") & set(base) \
        == {"bearing_mount_thickness", "output_mounting_PCD"}
    assert more_mass > base_mass


def test_ring_wall_minimum_comes_from_the_config(monkeypatch, tmp_path):
    """ringRadialWidthMM (config) is the CAD's minimum ring wall too: on a design where the ring is
    already wider than the output bearing (the minimum branch), raising it from 5 to 6 mm changes
    ring_radial_thickness and ring_OD and nothing else in the CAD file."""
    _, motor, material, gears, _ = golden_design("cpg__MAD_M6C12_KV170__10")

    def run(wall, folder):
        folder.mkdir()
        actuator, _, _, onshape = write_design(monkeypatch, folder, "cpg", motor, material, gears)
        if wall is not None:
            actuator.ringRadialWidthMM = wall
            actuator.setVariables()
            actuator.genEquationFile_editCADdirectly()
            onshape = equation_lines((folder / "CPG" / "cpg_equations_onshape.txt").read_text())
        return {n: float(x) for n, x in onshape}

    base, more = run(None, tmp_path / "a"), run(6, tmp_path / "b")
    assert (base["ring_radial_thickness"], more["ring_radial_thickness"]) == (5, 6)
    assert more["ring_OD"] == pytest.approx(base["ring_OD"] + 2)
    changed = {k for k in base if base[k] != more[k]}
    assert changed == downstream_of("cpg", "ringRadialWidthMM") & set(base) == {"ring_radial_thickness", "ring_OD"}
