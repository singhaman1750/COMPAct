import pandas as pd
import matplotlib.pyplot as plt

# Load CSVs (fix Windows path with raw string)
df_cpg = pd.read_csv(r"C:\Users\Quant\Documents\GitHub\Actuator_Optimization_3D_printed\plots\simulation\gearbox performance comparison\CPG_MAD.csv")
df_dspg = pd.read_csv(r"C:\Users\Quant\Documents\GitHub\Actuator_Optimization_3D_printed\plots\simulation\gearbox performance comparison\DSPG_MAD.csv")
df_sspg = pd.read_csv(r"C:\Users\Quant\Documents\GitHub\Actuator_Optimization_3D_printed\plots\simulation\gearbox performance comparison\SSPG_MAD.csv")
df_wpg = pd.read_csv(r"C:\Users\Quant\Documents\GitHub\Actuator_Optimization_3D_printed\plots\simulation\gearbox performance comparison\WPG_MAD.csv")

# Add identifiers
df_cpg["Type"] = "CPG"
df_dspg["Type"] = "DSPG"
df_sspg["Type"] = "SSPG"
df_wpg["Type"] = "WPG"

# Combine all
df_all = pd.concat([df_cpg, df_dspg, df_sspg, df_wpg])

# Define what to plot
y_metrics = ["mass", "eff", "Cost", "Actuator_width"]
x_metric = "gearRatio"

# Create 2x2 grid of plots
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()  # Make it easier to loop over

for i, y in enumerate(y_metrics):
    ax = axes[i]
    for label, group in df_all.groupby("Type"):
        ax.plot(group[x_metric], group[y], marker="o", markersize=4, label=label)
    ax.set_xlabel("Gear Ratio")
    ax.set_ylabel(y.capitalize())
    ax.set_title(f"{y.capitalize()} vs Gear Ratio")
    ax.grid(True)

# Put legend outside to avoid overlap
handles, labels = ax.get_legend_handles_labels()
fig.legend(handles, labels, loc="upper center", ncol=4)

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()
