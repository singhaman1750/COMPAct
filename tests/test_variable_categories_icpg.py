"""ICPG-only variable checks: the shared rules reach ICPG's names, the stress-rule face widths follow what they
depend on including the stator-height cap, and the planet-bearing gap moved to the config drives exactly its CAD
variables. The checks every gearbox gets are in test_variable_categories.py."""
import pytest

from variable_helpers import GEARBOXES, SPECS, downstream_of, equation_lines, golden_design, write_design

GB = "icpg"
SPEC = SPECS[GB]
CAD = SPEC["cad_variables"]
BY_NAME = {e["name"]: e for e in CAD}
FOLDER, ONSHAPE = "ICPG", "icpg_equations_onshape.txt"
UNCAPPED = ("RO100", (30, 30, 30, 90, 1.2, 1.2, 3))     # widths 7.6 / 7.6 / 6.5 mm: above the planet-bearing minimum, under the cap


def design(monkeypatch, tmp_path, name=None):
    if name is None:
        motor, gears = UNCAPPED
        return write_design(monkeypatch, tmp_path, GB, motor, "3dp", gears)
    _, motor, material, gears, _ = golden_design(name)
    return write_design(monkeypatch, tmp_path, GB, motor, material, gears)


def rerun(actuator, folder, **params):
    actuator.design_params.update(params)
    actuator.setVariables()
    actuator.updateFacewidth()
    actuator.setVariables()
    actuator.genEquationFile_editCADdirectly()
    return {n: float(x) for n, x in equation_lines((folder / FOLDER / ONSHAPE).read_text())}


def test_shared_rules_reach_icpg():
    assert (BY_NAME["Nr"]["category"], BY_NAME["Nr"]["subtype"]) == ("dependent", "implicit constraint")
    for n in ("fw_s_calc", "fw_p_b", "fw_r"):
        assert (BY_NAME[n]["category"], BY_NAME[n]["subtype"]) == ("dependent", "stress rule"), n
    assert (BY_NAME["fw_p_s"]["category"], BY_NAME["fw_p_s"]["subtype"]) == ("dependent", "formula")
    drivers = [e for e in CAD if e["subtype"] == "driver"]
    assert len(drivers) == 6 and all(e["category"] == "input" and e["confidence"] == "high" for e in drivers)   # Input / driver, decided 2026-10-31
    assert all(e["source"]["file"] == "icpg_params.json" for e in drivers)    # the runner passes no driver: the gearbox's own config


def test_optimisation_variables_are_the_gearbox_values(monkeypatch, tmp_path):
    actuator, _, _, onshape = design(monkeypatch, tmp_path, GEARBOXES[GB].golden()[0])
    v = {n: float(x) for n, x in onshape}
    g = actuator.internalcompoundPlanetaryGearbox
    assert (v["Ns"], v["Np_b"], v["Np_s"], v["num_planet"], v["module"]) == (g.Ns, g.NpBig, g.NpSmall, g.numPlanet, g.moduleBig)
    assert v["Nr"] == g.Ns + g.NpBig + g.NpSmall                               # the implicit ring constraint
    module_s = next(e for e in SPEC["code_only"] if e["name"] == "module_s")   # the small module: searched, not in the CAD
    assert (module_s["category"], module_s["attr"]) == ("optimisation", "module_s") and actuator.module_s == g.moduleSmall > 0
    assert (v["fw_s_calc"], v["fw_p_b"], v["fw_r"]) == pytest.approx((g.fwSunMM, g.fwPlanetBigMM, g.fwRingMM))
    assert v["fw_p_s"] == pytest.approx(v["fw_r"] + v["clearance_planet"])


@pytest.mark.parametrize("what", ["FOS", "serviceFactor", "motor_peak_torque", "gear_allowable_stress"])
def test_stress_rule_widths_follow_what_they_depend_on(monkeypatch, tmp_path, what):
    """Scaling FOS, the service factor or the motor torque by 1.5, or the allowable stress by 1 / 1.5, scales the stress
    widths by 1.5 on a design above the planet-bearing minimum and under the stator-height cap (module 1.2); the small
    planet's width follows the ring's and nothing outside the downstream chain changes."""
    def run(folder, change):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder)
        if change:
            if what == "FOS":
                actuator.FOS *= 1.5
            elif what == "serviceFactor":
                actuator.serviceFactor *= 1.5
            elif what == "motor_peak_torque":
                actuator.motor.maxMotorTorque *= 1.5
            else:
                actuator.internalcompoundPlanetaryGearbox.maxGearAllowableStressPa /= 1.5
            actuator.updateFacewidth()
            actuator.genEquationFile_editCADdirectly()
            onshape = equation_lines((folder / FOLDER / ONSHAPE).read_text())
        return {n: float(x) for n, x in onshape}, actuator

    base, act = run(tmp_path / "a", False)
    more, more_act = run(tmp_path / "b", True)
    assert act.torque_carried_fraction == more_act.torque_carried_fraction == 1.0                    # under the cap, before and after
    assert min(base["fw_p_b"], base["fw_r"]) > act.planet_bearing_width + act.planet_bearing_gap / 2    # not raised
    for fw in ("fw_s_calc", "fw_p_b", "fw_r"):
        assert more[fw] == pytest.approx(1.5 * base[fw], rel=1e-12), fw
    assert more["fw_p_s"] == pytest.approx(more["fw_r"] + more["clearance_planet"])
    changed = {k for k in base if base[k] != more[k]}
    # (fw_s_used stays at the motor height here: this short design sits on the sun-length floor)
    assert {"fw_s_calc", "fw_p_b", "fw_r", "fw_p_s"} <= changed <= downstream_of(GB, what)
    assert more["fw_s_used"] == base["fw_s_used"] == act.motor_height


