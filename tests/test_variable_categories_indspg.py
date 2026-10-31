"""INDSPG-only variable checks: the shared rules reach the stage-prefixed names, the alias names equal and are classified
like the name they repeat, the stress-rule face widths follow what they depend on, and the planet-bearing gap moved to the
config drives exactly its CAD variables. The checks every gearbox gets are in test_variable_categories.py."""
import pytest

import gearbox_runner
from variable_helpers import GEARBOXES, SPECS, downstream_of, equation_lines, golden_design, write_design

GB = "indspg"
SPEC = SPECS[GB]
CAD = SPEC["cad_variables"]
BY_NAME = {e["name"]: e for e in CAD}
FOLDER, ONSHAPE = "INDSPG", "indspg_equations_onshape.txt"


def design(monkeypatch, tmp_path, name):
    _, motor, material, gears, _ = golden_design(name)
    return write_design(monkeypatch, tmp_path, GB, motor, material, gears)


def rerun(actuator, folder, **params):
    actuator.design_params.update(params)
    actuator.setVariables()
    actuator.updateFacewidth()
    actuator.setVariables()
    actuator.genEquationFile_editCADdirectly()
    return {n: float(x) for n, x in equation_lines((folder / FOLDER / ONSHAPE).read_text())}


def test_shared_rules_reach_indspg():
    for n in ("a1_Nr", "a1_Nr2", "a2_Nr", "a2_Nr1"):
        assert (BY_NAME[n]["category"], BY_NAME[n]["subtype"]) == ("dependent", "implicit constraint"), n
    for n in ("a1_fw_s_calc", "a1_fw_r", "a1_fw_s_calc2", "a2_fw_s_calc", "a2_fw_r"):
        assert (BY_NAME[n]["category"], BY_NAME[n]["subtype"]) == ("dependent", "stress rule"), n
    for n in ("a2_fw_p", "a1_fw_p2"):                       # copies of the stage-2 ring width
        assert (BY_NAME[n]["category"], BY_NAME[n]["subtype"]) == ("dependent", "formula"), n
    assert (BY_NAME["a1_fw_p"]["category"], BY_NAME["a1_fw_p"]["subtype"]) == ("fixed", "planet part")   # stage 1: a fixed config width
    assert BY_NAME["a1_fw_p"]["source"]["key"] == "fw_p_1_fix"
    for n in ("a1_bearing_ID", "a1_bearing_OD", "a1_bearing_height"):                  # the stage-1 output bearing: fixed, from the config
        assert BY_NAME[n]["category"] == "fixed" and BY_NAME[n]["confidence"] == "high" and BY_NAME[n]["source"]["key"] == n, n


@pytest.mark.parametrize("name", GEARBOXES[GB].golden())
def test_alias_names_equal_the_name_they_repeat(monkeypatch, tmp_path, name):
    """43 names are written twice (a1_X and a2_X1, a1_X2 and a2_X, or a1_X and a2_X): the second is 'alias_of' the first, has
    the same value in the file and the same classification."""
    _, _, _, onshape = design(monkeypatch, tmp_path, name)
    v = {n: x for n, x in onshape}
    aliases = [e for e in CAD if "alias_of" in e]
    assert len(aliases) == 43
    for e in aliases:
        first = BY_NAME[e["alias_of"]]
        assert "alias_of" not in first, e["name"]
        assert v[e["name"]] == v[first["name"]], e["name"]                    # the same text, not only the same number
        for k in ("attr", "category", "subtype", "confidence", "source", "formula", "lookup", "rule", "depends_on"):
            assert e.get(k) == first.get(k), (e["name"], k)


def test_optimisation_variables_are_the_gearbox_values(monkeypatch, tmp_path):
    actuator, _, _, onshape = design(monkeypatch, tmp_path, GEARBOXES[GB].golden()[0])
    v = {n: float(x) for n, x in onshape}
    gb = actuator.inrunnerdoubleStagePlanetaryGearbox
    for p, stage in (("a1_", gb.Stage1), ("a2_", gb.Stage2)):
        assert (v[p + "Ns"], v[p + "Np"], v[p + "num_planet"], v[p + "module"]) == (stage.Ns, stage.Np, stage.numPlanet, stage.module)
        assert v[p + "Nr"] == stage.Ns + 2 * stage.Np                          # the implicit ring constraint
        assert (v[p + "fw_s_calc"], v[p + "fw_r"]) == pytest.approx((stage.fwSunMM, stage.fwRingMM))
    assert v["a2_fw_p"] == v["a2_fw_r"] and v["a1_fw_p"] == actuator.fw_p_1_fix            # stage 1's planet width is the config's


