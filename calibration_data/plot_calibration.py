import io
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Read the CSV file
df = pd.read_csv("motor_calibration_20251027_150528.csv")

# Create figure with subplots
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Motor Calibration Analysis", fontsize=16, fontweight="bold")

# Plot 1: Voltage vs Vibration (scatter + mean line)
ax1 = axes[0, 0]
voltages = df["Voltage (V)"].unique()
for voltage in voltages:
    data = df[df["Voltage (V)"] == voltage]
    ax1.scatter([voltage] * len(data), data["Vibration (g)"], alpha=0.6, s=100)

# Add mean line
means = df.groupby("Voltage (V)")["Vibration (g)"].mean()
ax1.plot(means.index, means.values, "r-", linewidth=2, marker="o", markersize=8, label="Mean")
ax1.set_xlabel("Voltage (V)", fontsize=12)
ax1.set_ylabel("Vibration (g)", fontsize=12)
ax1.set_title("Voltage vs Vibration", fontsize=14)
ax1.grid(True, alpha=0.3)
ax1.legend()

# Plot 2: PWM vs Vibration (scatter + mean line)
ax2 = axes[0, 1]
pwms = df["PWM"].unique()
for pwm in pwms:
    data = df[df["PWM"] == pwm]
    ax2.scatter([pwm] * len(data), data["Vibration (g)"], alpha=0.6, s=100)

# Add mean line
means = df.groupby("PWM")["Vibration (g)"].mean()
ax2.plot(means.index, means.values, "r-", linewidth=2, marker="o", markersize=8, label="Mean")
ax2.set_xlabel("PWM Value", fontsize=12)
ax2.set_ylabel("Vibration (g)", fontsize=12)
ax2.set_title("PWM vs Vibration", fontsize=14)
ax2.grid(True, alpha=0.3)
ax2.legend()

# Plot 3: Box plot by voltage
ax3 = axes[1, 0]
data_for_box = [df[df["Voltage (V)"] == v]["Vibration (g)"].values for v in voltages]
bp = ax3.boxplot(data_for_box, tick_labels=voltages, patch_artist=True)
for patch in bp["boxes"]:
    patch.set_facecolor("lightblue")
ax3.set_xlabel("Voltage (V)", fontsize=12)
ax3.set_ylabel("Vibration (g)", fontsize=12)
ax3.set_title("Vibration Distribution by Voltage", fontsize=14)
ax3.grid(True, alpha=0.3, axis="y")

# Plot 4: Statistics table
ax4 = axes[1, 1]
ax4.axis("off")

# Calculate statistics
stats = df.groupby("Voltage (V)")["Vibration (g)"].agg(["mean", "std", "min", "max"])
stats["PWM"] = df.groupby("Voltage (V)")["PWM"].first()
stats = stats[["PWM", "mean", "std", "min", "max"]]
stats = stats.round(3)

# Create table
table_data = []
table_data.append(["Voltage (V)", "PWM", "Mean (g)", "Std (g)", "Min (g)", "Max (g)"])
for idx, row in stats.iterrows():
    table_data.append(
        [
            f"{idx:.1f}",
            f'{int(row["PWM"])}',
            f'{row["mean"]:.3f}',
            f'{row["std"]:.3f}',
            f'{row["min"]:.3f}',
            f'{row["max"]:.3f}',
        ]
    )

table = ax4.table(
    cellText=table_data,
    cellLoc="center",
    loc="center",
    colWidths=[0.15, 0.12, 0.15, 0.15, 0.15, 0.15],
)
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2)

# Style header row
for i in range(6):
    table[(0, i)].set_facecolor("#4472C4")
    table[(0, i)].set_text_props(weight="bold", color="white")

# Alternate row colors
for i in range(1, len(table_data)):
    for j in range(6):
        if i % 2 == 0:
            table[(i, j)].set_facecolor("#E7E6E6")

ax4.set_title("Calibration Statistics", fontsize=14, pad=20)

plt.tight_layout()
plt.savefig("motor_calibration_plots.png", dpi=300, bbox_inches="tight")
print("✓ Saved: motor_calibration_plots.png")

# Create individual plots for better detail

# Individual plot 1: Voltage vs Vibration with error bars
plt.figure(figsize=(10, 6))
means = df.groupby("Voltage (V)")["Vibration (g)"].mean()
stds = df.groupby("Voltage (V)")["Vibration (g)"].std()

plt.errorbar(
    means.index,
    means.values,
    yerr=stds.values,
    fmt="o-",
    linewidth=2,
    markersize=10,
    capsize=5,
    capthick=2,
)
plt.scatter(
    df["Voltage (V)"],
    df["Vibration (g)"],
    alpha=0.4,
    s=80,
    color="gray",
    label="Individual samples",
)
plt.xlabel("Voltage (V)", fontsize=13)
plt.ylabel("Vibration (g)", fontsize=13)
plt.title("Motor Voltage vs Vibration Magnitude", fontsize=15, fontweight="bold")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig("voltage_vs_vibration.png", dpi=300, bbox_inches="tight")
print("✓ Saved: voltage_vs_vibration.png")

# Individual plot 2: PWM vs Vibration with error bars
plt.figure(figsize=(10, 6))
means = df.groupby("PWM")["Vibration (g)"].mean()
stds = df.groupby("PWM")["Vibration (g)"].std()

plt.errorbar(
    means.index,
    means.values,
    yerr=stds.values,
    fmt="s-",
    linewidth=2,
    markersize=10,
    capsize=5,
    capthick=2,
    color="green",
)
plt.scatter(
    df["PWM"], df["Vibration (g)"], alpha=0.4, s=80, color="gray", label="Individual samples"
)
plt.xlabel("PWM Value", fontsize=13)
plt.ylabel("Vibration (g)", fontsize=13)
plt.title("Motor PWM vs Vibration Magnitude", fontsize=15, fontweight="bold")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig("pwm_vs_vibration.png", dpi=300, bbox_inches="tight")
print("✓ Saved: pwm_vs_vibration.png")

print("\n📊 All plots generated successfully!")
print(f"Total data points: {len(df)}")
print(f"Voltage range: {df['Voltage (V)'].min():.1f}V - {df['Voltage (V)'].max():.1f}V")
print(f"Vibration range: {df['Vibration (g)'].min():.3f}g - {df['Vibration (g)'].max():.3f}g")
