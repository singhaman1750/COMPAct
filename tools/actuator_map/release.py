"""Release a map: copy a run's map files into tools/actuator_map/maps/<version>/ (committed) with
map.json (where it came from, settings, warnings) and a README.

    python tools/actuator_map/release.py --run full --version v1

Run table.py and fit.py on the run first. The case files and plots stay in the run folder
(gitignored); a released map is fits.json + tables + summaries, which map.py needs on its own.
"""
import argparse
import json
import shutil
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.actuator_map.sweep import git_commit  # noqa: E402
from tools.actuator_map.table import RUNS_DIR, load_cases  # noqa: E402

MAPS_DIR = REPO / "tools" / "actuator_map" / "maps"
FILES = ("fits.json", "fits.md", "summary.md")   # plus every table_<material>.csv

# Known issues that affect what the map says (ISSUES.md), as of this release.
KNOWN_ISSUES = [
    {"id": "metal-overestimate", "materials": ["metal"],
     "text": "Metal masses are overestimated: the metal mode reuses the 3D-printed shapes, the whole gearbox casing "
             "is weighed as steel, and planets are as wide as two planet bearings need. This favours compound "
             "types (CPG) in the metal map. See docs/metal_sspg_mass.md and ISSUES.md 'Material modes'."},
    {"id": "bug13", "types": ["indspg"],
     "text": "INDSPG raises instead of reporting 'no design' where it has none (ISSUES.md bug 13); those cases count "
             "as no design."},
    {"id": "CAD6", "types": ["idspg"], "text": "IDSPG stage-2 parts don't move in the CAD with smaller motors (RO80)."},
    {"id": "CAD7", "types": ["inwpg_dependent"],
     "text": "INWPG dependent output ring gear and bearing don't move in the CAD (RI80)."},
    {"id": "reflected-inertia", "text": "Reflected inertia is ratio^2 x rotor inertia only; the gears' inertia is not included. "
                                        "Framed motors' rotor inertias are estimates (+-30 %)."},
]


def coverage(cases):
    """Per motor and material: requested ratios with no design in any type, and the case counts."""
    feasible, asked, counts = defaultdict(set), defaultdict(set), Counter()
    for c in cases:
        key = (c["motor"], c["material"])
        asked[key].add(c["ratio_requested"])
        if c["feasible"]:
            feasible[key].add(c["ratio_requested"])
        counts["feasible" if c["feasible"] else ("error" if c.get("error") else "no design")] += 1
    gaps = {k: sorted(asked[k] - feasible[k]) for k in sorted(asked) if asked[k] - feasible[k]}
    return gaps, counts


def warnings_for(fits, gaps, run):
    out = []
    no_map = sorted({(m, mat) for m in run["motors"] for mat in run["materials"]
                     if mat not in fits["motors"].get(m, {})})
    for m, mat in no_map:
        out.append({"motor": m, "material": mat, "text": "no design in any gearbox type at any swept ratio; not in the map"})
    for (m, mat), ratios in gaps.items():
        if (m, mat) not in no_map:
            out.append({"motor": m, "material": mat, "text": f"no design at ratios {', '.join(f'{r:g}' for r in ratios)}"})
    for m, by_mat in sorted(fits["motors"].items()):
        for mat, e in sorted(by_mat.items()):
            capped = sorted({lo for lo, hi, gb in e["best_real_width"] if gb != "none"
                             and e["types"][gb]["quantities"].get("torque_carried_fraction") is not None
                             and min(e["types"][gb]["quantities"]["torque_carried_fraction"]["y"]) < 0.8})
            if capped:
                out.append({"motor": m, "material": mat,
                            "text": "the best type is torque-capped (< 80 % of peak) somewhere in the range; "
                                    "check flags['torque_capped'] / ['no_full_torque_design']"})
    return out


