"""DSPG-only variable checks: the shared rules reach the stage-prefixed names, the 79 alias names
equal and are classified like the name they repeat, the two stage files are the same values under
stage-local names, the stress-rule face widths follow what they depend on, and every number moved
to the config drives exactly its CAD variables (and the mass where it should). The checks every
gearbox gets are in test_variable_categories.py."""
import pytest

from variable_helpers import GEARBOXES, SPECS, downstream_of, equation_lines, golden_design, write_design

SPEC = SPECS["dspg"]
CAD = SPEC["cad_variables"]
BY_NAME = {e["name"]: e for e in CAD}
FOLDER = "DSPG"
ONSHAPE = "dspg_equations_onshape.txt"


def design(monkeypatch, tmp_path, name):
    _, motor, material, gears, _ = golden_design(name)
    return write_design(monkeypatch, tmp_path, "dspg", motor, material, gears)


def rerun(actuator, folder, **params):
    """Change config values on a built actuator, redo its variables and face widths, and return its
    Onshape file as name -> value."""
    actuator.design_params.update(params)
    actuator.setVariables()
    actuator.updateFacewidth()
    actuator.setVariables()
    actuator.genEquationFile_editCADdirectly()
    return {n: float(x) for n, x in equation_lines((folder / FOLDER / ONSHAPE).read_text())}


def test_shared_rules_reach_dspg():
    for n in ("a1_Nr", "a1_Nr2", "a2_Nr", "a2_Nr1"):
        assert (BY_NAME[n]["category"], BY_NAME[n]["subtype"]) == ("dependent", "implicit constraint"), n
    for n in ("a1_fw_s_calc", "a1_fw_r", "a1_fw_s_calc2", "a2_fw_s_calc", "a2_fw_r"):
        assert (BY_NAME[n]["category"], BY_NAME[n]["subtype"]) == ("dependent", "stress rule"), n
    for n in ("a1_fw_p", "a2_fw_p", "a1_fw_p2"):            # copies of the ring width
        assert (BY_NAME[n]["category"], BY_NAME[n]["subtype"]) == ("dependent", "formula"), n


@pytest.mark.parametrize("name", GEARBOXES["dspg"].golden())
def test_alias_names_equal_the_name_they_repeat(monkeypatch, tmp_path, name):
    """79 names are written twice (a1_X and a2_X1, a1_X2 and a2_X, or a1_X and a2_X): the second is
    'alias_of' the first, has the same value in the file and the same classification."""
    _, _, _, onshape = design(monkeypatch, tmp_path, name)
    v = {n: x for n, x in onshape}
    aliases = [e for e in CAD if "alias_of" in e]
    assert len(aliases) == 79
    for e in aliases:
        first = BY_NAME[e["alias_of"]]
        assert "alias_of" not in first, e["name"]                              # one level: an alias repeats a first name
        assert v[e["name"]] == v[first["name"]], e["name"]                    # the same text, not only the same number
        for k in ("attr", "category", "subtype", "confidence", "source", "formula", "lookup", "rule", "depends_on"):
            assert e.get(k) == first.get(k), (e["name"], k)


@pytest.mark.parametrize("name", GEARBOXES["dspg"].golden())
def test_stage_files_are_the_onshape_values_under_local_names(monkeypatch, tmp_path, name):
    """dspg_equations_stg1.txt / _stg2.txt carry the Onshape values without the stage prefix (some with
    spaces instead of underscores); helpers write them as a1_<name> / a2_<name>."""
    _, _, plain, onshape = design(monkeypatch, tmp_path, name)
    on = dict(onshape)
    aliases = SPEC["plain_file_aliases"]
    assert len(plain) == 257 and {aliases.get(n, n) for n, _ in plain} == set(on)
    for n, v in plain:
        assert v == on[aliases.get(n, n)], n


