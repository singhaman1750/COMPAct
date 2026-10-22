"""
Golden-output regression check for the gearbox optimisers.

Records, for every gearbox type in gearbox_runner.GEARBOXES and each of its golden
motors (GOLDEN_MOTORS), the optimiser's returned parameters, the CAD equation
files the run writes, and the results CSVs it writes (total mass, efficiency,
cost, per-part mass breakdown; run-time lines removed). A later `check` re-runs
the same cases and reports any difference, so refactors can be verified to
leave results unchanged.

Usage (from the repo root):
    python tests/golden/golden.py record            # (re)write all baselines
    python tests/golden/golden.py check             # compare against baselines
    python tests/golden/golden.py check --only idspg insspg_type_1
    python tests/golden/golden.py list              # show the cases
    python tests/golden/golden.py check --material metal

A baseline captures *current* behaviour, including known bugs and crashes.
When a commit is meant to change results, re-record only the affected cases
in that same commit and say so in the commit message.
"""

import argparse
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
import gearbox_runner  # noqa: E402
BASELINE_DIR = Path(__file__).resolve().parent / "baselines"
RUN_CASE = Path(__file__).resolve().parent / "_run_case.py"

# One ratio per family, inside each family's usual range, so that every case
# finds a feasible design (a baseline of "no solution" catches very little).
GEAR_RATIOS_BY_GROUP = {
    "SSPG": [6.5], "ISSPG": [6.5], "INSSPG": [6.5],
    "CPG": [10], "ICPG": [10], "INCPG": [10],
    "DSPG": [20], "IDSPG": [20], "INDSPG": [20],
    "WPG": [20], "INWPG": [20],
}
# Smaller motors only reach low ratios. ISSPG with RO60 finds no design at
# any ratio from 4 to 30, so it stays at the family ratio as a crash check.
GEAR_RATIO_OVERRIDES = {
    ("isspg_inside", "RO80"): [5],
    ("isspg_compact", "RO80"): [5],
    ("insspg_type_2", "RI80"): [5],
    ("icpg", "RO80"): [8],
}
FLOAT_REL_TOL = 1e-9

# The motors each gearbox type is checked with (every type accepts any motor of
# its kind from config_files/motors.json; these are the ones with baselines).
FRAMED_GOLDEN_MOTORS = ["U8_Lite", "U10_Plus_KV80", "MN8014", "VT8020_PRO", "MAD_M6C12_KV170"]
GOLDEN_MOTORS = {
    "sspg": FRAMED_GOLDEN_MOTORS,
    "cpg": FRAMED_GOLDEN_MOTORS,
    "wpg": FRAMED_GOLDEN_MOTORS,
    "dspg": FRAMED_GOLDEN_MOTORS,
    "icpg": ["RO100", "RO80"],
    "isspg_inside": ["RO100", "RO80", "RO60"],
    "isspg_compact": ["RO100", "RO80", "RO60"],
    "idspg": ["RO100"],
    "insspg_type_1": ["RI100", "RI80"],
    "insspg_type_2": ["RI100", "RI80"],
    "incpg_dependent": ["RI100"],
    "incpg_independent": ["RI100", "RI80"],
    "inwpg_dependent": ["RI100", "RI80"],
    "inwpg_independent": ["RI100", "RI80"],
    "indspg": ["RI100", "RI80"],
}

# Variants that write into the same CADs/<GROUP>/ folder share a group and
# must not run at the same time.
_VARIANT_SUFFIX = re.compile(r"_(type_\d+|dependent|independent|inside|compact)$")


def gearbox_group(gb_type):
    return _VARIANT_SUFFIX.sub("", gb_type).upper()


def gearbox_types():
    return list(gearbox_runner.GEARBOXES)


def all_cases(gear_ratios=None):
    cases = []
    for gb_type in gearbox_types():
        family_ratios = GEAR_RATIOS_BY_GROUP[gearbox_group(gb_type)]
        for motor in GOLDEN_MOTORS[gb_type]:
            ratios = gear_ratios or GEAR_RATIO_OVERRIDES.get((gb_type, motor), family_ratios)
            for gr in ratios:
                cases.append({"gb_type": gb_type, "motor": motor, "gear_ratio": gr})
        # Metal mode: one case per gearbox type, with its first golden motor.
        motor = GOLDEN_MOTORS[gb_type][0]
        for gr in gear_ratios or GEAR_RATIO_OVERRIDES.get((gb_type, motor), family_ratios):
            cases.append({"gb_type": gb_type, "motor": motor, "gear_ratio": gr, "material": "metal"})
    return cases


