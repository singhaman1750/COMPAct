"""INCPG-only variable checks (dependent and independent variants): the shared rules reach INCPG's names,
the stress-rule face widths follow what they depend on (the ring width adds one standard clearance), the
planet-bearing gap moved to the config drives exactly its CAD variables, and the per-motor rotor bearing
values come from the params file. The checks every gearbox gets are in test_variable_categories.py."""
import pytest

from variable_helpers import GEARBOXES, SPECS, downstream_of, equation_lines, golden_design, write_design

TYPES = tuple(gb for gb in ("incpg_dependent", "incpg_independent") if gb in SPECS)
FOLDER = "INCPG"


def by_name(gb):
    return {e["name"]: e for e in SPECS[gb]["cad_variables"]}


def design(monkeypatch, tmp_path, gb, name):
    _, motor, material, gears, _ = golden_design(name)
    return write_design(monkeypatch, tmp_path, gb, motor, material, gears)


def rerun(actuator, folder, gb, **params):
    actuator.design_params.update(params)
    actuator.setVariables()
    actuator.updateFacewidth()
    actuator.setVariables()
    actuator.genEquationFile_editCADdirectly()
    return {n: float(x) for n, x in equation_lines((folder / FOLDER / f"{gb}_equations_onshape.txt").read_text())}


@pytest.mark.parametrize("gb", TYPES)
def test_shared_rules_reach_incpg(gb):
    spec = by_name(gb)
    assert (spec["Nr"]["category"], spec["Nr"]["subtype"]) == ("dependent", "implicit constraint")
    for n in ("fw_s_calc", "fw_p_b"):
        assert (spec[n]["category"], spec[n]["subtype"]) == ("dependent", "stress rule"), n
    stress = next(e for e in SPECS[gb]["code_only"] if e["name"] == "fw_r_stress")        # the ring's stress width: code-only, not in the CAD
    assert (stress["category"], stress["subtype"], stress["attr"]) == ("dependent", "stress rule", "fwRingMM")
    for n in ("fw_r", "fw_p_s"):       # fw_r = fw_r_stress + standard_clearance_1_5mm (excepted from the shared rule); fw_p_s is a copy of fw_r
        assert (spec[n]["category"], spec[n]["subtype"]) == ("dependent", "formula"), n
    assert spec["fw_r"]["formula"] == "fw_r_stress + standard_clearance_1_5mm" and spec["fw_p_s"]["formula"] == "fw_r"
    assert spec["pressure_angle_deg"]["category"] == "fixed" and spec["pressure_angle"]["subtype"] == "formula"


@pytest.mark.parametrize("gb", TYPES)
def test_optimisation_variables_are_the_gearbox_values(monkeypatch, tmp_path, gb):
    actuator, _, _, onshape = design(monkeypatch, tmp_path, gb, GEARBOXES[gb].golden()[0])
    v = {n: float(x) for n, x in onshape}
    g = actuator.inrunnerCompoundPlanetaryGearbox
    assert (v["Ns"], v["Np_b"], v["Np_s"], v["num_planet"], v["module"]) == (g.Ns, g.NpBig, g.NpSmall, g.numPlanet, g.moduleBig)
    assert v["Nr"] == g.Ns + g.NpBig + g.NpSmall                               # the implicit ring constraint
    module_s = next(e for e in SPECS[gb]["code_only"] if e["name"] == "module_s")   # the small module: searched, not in the CAD
    assert (module_s["category"], module_s["attr"]) == ("optimisation", "module_s") and actuator.module_s == g.moduleSmall > 0
    assert (v["fw_s_calc"], v["fw_p_b"]) == pytest.approx((g.fwSunMM, g.fwPlanetBigMM))
    assert v["fw_r"] == pytest.approx(g.fwRingMM + v["standard_clearance_1_5mm"]) and v["fw_p_s"] == v["fw_r"]


@pytest.mark.parametrize("what", ["FOS", "serviceFactor", "motor_peak_torque", "gear_allowable_stress"])
@pytest.mark.parametrize("gb", TYPES)
def test_stress_rule_widths_follow_what_they_depend_on(monkeypatch, tmp_path, gb, what):
    """Doubling FOS, the service factor or the motor torque, or halving the allowable stress, doubles the stress
    widths on a design whose planets are above the planet-bearing minimum. fw_s_calc and fw_p_b double; the ring
    width is the stress width plus one standard clearance, so (fw_r - clearance) doubles; fw_p_s follows fw_r."""
    def run(folder, change):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, gb, f"{gb}__RI100__10")
        if change:
            if what == "FOS":
                actuator.FOS *= 2
            elif what == "serviceFactor":
                actuator.serviceFactor *= 2
            elif what == "motor_peak_torque":
                actuator.motor.maxMotorTorque *= 2
            else:
                actuator.inrunnerCompoundPlanetaryGearbox.maxGearAllowableStressPa /= 2
            actuator.updateFacewidth()
            actuator.genEquationFile_editCADdirectly()
            onshape = equation_lines((folder / FOLDER / f"{gb}_equations_onshape.txt").read_text())
        return {n: float(x) for n, x in onshape}, actuator

    base, act = run(tmp_path / "a", False)
    more, _ = run(tmp_path / "b", True)
    clr = base["standard_clearance_1_5mm"]
    assert base["fw_p_b"] > act.planet_bearing_width + act.planet_bearing_gap / 2 and base["fw_r"] - clr > act.planet_bearing_width   # not raised
    assert more["fw_s_calc"] == pytest.approx(2 * base["fw_s_calc"], rel=1e-12)
    assert more["fw_p_b"] == pytest.approx(2 * base["fw_p_b"], rel=1e-12)
    assert more["fw_r"] - clr == pytest.approx(2 * (base["fw_r"] - clr), rel=1e-12)
    assert more["fw_p_s"] == more["fw_r"]
    changed = {k for k in base if base[k] != more[k]}
    assert {"fw_s_calc", "fw_p_b", "fw_r", "fw_p_s", "fw_s_used"} <= changed <= downstream_of(gb, what)