def test_optimisation_variables_are_the_gearbox_values(monkeypatch, tmp_path):
    actuator, _, _, onshape = design(monkeypatch, tmp_path, GEARBOXES["dspg"].golden()[0])
    v = {n: float(x) for n, x in onshape}
    gb = actuator.doubleStagePlanetaryGearbox
    for p, stage in (("a1_", gb.Stage1), ("a2_", gb.Stage2)):
        assert (v[p + "Ns"], v[p + "Np"], v[p + "num_planet"], v[p + "module"]) == \
            (stage.Ns, stage.Np, stage.numPlanet, stage.module)
        assert v[p + "Nr"] == stage.Ns + 2 * stage.Np                          # the implicit ring constraint
        assert (v[p + "fw_s_calc"], v[p + "fw_r"], v[p + "fw_p"]) == \
            pytest.approx((stage.fwSunMM, stage.fwRingMM, stage.fwRingMM))


@pytest.mark.parametrize("what", ["FOS", "serviceFactor", "motor_peak_torque", "gear_allowable_stress"])
def test_stress_rule_widths_follow_what_they_depend_on(monkeypatch, tmp_path, what):
    """The face widths have no closed formula in the spec, so their dependencies are checked by changing
    them: doubling FOS, the service factor or the motor torque, or halving the allowable stress, doubles
    both stages' stress widths. On a design whose planets are above the planet-bearing minimum in both
    stages, every sun / ring width doubles, the planet copy follows, and nothing outside the downstream
    chain changes."""
    name = "dspg__VT8020_PRO__20"

    def run(folder, change):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, name)
        if change:
            if what == "FOS":
                actuator.FOS *= 2
            elif what == "serviceFactor":
                actuator.serviceFactor *= 2
            elif what == "motor_peak_torque":
                actuator.motor.maxMotorTorque *= 2
            else:
                for stage in (actuator.doubleStagePlanetaryGearbox.Stage1, actuator.doubleStagePlanetaryGearbox.Stage2):
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
    assert {"a1_fw_s_calc", "a1_fw_r", "a1_fw_p", "a2_fw_r", "a2_fw_p", "a1_fw_s_used", "a2_fw_s_used"} <= changed
    assert changed <= downstream_of("dspg", what)


def test_motor_case_clearance_comes_from_the_config(monkeypatch, tmp_path):
    """clearance_motor_and_case_min (config) drives both the CAD value (stage 1; stage 2 writes the same
    case) and the case mass: raising it from 5 to 7 on a design whose ring is narrower than the motor
    changes clearance_motor_and_case and exactly the CAD variables downstream of it, and the mass."""
    def run(minimum, folder):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, "dspg__U8_Lite__20")
        if minimum is not None:
            onshape = rerun(actuator, folder, clearance_motor_and_case_min=minimum).items()
        return {n: float(x) for n, x in onshape}, actuator.getMassKG_3DP()

    base, base_mass = run(None, tmp_path / "a")
    more, more_mass = run(7, tmp_path / "b")
    assert base["a1_clearance_motor_and_case"] == 5 and more["a1_clearance_motor_and_case"] == 7   # ring < motor here
    changed = {k for k in base if base[k] != more[k]}
    assert changed == downstream_of("dspg", "clearance_motor_and_case_min") & set(base)
    assert {"a1_clearance_motor_and_case", "a2_clearance_motor_and_case", "a1_Motor_case_ID", "a1_motor_case_OD_base",
            "a1_case_mounting_PCD", "a1_Motor_case_OD_max"} <= changed
    assert more_mass > base_mass