def case_id(case):
    material = case.get("material", "3dp")
    suffix = "" if material == "3dp" else f"__{material}"
    return f"{case['gb_type']}__{case['motor']}__{case['gear_ratio']}{suffix}"


def run_case(case):
    # Each case runs in its own temporary working directory, so the results/
    # CSVs it writes are captured there and never touch the repo's results/.
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "result.json"
        proc = subprocess.run(
            [
                sys.executable,
                str(RUN_CASE),
                case["gb_type"],
                case["motor"],
                str(case["gear_ratio"]),
                gearbox_group(case["gb_type"]),
                str(out_path),
                case.get("material", "3dp"),
            ],
            cwd=tmp,
            capture_output=True,
            text=True,
        )
        if not out_path.exists():
            raise RuntimeError(
                f"{case_id(case)}: runner produced no result\n{proc.stderr[-2000:]}"
            )
        return json.loads(out_path.read_text(encoding="utf-8"))


def run_cases(cases, workers):
    """Run cases in parallel, but cases in the same group one after another."""
    groups = {}
    for case in cases:
        groups.setdefault(gearbox_group(case["gb_type"]), []).append(case)

    def run_group(group_cases):
        results = []
        for case in group_cases:
            print(f"  running {case_id(case)}", flush=True)
            results.append((case, run_case(case)))
        return results

    with ThreadPoolExecutor(max_workers=workers) as pool:
        for group_results in pool.map(run_group, groups.values()):
            yield from group_results


def values_match(expected, actual):
    if isinstance(expected, float) and isinstance(actual, float):
        if math.isnan(expected) and math.isnan(actual):
            return True
        return math.isclose(expected, actual, rel_tol=FLOAT_REL_TOL, abs_tol=0.0)
    if isinstance(expected, list) and isinstance(actual, list):
        return len(expected) == len(actual) and all(
            values_match(e, a) for e, a in zip(expected, actual)
        )
    if isinstance(expected, dict) and isinstance(actual, dict):
        return expected.keys() == actual.keys() and all(
            values_match(expected[k], actual[k]) for k in expected
        )
    return expected == actual


def describe_differences(expected, actual):
    diffs = []
    if expected.get("error") != actual.get("error"):
        diffs.append(f"error: {expected.get('error')!r} -> {actual.get('error')!r}")
    exp_params = expected.get("opt_parameters")
    act_params = actual.get("opt_parameters")
    if not values_match(exp_params, act_params):
        if isinstance(exp_params, list) and isinstance(act_params, list):
            if len(exp_params) != len(act_params):
                diffs.append(
                    f"opt_parameters length {len(exp_params)} -> {len(act_params)}"
                )
            for i, (e, a) in enumerate(zip(exp_params, act_params)):
                if not values_match(e, a):
                    diffs.append(f"opt_parameters[{i}]: {e!r} -> {a!r}")
        else:
            diffs.append(f"opt_parameters: {exp_params!r} -> {act_params!r}")
    exp_files = expected.get("cad_files", {})
    act_files = actual.get("cad_files", {})
    for path in sorted(exp_files.keys() | act_files.keys()):
        if path not in act_files:
            diffs.append(f"CAD file no longer written: {path}")
        elif path not in exp_files:
            diffs.append(f"new CAD file written: {path}")
        elif exp_files[path] != act_files[path]:
            exp_lines = exp_files[path].splitlines()
            act_lines = act_files[path].splitlines()
            changed = sum(1 for e, a in zip(exp_lines, act_lines) if e != a)
            changed += abs(len(exp_lines) - len(act_lines))
            diffs.append(f"CAD file changed: {path} ({changed} lines differ)")
    exp_results = expected.get("results_files", {})
    act_results = actual.get("results_files", {})
    for path in sorted(exp_results.keys() | act_results.keys()):
        if path not in act_results:
            diffs.append(f"results file no longer written: {path}")
        elif path not in exp_results:
            diffs.append(f"new results file written: {path}")
        elif exp_results[path] != act_results[path]:
            diffs.append(f"results file changed: {path}")
            diffs.extend("    " + d for d in describe_value_changes(exp_results[path], act_results[path]))
    return diffs


_NAME = re.compile(r"^[A-Za-z_]")


