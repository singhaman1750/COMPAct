"""IDSPG-only variable checks: the shared rules reach the stage-prefixed names, the alias names equal and are classified
like the name they repeat, the stress-rule face widths follow what they depend on, and the planet-bearing gap moved to the
config drives exactly its CAD variables. The checks every gearbox gets are in test_variable_categories.py."""
import pytest

from variable_helpers import GEARBOXES, SPECS, downstream_of, equation_lines, golden_design, write_design

GB = "idspg"
SPEC = SPECS[GB]
CAD = SPEC["cad_variables"]
BY_NAME = {e["name"]: e for e in CAD}
FOLDER, ONSHAPE = "IDSPG", "idspg_equations_onshape.txt"


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


def test_shared_rules_reach_idspg():
    for n in ("a1_Nr", "a1_Nr2", "a2_Nr", "a2_Nr1"):
        assert (BY_NAME[n]["category"], BY_NAME[n]["subtype"]) == ("dependent", "implicit constraint"), n
    for n in ("a1_fw_s_calc", "a1_fw_r", "a1_fw_s_calc2", "a2_fw_s_calc", "a2_fw_r"):
        assert (BY_NAME[n]["category"], BY_NAME[n]["subtype"]) == ("dependent", "stress rule"), n
    for n in ("a1_fw_p", "a2_fw_p", "a1_fw_p2"):            # copies of the ring width
        assert (BY_NAME[n]["category"], BY_NAME[n]["subtype"]) == ("dependent", "formula"), n
    assert BY_NAME["a1_ring_OD"]["formula"] == "Stator_ID"  # the stage-1 ring fits the stator bore


@pytest.mark.parametrize("name", GEARBOXES[GB].golden())
def test_alias_names_equal_the_name_they_repeat(monkeypatch, tmp_path, name):
    """36 names are written twice (a1_X and a2_X1, a1_X2 and a2_X, or a1_X and a2_X): the second is 'alias_of' the first, has
    the same value in the file and the same classification."""
    _, _, _, onshape = design(monkeypatch, tmp_path, name)
    v = {n: x for n, x in onshape}
    aliases = [e for e in CAD if "alias_of" in e]
    assert len(aliases) == 36
    for e in aliases:
        first = BY_NAME[e["alias_of"]]
        assert "alias_of" not in first, e["name"]
        assert v[e["name"]] == v[first["name"]], e["name"]                    # the same text, not only the same number
        for k in ("attr", "category", "subtype", "confidence", "source", "formula", "lookup", "rule", "depends_on"):
            assert e.get(k) == first.get(k), (e["name"], k)


def test_optimisation_variables_are_the_gearbox_values(monkeypatch, tmp_path):
    actuator, _, _, onshape = design(monkeypatch, tmp_path, GEARBOXES[GB].golden()[0])
    v = {n: float(x) for n, x in onshape}
    gb = actuator.internaldoubleStagePlanetaryGearbox
    for p, stage in (("a1_", gb.Stage1), ("a2_", gb.Stage2)):
        assert (v[p + "Ns"], v[p + "Np"], v[p + "num_planet"], v[p + "module"]) == (stage.Ns, stage.Np, stage.numPlanet, stage.module)
        assert v[p + "Nr"] == stage.Ns + 2 * stage.Np                          # the implicit ring constraint
        assert (v[p + "fw_s_calc"], v[p + "fw_r"], v[p + "fw_p"]) == pytest.approx((stage.fwSunMM, stage.fwRingMM, stage.fwRingMM))
    assert v["a1_ring_OD"] == actuator.Stator_ID


@pytest.mark.parametrize("what", ["FOS", "serviceFactor", "motor_peak_torque", "gear_allowable_stress"])
def test_stress_rule_widths_follow_what_they_depend_on(monkeypatch, tmp_path, what):
    """Doubling FOS, the service factor or the motor torque, or halving the allowable stress, doubles both stages' stress
    widths on a design above the planet-bearing minimum in both stages; the planet copies follow and nothing outside the
    downstream chain changes."""
    def run(folder, change):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, f"{GB}__RO100__20")
        if change:
            if what == "FOS":
                actuator.FOS *= 2
            elif what == "serviceFactor":
                actuator.serviceFactor *= 2
            elif what == "motor_peak_torque":
                actuator.motor.maxMotorTorque *= 2
            else:
                for stage in (actuator.internaldoubleStagePlanetaryGearbox.Stage1, actuator.internaldoubleStagePlanetaryGearbox.Stage2):
                    stage.maxGearAllowableStressPa /= 2
            actuator.updateFacewidth()
            actuator.genEquationFile_editCADdirectly()
            onshape = equation_lines((folder / FOLDER / ONSHAPE).read_text())
        return {n: float(x) for n, x in onshape}, actuator

    base, act = run(tmp_path / "a", False)
    more, _ = run(tmp_path / "b", True)
    each_min = 2 * act.planet_bearing_width1 + act.planet_bearing_gap
    assert min(base["a1_fw_r"], base["a2_fw_r"]) > each_min                                # not raised in either stage
    for fw in ("a1_fw_s_calc", "a1_fw_r", "a2_fw_s_calc", "a2_fw_r"):
        assert more[fw] == pytest.approx(2 * base[fw], rel=1e-12), fw
    assert more["a1_fw_p"] == more["a1_fw_r"] and more["a2_fw_p"] == more["a2_fw_r"]
    changed = {k for k in base if base[k] != more[k]}
    assert {"a1_fw_s_calc", "a1_fw_r", "a1_fw_p", "a2_fw_r", "a2_fw_p"} <= changed <= downstream_of(GB, what)


def test_planet_bearing_gap_comes_from_the_config(monkeypatch, tmp_path):
    """planet_bearing_gap (config) sets the smallest planet and ring width of both stages: two bearings and the gap. On the
    metal golden design both stages' rings sit at that minimum (2 x 3.5 + 1.0 = 8.0 mm); a 3.0 mm gap makes every ring and
    planet width 10.0, leaves the sun widths alone and changes nothing outside the downstream chain."""
    def run(gap, folder):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, f"{GB}__RO100__20__metal")
        if gap is not None:
            onshape = rerun(actuator, folder, planet_bearing_gap=gap).items()
        return {n: float(x) for n, x in onshape}

    base, more = run(None, tmp_path / "a"), run(3.0, tmp_path / "b")
    assert base["a1_fw_r"] == base["a1_fw_p"] == base["a2_fw_r"] == base["a2_fw_p"] == 8.0
    assert max(base["a1_fw_s_calc"], base["a2_fw_s_calc"]) < 8.0                          # the sun widths are below the minimum
    assert more["a1_fw_r"] == more["a1_fw_p"] == more["a2_fw_r"] == more["a2_fw_p"] == 10.0
    assert (more["a1_fw_s_calc"], more["a2_fw_s_calc"]) == (base["a1_fw_s_calc"], base["a2_fw_s_calc"])
    changed = {k for k in base if base[k] != more[k]}
    assert {"a1_fw_r", "a1_fw_p", "a2_fw_r", "a2_fw_p"} <= changed <= downstream_of(GB, "planet_bearing_gap")
