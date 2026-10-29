"""Actuator-map fits: smooth functions of the gear ratio for each (motor, material, gearbox type).

    python tools/actuator_map/fit.py --name pilot

Reads a sweep run (via table.py) and writes into the run folder:
    fits.json   per motor / material / type: for each fitted quantity the polynomial coefficients,
                degree, error and the data points (for interpolation); the type's valid ratio
                intervals; the best type over the ratio range and the switch ratios
    fits.md     fit errors per type (worst marked) and the switch ratios
    plots/      one PNG per motor and material: mass, width, diameter, score vs ratio

Fitted quantities (against the design's real gear ratio): mass, widths, diameters, efficiency,
torque-carried fraction and the optimiser's cost. Output torque, speed and reflected inertia are
not fitted: they follow exactly from ratio, efficiency, fraction and the motor (see table.py).

Model: a polynomial of degree 0-3, the lowest whose RMS error is within FIT_TOLERANCE (1 %) of the
quantity's mean value above the best degree's. At most (n-1)//2 for n points (4 points: a straight
line), so a fit follows the trend instead of bending through every point. The designs are
discrete (teeth, modules, bearings), so neighbouring ratios scatter around the trend; the data
points are kept for exact piecewise-linear interpolation.

Best type at any ratio: each type valid there gets the real-width score from its fitted values
(table.py's formula, ratio error 0), the 80 % torque rule is applied, and the lowest wins. Switch
ratios are where that winner changes (scanned in SCAN_STEP steps, then refined by bisection).
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from numpy.polynomial import Polynomial

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools.actuator_map.table import (  # noqa: E402
    MIN_CARRIED_FRACTION_FOR_BEST, RUNS_DIR, build_rows, load_cases, load_gains)

QUANTITIES = ("mass_kg", "width_body_m", "width_with_driver_m", "dia_body_m", "dia_widest_m",
              "efficiency", "torque_carried_fraction", "compact_cost")
FIT_TOLERANCE = 0.01   # extra RMS allowed for a lower degree, as a share of the mean value
MAX_DEGREE = 3
SCAN_STEP = 0.01
WORST_REL_ERROR = 0.05  # fits.md marks quantities whose largest error is above 5 %


# ---- one quantity -------------------------------------------------------------------------------

def fit_quantity(x, y):
    """Polynomial fit of y(x); returns coef (low -> high, plain x), degree and errors."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    scale = max(float(np.mean(np.abs(y))), 1e-12)
    max_deg = max(0, min(MAX_DEGREE, (len(x) - 1) // 2))
    fits = []
    for deg in range(max_deg + 1):
        p = Polynomial.fit(x, y, deg).convert() if len(set(x)) > deg else Polynomial([float(np.mean(y))])
        rms = float(np.sqrt(np.mean((p(x) - y) ** 2)))
        fits.append((deg, p, rms))
    best_rms = min(f[2] for f in fits)
    deg, p, rms = next(f for f in fits if f[2] <= best_rms + FIT_TOLERANCE * scale)
    err = p(x) - y
    rel = np.abs(err) / np.maximum(np.abs(y), 1e-12)
    return {"coef": [float(c) for c in p.coef], "degree": deg, "rms": rms, "rms_rel": rms / scale,
            "max_abs": float(np.max(np.abs(err))), "max_rel": float(np.max(rel)),
            "x": [float(v) for v in x], "y": [float(v) for v in y]}


def evaluate(fit, x):
    value = float(Polynomial(fit["coef"])(x))
    return value


def interpolate(fit, x):
    """Piecewise-linear through the data points (exact at the designs)."""
    return float(np.interp(x, fit["x"], fit["y"]))


# ---- one type -----------------------------------------------------------------------------------

def valid_intervals(points, grid_step):
    """Runs of consecutive swept ratios with a design -> [low, high], covering both the requested
    and the real ratios (a request of 30 may give 29.57; the type still counts as valid up to 30)."""
    pts = sorted(points)  # (requested, real)
    runs = []
    for req, real in pts:
        if runs and req - runs[-1]["req"] <= grid_step * 1.001:
            runs[-1]["req"] = req
            runs[-1]["hi"] = max(runs[-1]["hi"], real, req)
            runs[-1]["lo"] = min(runs[-1]["lo"], real, req)
        else:
            runs.append({"req": req, "lo": min(real, req), "hi": max(real, req)})
    return [[r["lo"], r["hi"]] for r in runs]


def fit_type(rows, grid_step):
    x = [r["ratio"] for r in rows]
    out = {"n_points": len(rows), "ratio_range": [min(x), max(x)],
           "valid_intervals": valid_intervals([(r["ratio_requested"], r["ratio"]) for r in rows], grid_step),
           "quantities": {}}
    for q in QUANTITIES:
        pts = [(r["ratio"], r[q]) for r in rows if r[q] is not None]
        if pts:
            out["quantities"][q] = fit_quantity(*zip(*sorted(pts)))
    return out


def is_valid(type_fit, x):
    return any(lo - 1e-9 <= x <= hi + 1e-9 for lo, hi in type_fit["valid_intervals"])


def fitted_values(type_fit, x):
    v = {q: evaluate(f, x) for q, f in type_fit["quantities"].items()}
    if "torque_carried_fraction" in v:
        v["torque_carried_fraction"] = min(1.0, max(0.0, v["torque_carried_fraction"]))
    return v


def real_width_score(values, gains):
    """table.py's real-width score from fitted values (the design is taken to hit the ratio)."""
    return (gains["K_Mass"] * values["mass_kg"] + gains["K_Eff"] * values["efficiency"]
            + gains["K_Width_real"] * values["width_with_driver_m"] * 1000
            + gains["K_torque_shortfall"] * (1 - values.get("torque_carried_fraction", 1.0)))


# ---- best type over the ratio range -------------------------------------------------------------

def best_type(types, x, gains, rule="real_width"):
    """Best valid type at ratio x by fitted score with the 80 % rule; None if no type is valid."""
    scored = []
    for gb, tf in types.items():
        if not is_valid(tf, x):
            continue
        v = fitted_values(tf, x)
        if rule == "real_width":
            if "width_with_driver_m" not in v:
                continue
            score = real_width_score(v, gains)
        else:
            score = v["compact_cost"]
        scored.append((score, gb, v.get("torque_carried_fraction", 1.0)))
    if not scored:
        return None
    full = [s for s in scored if s[2] >= MIN_CARRIED_FRACTION_FOR_BEST]
    return min(full or scored)[1]


def switch_points(types, gains, lo, hi, rule="real_width"):
    """Intervals of the best type and the ratios where it changes."""
    xs = np.arange(lo, hi + SCAN_STEP / 2, SCAN_STEP)
    labels = [best_type(types, float(x), gains, rule) for x in xs]
    intervals, switches = [], []
    start = 0
    for i in range(1, len(xs) + 1):
        if i == len(xs) or labels[i] != labels[start]:
            if i < len(xs):  # refine the change between xs[i-1] and xs[i]
                a, b = float(xs[i - 1]), float(xs[i])
                for _ in range(30):
                    m = (a + b) / 2
                    if best_type(types, m, gains, rule) == labels[start]:
                        a = m
                    else:
                        b = m
                edge = (a + b) / 2
                switches.append({"ratio": round(edge, 4), "from": labels[start], "to": labels[i]})
            end = switches[-1]["ratio"] if i < len(xs) else float(xs[-1])
            begin = intervals[-1][1] if intervals else float(xs[0])
            intervals.append([round(begin, 4), round(end, 4), labels[start] or "none"])
            start = i
    keep = [iv for iv in intervals if iv[1] - iv[0] > SCAN_STEP / 2]
    switches = [s for s in switches if s["from"] and s["to"]
                and any(abs(iv[1] - s["ratio"]) < 1e-9 for iv in keep)]
    return keep, switches


# ---- whole run ----------------------------------------------------------------------------------

def build_fits(rows, grid_step, gains):
    grouped = defaultdict(lambda: defaultdict(list))
    for r in rows:
        grouped[(r["motor"], r["material"])][r["gb_type"]].append(r)
    result = {}
    for (motor, material), by_type in sorted(grouped.items()):
        types = {gb: fit_type(rs, grid_step) for gb, rs in sorted(by_type.items())}
        # the requested range: a design's real ratio can overshoot it slightly (30 -> 30.33)
        lo = min(r["ratio_requested"] for rs in by_type.values() for r in rs)
        hi = max(r["ratio_requested"] for rs in by_type.values() for r in rs)
        entry = {"types": types}
        for rule in ("real_width", "compact"):
            intervals, switches = switch_points(types, gains, lo, hi, rule)
            entry[f"best_{rule}"] = intervals
            entry[f"switches_{rule}"] = switches
        # where the fitted best differs from the table's winner at a swept ratio
        table_best = {(r["ratio_requested"]): r["gb_type"] for rs in by_type.values() for r in rs if r["best_by_real_width"]}
        entry["differs_from_table"] = [
            {"ratio": req, "table": t, "fitted": best_type(types, req, gains)}
            for req, t in sorted(table_best.items()) if best_type(types, req, gains) not in (t, None)]
        result.setdefault(motor, {})[material] = entry
    return result


def report(fits):
    lines = ["# Actuator map fits", "",
             f"Polynomial fits against the real gear ratio (degree 0–{MAX_DEGREE}). Each cell: typical error (RMS)",
             "/ largest error over the design points, in % of the value (the optimiser's cost: absolute,",
             f"since it can be near zero), and the degree. Largest errors above {WORST_REL_ERROR:.0%} are **bold**:",
             "usually real scatter between neighbouring designs (discrete teeth, modules, bearings).", ""]
    short = {"mass_kg": "mass", "width_body_m": "width", "width_with_driver_m": "width+drv", "dia_body_m": "Ø body",
             "dia_widest_m": "Ø widest", "efficiency": "η", "torque_carried_fraction": "fraction", "compact_cost": "cost"}
    for motor, by_mat in fits.items():
        for material, e in by_mat.items():
            lines += [f"## {motor}, {material}", ""]
            for rule in ("real_width", "compact"):
                lines.append(f"- **best ({rule.replace('_', ' ')}):** " + ", ".join(
                    f"{a:.2f}–{b:.2f} {t}" for a, b, t in e[f"best_{rule}"]))
            if e["differs_from_table"]:
                lines.append("- **fitted best differs from the table at:** " + ", ".join(
                    f"{d['ratio']:g} ({d['table']} → {d['fitted']})" for d in e["differs_from_table"]))
            lines += ["", "| Type | Points | Range | " + " | ".join(short[q] for q in QUANTITIES) + " |",
                      "|---|---|---|" + "---|" * len(QUANTITIES)]
            for gb, tf in e["types"].items():
                cells = []
                for q in QUANTITIES:
                    f = tf["quantities"].get(q)
                    if f is None:
                        cells.append("—")
                        continue
                    if q == "compact_cost":
                        cells.append(f"{f['rms']:.2f} / {f['max_abs']:.2f} (d{f['degree']})")
                        continue
                    txt = f"{100 * f['rms_rel']:.1f} / {100 * f['max_rel']:.1f} % (d{f['degree']})"
                    cells.append(f"**{txt}**" if f["max_rel"] > WORST_REL_ERROR else txt)
                lines.append(f"| {gb} | {tf['n_points']} | {tf['ratio_range'][0]:.1f}–{tf['ratio_range'][1]:.1f} | "
                             + " | ".join(cells) + " |")
            lines.append("")
    return "\n".join(lines) + "\n"


def plot(fits, gains, out_dir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    out_dir.mkdir(parents=True, exist_ok=True)
    panels = (("mass_kg", "mass [kg]", 1), ("width_with_driver_m", "width with driver [mm]", 1000),
              ("dia_body_m", "body diameter [mm]", 1000), (None, "real-width score", 1))
    for motor, by_mat in fits.items():
        for material, e in by_mat.items():
            fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True)
            for ax, (q, label, k) in zip(axes.flat, panels):
                for i, (gb, tf) in enumerate(e["types"].items()):
                    color = f"C{i}"
                    for lo, hi in tf["valid_intervals"]:
                        xs = np.linspace(lo, hi, 60)
                        if q is None:
                            if "width_with_driver_m" not in tf["quantities"]:
                                continue
                            ys = [real_width_score(fitted_values(tf, x), gains) for x in xs]
                        else:
                            ys = [evaluate(tf["quantities"][q], x) * k for x in xs] if q in tf["quantities"] else []
                        if len(ys):
                            ax.plot(xs, ys, color=color, label=gb if lo == tf["valid_intervals"][0][0] else None)
                    if q is not None and q in tf["quantities"]:
                        f = tf["quantities"][q]
                        ax.plot(f["x"], [v * k for v in f["y"]], "o", color=color, ms=3)
                for s in e["switches_real_width"]:
                    ax.axvline(s["ratio"], color="grey", ls=":", lw=1)
                ax.set_ylabel(label)
                ax.grid(alpha=0.3)
            axes[0, 0].legend(fontsize=8)
            for ax in axes[1]:
                ax.set_xlabel("gear ratio")
            best = ", ".join(f"{a:.1f}–{b:.1f} {t}" for a, b, t in e["best_real_width"])
            fig.suptitle(f"{motor}, {material} — best (real width): {best}", fontsize=10)
            fig.tight_layout()
            fig.savefig(out_dir / f"{motor}_{material}.png", dpi=110)
            plt.close(fig)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--name", required=True, help="run folder under tools/actuator_map/runs/")
    ap.add_argument("--no-plots", action="store_true")
    args = ap.parse_args(argv)
    run_dir = RUNS_DIR / args.name
    run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    ratios = sorted(run["ratios"])
    grid_step = min(b - a for a, b in zip(ratios, ratios[1:])) if len(ratios) > 1 else 1.0
    gains = load_gains()
    rows = build_rows(load_cases(run_dir))
    fits = build_fits(rows, grid_step, gains)
    meta = {"run": args.name, "commit": run.get("commit"), "gains": gains, "grid_step": grid_step,
            "min_carried_fraction_for_best": MIN_CARRIED_FRACTION_FOR_BEST, "quantities": list(QUANTITIES)}
    (run_dir / "fits.json").write_text(json.dumps({"meta": meta, "motors": fits}, indent=1), encoding="utf-8")
    (run_dir / "fits.md").write_text(report(fits), encoding="utf-8")
    if not args.no_plots:
        plot(fits, gains, run_dir / "plots")
    print(f"fitted {sum(len(e['types']) for m in fits.values() for e in m.values())} types; "
          f"wrote fits.json, fits.md{'' if args.no_plots else ', plots/'} in {run_dir}")


if __name__ == "__main__":
    main()
