"""Actuator-map table: turn a sweep's case files into one table per material.

    python tools/actuator_map/table.py --name pilot

Reads tools/actuator_map/runs/<name>/cases (from sweep.py), config_files/motors.json and
config_files/cost.json, and writes into the same run folder:
    table_3dp.csv, table_metal.csv   one row per (motor, requested ratio, gearbox type) with a design
    summary.md                       per motor and material: the best type at each ratio (both
                                     rules), where it changes, each type's ratio range, no-design /
                                     error counts

Units are SI (m, kg, N m, rad/s, kg m^2); speeds are also given in rpm.

Output torque and speed (motor values from motors.json, efficiency from COMPAct):
    peak torque  = motor peak torque x ratio x efficiency x torque_carried_fraction
    rated torque = min(motor rated torque, torque_carried_fraction x motor peak torque) x ratio x efficiency
                   (gears capped to carry part of the peak can still carry a smaller rated torque)
    speeds       = motor no-load / rated speed / ratio
    reflected rotor inertia = ratio^2 x motor rotor inertia (the gears' own inertia is not included yet)

Two scores pick the best type at each (motor, ratio, material); lower is better:
    compact_cost      the optimiser's own cost (planet face widths for width)
    real_width_score  K_Mass*mass + K_Eff*efficiency + K_Width_real*(width with driver mount, mm)
                      + |ratio - requested| + K_torque_shortfall*(1 - torque_carried_fraction)
Gains come from config_files/cost.json. The real-width score is the map's main rule; the
optimiser's cost is kept as a second one. Rules for "best" (pilot review, 2026-10-29):
  - a capped design can be best only if its gears carry >= MIN_CARRIED_FRACTION_FOR_BEST of the
    peak torque; if no design of that motor/ratio/material does, the best of all is still given
    and every row of the group is marked no_full_torque_design
  - near_best_* lists every type whose score is within NEAR_BEST_REL of the best (near-ties, where
    the winner can flip from one ratio to the next)
"""
import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

RUNS_DIR = REPO / "tools" / "actuator_map" / "runs"
MIN_CARRIED_FRACTION_FOR_BEST = 0.8   # capped designs below this can't be best (if anything else exists)
NEAR_BEST_REL = 0.02                  # near-best: score within 2 % of the best
MATERIALS = ("3dp", "metal")
RPM_TO_RAD_S = 2 * math.pi / 60

# Open CAD issues (ISSUES.md) per gearbox type: the CAD model may need a fix for some designs.
OPEN_CAD_ISSUES = {
    "sspg": ["CAD1"],               # sun-gear countersink radius not parametric
    "dspg": ["CAD3"],               # stage-1 ring split with small motors
    "incpg_dependent": ["CAD4"],    # extra material in the ring teeth
    "incpg_independent": ["CAD5"],  # casing feature loses its face, two mates fail
    "idspg": ["CAD6"],              # stage-2 parts don't move (seen with RO80)
    "inwpg_dependent": ["CAD7"],    # output ring / bearing don't move (seen with RI80)
}

# CAD variable -> common gear column, per family. Two-stage types: stage 1 from a1_*, stage 2
# from a2_* (the a1_*2 copies are the same values).
GEAR_COLUMNS = ("ns", "np", "np_small", "nr", "nr_small", "module", "n_planets",
                "ns_2", "np_2", "nr_2", "module_2", "n_planets_2")
_SINGLE = {"ns": "Ns", "np": "Np", "nr": "Nr", "module": "module", "n_planets": "num_planet"}
_COMPOUND = {"ns": "Ns", "np": "Np_b", "np_small": "Np_s", "nr": "Nr", "module": "module", "n_planets": "num_planet"}
_WOLFROM = {"ns": "Ns", "np": "Np_b", "np_small": "Np_s", "nr": "Nr_b", "nr_small": "Nr_s", "module": "module",
            "n_planets": "num_planet"}
_DOUBLE = {"ns": "a1_Ns", "np": "a1_Np", "nr": "a1_Nr", "module": "a1_module", "n_planets": "a1_num_planet",
           "ns_2": "a2_Ns", "np_2": "a2_Np", "nr_2": "a2_Nr", "module_2": "a2_module", "n_planets_2": "a2_num_planet"}
GEAR_VARS = {
    **{t: _SINGLE for t in ("sspg", "isspg_inside", "isspg_compact", "insspg_type_1", "insspg_type_2")},
    **{t: _COMPOUND for t in ("cpg", "icpg", "incpg_dependent", "incpg_independent")},
    **{t: _WOLFROM for t in ("wpg", "inwpg_dependent", "inwpg_independent")},
    **{t: _DOUBLE for t in ("dspg", "idspg", "indspg")},
}

