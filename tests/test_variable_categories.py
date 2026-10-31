"""Variable categories (config_files/variables/<gearbox>_variables.json): every variable a gearbox
writes to its CAD file is sorted into input / optimisation / fixed / dependent. These tests are the
number check, run for every gearbox that has a spec (tests/variable_helpers.py): the lists must
match what the code writes, one entry per variable, and every source, formula and lookup in the
spec must give the value the code gives.

Each design is built with gearbox_runner and its equation files are written to a temporary folder
(COMPACT_CAD_DIR), so CADs/ is never touched. Gearbox-specific checks are in
test_variable_categories_<gearbox>.py.
"""
import ast
import json
import math
import re
import tempfile
from collections import Counter
from pathlib import Path

import pytest

from variable_helpers import CONFIG, GEARBOXES, REPO, SPECS, equation_lines, golden_design, write_design

import gearbox_runner  # noqa: E402  (variable_helpers put the repo on sys.path)
from CommonComponents import bearings_discrete, nuts_and_bolts_dimensions  # noqa: E402
from tools.variables.render import CATEGORIES, load_rules, render  # noqa: E402

CASES = [(gb, name) for gb in SPECS for name in GEARBOXES[gb].golden()] + \
        [(gb, f"extra{i}") for gb in SPECS for i in range(len(GEARBOXES[gb].extra))]


def entries(gb):
    return SPECS[gb]["cad_variables"], SPECS[gb]["code_only"]


@pytest.fixture(scope="module", params=CASES, ids=[f"{gb}-{n}" for gb, n in CASES])
def design(request, tmp_path_factory):
    gb, name = request.param
    mp = pytest.MonkeyPatch()
    try:
        if name.startswith("extra"):
            motor, gears = GEARBOXES[gb].extra[int(name[5:])]
            material, baseline = "3dp", None
        else:
            _, motor, material, gears, baseline = golden_design(name)
        out = write_design(mp, tmp_path_factory.mktemp("cad"), gb, motor, material, gears)
    finally:
        mp.undo()
    return (gb, baseline) + out


# ---- the lists ------------------------------------------------------------------------------------

@pytest.mark.parametrize("gb", SPECS)
def test_counts_and_one_category_each(gb):
    cad, code = entries(gb)
    names = [e["name"] for e in cad]
    assert len(set(names)) == len(names) == sum(GEARBOXES[gb].counts.values())
    assert len(code) == GEARBOXES[gb].code_only and not set(names) & {e["name"] for e in code}
    assert Counter(e["category"] for e in cad) == GEARBOXES[gb].counts
    for e in cad + code:
        assert e["category"] in CATEGORIES and e["confidence"] in SPECS[gb]["confidence"], e["name"]
        assert e["reason"], e["name"]


def test_spec_lists_exactly_the_variables_the_code_writes(design):
    gb, baseline, _, _, plain, onshape = design
    cad, _ = entries(gb)
    assert [n for n, _ in onshape] == [e["name"] for e in cad]          # same names, same order
    aliases = SPECS[gb].get("plain_file_aliases", {})
    plain_names = {n for n, _ in plain}
    assert sorted({aliases.get(n, n) for n in plain_names}) == sorted(e["name"] for e in cad)
    written_twice = sum(1 for k, v in aliases.items() if k in plain_names and v in plain_names)
    assert len(plain) == len(onshape) + written_twice                    # e.g. "pressure angle"
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


@pytest.mark.parametrize("gb", SPECS)
def test_every_dependency_is_classified(gb):
    cad, code = entries(gb)
    known = {e["name"] for e in cad + code}
    for e in cad + code:
        missing = [d for d in e.get("depends_on", []) if d not in known]
        assert not missing, (e["name"], missing)
        if e["category"] == "dependent":
            assert e["depends_on"] and ("formula" in e or "lookup" in e or "rule" in e), e["name"]
        else:
            assert "source" in e, e["name"]


@pytest.mark.parametrize("gb", SPECS)
def test_depends_on_lists_exactly_the_names_in_each_formula_and_lookup(gb):
    cad, code = entries(gb)
    for e in cad + code:
        if "formula" in e:
            exprs = [e["formula"]]
        elif "lookup" in e:
            exprs = [v for k, v in e["lookup"]["args"].items() if k != "bolt_type"]
        else:
            continue
        used = {n.id for x in exprs for n in ast.walk(ast.parse(x, mode="eval")) if isinstance(n, ast.Name)}
        assert used - {"cos", "sqrt", "pi"} == set(e["depends_on"]), e["name"]