@pytest.mark.parametrize("key, value, stack", [("gear_axial_margin_mm", 5.0, lambda stator, gap: stator - 5.0),
                                                ("planet_step_gap_mm", 2.5, lambda stator, gap: stator - 3.0)])
def test_stator_height_cap_comes_from_the_config(monkeypatch, tmp_path, key, value, stack):
    """The two planet steps (big + small) plus planet_step_gap_mm must fit the stator height less gear_axial_margin_mm:
    on a 3d-printed design that hits the cap they fill it exactly, and each config value changes the gears and exactly
    the CAD variables downstream of it."""
    def run(change, folder):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, f"{GB}__RO100__10")
        if change:
            onshape = rerun(actuator, folder, **{key: value}).items()
        return {n: float(x) for n, x in onshape}, actuator

    base, act = run(False, tmp_path / "a")
    more, more_act = run(True, tmp_path / "b")
    stator = act.motor.stator_height
    assert act.torque_carried_fraction < 1.0 and more_act.torque_carried_fraction < 1.0              # capped both times
    assert base["fw_p_b"] + base["fw_r"] + 1.5 == pytest.approx(stator - 3.0)                       # margin 3, gap 1.5
    gap = value if key == "planet_step_gap_mm" else 1.5
    margin = value if key == "gear_axial_margin_mm" else 3.0
    assert more["fw_p_b"] + more["fw_r"] + gap == pytest.approx(stator - margin)
    changed = {k for k in base if base[k] != more[k]}
    assert {"fw_s_calc", "fw_p_b", "fw_r", "fw_s_used"} <= changed <= downstream_of(GB, key)


def test_planet_bearing_gap_comes_from_the_config(monkeypatch, tmp_path):
    """planet_bearing_gap (config) sets the smallest planet widths: the two planets hold two bearings and the gap, each
    gear at least one bearing and half the gap. On the metal golden design the planets sum to 23.4 mm; an 18 mm gap
    (minimum 25 mm, each at least 3.5 + 9 = 12.5 mm) raises the big planet from 10.3 to 12.5, leaves the ring (13.0), the
    sun and the cap alone and changes nothing outside the downstream chain."""
    def run(gap, folder):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, f"{GB}__RO100__10__metal")
        if gap is not None:
            onshape = rerun(actuator, folder, planet_bearing_gap=gap).items()
        return {n: float(x) for n, x in onshape}

    base, more = run(None, tmp_path / "a"), run(18.0, tmp_path / "b")
    assert base["fw_p_b"] + base["fw_r"] < 25.0 and base["fw_p_b"] < 12.5 < base["fw_r"]            # only the big planet is raised
    assert more["fw_p_b"] == 12.5 and more["fw_r"] == base["fw_r"] and more["fw_s_calc"] == base["fw_s_calc"]
    changed = {k for k in base if base[k] != more[k]}
    assert {"fw_p_b", "fw_s_used"} <= changed <= downstream_of(GB, "planet_bearing_gap")


def test_sun_width_depends_on_the_planet_bearing_minimum_through_the_cap(monkeypatch, tmp_path):
    """The stator-height cap scales all four widths, including the sun's, by a factor that depends on the planets' widths, which
    the planet-bearing minimum can raise. On the metal golden design a 21 mm gap (each planet at least 3.5 + 10.5 = 14 mm) pushes
    the two planet steps past the cap (14 + 14 + 1.5 > 28.5): the factor drops below 1 and the sun width shrinks with it, so
    fw_s_calc changes with planet_bearing_gap and the spec lists that dependency."""
    def run(gap, folder):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, f"{GB}__RO100__10__metal")
        if gap is not None:
            onshape = rerun(actuator, folder, planet_bearing_gap=gap).items()
        return {n: float(x) for n, x in onshape}, actuator

    base, act = run(None, tmp_path / "a")
    more, more_act = run(21.0, tmp_path / "b")
    assert act.torque_carried_fraction == 1.0 and more_act.torque_carried_fraction < 1.0
    assert more["fw_s_calc"] < base["fw_s_calc"]
    assert {"planet_bearing_width", "planet_bearing_gap"} <= set(BY_NAME["fw_s_calc"]["depends_on"])
    changed = {k for k in base if base[k] != more[k]}
    assert {"fw_s_calc", "fw_p_b", "fw_r"} <= changed <= downstream_of(GB, "planet_bearing_gap")
