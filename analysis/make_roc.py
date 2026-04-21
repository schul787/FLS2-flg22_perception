import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc

# -----------------------------
# File paths
# -----------------------------
input_csv = "alphafold_scores_with_known.csv"
output_png = "roc_curve.png"

# -----------------------------
# Load data
# -----------------------------
df = pd.read_csv(input_csv)

# Compute average FLS2-flg22 ipTM across the 3 replicates
score_cols = [
    "Rep 1 FLS2-flg22 iptm",
    "Rep 2 FLS2-flg22 iptm",
    "Rep 3 FLS2-flg22 iptm",
]

df["avg_iptm"] = df[score_cols].mean(axis=1)

# Convert Known Outcome to binary labels
# no perception = 0, perception = 1
outcome_map = {
    "No perception": 0,
    "Perception": 1,
}

df["y_true"] = df["Known Outcome"].map(outcome_map)

# Drop rows missing labels or scores
plot_df = df.dropna(subset=["y_true", "avg_iptm", "Name"]).copy()

# -----------------------------
# Define subsets
# -----------------------------
all_data = plot_df
atfls2_data = plot_df[plot_df["Name"].str.startswith("AtFLS2")]
non_atfls2_data = plot_df[~plot_df["Name"].str.startswith("AtFLS2")]

subsets = [
    ("All data", all_data),
    ("AtFLS2", atfls2_data),
    ("Non-AtFLS2", non_atfls2_data),
]

# -----------------------------
# Plot ROC curves
# -----------------------------
plt.figure(figsize=(6, 6))

for label, subset in subsets:
    if subset["y_true"].nunique() < 2:
        print(f"Skipping {label}: need both 0 and 1 labels present.")
        continue

    fpr, tpr, _ = roc_curve(subset["y_true"], subset["avg_iptm"])
    roc_auc = auc(fpr, tpr)
    plt.plot(fpr, tpr, linewidth=2, label=f"{label} (AUC {roc_auc:.3f})")

plt.plot([0, 1], [0, 1], linestyle="--", color="gray", linewidth=1.5)

plt.xlim(0, 1)
plt.ylim(0, 1)
plt.xlabel("False positive rate")
plt.ylabel("True positive rate")
plt.title("ROC Curve: average FLS2-flg22 ipTM")
plt.legend(frameon=False)
plt.tight_layout()

plt.savefig(output_png, dpi=300)
plt.show()