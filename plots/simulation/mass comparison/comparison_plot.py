import pandas as pd
import matplotlib.pyplot as plt

# Load CSVs (fix Windows path with raw string)
df_cpg = pd.read_csv(r"C:\Users\Quant\Documents\GitHub\Actuator_Optimization_3D_printed\plots\simulation\mass comparison\3DP Mass Comparison - cpg.csv")
df_sspg = pd.read_csv(r"C:\Users\Quant\Documents\GitHub\Actuator_Optimization_3D_printed\plots\simulation\mass comparison\3DP Mass Comparison - sspg.csv")
df_dspg = pd.read_csv(r"C:\Users\Quant\Documents\GitHub\Actuator_Optimization_3D_printed\plots\simulation\mass comparison\3DP Mass Comparison - dspg.csv")
df_wpg = pd.read_csv(r"C:\Users\Quant\Documents\GitHub\Actuator_Optimization_3D_printed\plots\simulation\mass comparison\3DP Mass Comparison - wpg.csv")

# Ordered list of (name, dataframe) pairs
data = [
    ("SSPG", df_sspg),
    ("DSPG", df_dspg),
    ("CPG", df_cpg),
    ("WPG", df_wpg)
]

# Create 2x2 subplot grid
fig, axes = plt.subplots(2, 2, figsize=(10, 6))
axes = axes.flatten()

for ax, (name, df) in zip(axes, data):
    # Plot Python vs SolidWorks mass
    ax.plot(df["Gear Ratio"], df["Mass Model Python"], marker="o", markersize=4, label="Mass Model")
    ax.plot(df["Gear Ratio"], df["Mass Solidworks"], marker="s", markersize=4, label="Mass SolidWorks")
    
    ax.set_title(f"{name} Mass vs Gear Ratio")
    ax.set_xlabel("Gear Ratio")
    ax.set_ylabel("Mass (g)")
    ax.grid(True)
    ax.legend()

plt.tight_layout()
plt.show()
