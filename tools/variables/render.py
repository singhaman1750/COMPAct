"""Write docs/variables/<gearbox>.md from config_files/variables/<gearbox>_variables.json.

    python tools/variables/render.py            # every gearbox with a variables file
    python tools/variables/render.py sspg

The JSON file is the source; the Markdown page is generated from it and never edited by hand
(tests/test_variable_categories.py checks that they match).
"""
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SPEC_DIR = REPO / "config_files" / "variables"
DOCS_DIR = REPO / "docs" / "variables"
CATEGORIES = ("input", "optimisation", "fixed", "dependent")
TITLES = {"input": "Input", "optimisation": "Optimisation", "fixed": "Fixed", "dependent": "Dependent"}


def load(gearbox):
    return json.loads((SPEC_DIR / f"{gearbox}_variables.json").read_text(encoding="utf-8"))


def _source(e):
    if "formula" in e:
        return f"`{e['formula']}`"
    if "lookup" in e:
        lk = e["lookup"]
        args = ", ".join(f"{k}={v}" for k, v in lk["args"].items())
        return f"`{lk['function']}({args})` → {lk.get('field') or lk.get('method')}"
    s = e.get("source", {})
    if "optimiser" in s:
        return f"optimiser (`{s['optimiser']}`)"
    return f"{s['file']} → {s['block']} → `{s['key']}`"


def _table(entries):
    lines = ["| # | Variable | Sub-type | Source / formula | Depends on | Confidence | Why |",
             "|---|---|---|---|---|---|---|"]
    for i, e in enumerate(entries, 1):
        deps = ", ".join(e.get("depends_on", []))
        lines.append(f"| {i} | `{e['name']}` | {e['subtype']} | {_source(e)} | {deps} | {e['confidence']} | {e['reason']} |")
    return lines


def render(spec):
    gb = spec["gearbox"].upper()
    cad, code = spec["cad_variables"], spec["code_only"]
    count = Counter(e["category"] for e in cad)
    conf = Counter(e["confidence"] for e in cad)
    out = [f"# {gb} variables by category", "",
           f"Generated from `config_files/variables/{spec['gearbox']}_variables.json` by "
           "`python tools/variables/render.py`; edit the JSON, not this page.", "",
           spec["about"], "", "## Categories", ""]
    out += [f"- **{TITLES[c]}**: {spec['categories'][c]}" for c in CATEGORIES]
    out += ["", "Confidence:", ""] + [f"- **{k}**: {v}" for k, v in spec["confidence"].items()]
    out += ["", "## Count", "",
            "| Category | CAD variables | Code-only |", "|---|---|---|"]
    code_count = Counter(e["category"] for e in code)
    for c in CATEGORIES:
        out.append(f"| {TITLES[c]} | {count[c]} | {code_count[c]} |")
    out.append(f"| **Total** | **{len(cad)}** | **{len(code)}** |")
    out += ["", "CAD variables by confidence: " + ", ".join(f"{k} {conf[k]}" for k in ("high", "medium", "low")), ""]
    review = [e for e in cad + code if e["confidence"] != "high"]
    if review:
        out += ["## To review (not high confidence)", ""]
        out += [f"- `{e['name']}` ({TITLES[e['category']]}, {e['confidence']}): {e['reason']}" for e in review]
        out.append("")
    for c in CATEGORIES:
        entries = [e for e in cad if e["category"] == c]
        out += [f"## {TITLES[c]} ({len(entries)})", ""] + _table(entries) + [""]
    out += [f"## Used by the code, not written to the CAD file ({len(code)})", ""] + _table(code) + [""]
    out += [f"## Config blocks {gb} doesn't read", ""]
    out += [f"- {b['file']} → `{b['block']}`: {b['reason']}" for b in spec["unused_config_blocks"]]
    if spec.get("plain_file_aliases"):
        out += ["", "## Names in the plain equation file", "",
                f"`CADs/{gb}/{spec['gearbox']}_equations.txt` writes the same values; these names differ there:", ""]
        out += [f"- `\"{k}\"` = `{v}`" for k, v in spec["plain_file_aliases"].items()]
    return "\n".join(out) + "\n"


def main(argv=None):
    names = (argv if argv is not None else sys.argv[1:]) or sorted(p.name[:-len("_variables.json")]
                                                                  for p in SPEC_DIR.glob("*_variables.json"))
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    for gb in names:
        (DOCS_DIR / f"{gb}.md").write_text(render(load(gb)), encoding="utf-8")
        print(f"wrote docs/variables/{gb}.md")


if __name__ == "__main__":
    main()
