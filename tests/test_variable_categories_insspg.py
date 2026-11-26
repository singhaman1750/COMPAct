"""INSSPG-only variable checks (types 1 and 2 share one class): the shared rules reach INSSPG's names,
type 2's spec equals type 1's except fw_s_used, the stress-rule face widths follow what they depend on,
and the planet-bearing gap moved to the config drives exactly its CAD variables. The checks every
gearbox gets are in test_variable_categories.py."""
import pytest

import gearbox_runner
from variable_helpers import GEARBOXES, SPECS, downstream_of, equation_lines, golden_design, write_design

TYPES = tuple(gb for gb in ("insspg_type_1", "insspg_type_2") if gb in SPECS)
FOLDER = "INSSPG"


def by_name(gb):
    return {e["name"]: e for e in SPECS[gb]["cad_variables"]}


def design(monkeypatch, tmp_path, gb, name):
    _, motor, material, gears, _ = golden_design(name)
    return write_design(monkeypatch, tmp_path, gb, motor, material, gears)


@pytest.mark.parametrize("gb", TYPES)
def test_shared_rules_reach_insspg(gb):
    spec = by_name(gb)
    assert (spec["Nr"]["category"], spec["Nr"]["subtype"]) == ("dependent", "implicit constraint")
    for n in ("fw_s_calc", "fw_p", "fw_r"):
        assert (spec[n]["category"], spec[n]["subtype"]) == ("dependent", "stress rule"), n


@pytest.mark.skipif(len(TYPES) < 2, reason="needs both INSSPG specs")
def test_type_2_differs_from_type_1_only_in_fw_s_used():
    one, two = SPECS["insspg_type_1"], SPECS["insspg_type_2"]
    a, b = one["cad_variables"], two["cad_variables"]
    assert [e["name"] for e in a] == [e["name"] for e in b]
    assert [e for e in a if e not in b] == [next(e for e in a if e["name"] == "fw_s_used")]
    assert one["code_only"] == two["code_only"]
    f1 = by_name("insspg_type_1")["fw_s_used"]
    f2 = by_name("insspg_type_2")["fw_s_used"]
    assert "rotor_support_bearing_height" in f1["formula"] and "Rotor_height" not in f1["formula"]
    assert "Rotor_height" in f2["formula"] and "rotor_support_bearing_height" not in f2["formula"]


@pytest.mark.parametrize("gb", TYPES)
def test_optimisation_variables_are_the_gearbox_values(monkeypatch, tmp_path, gb):
    actuator, _, _, onshape = design(monkeypatch, tmp_path, gb, GEARBOXES[gb].golden()[0])
    v = {n: float(x) for n, x in onshape}
    g = actuator.planetaryGearbox
    assert (v["Ns"], v["Np"], v["num_planet"], v["module"]) == (g.Ns, g.Np, g.numPlanet, g.module)
    assert v["Nr"] == g.Ns + 2 * g.Np                                        # the implicit ring constraint
    assert (v["fw_s_calc"], v["fw_p"], v["fw_r"]) == pytest.approx((g.fwSunMM, g.fwPlanetMM, g.fwRingMM))


@pytest.mark.parametrize("what", ["FOS", "serviceFactor", "motor_peak_torque", "gear_allowable_stress"])
@pytest.mark.parametrize("gb", TYPES)
def test_stress_rule_widths_follow_what_they_depend_on(monkeypatch, tmp_path, gb, what):
    """Doubling FOS, the service factor or the motor torque, or halving the allowable stress, doubles the
    stress widths on a design whose planets are above the planet-bearing minimum; the ring and planet widths
    are the same value and nothing outside the downstream chain changes."""
    def run(folder, change):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, gb, f"{gb}__RI100__6.5")
        if change:
            if what == "FOS":
                actuator.FOS *= 2
            elif what == "serviceFactor":
                actuator.serviceFactor *= 2
            elif what == "motor_peak_torque":
                actuator.motor.maxMotorTorque *= 2
            else:
                actuator.planetaryGearbox.maxGearAllowableStressPa /= 2
            actuator.updateFacewidth()
            actuator.genEquationFile_editCADdirectly()
            onshape = equation_lines((folder / FOLDER / f"{gb}_equations_onshape.txt").read_text())
        return {n: float(x) for n, x in onshape}, actuator

    base, act = run(tmp_path / "a", False)
    more, _ = run(tmp_path / "b", True)
    assert base["fw_p"] > 2 * act.planet_bearing_width + act.planet_bearing_gap                 # not raised
    for fw in ("fw_s_calc", "fw_p", "fw_r"):
        assert more[fw] == pytest.approx(2 * base[fw], rel=1e-12), fw
    changed = {k for k in base if base[k] != more[k]}
    assert {"fw_s_calc", "fw_p", "fw_r", "fw_s_used"} <= changed <= downstream_of(gb, what)


