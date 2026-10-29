"""Variable categories (config_files/variables/<gearbox>_variables.json): every variable a gearbox
writes to its CAD file is sorted into input / optimisation / fixed / dependent. These tests are the
number check: the lists must match what the code writes, one entry per variable, and every source,
formula and lookup in the spec must give the value the code gives.

Each design is built with gearbox_runner and its equation files are written to a temporary folder
(COMPACT_CAD_DIR), so CADs/ is never touched.
"""
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tests" / "golden"))

import gearbox_runner  # noqa: E402
from CommonComponents import bearings_discrete, nuts_and_bolts_dimensions  # noqa: E402
from golden import BASELINE_DIR  # noqa: E402
from tools.variables.render import CATEGORIES, load, load_rules, render  # noqa: E402

CONFIG = REPO / "config_files"
SPEC = load("sspg")
CAD = SPEC["cad_variables"]
CODE = SPEC["code_only"]
ALL = {e["name"]: e for e in CAD + CODE}

# Golden designs (their CAD files are in the baselines), plus made-up gear sets that reach the other
# branch of each two-case rule (ring gear wider than the motor, bearing narrower than the ring).
GOLDEN = sorted(p.stem for p in BASELINE_DIR.glob("sspg__*.json"))
EXTRA = [("U8_Lite", 20, 40, 1.2, 3), ("MAD_M6C12_KV170", 18, 30, 0.5, 3), ("VT8020_PRO", 30, 60, 1.0, 4)]


def equation_lines(text):
    return re.findall(r'^"(.+?)"\s*=\s*([-\d.eE+]+)', text, re.M)


def write_files(monkeypatch, tmp_path, motor, material, Ns, Np, Nr, module, num_planet):
    """Build the actuator for this gear set and write its two equation files; return the actuator,
    the optimisation settings and the two files' (name, value) lines."""
    monkeypatch.setenv("COMPACT_CAD_DIR", str(tmp_path))
    actuator, optimizer = gearbox_runner.build("sspg", motor, material)
    gb = actuator.planetaryGearbox
    gb.setNs(Ns), gb.setNp(Np), gb.setNr(Nr), gb.setModule(module), gb.setNumPlanet(num_planet)
    actuator.updateFacewidth()
    actuator.genEquationFile_editCADdirectly()
    plain = equation_lines((tmp_path / "SSPG" / "sspg_equations.txt").read_text())
    onshape = equation_lines((tmp_path / "SSPG" / "sspg_equations_onshape.txt").read_text())
    return actuator, optimizer, plain, onshape


@pytest.fixture(scope="module", params=GOLDEN + [f"extra{i}" for i in range(len(EXTRA))])
def design(request, tmp_path_factory):
    mp = pytest.MonkeyPatch()
    tmp = tmp_path_factory.mktemp("cad")
    try:
        if request.param.startswith("extra"):
            motor, Ns, Np, module, n = EXTRA[int(request.param[5:])]
            out = write_files(mp, tmp, motor, "3dp", Ns, Np, Ns + 2 * Np, module, n)
            baseline = None
        else:
            b = json.loads((BASELINE_DIR / f"{request.param}.json").read_text(encoding="utf-8"))
            _, n, Ns, Np, Nr, module = b["opt_parameters"]
            out = write_files(mp, tmp, b["motor"], b.get("material", "3dp"), Ns, Np, Nr, module, n)
            (baseline,) = [t for p, t in b["cad_files"].items() if p.endswith("sspg_equations_onshape.txt")]
    finally:
        mp.undo()
    return (request.param, baseline) + out


# ---- the lists ------------------------------------------------------------------------------------

def test_counts_and_one_category_each():
    names = [e["name"] for e in CAD]
    assert len(names) == 113 and len(set(names)) == 113
    assert len(CODE) == 27 and not set(names) & {e["name"] for e in CODE}
    assert Counter(e["category"] for e in CAD) == {"input": 18, "optimisation": 4, "fixed": 43, "dependent": 48}
    for e in CAD + CODE:
        assert e["category"] in CATEGORIES and e["confidence"] in SPEC["confidence"], e["name"]
        assert e["reason"], e["name"]