def readme(version, meta, run, counts, warnings):
    lines = [f"# Actuator map {version}", "",
             "Released COMPAct actuator map: the best gearbox type and the whole actuator's mass, size, torque, "
             "speed and reflected inertia for each motor, gear ratio and material. Read it with "
             "`tools/actuator_map/map.py` (standalone: copy `map.py` and this folder into another project).", "",
             "```python", "from tools.actuator_map.map import ActuatorMap",
             f'amap = ActuatorMap("tools/actuator_map/maps/{version}")',
             'a = amap.actuator("U8_Lite", 9.3, "3dp")      # best type at 9.3:1',
             "a.gb_type, a.mass, a.width, a.peak_torque, a.flags", "```", "",
             "Optimise with the smooth fits (the default, with derivatives); read the final design with "
             "`method=\"interp\"`. `flags[\"fit_error_high\"]` lists quantities whose fit is more than "
             f"{meta['fit_error_flag_rel']:.0%} off at some design.", "",
             "## Contents", "",
             "| File | |", "|---|---|",
             "| `fits.json` | everything `map.py` needs: fits, best types, motor values, gains, rules |",
             "| `fits.md` | fit quality and best types per motor and material |",
             "| `summary.md` | best type at each swept ratio |",
             "| `table_<material>.csv` | every optimised design (one row per type and ratio) |",
             "| `map.json` | where this map came from, its settings and warnings |", "",
             "## Source", "",
             f"- sweep run `{map_json_source(run)['run']}`, COMPAct commit `{run['commit']}`",
             f"- {len(run['motors'])} motors, ratios {run['ratios'][0]:g}-{run['ratios'][-1]:g} "
             f"(step {run['ratios'][1] - run['ratios'][0]:g}), materials {', '.join(run['materials'])}",
             f"- {sum(counts.values())} cases: {counts['feasible']} with a design, {counts['no design']} without, "
             f"{counts['error']} raised (counted as no design)", "",
             "## Known issues", ""]
    lines += [f"- **{k['id']}**: {k['text']}" for k in KNOWN_ISSUES]
    lines += ["", "## Warnings", ""]
    lines += [f"- {w['motor']} ({w['material']}): {w['text']}" for w in warnings]
    return "\n".join(lines) + "\n"


def map_json_source(run):
    return {"run": run["name"], "commit": run["commit"], "started": run.get("started")}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--run", required=True, help="run folder under tools/actuator_map/runs/")
    ap.add_argument("--version", required=True, help="e.g. v1; written to tools/actuator_map/maps/<version>/")
    ap.add_argument("--force", action="store_true", help="overwrite an existing release folder")
    args = ap.parse_args(argv)

    run_dir = RUNS_DIR / args.run
    out = MAPS_DIR / args.version
    if out.exists() and not args.force:
        ap.error(f"{out} exists (use --force to overwrite)")
    missing = [f for f in FILES if not (run_dir / f).is_file()]
    tables = sorted(p.name for p in run_dir.glob("table_*.csv"))
    if missing or not tables:
        missing += [] if tables else ["table_*.csv"]
        ap.error(f"run {args.run} lacks {', '.join(missing)}: run table.py and fit.py first")

    run = json.loads((run_dir / "run.json").read_text(encoding="utf-8")) | {"name": args.run}
    fits = json.loads((run_dir / "fits.json").read_text(encoding="utf-8"))
    gaps, counts = coverage(load_cases(run_dir))
    warnings = warnings_for(fits, gaps, run)

    out.mkdir(parents=True, exist_ok=True)
    for f in FILES + tuple(tables):
        shutil.copyfile(run_dir / f, out / f)
    meta = fits["meta"]
    map_json = {
        "version": args.version, "released": date.today().isoformat(), "released_from_commit": git_commit(),
        "source": map_json_source(run),
        "grid": {"motors": run["motors"], "ratios": run["ratios"], "materials": run["materials"]},
        "cases": dict(counts),
        "settings": {k: meta[k] for k in ("format", "gains", "grid_step", "min_carried_fraction_for_best",
                                          "near_best_rel", "min_best_interval", "fit_error_flag_rel") if k in meta},
        "known_issues": KNOWN_ISSUES,
        "warnings": warnings,
    }
    (out / "map.json").write_text(json.dumps(map_json, indent=1) + "\n", encoding="utf-8")
    (out / "README.md").write_text(readme(args.version, meta, run, counts, warnings), encoding="utf-8")
    print(f"released {args.run} as {out}: {', '.join(FILES + tuple(tables))}, map.json, README.md "
          f"({len(warnings)} warnings)")


if __name__ == "__main__":
    main()