@pytest.mark.parametrize("gb", SPECS)
def test_every_config_key_is_accounted_for(gb):
    cad, code = entries(gb)
    pfile = GEARBOXES[gb].params_file
    params = json.loads((CONFIG / pfile).read_text(encoding="utf-8"))
    used = {(s["block"], s["key"]) for e in cad + code if (s := e.get("source", {})).get("file") == pfile}
    unused = {b["block"] for b in SPECS[gb]["unused_config_blocks"]}
    assert set(params) == unused | {b for b, _ in used}
    for block, keys in params.items():
        if block not in unused:
            assert {(block, k) for k in keys} <= used, sorted(set(keys) - {k for b, k in used if b == block})


@pytest.mark.parametrize("gb", SPECS)
def test_docs_page_is_up_to_date(gb):
    page = (REPO / "docs" / "variables" / f"{gb}.md").read_text(encoding="utf-8")
    assert page == render(SPECS[gb]), f"run: python tools/variables/render.py {gb}"


# ---- the values -----------------------------------------------------------------------------------

def values(gb, actuator, onshape):
    """name -> value for every classified variable: CAD values from the file, code-only ones from the
    actuator (or its gearbox) and the optimisation settings."""
    _, code = entries(gb)
    vals = {n: float(v) for n, v in onshape}
    params = json.loads((CONFIG / GEARBOXES[gb].params_file).read_text(encoding="utf-8"))
    for e in code:
        if "attr" not in e:
            s = e["source"]
            vals[e["name"]] = params[s["block"]][s["key"]]
        elif hasattr(actuator, e["attr"]):
            vals[e["name"]] = getattr(actuator, e["attr"])
        else:
            vals[e["name"]] = getattr(getattr(actuator, GEARBOXES[gb].gearbox_attr), e["attr"])
    return vals


def test_attr_matches_the_file(design):
    gb, _, actuator, _, _, onshape = design
    cad, _ = entries(gb)
    for (name, v), e in zip(onshape, cad):
        assert getattr(actuator, e["attr"]) == pytest.approx(float(v), rel=1e-9), name


def test_sources_give_the_values(design):
    gb, _, actuator, _, _, onshape = design
    cad, code = entries(gb)
    vals = values(gb, actuator, onshape)
    params = json.loads((CONFIG / GEARBOXES[gb].params_file).read_text(encoding="utf-8"))
    motors = json.loads((CONFIG / "motors.json").read_text(encoding="utf-8"))
    material = "metal" if actuator.results_suffix else "3dp"
    names = {"<motor>": actuator.motor.motorName, "<gear material>": gearbox_runner.MATERIAL_MODES[material][0]}

    def lookup(data, block):
        for part in block.split("."):
            data = data[names.get(part, part)]
        return data
    for e in cad + code:
        s = e.get("source", {})
        if s.get("file") == GEARBOXES[gb].params_file:
            expected = params[s["block"]][s["key"]]
        elif s.get("file") == "motors.json":
            expected = lookup(motors, s["block"])[s["key"]]
        elif s.get("file", "").endswith(".json") and s["file"] not in (GEARBOXES[gb].params_file, "motors.json"):
            # config.json, or the gearbox's own config file (gear standard, MIT factors, ...)
            expected = lookup(json.loads((CONFIG / s["file"]).read_text(encoding="utf-8")), s["block"])[s["key"]]
        else:
            continue
        assert vals[e["name"]] == pytest.approx(expected, rel=1e-9), e["name"]


def test_formulas_and_lookups_give_the_values(design):
    gb, _, actuator, _, _, onshape = design
    cad, code = entries(gb)
    vals = values(gb, actuator, onshape)
    env = {"cos": math.cos, "sqrt": math.sqrt, "pi": math.pi, "__builtins__": {}}
    for e in cad + code:
        if "formula" in e:
            got = eval(e["formula"], env, dict(vals))
        elif "lookup" in e:
            lk = e["lookup"]
            args = {k: (eval(v, env, dict(vals)) if k != "bolt_type" else v) for k, v in lk["args"].items()}
            if lk["function"] == "bearings_discrete":
                got = getattr(bearings_discrete(**args), lk["method"])()
            else:
                got = getattr(nuts_and_bolts_dimensions(**args), lk["field"])
        else:
            continue
        assert got == pytest.approx(vals[e["name"]], rel=1e-9, abs=1e-12), e["name"]


@pytest.mark.parametrize("gb", [gb for gb in SPECS if GEARBOXES[gb].branches])
def test_both_branches_of_the_two_case_rules_are_checked(gb):
    spec = GEARBOXES[gb]
    seen = {}
    mp = pytest.MonkeyPatch()
    sets = [golden_design(n)[1:4:2] for n in spec.golden()] + list(spec.extra)   # (motor, gears)
    try:
        for motor, gears in sets:
            with tempfile.TemporaryDirectory() as tmp:
                actuator, *_ = write_design(mp, Path(tmp), gb, motor, "3dp", gears)
            for rule, branch in spec.branches(actuator).items():
                seen.setdefault(rule, set()).add(branch)
    finally:
        mp.undo()
    assert all(s == {True, False} for s in seen.values()), seen