def test_spec_lists_exactly_the_variables_the_code_writes(design):
    _, baseline, _, _, plain, onshape = design
    assert [n for n, _ in onshape] == [e["name"] for e in CAD]          # same names, same order, 113
    aliases = SPEC["plain_file_aliases"]
    assert sorted({aliases.get(n, n) for n, _ in plain}) == sorted(e["name"] for e in CAD)
    assert len(plain) == len(onshape) + 1                                # "pressure angle" is written twice
    if baseline is not None:                                             # the golden design is reproduced
        expected = equation_lines(baseline)
        assert [n for n, _ in onshape] == [n for n, _ in expected]
        assert [float(v) for _, v in onshape] == pytest.approx([float(v) for _, v in expected], rel=1e-9)


def test_shared_rules_hold_in_every_gearbox_file():
    rules = load_rules()["rules"]
    files = sorted(CONFIG.glob("variables/*_variables.json"))
    assert files
    for path in files:
        spec = json.loads(path.read_text(encoding="utf-8"))
        for e in spec["cad_variables"] + spec["code_only"]:
            for r in rules:
                if re.match(r["name_pattern"], e["name"]):
                    assert (e["category"], e["subtype"]) == (r["category"], r["subtype"]), (path.name, e["name"])
    names = {e["name"] for e in CAD}
    assert {"Nr", "fw_s_calc", "fw_p", "fw_r"} <= names     # the rules do apply to SSPG


def test_every_dependency_is_classified():
    for e in CAD + CODE:
        missing = [d for d in e.get("depends_on", []) if d not in ALL]
        assert not missing, (e["name"], missing)
        if e["category"] == "dependent":
            assert e["depends_on"] and ("formula" in e or "lookup" in e or "rule" in e), e["name"]
        else:
            assert "source" in e, e["name"]


def test_every_config_key_is_accounted_for():
    params = json.loads((CONFIG / "sspg_params.json").read_text(encoding="utf-8"))
    used = {(s["block"], s["key"]) for e in CAD + CODE if (s := e.get("source", {})).get("file") == "sspg_params.json"}
    unused = {b["block"] for b in SPEC["unused_config_blocks"]}
    assert set(params) == unused | {b for b, _ in used}
    for block, keys in params.items():
        if block not in unused:
            assert {(block, k) for k in keys} <= used, sorted(set(keys) - {k for b, k in used if b == block})


# ---- the values -----------------------------------------------------------------------------------

def values(actuator, optimizer, onshape):
    """name -> value for every classified variable: CAD values from the file, code-only ones from the
    actuator (or its gearbox) and the optimisation settings."""
    vals = {n: float(v) for n, v in onshape}
    params = json.loads((CONFIG / "sspg_params.json").read_text(encoding="utf-8"))["sspg_optimization_parameters"]
    for e in CODE:
        if "attr" not in e:
            vals[e["name"]] = params[e["name"]]
        elif hasattr(actuator, e["attr"]):
            vals[e["name"]] = getattr(actuator, e["attr"])
        else:
            vals[e["name"]] = getattr(actuator.planetaryGearbox, e["attr"])
    return vals


def test_attr_matches_the_file(design):
    _, _, actuator, _, _, onshape = design
    for (name, v), e in zip(onshape, CAD):
        assert getattr(actuator, e["attr"]) == pytest.approx(float(v), rel=1e-9), name