@pytest.mark.parametrize("gb", TYPES)
def test_planet_bearing_gap_comes_from_the_config(monkeypatch, tmp_path, gb):
    """planet_bearing_gap (config) sets the smallest planet and ring width: two bearings and the gap. On the metal
    golden design they sit at that minimum (2 x 3.5 + 1.0 = 8.0 mm); a 3.0 mm gap makes fw_p = fw_r = 10.0, leaves
    fw_s_calc alone and changes nothing outside the downstream chain."""
    def run(gap, folder):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, gb, f"{gb}__RI100__6.5__metal")
        if gap is not None:
            actuator.design_params["planet_bearing_gap"] = gap
            actuator.setVariables()
            actuator.updateFacewidth()
            actuator.setVariables()
            actuator.genEquationFile_editCADdirectly()
            onshape = equation_lines((folder / FOLDER / f"{gb}_equations_onshape.txt").read_text())
        return {n: float(x) for n, x in onshape}

    base, more = run(None, tmp_path / "a"), run(3.0, tmp_path / "b")
    assert base["fw_p"] == base["fw_r"] == 8.0 and base["fw_s_calc"] < 8.0                      # at the bearing minimum
    assert more["fw_p"] == more["fw_r"] == 10.0 and more["fw_s_calc"] == base["fw_s_calc"]
    changed = {k for k in base if base[k] != more[k]}
    assert {"fw_p", "fw_r", "fw_s_used"} <= changed <= downstream_of(gb, "planet_bearing_gap")


def rerun(actuator, folder, **params):
    actuator.design_params.update(params)
    actuator.setVariables()
    actuator.updateFacewidth()
    actuator.setVariables()
    actuator.genEquationFile_editCADdirectly()
    return {n: float(x) for n, x in equation_lines((folder / FOLDER / f"{actuator.insspg_type}_equations_onshape.txt").read_text())}


@pytest.mark.parametrize("gb", TYPES)
@pytest.mark.parametrize("key, value, moves, setup", [
    ("rotor_support_bearing_OD_clearance", 14, "rotor_support_bearing_OD", {}),
    ("rotor_upper_support_bearing_clearance_multiple", 15, "rotor_upper_support_bearing_OD", {}),
    ("sun_support_OD_max", 10, "sun_support_OD", {}),
    ("sun_support_clearance_multiple", 6, "sun_support_OD", {"sun_support_OD_max": 1000}),   # lift the cap so the margin shows
])
def test_moved_numbers_come_from_the_config(monkeypatch, tmp_path, gb, key, value, moves, setup):
    """The numbers moved to insspg_params.json (4, 5, 21 and 3, value-identical): each drives the CAD variable it sets and
    nothing outside what depends on it."""
    actuator, _, _, _ = design(monkeypatch, tmp_path, gb, GEARBOXES[gb].golden()[0])
    base = rerun(actuator, tmp_path, **setup)
    more = rerun(actuator, tmp_path, **{key: value})
    changed = {k for k in base if base[k] != more[k]}
    assert moves in changed and changed <= downstream_of(gb, key)


@pytest.mark.parametrize("gb", TYPES)
def test_max_diameter_margin_comes_from_the_config(monkeypatch, tmp_path, gb):
    """gearbox_runner's largest INSSPG gearbox diameter is the stator OD less max_diameter_stator_OD_margin (5.5 mm) and
    the clearances."""
    actuator, _, _, _ = design(monkeypatch, tmp_path, gb, GEARBOXES[gb].golden()[0])
    rule = gearbox_runner.GEARBOXES[gb].max_diameter
    d = dict(actuator.design_params)
    base = rule(actuator.motor, d, {})
    assert base == pytest.approx(actuator.motor.getStatorODMM() - 5.5 - 2 * d["standard_clearance_1_5mm"] - d["loose_clearance_3DP"] / 2)
    d["max_diameter_stator_OD_margin"] += 2
    assert rule(actuator.motor, d, {}) == pytest.approx(base - 2)
