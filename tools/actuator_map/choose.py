"""Actuator select: the motor, gearbox type, gear ratio and gearbox parameters for a required output
peak torque and no-load speed, optimal in the actuator map's sense.

    python tools/actuator_map/choose.py --torque 30 --speed 25 --material 3dp
    python tools/actuator_map/choose.py --torque 30 --speed_rpm 240 --no-map     # no map: optimise all

1. Screening (default): ActuatorMap.select() ranks every (motor, type) from a released map's fits
   (milliseconds), asking for `--margin` (2 %) more torque and speed than needed, since the fits
   are approximate. The first `--shortlist` (8) go on.
2. Confirmation: the normal optimiser runs for each shortlisted (motor, type, ratio), as the sweep
   does (case.py). The output torque and speed are recomputed from the design's real ratio,
   efficiency and torque_carried_fraction. A design that misses by a little is run again at a
   corrected ratio (at most `--rounds` times), if the other target still holds there.
3. Ranking: designs that meet the ask first, by score (the map's real-width score, or the
   optimiser's cost with --rule compact_cost, both without the ratio-error term since the ratio is
   chosen here, not asked); then the misses, smallest shortfall first.

--no-map skips screening: every motor and type is optimised at every whole ratio from
torque / motor peak (the lowest possible ratio, efficiency 1) to motor no-load speed / speed, plus
that top end itself (minutes to tens of minutes). A motor that can't reach the ask gets one run at
the ratio between its torque and speed limits, as a closest miss.

Output: tools/actuator_map/runs/select_<name>/ (gitignored)
    result.json                          the ask, options, commits, every confirmed design ranked
    cads/<motor>__<type>__<ratio>/       the CAD equation files of every confirmed design
The ranked table is also printed. No-load speeds are motors.json's (KV x 48 V for framed motors).
"""
import argparse
import json
import math
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools.actuator_map.map import RPM_TO_RAD_S, ActuatorMap  # noqa: E402
from tools.actuator_map.sweep import MATERIALS, _quiet_worker, git_commit, ratio_tag, types_for  # noqa: E402
from tools.actuator_map.table import GEAR_COLUMNS, load_gains, load_motors, make_row  # noqa: E402

RUNS_DIR = REPO / "tools" / "actuator_map" / "runs"
MAPS_DIR = REPO / "tools" / "actuator_map" / "maps"
RATIO_NUDGE = 1.005      # a corrected ratio aims 0.5 % past the target it missed


def latest_map():
    versions = sorted((p for p in MAPS_DIR.glob("v*") if (p / "fits.json").is_file()),
                      key=lambda p: int(p.name[1:]) if p.name[1:].isdigit() else -1)
    return versions[-1] if versions else None


def stale_files(map_commit):
    """Optimiser code / config files changed since the map's sweep (committed or not)."""
    if not map_commit:
        return []
    spec = ["--", "*.py", "config_files", ":(exclude)tools", ":(exclude)tests"]
    out = subprocess.run(["git", "diff", "--name-only", map_commit.split("-")[0], *spec],
                         cwd=REPO, capture_output=True, text=True)
    return out.stdout.split() if out.returncode == 0 else ["(map commit not found)"]


def evaluate(case, motor_entry, gains, torque, speed, rule):
    """A confirmed design's row (table.py's make_row) with the ask's verdict and the score."""
    row = make_row(case, motor_entry, gains)
    ratio_error = abs(case["gear_ratio"] - case["ratio_requested"])
    if rule == "compact_cost":
        score = case["cost"] - ratio_error
    else:
        score = None if row["real_width_score"] is None else row["real_width_score"] - ratio_error
    t, w = row["peak_torque_out_Nm"], row["no_load_speed_out_rad_s"]
    shortfall = max(0.0, 1 - t / torque) + max(0.0, 1 - w / speed)
    return {**row, "score": score, "meets": shortfall == 0, "shortfall": shortfall,
            "torque_margin": t / torque - 1, "speed_margin": w / speed - 1,
            "opt_parameters": case["opt_parameters"]}


def corrected_ratio(row, motor_entry, torque, speed):
    """The ratio to try next for a design that misses, or None if fixing one target breaks the other."""
    el = motor_entry["electrical"]
    tp, w0 = el["peak_torque_Nm"], el["no_load_speed_rpm"] * RPM_TO_RAD_S
    eta_f = row["efficiency"] * row["torque_carried_fraction"]
    if row["torque_margin"] < 0 <= row["speed_margin"]:
        r = row["ratio"] * torque / row["peak_torque_out_Nm"] * RATIO_NUDGE
        return round(r, 3) if w0 / r >= speed else None
    if row["speed_margin"] < 0 <= row["torque_margin"]:
        r = w0 / speed / RATIO_NUDGE
        return round(r, 3) if tp * r * eta_f >= torque else None
    return None


def _run(job):
    from tools.actuator_map.case import run_case
    gb, motor, ratio, material, cad_out = job
    try:
        return job, run_case(gb, motor, ratio, material, cad_out=cad_out)
    except Exception as e:  # one failing case never stops the search
        return job, {"gb_type": gb, "motor": motor, "ratio_requested": ratio, "material": material,
                     "feasible": False, "error": f"{type(e).__name__}: {e}"}