def test_sources_give_the_values(design):
    _, _, actuator, optimizer, _, onshape = design
    vals = values(actuator, optimizer, onshape)
    config = json.loads((CONFIG / "config.json").read_text(encoding="utf-8"))
    params = json.loads((CONFIG / "sspg_params.json").read_text(encoding="utf-8"))
    motors = json.loads((CONFIG / "motors.json").read_text(encoding="utf-8"))
    material = "metal" if actuator.results_suffix else "3dp"
    names = {"<motor>": actuator.motor.motorName, "<gear material>": gearbox_runner.MATERIAL_MODES[material][0]}

    def lookup(data, block):
        for part in block.split("."):
            data = data[names.get(part, part)]
        return data
    for e in CAD + CODE:
        s = e.get("source", {})
        if s.get("file") == "sspg_params.json":
            expected = params[s["block"]][s["key"]]
        elif s.get("file") == "motors.json":
            expected = lookup(motors, s["block"])[s["key"]]
        elif s.get("file") == "config.json":
            expected = lookup(config, s["block"])[s["key"]]
        else:
            continue
        assert vals[e["name"]] == pytest.approx(expected, rel=1e-9), e["name"]
    gb = actuator.planetaryGearbox
    assert (vals["Ns"], vals["Np"], vals["module"], vals["num_planet"]) == (gb.Ns, gb.Np, gb.module, gb.numPlanet)
    assert (vals["fw_s_calc"], vals["fw_p"], vals["fw_r"]) == pytest.approx((gb.fwSunMM, gb.fwPlanetMM, gb.fwRingMM))


def test_formulas_and_lookups_give_the_values(design):
    _, _, actuator, optimizer, _, onshape = design
    vals = values(actuator, optimizer, onshape)
    env = {"cos": math.cos, "sqrt": math.sqrt, "pi": math.pi, "__builtins__": {}}
    for e in CAD + CODE:
        if "formula" in e:
            got = eval(e["formula"], env, dict(vals))
        elif "lookup" in e:
            lk = e["lookup"]
            args = {k: (eval(v, env, dict(vals)) if k != "bolt_type" else v) for k, v in lk["args"].items()}
            if lk["function"] == "bearings_discrete":
                got = getattr(bearings_discrete(args["idRequiredMM"]), lk["method"])()
            else:
                got = getattr(nuts_and_bolts_dimensions(**args), lk["field"])
        else:
            continue
        assert got == pytest.approx(vals[e["name"]], rel=1e-9, abs=1e-12), e["name"]


def test_both_branches_of_the_two_case_rules_are_checked():
    seen = {"ring wider than motor": set(), "bearing wider than ring": set()}
    mp = pytest.MonkeyPatch()
    designs = [json.loads((BASELINE_DIR / f"{n}.json").read_text(encoding="utf-8")) for n in GOLDEN]
    sets = [(b["motor"], *b["opt_parameters"][2:6], b["opt_parameters"][1]) for b in designs]
    sets += [(m, Ns, Np, Ns + 2 * Np, mod, n) for m, Ns, Np, mod, n in EXTRA]
    import tempfile
    for motor, Ns, Np, Nr, module, n in sets:
        with tempfile.TemporaryDirectory() as tmp:
            actuator, *_ = write_files(mp, Path(tmp), motor, "3dp", Ns, Np, Nr, module, n)
        seen["ring wider than motor"].add(actuator.ring_OD >= actuator.motor_OD)
        seen["bearing wider than ring"].add(actuator.bearing_OD + actuator.output_mounting_hole_dia * 4
                                            > actuator.Nr * actuator.module + 2 * actuator.h_b)
    mp.undo()
    assert all(s == {True, False} for s in seen.values()), seen


def test_docs_page_is_up_to_date():
    page = (REPO / "docs" / "variables" / "sspg.md").read_text(encoding="utf-8")
    assert page == render(SPEC), "run: python tools/variables/render.py sspg"


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
    minimum = 2 * act.planet_bearing_width + act.standard_clearance_1_5mm * 2 / 3
    for fw in ("fw_p", "fw_r"):
        assert more[fw] == pytest.approx(max(2 * base["fw_s_calc"], minimum), rel=1e-12)
    downstream = {what}
    for e in CAD:
        if set(e.get("depends_on", [])) & downstream:
            downstream.add(e["name"])
    changed = {k for k in base if base[k] != more[k]}
    assert "fw_s_calc" in changed and changed <= downstream