@pytest.mark.parametrize("what", ["FOS", "serviceFactor", "motor_peak_torque", "gear_allowable_stress"])
def test_stress_rule_widths_follow_what_they_depend_on(monkeypatch, tmp_path, what):
    """Doubling FOS, the service factor or the motor torque, or halving the allowable stress, doubles both stages' stress
    widths on a design above the planet-bearing minimum in both stages; the planet copies follow and nothing outside the
    downstream chain changes."""
    def run(folder, change):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, f"{GB}__RI100__20")
        if change:
            if what == "FOS":
                actuator.FOS *= 2
            elif what == "serviceFactor":
                actuator.serviceFactor *= 2
            elif what == "motor_peak_torque":
                actuator.motor.maxMotorTorque *= 2
            else:
                for stage in (actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1, actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2):
                    stage.maxGearAllowableStressPa /= 2
            actuator.updateFacewidth()
            actuator.genEquationFile_editCADdirectly()
            onshape = equation_lines((folder / FOLDER / ONSHAPE).read_text())
        return {n: float(x) for n, x in onshape}, actuator

    base, act = run(tmp_path / "a", False)
    more, _ = run(tmp_path / "b", True)
    assert base["a1_fw_r"] > 2 * act.planet_bearing_width1 + act.planet_bearing_gap                  # not raised in either stage
    assert base["a2_fw_r"] > 2 * act.planet_bearing_width2 + act.planet_bearing_gap
    for fw in ("a1_fw_s_calc", "a1_fw_r", "a2_fw_s_calc", "a2_fw_r"):
        assert more[fw] == pytest.approx(2 * base[fw], rel=1e-12), fw
    assert more["a1_fw_p"] == base["a1_fw_p"] and more["a2_fw_p"] == more["a2_fw_r"]                # stage 1's planet width is a config value
    changed = {k for k in base if base[k] != more[k]}
    assert {"a1_fw_s_calc", "a1_fw_r", "a2_fw_r", "a2_fw_p"} <= changed <= downstream_of(GB, what)


def test_planet_bearing_gap_comes_from_the_config(monkeypatch, tmp_path):
    """planet_bearing_gap (config) sets the smallest planet and ring width of both stages: two bearings and the gap. On the
    metal golden design both stages' rings sit at that minimum (2 x 3.5 + 1.0 = 8.0 mm in stage 1, 2 x 5 + 1.0 = 11.0 mm in
    stage 2); a 3.0 mm gap makes them 10.0 and 13.0, leaves the sun widths and stage 1's fixed planet width alone and changes
    nothing outside the downstream chain."""
    def run(gap, folder):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, f"{GB}__RI100__20__metal")
        if gap is not None:
            onshape = rerun(actuator, folder, planet_bearing_gap=gap).items()
        return {n: float(x) for n, x in onshape}

    base, more = run(None, tmp_path / "a"), run(3.0, tmp_path / "b")
    assert base["a1_fw_r"] == 8.0 and base["a2_fw_r"] == base["a2_fw_p"] == 11.0                  # both rings at the bearing minimum
    assert base["a1_fw_s_calc"] < 8.0 and base["a2_fw_s_calc"] < 11.0                            # the sun widths are below it
    assert more["a1_fw_r"] == 10.0 and more["a2_fw_r"] == more["a2_fw_p"] == 13.0
    assert (more["a1_fw_s_calc"], more["a2_fw_s_calc"], more["a1_fw_p"]) == (base["a1_fw_s_calc"], base["a2_fw_s_calc"], base["a1_fw_p"])
    changed = {k for k in base if base[k] != more[k]}
    assert {"a1_fw_r", "a2_fw_r", "a2_fw_p"} <= changed <= downstream_of(GB, "planet_bearing_gap")