def named_values(text):
    """Pull 'name: value' lines and header/row tables out of a results CSV."""
    lines = [line.strip() for line in text.splitlines()]
    values = {}

    def put(name, value):
        key, n = name, 2
        while key in values:
            key, n = f"{name}#{n}", n + 1
        values[key] = value

    i = 0
    while i < len(lines):
        line = lines[i]
        pair = re.match(r"^([A-Za-z_][\w .()/-]*?)\s*:\s*(\S.*)$", line)
        if pair and "," not in line:
            put(pair.group(1).strip(), pair.group(2).strip())
            i += 1
            continue
        header = [h.strip() for h in line.split(",")]
        if "," in line and all(_NAME.match(h) for h in header if h):
            j = i + 1
            while j < len(lines) and "," in lines[j] and not _NAME.match(lines[j]):
                row = [v.strip() for v in lines[j].split(",")]
                for k, value in enumerate(row):
                    name = header[k] if k < len(header) and header[k] else f"{header[-1] or 'column'}+{k}"
                    if value:
                        put(name, value)
                j += 1
            if j > i + 1:
                i = j
                continue
        i += 1
    return values


def describe_value_changes(expected_text, actual_text, limit=25):
    expected, actual = named_values(expected_text), named_values(actual_text)
    changes = [
        f"{key}: {expected.get(key, '(missing)')} -> {actual.get(key, '(missing)')}"
        for key in list(expected) + [k for k in actual if k not in expected]
        if expected.get(key) != actual.get(key)
    ]
    if not changes:
        changes = ["(text differs, but no named value changed)"]
    if len(changes) > limit:
        changes = changes[:limit] + [f"... and {len(changes) - limit} more"]
    return changes


def select_cases(args):
    cases = all_cases(args.gear_ratios)
    if args.only:
        cases = [c for c in cases if c["gb_type"] in args.only]
        unknown = set(args.only) - {c["gb_type"] for c in cases}
        if unknown:
            sys.exit(f"unknown gearbox type(s): {', '.join(sorted(unknown))}")
    if args.material:
        cases = [c for c in cases if c.get("material", "3dp") == args.material]
    return cases


def cmd_list(args):
    for case in select_cases(args):
        print(f"{case_id(case):45} group={gearbox_group(case['gb_type'])}")


def cmd_record(args):
    cases = select_cases(args)
    BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Recording {len(cases)} cases")
    for case, result in run_cases(cases, args.workers):
        path = BASELINE_DIR / f"{case_id(case)}.json"
        path.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        if result.get("error"):
            status = "ERROR " + result["error"]
        elif result.get("opt_parameters") is None:
            status = "no feasible design"
        else:
            status = "ok"
        print(f"  recorded {case_id(case)}: {status}")


def cmd_check(args):
    cases = select_cases(args)
    missing = [c for c in cases if not (BASELINE_DIR / f"{case_id(c)}.json").exists()]
    if missing:
        sys.exit("no baseline for: " + ", ".join(case_id(c) for c in missing))
    print(f"Checking {len(cases)} cases")
    failures = {}
    for case, result in run_cases(cases, args.workers):
        expected = json.loads(
            (BASELINE_DIR / f"{case_id(case)}.json").read_text(encoding="utf-8")
        )
        diffs = describe_differences(expected, result)
        if diffs:
            failures[case_id(case)] = diffs
    if failures:
        print(f"\n{len(failures)} of {len(cases)} cases differ from the baseline:")
        for cid, diffs in sorted(failures.items()):
            print(f"- {cid}")
            for d in diffs:
                print(f"    {d}")
        sys.exit(1)
    print(f"\nAll {len(cases)} cases match the baseline.")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("command", choices=["list", "record", "check"])
    parser.add_argument("--only", nargs="+", metavar="GB_TYPE", help="limit to these gearbox types")
    parser.add_argument("--material", choices=list(gearbox_runner.MATERIAL_MODES),
                        help="limit to cases in this material mode")
    parser.add_argument(
        "--gear-ratios", nargs="+", type=float, metavar="GR",
        help="override the per-family ratios in GEAR_RATIOS_BY_GROUP",
    )
    parser.add_argument("--workers", type=int, default=min(12, os.cpu_count() or 1))
    args = parser.parse_args()
    {"list": cmd_list, "record": cmd_record, "check": cmd_check}[args.command](args)


if __name__ == "__main__":
    main()
