import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# File paths
SSPG_File1 = r"./sspg_backlash_sine_vel_2.500tps_2.00s.csv"
CPG_File2  = r"./cpg_backlash_sine_vel_2.500tps_2.00s.csv"

# Column names
x_col = "time_s"
y_col = "backlash_rad"

# Read CSV files
df_sspg = pd.read_csv(SSPG_File1)
df_cpg = pd.read_csv(CPG_File2)

# Compute averages
avg_sspg = df_sspg[y_col].mean()
avg_cpg = df_cpg[y_col].mean()

max_sspg = df_sspg[y_col].max()
max_cpg = df_cpg[y_col].max()

min_sspg = df_sspg[y_col].min()
min_cpg = df_cpg[y_col].min()

print(f"Average SSPG backlash_rad: {avg_sspg:.6f} rad")
print(f"Average CPG backlash_rad:  {avg_cpg:.6f} rad")

print(f"Maximum SSPG backlash_rad: {max_sspg:.6f} rad")
print(f"Maximum CPG backlash_rad:  {max_cpg:.6f} rad")

print(f"Minimum SSPG backlash_rad: {min_sspg:.6f} rad")
print(f"Minimum CPG backlash_rad:  {min_cpg:.6f} rad")

print(f"SSPG backlash_rad: {max_sspg-min_sspg:.6f} rad, {(max_sspg-min_sspg)*(180/np.pi):.6f} deg")
print(f"CPG backlash_rad:  {max_cpg-min_cpg:.6f} rad, {(max_cpg-min_cpg)*(180/np.pi):.6f} deg")

# Font sizes (modifiable)
axis_fontsize = 20
legend_fontsize = 18
tick_size = 18

# Plot
plt.figure(figsize=(10, 6))
plt.scatter(df_sspg[x_col], df_sspg[y_col], label=f"SSPG (7.2:1)",# Max_diff={max_sspg-min_sspg:.4f} rad",
            color="blue", s=15, alpha=0.7)
plt.scatter(df_cpg[x_col], df_cpg[y_col], label=f"CPG (14:1)",# Max_diff={max_cpg-min_cpg:.4f} rad",
            color="red", s=15, alpha=0.7)

# Labels and title
plt.xlabel("Time (s)", fontsize=axis_fontsize)
plt.ylabel("Backlash (rad)", fontsize=axis_fontsize)
plt.title("No-load backlash: SSPG(blue) and CPG(red)", fontsize=axis_fontsize)

# legend
# plt.legend(fontsize=legend_fontsize)
# plt.legend(fontsize=legend_fontsize, loc="upper left", bbox_to_anchor=(1, 0.5))
# plt.tight_layout(rect=[0, 0, 0.85, 1])  # give space for legend


# Grid
plt.grid(True, linestyle="--", alpha=0.6)

plt.tick_params(axis='both', which='major', labelsize=tick_size)  # change 12 to any size

plt.tight_layout()
plt.show()