def run_jobs(jobs, workers, out):
    """[(gb, motor, ratio, material)] -> [(job, case result)], run in parallel."""
    full = [(*j, str(out / "cads" / f"{j[1]}__{j[0]}__{ratio_tag(j[2])}")) for j in jobs]
    if not full:
        return []
    with ProcessPoolExecutor(min(workers, len(full)), initializer=_quiet_worker) as ex:
        return [(job[:4], res) for job, res in ex.map(_run, full)]


def no_map_ratios(motor_entry, torque, speed, min_ratio, max_ratio):
    """Whole ratios from the lowest possible (efficiency 1) to the speed limit, plus the limit itself;
    or the one ratio between the two limits for a motor that can't reach the ask."""
    el = motor_entry["electrical"]
    lo = max(min_ratio, torque / el["peak_torque_Nm"])
    hi = min(max_ratio, el["no_load_speed_rpm"] * RPM_TO_RAD_S / speed)
    if lo <= hi:
        whole = [float(r) for r in range(math.ceil(lo), math.floor(hi) + 1)]
        return sorted(set(whole + [math.floor(hi * 100) / 100]))
    mid = math.sqrt(torque / el["peak_torque_Nm"] * el["no_load_speed_rpm"] * RPM_TO_RAD_S / speed)
    return [round(min(max_ratio, max(min_ratio, mid)), 2)]


def rank(rows):
    return sorted(rows, key=lambda r: (not r["meets"], round(r["shortfall"], 12),
                                       math.inf if r["score"] is None else r["score"], r["motor"], r["gb_type"]))


def best_per_pair(rows):
    """The best confirmed design of each (motor, type)."""
    best = {}
    for r in rank(rows):
        best.setdefault((r["motor"], r["gb_type"]), r)
    return rank(best.values())


