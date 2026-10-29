"""Plot how well the map's fits follow the designs: the designs, the smooth fit, the interp line, a
band of +-fit_error_flag_rel (5 %) around the fit, and below it the error at each design.

    # one gearbox type, several quantities
    python tools/actuator_map/plot_fit.py type tools/actuator_map/maps/v1 U8_Lite 3dp dspg out.png
    python tools/actuator_map/plot_fit.py type MAP MOTOR MATERIAL GB_TYPE OUT.png mass_kg efficiency

    # every gearbox type with one motor, one quantity
    python tools/actuator_map/plot_fit.py overview tools/actuator_map/maps/v1 3dp out.png [mass_kg]

MAP is a released map folder or a run folder. Needs matplotlib (requirements-dev.txt).
"""
import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.actuator_map.map import ActuatorMap  # noqa: E402

LABELS = {"mass_kg": (1000, "mass [g]"), "width_with_driver_m": (1000, "width with driver [mm]"),
          "width_body_m": (1000, "body width [mm]"), "dia_body_m": (1000, "body diameter [mm]"),
          "dia_widest_m": (1000, "widest diameter [mm]"), "efficiency": (100, "efficiency [%]"),
          "torque_carried_fraction": (100, "torque carried [%]")}
# One motor per motor type, so every gearbox type appears once in the overview.
OVERVIEW = [("U8_Lite", t) for t in ("sspg", "cpg", "dspg", "wpg")] + \
           [("RO100", t) for t in ("isspg_compact", "isspg_inside", "icpg", "idspg")] + \
           [("RI100", t) for t in ("insspg_type_1", "insspg_type_2", "incpg_dependent", "incpg_independent",
                                   "indspg", "inwpg_dependent", "inwpg_independent")]


def draw(amap, tf, q, ax, axe, legend=False):
    """One quantity of one type: fit and designs on ax, error per design on axe. Returns the fit."""
    limit = amap.meta.get("fit_error_flag_rel", 0.05)
    s, _ = LABELS[q]
    f = tf["quantities"][q]
    x, y = np.array(f["x"]), np.array(f["y"])
    xs = np.linspace(x.min(), x.max(), 400)
    fit = np.array([amap._values(tf, v, "fit")[0][q] for v in xs])
    for b in f.get("breaks", []):                       # a gap at each break, so the step shows
        fit[np.argmin(abs(xs - b))] = np.nan
    err = (np.array([amap._values(tf, v, "fit")[0][q] for v in x]) - y) / y * 100
    off = np.abs(err) > limit * 100
    ax.fill_between(xs, fit * s * (1 - limit), fit * s * (1 + limit), color="tab:blue", alpha=0.12,
                    label=f"fit ±{limit:.0%}")
    ax.plot(x, y * s, color="0.6", lw=0.9, label="interp (designs joined)")
    ax.plot(xs, fit * s, color="tab:blue", lw=1.8, label="fit")
    ax.scatter(x[~off], y[~off] * s, color="k", s=12, zorder=3, label="designs")
    ax.scatter(x[off], y[off] * s, color="tab:red", s=18, zorder=3, label=f"design > {limit:.0%} off")
    for b in f.get("breaks", []):
        for a in (ax, axe):
            a.axvline(b, color="tab:orange", ls="--", lw=0.9)
    axe.bar(x, err, width=0.3, color=np.where(off, "tab:red", "tab:blue"))
    axe.axhspan(-limit * 100, limit * 100, color="tab:blue", alpha=0.08)
    axe.axhline(0, color="k", lw=0.6)
    axe.set_xlim(ax.get_xlim())
    for a in (ax, axe):
        a.grid(alpha=0.3)
    ax.tick_params(labelbottom=False)
    axe.set_xlabel("gear ratio")
    if legend:
        ax.legend(fontsize=7)
    return f


