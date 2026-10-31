"""ISSPG-only variable checks (compact and inside variants): the shared rules reach ISSPG's names, the
stress-rule face widths follow what they depend on including the stator-height cap, and the planet-bearing
gap moved to the config drives exactly its CAD variables. The checks every gearbox gets are in
test_variable_categories.py."""
import pytest

from variable_helpers import GEARBOXES, SPECS, downstream_of, equation_lines, golden_design, write_design

TYPES = tuple(gb for gb in ("isspg_compact", "isspg_inside") if gb in SPECS)
FOLDER = "ISSPG"
UNCAPPED = ("RO100", (24, 54, 132, 1.2, 3))      # widths 9.9 mm: above the planet-bearing minimum, under the stator-height cap


def by_name(gb):
    return {e["name"]: e for e in SPECS[gb]["cad_variables"]}


def design(monkeypatch, tmp_path, gb, name=None):
    if name is None:
        motor, gears = UNCAPPED
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
def test_shared_rules_reach_isspg(gb):
    spec = by_name(gb)
    assert (spec["Nr"]["category"], spec["Nr"]["subtype"]) == ("dependent", "implicit constraint")
    for n in ("fw_s_calc", "fw_p", "fw_r"):
        assert (spec[n]["category"], spec[n]["subtype"]) == ("dependent", "stress rule"), n
    for n in ("motor_OD", "motor_height", "stator_height", "rotor_ID"):
        assert (spec[n]["category"], spec[n]["subtype"]) == ("input", "motor"), n
    for n in ("clearance_motor_and_case", "wire_slot_length", "wire_slot_radius"):    # config values here, not computed / read from the motor
        assert spec[n]["category"] == "fixed", n


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
    """Doubling FOS, the service factor or the motor torque, or halving the allowable stress, doubles the stress
    widths on a design above the planet-bearing minimum and under the stator-height cap (module 1.2); the three
    widths are one value and nothing outside the downstream chain changes."""
    def run(folder, change):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, gb)
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
    more, more_act = run(tmp_path / "b", True)
    assert act.torque_carried_fraction == more_act.torque_carried_fraction == 1.0                     # under the cap, before and after
    assert base["fw_p"] > 2 * act.planet_bearing_width + act.planet_bearing_gap                       # not raised
    for fw in ("fw_s_calc", "fw_p", "fw_r"):
        assert more[fw] == pytest.approx(2 * base[fw], rel=1e-12), fw
    changed = {k for k in base if base[k] != more[k]}
    assert {"fw_s_calc", "fw_p", "fw_r", "fw_s_used"} <= changed <= downstream_of(gb, what)


@pytest.mark.parametrize("gb", TYPES)
def test_stator_height_cap_comes_from_the_config(monkeypatch, tmp_path, gb):
    """gear_axial_margin_mm (config) is the margin below the stator height that the gears must fit: on a 3d-printed
    design that hits the cap, the ring width equals stator_height - margin, and shrinking the margin from 10 to 5 mm
    lengthens the gears by 5 mm and changes exactly the CAD variables downstream of it."""
    def run(margin, folder):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, gb, f"{gb}__RO100__6.5")
        if margin is not None:
            onshape = rerun(actuator, folder, gb, gear_axial_margin_mm=margin).items()
        return {n: float(x) for n, x in onshape}, actuator

    base, act = run(None, tmp_path / "a")
    more, more_act = run(5.0, tmp_path / "b")
    stator = act.motor.stator_height
    assert act.torque_carried_fraction < 1.0 and more_act.torque_carried_fraction < 1.0              # capped both times
    assert base["fw_r"] == pytest.approx(stator - 10.0) and more["fw_r"] == pytest.approx(stator - 5.0)
    changed = {k for k in base if base[k] != more[k]}
    assert {"fw_s_calc", "fw_p", "fw_r", "fw_s_used"} <= changed <= downstream_of(gb, "gear_axial_margin_mm")


@pytest.mark.parametrize("gb", TYPES)
def test_planet_bearing_gap_comes_from_the_config(monkeypatch, tmp_path, gb):
    """planet_bearing_gap (config) sets the smallest planet and ring width: two bearings and the gap. On the metal
    golden design the gears are 10.0 mm wide; a 12 mm gap (minimum 2 x 3.5 + 12 = 19 mm) raises the planet and the
    ring to 19.0, leaves fw_s_calc alone and changes nothing outside the downstream chain."""
    def run(gap, folder):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, gb, f"{gb}__RO100__6.5__metal")
        if gap is not None:
            onshape = rerun(actuator, folder, gb, planet_bearing_gap=gap).items()
        return {n: float(x) for n, x in onshape}

    base, more = run(None, tmp_path / "a"), run(12.0, tmp_path / "b")
    assert base["fw_p"] == base["fw_r"] < 19.0 and base["fw_p"] >= 8.0                               # below the new minimum
    assert more["fw_p"] == more["fw_r"] == 19.0 and more["fw_s_calc"] == base["fw_s_calc"]
    changed = {k for k in base if base[k] != more[k]}
    assert {"fw_p", "fw_r", "fw_s_used"} <= changed <= downstream_of(gb, "planet_bearing_gap")