def print_table(rows, n):
    gear = lambda r: " ".join(f"{c}={r[c]}" for c in GEAR_COLUMNS if r.get(c) is not None)  # noqa: E731
    print(f"\n{'#':>2} {'motor':18} {'type':18} {'ratio':>6} {'meets':5} {'torque':>8} {'speed':>8} "
          f"{'mass':>6} {'width':>6} {'dia':>6} {'eff':>5} {'score':>6}  gears")
    print(f"{'':2} {'':18} {'':18} {'':6} {'':5} {'N m':>8} {'rad/s':>8} {'kg':>6} {'mm':>6} {'mm':>6} {'':5} {'':6}")
    for i, r in enumerate(rows[:n], 1):
        score = "-" if r["score"] is None else f"{r['score']:.3f}"
        print(f"{i:>2} {r['motor']:18} {r['gb_type']:18} {r['ratio']:6.2f} {'yes' if r['meets'] else 'no':5} "
              f"{r['peak_torque_out_Nm']:8.2f} {r['no_load_speed_out_rad_s']:8.2f} {r['mass_kg']:6.3f} "
              f"{1000 * (r['width_with_driver_m'] or 0):6.1f} {1000 * (r['dia_body_m'] or 0):6.1f} "
              f"{r['efficiency']:5.3f} {score:>6}  {gear(r)}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--torque", type=float, required=True, help="output peak torque needed, N m")
    sp = ap.add_mutually_exclusive_group(required=True)
    sp.add_argument("--speed", type=float, help="output no-load speed needed, rad/s")
    sp.add_argument("--speed_rpm", type=float, help="output no-load speed needed, rpm")
    ap.add_argument("--material", default="3dp", choices=MATERIALS)
    ap.add_argument("--motors", nargs="+", help="only these motors (default: all)")
    ap.add_argument("--types", nargs="+", help="only these gearbox types")
    ap.add_argument("--rule", default="real_width", choices=("real_width", "compact_cost"))
    ap.add_argument("--map", type=Path, help="map folder for screening (default: the latest in maps/)")
    ap.add_argument("--no-map", dest="no_map", action="store_true", help="skip screening: optimise every motor and type")
    ap.add_argument("--shortlist", type=int, default=8, help="screened candidates to confirm (default 8)")
    ap.add_argument("--margin", type=float, default=0.02, help="extra torque and speed asked of the fits (default 0.02)")
    ap.add_argument("--rounds", type=int, default=2, help="ratio corrections per design that misses (default 2)")
    ap.add_argument("--min_ratio", type=float, default=4.0, help="--no-map: lowest ratio tried (default 4)")
    ap.add_argument("--max_ratio", type=float, default=40.0, help="--no-map: highest ratio tried (default 40)")
    ap.add_argument("--top", type=int, default=10, help="rows printed (default 10)")
    ap.add_argument("--name", help="run folder: runs/select_<name>/ (default from the ask)")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    args = ap.parse_args(argv)

    torque = args.torque
    speed = args.speed if args.speed is not None else args.speed_rpm * RPM_TO_RAD_S
    if torque <= 0 or speed <= 0:
        ap.error("torque and speed must be positive")
    motors_json, gains = load_motors(), load_gains()
    unknown = [m for m in args.motors or [] if m not in motors_json]
    if unknown:
        ap.error(f"unknown motor(s): {', '.join(unknown)}")
    name = args.name or f"{torque:g}Nm_{speed:.4g}rads_{args.material}{'_nomap' if args.no_map else ''}"
    out = RUNS_DIR / f"select_{name}"
    out.mkdir(parents=True, exist_ok=True)
    started, commit = time.time(), git_commit()
    print(f"ask: {torque:g} N m peak, {speed:.4g} rad/s ({speed / RPM_TO_RAD_S:.4g} rpm) no-load, {args.material}")
    if commit.endswith("-dirty"):
        print("note: uncommitted changes in the optimiser code or config", flush=True)

    info = {"ask": {"torque_Nm": torque, "speed_rad_s": speed, "material": args.material},
            "options": {k: (str(v) if isinstance(v, Path) else v) for k, v in vars(args).items()},
            "commit": commit, "started": datetime.now(timezone.utc).isoformat(timespec="seconds")}

    if args.no_map:
        jobs = [(gb, m, r, args.material)
                for m in (args.motors or sorted(motors_json))
                for gb in types_for(motors_json[m]["type"]) if not args.types or gb in args.types
                for r in no_map_ratios(motors_json[m], torque, speed, args.min_ratio, args.max_ratio)]
        print(f"--no-map: {len(jobs)} optimiser runs on {args.workers} workers", flush=True)
        screened = []
    else:
        map_dir = args.map or latest_map()
        if map_dir is None:
            ap.error("no released map in tools/actuator_map/maps/; use --map or --no-map")
        amap = ActuatorMap(map_dir)
        stale = stale_files(amap.meta.get("commit"))
        info["map"] = {"path": str(map_dir), "commit": amap.meta.get("commit"), "changed_since": stale}
        print(f"map: {map_dir} (sweep commit {str(amap.meta.get('commit'))[:7]})")
        if stale:
            print(f"warning: {len(stale)} optimiser file(s) changed since the map's sweep; screening may be "
                  f"off (confirmation uses the current code): {', '.join(stale[:5])}{' ...' if len(stale) > 5 else ''}")
        cands = amap.select(torque * (1 + args.margin), speed * (1 + args.margin), args.material,
                            motors=args.motors, types=args.types, rule=args.rule)
        meeting = {c.motor for c in cands if c.meets}
        beyond = sorted({c.motor for c in cands if c.flags.get("window_beyond_map") and c.motor not in meeting})
        if beyond:
            print(f"note: outside the map's ratios for {', '.join(beyond)}; try --no-map for them")
        screened = [{"motor": c.motor, "gb_type": c.gb_type, "ratio": c.ratio, "meets": c.meets,
                     "shortfall": c.shortfall, "window": c.window, "score": c.score, "mass_kg": c.actuator.mass,
                     "flags": c.flags} for c in cands]
        jobs = [(c.gb_type, c.motor, round(c.ratio, 3), args.material) for c in cands[:args.shortlist]]
        print(f"screened {len(cands)} (motor, type): {sum(c.meets for c in cands)} meet the ask in the map; "
              f"confirming {len(jobs)} on {min(args.workers, max(1, len(jobs)))} workers", flush=True)

    rows, errors, done = [], [], set()
    for round_no in range(args.rounds + 1):
        jobs = [j for j in jobs if j not in done]
        if not jobs:
            break
        if round_no:
            print(f"round {round_no}: {len(jobs)} design(s) re-run at a corrected ratio", flush=True)
        done.update(jobs)
        retry = []
        for (gb, motor, ratio, material), res in run_jobs(jobs, args.workers, out):
            if not res.get("feasible"):
                errors.append({"gb_type": gb, "motor": motor, "ratio_requested": ratio, "error": res.get("error")})
                continue
            row = evaluate(res, motors_json[motor], gains, torque, speed, args.rule)
            row["cad_dir"] = str(out / "cads" / f"{motor}__{gb}__{ratio_tag(ratio)}")
            row["round"] = round_no
            rows.append(row)
            if not row["meets"] and not args.no_map:
                r = corrected_ratio(row, motors_json[motor], torque, speed)
                if r is not None:
                    retry.append((gb, motor, r, material))
        jobs = retry

    ranked = best_per_pair(rows)
    print_table(ranked, args.top)
    if not ranked:
        print("no design found")
    elif not ranked[0]["meets"]:
        print("\nno design meets the ask; the rows are the closest misses")
    if errors:
        print(f"\n{len(errors)} run(s) without a design (no design at that ratio, or an optimiser error)")
    info.update({"elapsed_s": round(time.time() - started, 1), "ranked": ranked, "all_runs": rows,
                 "no_design": errors, "screened": screened})
    (out / "result.json").write_text(json.dumps(info, indent=1, default=str), encoding="utf-8")
    print(f"\n{time.time() - started:.0f} s; written to {out}")
    return ranked


if __name__ == "__main__":
    main()