COLUMNS = (
    "motor", "motor_type", "material", "gb_type", "ratio_requested", "ratio",
    *GEAR_COLUMNS,
    "mass_kg", "width_body_m", "width_with_driver_m", "dia_body_m", "dia_widest_m", "efficiency",
    "torque_carried_fraction", "peak_torque_out_Nm", "rated_torque_out_Nm",
    "no_load_speed_out_rad_s", "rated_speed_out_rad_s", "no_load_speed_out_rpm", "rated_speed_out_rpm",
    "rotor_inertia_kgm2", "reflected_inertia_kgm2", "rotor_inertia_basis",
    "real_width_score", "compact_cost", "best_by_real_width", "best_by_compact_cost",
    "near_best_real_width", "near_best_compact", "no_full_torque_design",
    "torque_capped", "geometry_approx", "cad_issues", "commit",
)


def load_motors(path=REPO / "config_files" / "motors.json"):
    return json.loads(Path(path).read_text(encoding="utf-8"))["motors"]


def load_gains(path=REPO / "config_files" / "cost.json"):
    return json.loads(Path(path).read_text(encoding="utf-8"))["Cost_gain_parameters"]


def _mm_to_m(x):
    return None if x is None else x / 1000


def make_row(case, motor_entry, gains):
    """One table row from a feasible case (as written by sweep.py)."""
    v, gb = case["cad_vars"], case["gb_type"]
    ratio, eff, frac = case["gear_ratio"], case["efficiency"], case["torque_carried_fraction"]
    el, mech = motor_entry["electrical"], motor_entry.get("mechanical", {})
    gears = {col: v.get(var) for col, var in GEAR_VARS[gb].items()}
    gears = {col: (x if x is None or col.startswith("module") else int(round(x))) for col, x in gears.items()}  # counts
    width_drv_mm = case.get("width_with_driver_mm")
    real_score = None if width_drv_mm is None else (
        gains["K_Mass"] * case["mass_kg"] + gains["K_Eff"] * eff + gains["K_Width_real"] * width_drv_mm
        + abs(ratio - case["ratio_requested"]) + gains["K_torque_shortfall"] * (1 - frac))
    rated_motor = el.get("rated_torque_Nm")
    rated_speed = el.get("rated_speed_rpm")
    j_rotor = mech.get("rotor_inertia_kgm2")
    return {
        "motor": case["motor"], "motor_type": motor_entry["type"], "material": case["material"], "gb_type": gb,
        "ratio_requested": case["ratio_requested"], "ratio": ratio,
        **{col: gears.get(col) for col in GEAR_COLUMNS},
        "mass_kg": case["mass_kg"],
        "width_body_m": _mm_to_m(case.get("width_body_mm")),
        "width_with_driver_m": _mm_to_m(width_drv_mm),
        "dia_body_m": _mm_to_m(case.get("dia_body_mm")),
        "dia_widest_m": _mm_to_m(case.get("dia_widest_mm")),
        "efficiency": eff,
        "torque_carried_fraction": frac,
        "peak_torque_out_Nm": el["peak_torque_Nm"] * ratio * eff * frac,
        "rated_torque_out_Nm": None if rated_motor is None else min(rated_motor, frac * el["peak_torque_Nm"]) * ratio * eff,
        "no_load_speed_out_rad_s": el["no_load_speed_rpm"] * RPM_TO_RAD_S / ratio,
        "rated_speed_out_rad_s": None if rated_speed is None else rated_speed * RPM_TO_RAD_S / ratio,
        "no_load_speed_out_rpm": el["no_load_speed_rpm"] / ratio,
        "rated_speed_out_rpm": None if rated_speed is None else rated_speed / ratio,
        "rotor_inertia_kgm2": j_rotor,
        "reflected_inertia_kgm2": None if j_rotor is None else ratio ** 2 * j_rotor,
        "rotor_inertia_basis": mech.get("rotor_inertia_basis"),
        "compact_cost": case["cost"],
        "real_width_score": real_score,
        "best_by_real_width": False,
        "best_by_compact_cost": False,
        "near_best_real_width": "",
        "near_best_compact": "",
        "no_full_torque_design": False,
        "torque_capped": frac < 1,
        "geometry_approx": bool(case.get("geometry_notes")),
        "cad_issues": " ".join(OPEN_CAD_ISSUES.get(gb, [])),
        "commit": case.get("commit"),
    }


RULES = (("best_by_real_width", "near_best_real_width", "real_width_score"),
         ("best_by_compact_cost", "near_best_compact", "compact_cost"))


