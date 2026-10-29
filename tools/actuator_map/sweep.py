"""Actuator-map sweep: run COMPAct for every (motor, gearbox type, gear ratio, material) and save
one JSON file per case.

    python tools/actuator_map/sweep.py --name pilot \
        --motors U8_Lite MN8014 MAD_M6C12_KV170 RO100 RI100 --ratios 4:30:1

Each motor is run with every gearbox type that takes its motor type (framed outrunner: SSPG, CPG,
WPG, DSPG; frameless outrunner: ISSPG x2, ICPG, IDSPG; frameless inrunner: INSSPG x2, INCPG x2,
INWPG x2, INDSPG), unless --types narrows it. Cases run in parallel, each in its own temporary
folder (see case.py), so the repo's CADs/ and results/ are not touched.

Output: tools/actuator_map/runs/<name>/ (gitignored)
    run.json                                     what was asked for, git commit, start time
    cases/<material>/<motor>/<gb_type>__<ratio>.json   one result per case
A case whose file exists is skipped, so an interrupted sweep continues where it stopped; delete
the folder (or use a new --name) to start again.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import gearbox_runner  # noqa: E402

RUNS_DIR = REPO / "tools" / "actuator_map" / "runs"
MATERIALS = ("3dp", "metal")
SLOW_FIRST = ("dspg", "idspg", "indspg", "wpg", "inwpg_dependent", "inwpg_independent")


def motor_types():
    with open(REPO / "config_files" / "motors.json") as f:
        return {name: m["type"] for name, m in json.load(f)["motors"].items()}


def types_for(motor_type):
    return [gb for gb, spec in gearbox_runner.GEARBOXES.items() if spec.motor_type == motor_type]


def parse_ratios(text):
    """'4:30:1' -> 4, 5, ..., 30 (end included); '6.5 10' -> 6.5, 10."""
    if ":" in text:
        start, stop, step = (float(x) for x in text.split(":"))
        n = int(round((stop - start) / step))
        return [round(start + i * step, 6) for i in range(n + 1)]
    return [float(x) for x in text.replace(",", " ").split()]


def ratio_tag(ratio):
    return f"{ratio:g}".replace(".", "p")


def case_path(out, material, motor, gb_type, ratio):
    return out / "cases" / material / motor / f"{gb_type}__{ratio_tag(ratio)}.json"


def git_commit():
    def git(*args):
        return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True).stdout.strip()
    commit = git("rev-parse", "HEAD")
    dirty = bool(git("status", "--porcelain", "--untracked-files=no", "--", "*.py", "config_files"))
    return commit + ("-dirty" if dirty else "")


def _quiet_worker():
    """The optimisers print some notes straight to the real stdout; keep the sweep's output clean."""
    devnull = open(os.devnull, "w")
    os.dup2(devnull.fileno(), 1)
    sys.stdout = sys.__stdout__ = devnull


def _run(case, path, commit):
    from tools.actuator_map.case import run_case
    try:
        result = run_case(*case)
    except Exception as e:  # never let one case stop the sweep
        gb, motor, ratio, material = case
        result = {"gb_type": gb, "motor": motor, "ratio_requested": ratio, "material": material,
                  "feasible": False, "error": f"{type(e).__name__}: {e}"}
    result["commit"] = commit
    result["created"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(result, indent=1))
    tmp.replace(path)  # written whole or not at all, so a stopped sweep never leaves half a file
    return case, result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--name", required=True, help="run folder name under tools/actuator_map/runs/")
    ap.add_argument("--motors", nargs="+", required=True, help="motor names from config_files/motors.json")
    ap.add_argument("--ratios", required=True, help="'start:stop:step' (stop included) or a list, e.g. '6.5 10'")
    ap.add_argument("--materials", nargs="+", default=list(MATERIALS), choices=MATERIALS)
    ap.add_argument("--types", nargs="+", help="limit to these gearbox types")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    args = ap.parse_args(argv)

    known = motor_types()
    unknown = [m for m in args.motors if m not in known]
    if unknown:
        ap.error(f"unknown motor(s): {', '.join(unknown)}")
    if args.types:
        bad = [t for t in args.types if t not in gearbox_runner.GEARBOXES]
        if bad:
            ap.error(f"unknown gearbox type(s): {', '.join(bad)}")
    ratios = parse_ratios(args.ratios)

    cases = [(gb, motor, ratio, material)
             for material in args.materials for motor in args.motors
             for gb in types_for(known[motor]) if not args.types or gb in args.types
             for ratio in ratios]
    cases.sort(key=lambda c: c[0] not in SLOW_FIRST)  # long two-stage searches start first

    out = RUNS_DIR / args.name
    out.mkdir(parents=True, exist_ok=True)
    commit = git_commit()
    (out / "run.json").write_text(json.dumps({
        "motors": args.motors, "ratios": ratios, "materials": args.materials, "types": args.types,
        "commit": commit, "started": datetime.now(timezone.utc).isoformat(timespec="seconds")}, indent=1))

    todo = [c for c in cases if not case_path(out, c[3], c[1], c[0], c[2]).exists()]
    print(f"{len(cases)} cases, {len(cases) - len(todo)} already done, {len(todo)} to run "
          f"on {args.workers} workers -> {out}", flush=True)
    if commit.endswith("-dirty"):
        print("note: uncommitted changes in the optimiser code or config; results record the commit as -dirty",
              flush=True)

    started, counts = time.time(), {"feasible": 0, "no design": 0, "error": 0}
    with ProcessPoolExecutor(args.workers, initializer=_quiet_worker) as ex:
        futures = [ex.submit(_run, c, case_path(out, c[3], c[1], c[0], c[2]), commit) for c in todo]
        for i, fut in enumerate(as_completed(futures), 1):
            (gb, motor, ratio, material), r = fut.result()
            status = "feasible" if r["feasible"] else ("error" if r["error"] else "no design")
            counts[status] += 1
            if r["feasible"] and not r["same_cad_file"]:
                print(f"WARNING {gb} {motor} {ratio} {material}: rewritten CAD file differs", flush=True)
            if i % 25 == 0 or i == len(futures):
                print(f"  {i}/{len(futures)} done ({time.time() - started:.0f} s) {counts}", flush=True)
    print(f"finished in {time.time() - started:.0f} s: {counts}")


if __name__ == "__main__":
    main()
