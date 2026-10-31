"""INWPG-only variable checks (dependent and independent variants): the shared rules reach INWPG's names
(fw_p_b is a copy of fw_r_b here, the reverse of WPG), the stress-rule face widths follow what they depend on
including the planet-stack cap, the planet-bearing gap moved to the config drives exactly its CAD variables, and
the per-motor rotor bearing values come from the params file. The checks every gearbox gets are in
test_variable_categories.py."""
import pytest

from variable_helpers import GEARBOXES, SPECS, downstream_of, equation_lines, golden_design, write_design

TYPES = tuple(gb for gb in ("inwpg_dependent", "inwpg_independent") if gb in SPECS)
FOLDER = "INWPG"


def by_name(gb):
    return {e["name"]: e for e in SPECS[gb]["cad_variables"]}


def design(monkeypatch, tmp_path, gb, name):
    if name.startswith("extra"):
        motor, gears = GEARBOXES[gb].extra[int(name[5:])]
        return write_design(monkeypatch, tmp_path, gb, motor, "3dp", gears)
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
def test_shared_rules_reach_inwpg(gb):
    spec = by_name(gb)
    for n in ("Nr_b", "Nr_s"):
        assert (spec[n]["category"], spec[n]["subtype"]) == ("dependent", "implicit constraint"), n
    for n in ("fw_s_calc", "fw_r_b", "fw_r_s"):
        assert (spec[n]["category"], spec[n]["subtype"]) == ("dependent", "stress rule"), n
    for n in ("fw_p_b", "fw_p_s"):     # fw_p_b = fw_r_b (excepted from the shared rule, which is WPG's), fw_p_s = fw_r_s + clearance_planet
        assert (spec[n]["category"], spec[n]["subtype"]) == ("dependent", "formula"), n
    assert spec["fw_p_b"]["formula"] == "fw_r_b"


@pytest.mark.parametrize("gb", TYPES)
def test_optimisation_variables_are_the_gearbox_values(monkeypatch, tmp_path, gb):
    actuator, _, _, onshape = design(monkeypatch, tmp_path, gb, GEARBOXES[gb].golden()[0])
    v = {n: float(x) for n, x in onshape}
    g = actuator.inrunnerWolfromPlanetaryGearbox
    assert (v["Ns"], v["Np_b"], v["Np_s"], v["num_planet"], v["module"]) == (g.Ns, g.NpBig, g.NpSmall, g.numPlanet, g.moduleBig)
    assert (v["Nr_b"], v["Nr_s"]) == (g.Ns + 2 * g.NpBig, g.Ns + g.NpBig + g.NpSmall)         # the implicit ring constraints
    module_s = next(e for e in SPECS[gb]["code_only"] if e["name"] == "module_s")        # the small module: searched, not in the CAD
    assert (module_s["category"], module_s["attr"]) == ("optimisation", "module_s") and actuator.module_s == g.moduleSmall > 0
    assert (v["fw_s_calc"], v["fw_r_b"], v["fw_r_s"]) == pytest.approx((g.fwSunMM, g.fwRingBigMM, g.fwRingSmallMM))
    assert v["fw_p_b"] == v["fw_r_b"] and v["fw_p_s"] == pytest.approx(v["fw_r_s"] + v["clearance_planet"])


@pytest.mark.parametrize("what", ["FOS", "serviceFactor", "motor_peak_torque", "gear_allowable_stress"])
@pytest.mark.parametrize("gb", TYPES)
def test_stress_rule_widths_follow_what_they_depend_on(monkeypatch, tmp_path, gb, what):
    """Doubling FOS, the service factor or the motor torque, or halving the allowable stress, doubles the stress
    widths on a design whose planets are above the planet-bearing minimum and whose planet stack stays under the
    cap (module 1.2): the sun, big-ring and small-ring widths double, the copies follow."""
    def run(folder, change):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, gb, "extra0")
        if change:
            if what == "FOS":
                actuator.FOS *= 2
            elif what == "serviceFactor":
                actuator.serviceFactor *= 2
            elif what == "motor_peak_torque":
                actuator.motor.maxMotorTorque *= 2
            else:
                actuator.inrunnerWolfromPlanetaryGearbox.maxGearAllowableStressPa /= 2
            actuator.updateFacewidth()
            actuator.genEquationFile_editCADdirectly()
            onshape = equation_lines((folder / FOLDER / f"{gb}_equations_onshape.txt").read_text())
        return {n: float(x) for n, x in onshape}, actuator

    base, act = run(tmp_path / "a", False)
    more, more_act = run(tmp_path / "b", True)
    assert act.torque_carried_fraction == more_act.torque_carried_fraction == 1.0                  # under the cap, before and after
    assert min(base["fw_r_b"], base["fw_r_s"]) > act.planet_bearing_width + act.planet_bearing_gap / 2   # not raised
    for fw in ("fw_s_calc", "fw_r_b", "fw_r_s"):
        assert more[fw] == pytest.approx(2 * base[fw], rel=1e-12), fw
    assert more["fw_p_b"] == more["fw_r_b"] and more["fw_p_s"] == pytest.approx(more["fw_r_s"] + more["clearance_planet"])
    changed = {k for k in base if base[k] != more[k]}
    assert {"fw_s_calc", "fw_r_b", "fw_p_b", "fw_r_s", "fw_p_s", "fw_s_used"} <= changed <= downstream_of(gb, what)