def test_case_mounting_hole_overlap_comes_from_the_config(monkeypatch, tmp_path):
    """case_mounting_hole_wall_overlap (config) sets case_mounting_hole_shift: raising it by 0.5 lowers the
    shift by 0.5 and changes exactly the CAD variables downstream of it; the mass doesn't use it."""
    def run(overlap, folder):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, "dspg__U8_Lite__20")
        if overlap is not None:
            onshape = rerun(actuator, folder, case_mounting_hole_wall_overlap=overlap).items()
        return {n: float(x) for n, x in onshape}, actuator.getMassKG_3DP()

    base, base_mass = run(None, tmp_path / "a")
    more, more_mass = run(1.0, tmp_path / "b")
    assert more["a1_case_mounting_hole_shift"] == pytest.approx(base["a1_case_mounting_hole_shift"] - 0.5)
    changed = {k for k in base if base[k] != more[k]}
    assert changed == downstream_of("dspg", "case_mounting_hole_wall_overlap") & set(base)
    assert {"a1_case_mounting_hole_shift", "a2_case_mounting_hole_shift", "a1_case_mounting_PCD", "a1_Motor_case_OD_max"} <= changed
    assert more_mass == base_mass


def test_bearing_mount_wall_multiple_comes_from_the_config(monkeypatch, tmp_path):
    """bearing_mount_wall_bolt_dia_multiple (config) drives both stages' CAD value and the mass. On a design
    where each stage's bearing plus its bolts is wider than the ring gear, raising it from 2 to 3 turns the
    wall from 2 to 3 output-bolt diameters in both stages and changes exactly the CAD variables downstream."""
    def run(multiple, folder):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, "dspg__VT8020_PRO__20")
        if multiple is not None:
            onshape = rerun(actuator, folder, bearing_mount_wall_bolt_dia_multiple=multiple).items()
        return {n: float(x) for n, x in onshape}, actuator.getMassKG_3DP()

    base, base_mass = run(None, tmp_path / "a")
    more, more_mass = run(3, tmp_path / "b")
    for p in ("a1_", "a2_"):
        d = base[p + "output_mounting_hole_dia"]
        assert (base[p + "bearing_mount_thickness"], more[p + "bearing_mount_thickness"]) == (2 * d, 3 * d), p
    changed = {k for k in base if base[k] != more[k]}
    assert changed == downstream_of("dspg", "bearing_mount_wall_bolt_dia_multiple") & set(base)
    assert {"a1_bearing_mount_thickness", "a2_bearing_mount_thickness", "a1_output_mounting_PCD",
            "a2_output_mounting_PCD", "a1_stg1_stg2_mounting_extra_width"} <= changed
    assert more_mass > base_mass


def test_planet_bearing_gap_comes_from_the_config(monkeypatch, tmp_path):
    """planet_bearing_gap (config) sets the smallest planet and ring widths of both stages: two bearings
    and the gap. On the metal golden design both stages' rings sit at that minimum (2 x 3.5 + 1.0 = 8.0 mm);
    a 3.0 mm gap makes every ring and planet width 10.0, leaves the sun widths alone and changes nothing
    outside the downstream chain."""
    def run(gap, folder):
        folder.mkdir()
        actuator, _, _, onshape = design(monkeypatch, folder, "dspg__U8_Lite__20__metal")
        if gap is not None:
            onshape = rerun(actuator, folder, planet_bearing_gap=gap).items()
        return {n: float(x) for n, x in onshape}

    base, more = run(None, tmp_path / "a"), run(3.0, tmp_path / "b")
    assert base["a1_fw_r"] == base["a1_fw_p"] == base["a2_fw_r"] == base["a2_fw_p"] == 8.0
    assert max(base["a1_fw_s_calc"], base["a2_fw_s_calc"]) < 8.0                          # at the bearing minimum
    assert more["a1_fw_r"] == more["a1_fw_p"] == more["a2_fw_r"] == more["a2_fw_p"] == 10.0
    assert (more["a1_fw_s_calc"], more["a2_fw_s_calc"]) == (base["a1_fw_s_calc"], base["a2_fw_s_calc"])
    changed = {k for k in base if base[k] != more[k]}
    assert {"a1_fw_r", "a1_fw_p", "a2_fw_r", "a2_fw_p", "a1_fw_s_used", "a2_fw_s_used"} <= changed
    assert changed <= downstream_of("dspg", "planet_bearing_gap")
