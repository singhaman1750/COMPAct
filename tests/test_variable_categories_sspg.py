"""SSPG-only variable checks: its config keys drive exactly the CAD variables they should, the
stress-rule face widths follow what they depend on, and the shared rules reach SSPG's names.
The checks every gearbox gets are in test_variable_categories.py."""
import json

import pytest

from variable_helpers import BASELINE_DIR, GEARBOXES, SPECS, equation_lines, golden_design, write_design

CAD = SPECS["sspg"]["cad_variables"]
GOLDEN = GEARBOXES["sspg"].golden()


def write_files(monkeypatch, folder, motor, material, Ns, Np, Nr, module, num_planet):
    return write_design(monkeypatch, folder, "sspg", motor, material, (Ns, Np, Nr, module, num_planet))


def test_shared_rules_reach_sspg():
    assert {"Nr", "fw_s_calc", "fw_p", "fw_r"} <= {e["name"] for e in CAD}


def test_optimisation_variables_are_the_gearbox_values(monkeypatch, tmp_path):
    _, motor, material, gears, _ = golden_design(GOLDEN[0])
    actuator, _, _, onshape = write_design(monkeypatch, tmp_path, "sspg", motor, material, gears)
    vals = {n: float(v) for n, v in onshape}
    gb = actuator.planetaryGearbox
    assert (vals["Ns"], vals["Np"], vals["module"], vals["num_planet"]) == (gb.Ns, gb.Np, gb.module, gb.numPlanet)
    assert (vals["fw_s_calc"], vals["fw_p"], vals["fw_r"]) == pytest.approx((gb.fwSunMM, gb.fwPlanetMM, gb.fwRingMM))


def test_motor_case_clearance_comes_from_the_config(monkeypatch, tmp_path):
    """clearance_motor_and_case_min (config) drives both the CAD value and the case mass: raising it
    changes clearance_motor_and_case and exactly the CAD variables that depend on it, and the mass."""
    b = json.loads((BASELINE_DIR / "sspg__U8_Lite__6.5.json").read_text(encoding="utf-8"))
    _, n, Ns, Np, Nr, module = b["opt_parameters"]

    def run(clearance_min, folder):
        actuator, _, _, onshape = write_files(monkeypatch, folder, "U8_Lite", "3dp", Ns, Np, Nr, module, n)
        if clearance_min is not None:
            actuator.design_params["clearance_motor_and_case_min"] = clearance_min
            actuator.setVariables()
            actuator.genEquationFile_editCADdirectly()
            onshape = equation_lines((folder / "SSPG" / "sspg_equations_onshape.txt").read_text())
        return dict((k, float(v)) for k, v in onshape), actuator.getMassKG_3DP()

    (tmp_path / "a").mkdir(), (tmp_path / "b").mkdir()
    base, base_mass = run(None, tmp_path / "a")
    more, more_mass = run(7, tmp_path / "b")
    assert base["clearance_motor_and_case"] == 5 and more["clearance_motor_and_case"] == 7   # ring gear < motor here
    downstream = {"clearance_motor_and_case"}
    for e in CAD:                                     # everything that depends on it, directly or not
        if set(e.get("depends_on", [])) & downstream:
            downstream.add(e["name"])
    assert {k for k in base if base[k] != more[k]} == downstream
    assert more_mass > base_mass


def test_case_mounting_hole_overlap_comes_from_the_config(monkeypatch, tmp_path):
    """case_mounting_hole_wall_overlap (config) sets case_mounting_hole_shift: raising it by 0.5 lowers
    the shift by 0.5 and changes exactly the CAD variables downstream of it; the mass doesn't use it."""
    b = json.loads((BASELINE_DIR / "sspg__U8_Lite__6.5.json").read_text(encoding="utf-8"))
    _, n, Ns, Np, Nr, module = b["opt_parameters"]

    def run(overlap, folder):
        folder.mkdir()
        actuator, _, _, onshape = write_files(monkeypatch, folder, "U8_Lite", "3dp", Ns, Np, Nr, module, n)
        if overlap is not None:
            actuator.design_params["case_mounting_hole_wall_overlap"] = overlap
            actuator.setVariables()
            actuator.genEquationFile_editCADdirectly()
            onshape = equation_lines((folder / "SSPG" / "sspg_equations_onshape.txt").read_text())
        return dict((k, float(v)) for k, v in onshape), actuator.getMassKG_3DP()

    base, base_mass = run(None, tmp_path / "a")
    more, more_mass = run(1.0, tmp_path / "b")
    assert more["case_mounting_hole_shift"] == pytest.approx(base["case_mounting_hole_shift"] - 0.5)
    downstream = {"case_mounting_hole_shift"}
    for e in CAD:
        if set(e.get("depends_on", [])) & downstream:
            downstream.add(e["name"])
    assert downstream == {"case_mounting_hole_shift", "case_mounting_PCD", "Motor_case_OD_max"}
    assert {k for k in base if base[k] != more[k]} == downstream
    assert more_mass == base_mass