def mark_best(rows):
    """Per (motor, material, requested ratio): the best row by each rule, the near-best types and
    whether any design carries at least MIN_CARRIED_FRACTION_FOR_BEST of the peak torque."""
    groups = defaultdict(list)
    for r in rows:
        groups[(r["motor"], r["material"], r["ratio_requested"])].append(r)
    for group in groups.values():
        full = [r for r in group if r["torque_carried_fraction"] >= MIN_CARRIED_FRACTION_FOR_BEST]
        for r in group:
            r["no_full_torque_design"] = not full
        for flag, near_col, score in RULES:
            pool = [r for r in (full or group) if r[score] is not None]
            if not pool:
                continue
            best = min(pool, key=lambda r: (r[score], r["gb_type"]))
            best[flag] = True
            limit = best[score] + NEAR_BEST_REL * abs(best[score])
            near = " ".join(r["gb_type"] for r in sorted(pool, key=lambda r: (r[score], r["gb_type"])) if r[score] <= limit)
            for r in group:
                r[near_col] = near
    return rows


def load_cases(run_dir):
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted((Path(run_dir) / "cases").rglob("*.json"))]


def build_rows(cases, motors=None, gains=None):
    motors = motors or load_motors()
    gains = gains or load_gains()
    rows = [make_row(c, motors[c["motor"]], gains) for c in cases if c["feasible"]]
    rows.sort(key=lambda r: (r["material"], r["motor"], r["ratio_requested"], r["gb_type"]))
    return mark_best(rows)


def write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r[k] is None else r[k]) for k in COLUMNS})


def summary(cases, rows):
    lines = ["# Actuator map summary", "",
             "Best type at each requested ratio (lowest score): by the real-width score (the map's rule)",
             "and by the optimiser's cost. `*` = the winner's gears are capped (carry < 100 % of peak",
             f"torque); `~` = near-tie (another type within {NEAR_BEST_REL:.0%} of the best score); `!` = no design",
             f"carries {MIN_CARRIED_FRACTION_FOR_BEST:.0%} of the peak torque, so a more capped one is given.", ""]
    by_mm = defaultdict(list)
    for r in rows:
        by_mm[(r["motor"], r["material"])].append(r)
    for (motor, material), rs in sorted(by_mm.items()):
        lines += [f"## {motor}, {material}", ""]
        for (flag, near_col, _), title in zip(RULES, ("real width", "compact cost")):
            winners = sorted((r for r in rs if r[flag]), key=lambda r: r["ratio_requested"])
            runs, prev = [], None
            for r in winners:
                name = (r["gb_type"] + ("*" if r["torque_capped"] else "") + ("~" if " " in r[near_col] else "")
                        + ("!" if r["no_full_torque_design"] else ""))
                if prev and prev[0] == name:
                    prev[2] = r["ratio_requested"]
                else:
                    prev = [name, r["ratio_requested"], r["ratio_requested"]]
                    runs.append(prev)
            lines.append(f"- **{title}:** " + ", ".join(f"{a:g}–{b:g} {n}" if a != b else f"{a:g} {n}" for n, a, b in runs))
        ranges = defaultdict(list)
        for r in rs:
            ranges[r["gb_type"]].append(r["ratio_requested"])
        lines.append("- **ratio range with a design:** " + ", ".join(
            f"{t} {min(x):g}–{max(x):g} ({len(x)})" for t, x in sorted(ranges.items())))
        lines.append("")
    no_design = defaultdict(int)
    errors = defaultdict(int)
    for c in cases:
        if not c["feasible"]:
            (errors if c.get("error") else no_design)[(c["gb_type"], c["material"])] += 1
    lines += ["## Cases without a design", "",
              "| Type | Material | No design | Error |", "|---|---|---|---|"]
    for key in sorted(set(no_design) | set(errors)):
        lines.append(f"| {key[0]} | {key[1]} | {no_design.get(key, 0)} | {errors.get(key, 0)} |")
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--name", required=True, help="run folder under tools/actuator_map/runs/")
    args = ap.parse_args(argv)
    run_dir = RUNS_DIR / args.name
    cases = load_cases(run_dir)
    rows = build_rows(cases)
    for material in MATERIALS:
        part = [r for r in rows if r["material"] == material]
        if part:
            write_csv(part, run_dir / f"table_{material}.csv")
    (run_dir / "summary.md").write_text(summary(cases, rows), encoding="utf-8")
    print(f"{len(cases)} cases -> {len(rows)} rows; wrote table_*.csv and summary.md in {run_dir}")


if __name__ == "__main__":
    main()
