import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def _fit_line(x, y):
    """Return dict with slope m, intercept b, and R²; None if not enough points."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.size < 2:
        return None
    m, b = np.polyfit(x, y, 1)
    yhat = m * x + b
    ss_res = np.sum((y - yhat) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan
    return {"m": m, "b": b, "r2": r2}

def plot_csv_data(file1, file2,
                  axis_fontsize=18,
                  tick_fontsize=16,
                  legend_fontsize=16,
                  line_width=3.0):
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # sanity check
    for idx, df in enumerate([df1, df2], start=1):
        for c in ["encoder_pos_rad", "output_torque_Nm"]:
            if c not in df.columns:
                raise KeyError(f"File {idx} is missing required column: {c}")

    # raw data
    x1, y1 = df1["output_torque_Nm"].astype(float), df1["encoder_pos_rad"].astype(float)
    x2, y2 = df2["output_torque_Nm"].astype(float), df2["encoder_pos_rad"].astype(float)

    # masks (exclude x == 0 from fits)
    pos1 = x1 > 0
    neg1 = x1 < 0
    pos2 = x2 > 0
    neg2 = x2 < 0

    y1 = y1 / 7.2   # SSPG
    y2 = y2 / 14    # CPG

    # fits
    fit1_pos = _fit_line(x1[pos1], y1[pos1]) if pos1.any() else None
    fit1_neg = _fit_line(x1[neg1], y1[neg1]) if neg1.any() else None
    fit2_pos = _fit_line(x2[pos2], y2[pos2]) if pos2.any() else None
    fit2_neg = _fit_line(x2[neg2], y2[neg2]) if neg2.any() else None

    # plot raw curves
    plt.figure(figsize=(9, 6))
    plt.plot(x1, y1, label="SSPG (7.2:1)", alpha=0.7, linewidth=line_width, color="blue")
    plt.plot(x2, y2, label="CPG (14:1)", alpha=0.7, linewidth=line_width, color="red")

    # helper to draw a fitted segment over its actual x-range
    def draw_fit(fit, x_subset, label_prefix, color):
        if fit is None or x_subset.size == 0:
            return
        xline = np.linspace(float(x_subset.min()), float(x_subset.max()), 100)
        yline = fit["m"] * xline + fit["b"]
        plt.plot(xline, yline, linestyle="--", color=color, linewidth=line_width)
                #  label=f"{label_prefix}: y={fit['m']:.4f}x+{fit['b']:.4f} (R²={fit['r2']:.3f})")

    # draw fits
    draw_fit(fit1_pos, x1[pos1], "SSPG fit (+)", "blue")
    draw_fit(fit1_neg, x1[neg1], "SSPG fit (−)", "blue")
    draw_fit(fit2_pos, x2[pos2], "CPG fit (+)", "red")
    draw_fit(fit2_neg, x2[neg2], "CPG fit (−)", "red")

    # labels, legend, grid
    plt.xlabel("Actuator Torque [Nm]", fontsize=axis_fontsize)
    plt.ylabel("Deflection [rad]", fontsize=axis_fontsize)
    plt.tick_params(axis='both', which='major', labelsize=tick_fontsize)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=legend_fontsize)
    plt.tight_layout()
    plt.show()

    # Optional: print stiffness (Nm/rad) for convenience
    def print_fit(name, fit):
        if fit is None:
            print(f"{name}: not enough points")
        else:
            stiffness = (1.0 / fit["m"]) if fit["m"] != 0 else np.inf
            print(f"{name}: slope={fit['m']:.6f} rad/Nm, intercept={fit['b']:.6f}, R²={fit['r2']:.4f}, "
                  f"stiffness≈{stiffness:.6f} Nm/rad")

    print_fit("SSPG (+)", fit1_pos)
    print_fit("SSPG (−)", fit1_neg)
    print_fit("CPG (+)", fit2_pos)
    print_fit("CPG (−)", fit2_neg)

# Example usage
plot_csv_data(
    r"./transmission_stiffness_sspg.csv",
    r"./transmission_stiffness_cpg.csv",
    axis_fontsize=20,
    tick_fontsize=18,
    legend_fontsize=18,
    line_width=3.0
)