def test_bearing_mount_wall_multiple_comes_from_the_config(monkeypatch, tmp_path):
    """bearing_mount_wall_bolt_dia_multiple (config) drives both the CAD value and the mass. On a
    design where the bearing plus its bolts is wider than the ring gear, raising it from 2 to 3 turns
    the wall from 2 to 3 output-bolt diameters and changes exactly the CAD variables downstream of it."""
    for name in GOLDEN:   # a design in the first branch of the rule
        b = json.loads((BASELINE_DIR / f"{name}.json").read_text(encoding="utf-8"))
        if b.get("material", "3dp") != "3dp":
            continue
        _, n, Ns, Np, Nr, module = b["opt_parameters"]
        (tmp_path / name).mkdir()
        actuator, *_ = write_files(monkeypatch, tmp_path / name, b["motor"], "3dp", Ns, Np, Nr, module, n)
        if actuator.bearing_mount_thickness == actuator.output_mounting_hole_dia * 2:
            break
    else:
        pytest.fail("no golden SSPG design in the first branch of the bearing-mount rule")

    def run(multiple, folder):
        folder.mkdir()
        actuator, _, _, onshape = write_files(monkeypatch, folder, b["motor"], "3dp", Ns, Np, Nr, module, n)
        if multiple is not None:
            actuator.design_params["bearing_mount_wall_bolt_dia_multiple"] = multiple
            actuator.setVariables()
            actuator.genEquationFile_editCADdirectly()
            onshape = equation_lines((folder / "SSPG" / "sspg_equations_onshape.txt").read_text())
        return dict((k, float(v)) for k, v in onshape), actuator.getMassKG_3DP()

    base, base_mass = run(None, tmp_path / "a")
    more, more_mass = run(3, tmp_path / "b")
    d = base["output_mounting_hole_dia"]
    assert (base["bearing_mount_thickness"], more["bearing_mount_thickness"]) == (2 * d, 3 * d)
    downstream = {"bearing_mount_thickness"}
    for e in CAD:
        if set(e.get("depends_on", [])) & downstream:
            downstream.add(e["name"])
    assert downstream == {"bearing_mount_thickness", "output_mounting_PCD"}
    assert {k for k in base if base[k] != more[k]} == downstream
    assert more_mass > base_mass


@pytest.mark.parametrize("what", ["FOS", "serviceFactor", "motor_peak_torque", "gear_allowable_stress"])
def test_stress_rule_widths_follow_what_they_depend_on(monkeypatch, tmp_path, what):
    """The face widths have no closed formula in the spec (the contact ratio is involved), so their
    dependencies are checked by changing them: doubling FOS, the service factor or the motor torque,
    or halving the allowable stress, doubles the stress width b. fw_s_calc = b doubles; fw_p and
    fw_r = max(b, planet-bearing minimum) double when above the minimum. Nothing outside the
    downstream chain changes."""
    b = json.loads((BASELINE_DIR / "sspg__U8_Lite__6.5.json").read_text(encoding="utf-8"))
    _, n, Ns, Np, Nr, module = b["opt_parameters"]

    def run(folder, change):
        folder.mkdir()
        actuator, _, _, onshape = write_files(monkeypatch, folder, "U8_Lite", "3dp", Ns, Np, Nr, module, n)
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
            onshape = equation_lines((folder / "SSPG" / "sspg_equations_onshape.txt").read_text())
        return dict((k, float(v)) for k, v in onshape), actuator

    base, act = run(tmp_path / "a", False)
    more, _ = run(tmp_path / "b", True)
    assert more["fw_s_calc"] == pytest.approx(2 * base["fw_s_calc"], rel=1e-12)
    minimum = 2 * act.planet_bearing_width + act.planet_bearing_gap
    for fw in ("fw_p", "fw_r"):
        assert more[fw] == pytest.approx(max(2 * base["fw_s_calc"], minimum), rel=1e-12)
    downstream = {what}
    for e in CAD:
        if set(e.get("depends_on", [])) & downstream:
            downstream.add(e["name"])
    changed = {k for k in base if base[k] != more[k]}
    assert "fw_s_calc" in changed and changed <= downstream


def test_planet_bearing_gap_comes_from_the_config(monkeypatch, tmp_path):
    """planet_bearing_gap (config) sets the smallest planet / ring face width. On a design at that
    minimum (U8_Lite 6.5 in metal: 2 x 3.5 + 1.0 = 8.0 mm; the steel stress width is only ~1.7 mm), a 3.0 mm gap makes fw_p = fw_r = 10.0, leaves the
    stress width fw_s_calc alone and changes nothing outside the downstream chain."""
    b = json.loads((BASELINE_DIR / "sspg__U8_Lite__6.5__metal.json").read_text(encoding="utf-8"))
    _, n, Ns, Np, Nr, module = b["opt_parameters"]

    def run(gap, folder):
        folder.mkdir()
        actuator, _, _, onshape = write_files(monkeypatch, folder, "U8_Lite", "metal", Ns, Np, Nr, module, n)
        if gap is not None:
            actuator.design_params["planet_bearing_gap"] = gap
            actuator.setVariables()
            actuator.updateFacewidth()
            actuator.genEquationFile_editCADdirectly()
            onshape = equation_lines((folder / "SSPG" / "sspg_equations_onshape.txt").read_text())
        return dict((k, float(v)) for k, v in onshape)

    base, more = run(None, tmp_path / "a"), run(3.0, tmp_path / "b")
    assert base["fw_p"] == base["fw_r"] == 8.0 and base["fw_s_calc"] < 8.0      # at the bearing minimum
    assert more["fw_p"] == more["fw_r"] == 10.0 and more["fw_s_calc"] == base["fw_s_calc"]
    downstream = {"planet_bearing_gap"}
    for e in CAD:
        if set(e.get("depends_on", [])) & downstream:
            downstream.add(e["name"])
    changed = {k for k in base if base[k] != more[k]}
    assert {"fw_p", "fw_r", "fw_s_used"} <= changed <= downstream