@pytest.mark.parametrize("gb", TYPES)
def test_planet_stack_cap_comes_from_the_config(monkeypatch, tmp_path, gb):
    """planet_stack_stator_heights (config) caps the planet stack (big ring + small ring + clearance_planet) at that
    many stator heights: on a 3d-printed design that hits the cap, the stack equals the cap, and raising it from 2 to
    2.4 stator heights lengthens the gears, changing exactly the CAD variables downstream of it."""
    def run(heights, folder):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, gb, f"{gb}__RI100__20")
        if heights is not None:
            onshape = rerun(actuator, folder, gb, planet_stack_stator_heights=heights).items()
        return {n: float(x) for n, x in onshape}, actuator

    base, act = run(None, tmp_path / "a")
    more, more_act = run(2.4, tmp_path / "b")
    stator = act.motor.stator_height
    assert act.torque_carried_fraction < 1.0 and more_act.torque_carried_fraction < 1.0                 # capped both times
    assert base["fw_r_b"] + base["fw_r_s"] + base["clearance_planet"] == pytest.approx(2.0 * stator)
    assert more["fw_r_b"] + more["fw_r_s"] + more["clearance_planet"] == pytest.approx(2.4 * stator)
    changed = {k for k in base if base[k] != more[k]}
    assert {"fw_s_calc", "fw_r_b", "fw_p_b", "fw_r_s", "fw_p_s", "fw_s_used"} <= changed <= downstream_of(gb, "planet_stack_stator_heights")


@pytest.mark.parametrize("gb", TYPES)
def test_planet_bearing_gap_comes_from_the_config(monkeypatch, tmp_path, gb):
    """planet_bearing_gap (config) sets the smallest planet widths: the two planets hold two bearings and the gap,
    each gear at least one bearing and half the gap. On the metal golden design the rings sum to 15.8 mm; a 20 mm gap
    (minimum 27 mm, each at least 3.5 + 10 = 13.5 mm) raises both rings to 13.5, so fw_p_s = 13.5 + 1.5 = 15.0;
    fw_s_calc is unchanged and nothing outside the downstream chain changes."""
    def run(gap, folder):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, gb, f"{gb}__RI100__20__metal")
        if gap is not None:
            onshape = rerun(actuator, folder, gb, planet_bearing_gap=gap).items()
        return {n: float(x) for n, x in onshape}

    base, more = run(None, tmp_path / "a"), run(20.0, tmp_path / "b")
    assert base["fw_r_b"] + base["fw_r_s"] < 27.0 and base["fw_r_b"] < 13.5 and base["fw_r_s"] < 13.5      # below the new minimum
    assert more["fw_r_b"] == more["fw_p_b"] == more["fw_r_s"] == 13.5 and more["fw_p_s"] == 13.5 + more["clearance_planet"]
    assert more["fw_s_calc"] == base["fw_s_calc"]
    changed = {k for k in base if base[k] != more[k]}
    assert {"fw_r_b", "fw_p_b", "fw_r_s", "fw_p_s", "fw_s_used"} <= changed <= downstream_of(gb, "planet_bearing_gap")


def test_motor_minimum_for_the_rotor_top_bearing_comes_from_the_config(monkeypatch, tmp_path):
    """min_rotor_top_bearing_ID (one value per motor) is the smallest bore of the dependent variant's rotor top
    bearing: raising RI100's from 25 to 45 mm changes the top bearing and exactly the CAD variables downstream."""
    gb = "inwpg_dependent"

    def run(minimum, folder):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, gb, f"{gb}__RI100__20")
        if minimum is not None:
            actuator.design_params["min_rotor_top_bearing_ID"] = {"RI100": minimum, "RI80": 0}
            onshape = rerun(actuator, folder, gb).items()
        return {n: float(x) for n, x in onshape}

    base, more = run(None, tmp_path / "a"), run(45, tmp_path / "b")
    assert more["rotor_top_bearing_ID"] > base["rotor_top_bearing_ID"] >= 25
    changed = {k for k in base if base[k] != more[k]}
    assert "rotor_top_bearing_ID" in changed and changed <= downstream_of(gb, "min_rotor_top_bearing_ID")


@pytest.mark.skipif("inwpg_independent" not in SPECS, reason="needs the independent spec")
def test_rotor_top_bearing_of_the_independent_variant_comes_from_the_config(monkeypatch, tmp_path):
    """The independent variant takes the rotor top bearing from the params file, one value per motor (no catalogue
    lookup): giving RI100 RI80's bearing changes the three rotor_top_bearing values and exactly the CAD variables
    downstream of them (the sun hub, ...), and nothing else."""
    gb = "inwpg_independent"
    names = ("rotor_top_bearing_ID", "rotor_top_bearing_OD", "rotor_top_bearing_width")

    def run(swap, folder):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, gb, f"{gb}__RI100__20")
        if swap:
            for key in names:
                actuator.design_params[key] = {"RI100": actuator.design_params[key]["RI80"], "RI80": actuator.design_params[key]["RI80"]}
            onshape = rerun(actuator, folder, gb).items()
        return {n: float(x) for n, x in onshape}

    base, more = run(False, tmp_path / "a"), run(True, tmp_path / "b")
    assert [more[n] for n in names] != [base[n] for n in names]
    changed = {k for k in base if base[k] != more[k]}
    assert changed == downstream_of(gb, *names) & set(base)
    assert set(names) | {"sun_hub_dia"} <= changed