def stats(f):
    return (f"RMS {f['rms_rel']*100:.1f} %  max {f['max_rel']*100:.1f} %  "
            f"{'+'.join('d%d' % p['degree'] for p in f['pieces'])}")


def plot_type(amap, motor, material, gb, out, quantities):
    tf = amap._type(motor, material, gb)
    fig = plt.figure(figsize=(5.2 * len(quantities), 6.2))
    grid = fig.add_gridspec(2, len(quantities), height_ratios=[2.3, 1], hspace=0.08, wspace=0.3)
    for k, q in enumerate(quantities):
        ax, axe = fig.add_subplot(grid[0, k]), fig.add_subplot(grid[1, k])
        f = draw(amap, tf, q, ax, axe, legend=k == 0)
        ax.set_title(f"{LABELS[q][1]}\n{stats(f)}", fontsize=10)
        ax.set_ylabel(LABELS[q][1])
        axe.set_ylabel("fit − design [%]")
    fig.suptitle(f"{motor} · {material} · {gb}", fontsize=13)
    fig.savefig(out, dpi=110, bbox_inches="tight")


def plot_overview(amap, material, out, q):
    limit = amap.meta.get("fit_error_flag_rel", 0.05)
    cols, rows = 5, 3
    fig = plt.figure(figsize=(4.0 * cols, 4.6 * rows))
    outer = fig.add_gridspec(rows, cols, hspace=0.42, wspace=0.32)
    for n, (motor, gb) in enumerate(OVERVIEW):
        inner = outer[n // cols, n % cols].subgridspec(2, 1, height_ratios=[2.3, 1], hspace=0.08)
        ax, axe = fig.add_subplot(inner[0]), fig.add_subplot(inner[1])
        try:
            tf = amap._type(motor, material, gb)
        except KeyError:
            ax.text(0.5, 0.5, "no designs", ha="center", va="center", transform=ax.transAxes)
            ax.set_title(f"{gb} ({motor})", fontsize=9)
            continue
        f = draw(amap, tf, q, ax, axe)
        ax.set_title(f"{gb}  ({motor}, n={len(f['x'])})\n{stats(f)}", fontsize=9,
                     color="tab:red" if f["max_rel"] > limit else "k")
        ax.tick_params(labelsize=7)
        axe.tick_params(labelsize=7)
        if n % cols == 0:
            ax.set_ylabel(LABELS[q][1], fontsize=8)
            axe.set_ylabel("fit−design %", fontsize=8)
    fig.suptitle(f"{material} · {LABELS[q][1].split(' [')[0]}: designs (dots), fit (blue), ±{limit:.0%} band, "
                 f"designs more than {limit:.0%} off in red, piece breaks dashed; red title: some design "
                 f"over {limit:.0%} off", fontsize=12)
    fig.savefig(out, dpi=100, bbox_inches="tight")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="mode", required=True)
    t = sub.add_parser("type", help="one gearbox type, several quantities")
    t.add_argument("map"), t.add_argument("motor"), t.add_argument("material"), t.add_argument("gb_type")
    t.add_argument("out"), t.add_argument("quantities", nargs="*", help=f"any of {', '.join(LABELS)}")
    o = sub.add_parser("overview", help="every gearbox type with one motor, one quantity")
    o.add_argument("map"), o.add_argument("material"), o.add_argument("out")
    o.add_argument("quantity", nargs="?", default="mass_kg", choices=list(LABELS))
    args = ap.parse_args(argv)
    bad = [q for q in getattr(args, "quantities", []) if q not in LABELS]
    if bad:
        ap.error(f"unknown quantity: {', '.join(bad)}; choose from {', '.join(LABELS)}")
    amap = ActuatorMap(args.map)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    if args.mode == "type":
        plot_type(amap, args.motor, args.material, args.gb_type, args.out, args.quantities or
                  ["mass_kg", "width_with_driver_m", "efficiency"])
    else:
        plot_overview(amap, args.material, args.out, args.quantity)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