@pytest.mark.parametrize("key, value", [("a1_bearing_ID", 40.0), ("a1_bearing_OD", 50.0), ("a1_bearing_height", 6.0)])
def test_output_bearing_size_comes_from_the_config(monkeypatch, tmp_path, key, value):
    """The stage-1 output bearing's size (config, ISSUES bug 22) sets its CAD variable under both stage prefixes and
    changes nothing outside what depends on it."""
    actuator, _, _, onshape = design(monkeypatch, tmp_path, GEARBOXES[GB].golden()[0])
    base = {n: float(x) for n, x in onshape}
    more = rerun(actuator, tmp_path, **{key: value})
    alias = next(e["name"] for e in CAD if e.get("alias_of") == key)
    assert more[key] == more[alias] == value and base[key] != value
    changed = {k for k in base if base[k] != more[k]}
    assert {key, alias} <= changed <= downstream_of(GB, key, alias)


def test_output_bearing_mass_comes_from_the_config(monkeypatch, tmp_path):
    """a1_bearing_massKg (config) is the stage-1 output bearing's mass: it adds to the stage-1 bearing mass and the
    actuator mass one for one and leaves the CAD file alone."""
    actuator, _, _, onshape = design(monkeypatch, tmp_path, GEARBOXES[GB].golden()[0])
    mass, bearings = actuator.getMassKG_3DP(), actuator.bearing_mass_stg1
    more = rerun(actuator, tmp_path, a1_bearing_massKg=actuator.bearing1_massKg + 0.01)
    assert more == {n: float(x) for n, x in onshape}
    assert actuator.getMassKG_3DP() == pytest.approx(mass + 0.01, abs=1e-12)
    assert actuator.bearing_mass_stg1 == pytest.approx(bearings + 0.01, abs=1e-12)


@pytest.mark.parametrize("key, value, moves", [("sun_hub_rotor_gap", 4, "a1_sun_hub_dia"),
                                               ("rotor_mount_hole_wall", 3, "rotor_mount_hole_PCD")])
def test_moved_numbers_come_from_the_config(monkeypatch, tmp_path, key, value, moves):
    """sun_hub_rotor_gap (2) and rotor_mount_hole_wall (2), moved to the config value-identically, drive the CAD variable they
    set and nothing outside what depends on them."""
    actuator, _, _, onshape = design(monkeypatch, tmp_path, GEARBOXES[GB].golden()[0])
    base = {n: float(x) for n, x in onshape}
    more = rerun(actuator, tmp_path, **{key: value})
    changed = {k for k in base if base[k] != more[k]}
    assert moves in changed and changed <= downstream_of(GB, key)


@pytest.mark.parametrize("motor, extra", [("RI100", 0), ("RI80", 0.5)])
def test_stage1_sun_extra_length_is_per_motor(monkeypatch, tmp_path, motor, extra):
    """sun1_extra_clearance_multiple (one value per motor) replaces the old rotor-height == 19 check: RI80 gets 0.5 extra
    clearances on the stage-1 sun length, RI100 none."""
    name = next(n for n in GEARBOXES[GB].golden() if f"__{motor}__" in n)
    actuator, _, _, onshape = design(monkeypatch, tmp_path, name)
    a = actuator
    assert a.sun1_extra_clearance_multiple == extra
    v = {n: float(x) for n, x in onshape}
    assert v["a1_fw_s_used"] == pytest.approx(a.fw_p_1_fix + a.clearance_planet + a.sec_carrier_thickness1
                                              + a.standard_clearance_1_5mm * (2 + extra))


def test_stage1_max_diameter_margin_comes_from_the_config(monkeypatch, tmp_path):
    actuator, _, _, _ = design(monkeypatch, tmp_path, GEARBOXES[GB].golden()[0])
    rule = gearbox_runner.GEARBOXES[GB].max_diameter_stage1
    d = dict(actuator.design_params)
    base = rule(actuator.motor, d, {})
    assert base == pytest.approx(actuator.motor.getRotorIDMM() - 4 * d["standard_clearance_1_5mm"])
    d["max_diameter_stage1_clearance_multiple"] += 2
    assert rule(actuator.motor, d, {}) == pytest.approx(base - 2 * d["standard_clearance_1_5mm"])
