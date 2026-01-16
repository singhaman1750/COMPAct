import pandas as pd
import matplotlib.pyplot as plt

# Load CSVs
df_sspg = pd.read_csv(r"./SSPG_MAD.csv")
df_cpg  = pd.read_csv(r"./CPG_MAD.csv")
df_wpg  = pd.read_csv(r"./WPG_MAD.csv")
df_dspg = pd.read_csv(r"./DSPG_MAD.csv")

# Function to add Cost column
def add_cost(df):
    df["Cost"] = df["mass"] - 2 * df["eff"] + 0.2 * df["Actuator_width"]
    return df

# Apply to all
df_sspg = add_cost(df_sspg)
df_cpg  = add_cost(df_cpg)
df_wpg  = add_cost(df_wpg)
df_dspg = add_cost(df_dspg)

# Add identifiers
df_sspg["Type"] = "SSPG"
df_cpg["Type"]  = "CPG"
df_wpg["Type"]  = "WPG"
df_dspg["Type"] = "DSPG"

# Combine all
df_all = pd.concat([df_sspg, df_cpg, df_wpg, df_dspg])

# Define what to plot 
y_metrics = ["mass", "eff", "Cost", "Actuator_width"]
x_metric = "gearRatio"

# Create 2x2 grid of plots
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()

for i, y in enumerate(y_metrics):
    ax = axes[i]
    for label, group in df_all.groupby("Type"):
        ax.plot(group[x_metric], group[y], marker="o", markersize=4, label=label)
    ax.set_xlabel("Gear Ratio")
    ax.set_ylabel(y.capitalize())
    ax.set_title(f"{y.capitalize()} vs Gear Ratio")
    ax.grid(True)

# Put legend outside
handles, labels = ax.get_legend_handles_labels()
fig.legend(handles, labels, loc="upper center", ncol=4)

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()