@pytest.mark.parametrize("gb", TYPES)
def test_planet_bearing_gap_comes_from_the_config(monkeypatch, tmp_path, gb):
    """planet_bearing_gap (config) sets the smallest planet widths: the two planets together hold two bearings and
    the gap, each gear at least one bearing and half the gap. On the metal golden design the planets sum to 8.3 mm;
    a 6.0 mm gap (minimum 13.0 mm, each at least 3.5 + 3.0 = 6.5 mm) raises the big planet and the small planet to
    6.5, so fw_r = 6.5 + 1.5 = 8.0 and fw_p_s = 8.0; fw_s_calc is unchanged and nothing outside the chain changes."""
    def run(gap, folder):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, gb, f"{gb}__RI100__10__metal")
        if gap is not None:
            onshape = rerun(actuator, folder, gb, planet_bearing_gap=gap).items()
        return {n: float(x) for n, x in onshape}

    base, more = run(None, tmp_path / "a"), run(6.0, tmp_path / "b")
    clr = base["standard_clearance_1_5mm"]
    assert base["fw_p_b"] + base["fw_r"] - clr >= 8.0 and base["fw_p_b"] < 6.5 and base["fw_r"] - clr < 6.5   # below the new minimum
    assert more["fw_p_b"] == 6.5 and more["fw_r"] == 6.5 + clr and more["fw_p_s"] == more["fw_r"]
    assert more["fw_s_calc"] == base["fw_s_calc"]
    changed = {k for k in base if base[k] != more[k]}
    assert {"fw_p_b", "fw_r", "fw_p_s", "fw_s_used"} <= changed <= downstream_of(gb, "planet_bearing_gap")


def test_motor_minimum_for_the_rotor_top_bearing_comes_from_the_config(monkeypatch, tmp_path):
    """min_rotor_top_bearing_ID (one value per motor) is the smallest bore of the dependent variant's rotor top
    bearing: raising RI100's from 25 to 45 mm changes the top bearing and exactly the CAD variables downstream."""
    gb = "incpg_dependent"

    def run(minimum, folder):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, gb, f"{gb}__RI100__10")
        if minimum is not None:
            actuator.design_params["min_rotor_top_bearing_ID"] = {"RI100": minimum, "RI80": 0}
            onshape = rerun(actuator, folder, gb).items()
        return {n: float(x) for n, x in onshape}

    base, more = run(None, tmp_path / "a"), run(45, tmp_path / "b")
    assert more["rotor_top_bearing_ID"] > base["rotor_top_bearing_ID"] >= 25
    changed = {k for k in base if base[k] != more[k]}
    assert "rotor_top_bearing_ID" in changed and changed <= downstream_of(gb, "min_rotor_top_bearing_ID")


@pytest.mark.skipif("incpg_independent" not in SPECS, reason="needs the independent spec")
def test_rotor_top_bearing_of_the_independent_variant_comes_from_the_config(monkeypatch, tmp_path):
    """The independent variant takes the rotor top bearing from the params file, one value per motor (no catalogue
    lookup): giving RI100 RI80's bearing (35 x 47 x 7 mm instead of 40 x 50 x 6) changes the three rotor_top_bearing
    values and exactly the CAD variables downstream of them (the sun hub, ...), and nothing else."""
    gb = "incpg_independent"
    names = ("rotor_top_bearing_ID", "rotor_top_bearing_OD", "rotor_top_bearing_width")

    def run(swap, folder):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, gb, f"{gb}__RI100__10")
        if swap:
            for key in names:
                actuator.design_params[key] = {"RI100": actuator.design_params[key]["RI80"], "RI80": actuator.design_params[key]["RI80"]}
            onshape = rerun(actuator, folder, gb).items()
        return {n: float(x) for n, x in onshape}

    base, more = run(False, tmp_path / "a"), run(True, tmp_path / "b")
    assert [base[n] for n in names] == [40, 50, 6] and [more[n] for n in names] == [35, 47, 7]
    changed = {k for k in base if base[k] != more[k]}
    assert changed == downstream_of(gb, *names) & set(base)
    assert set(names) | {"sun_hub_dia"} <= changed
