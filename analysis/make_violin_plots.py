import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu

# -----------------------------
# File paths
# -----------------------------
input_csv = "alphafold_scores_with_known.csv"
output_png = "violin_plot.png"

# -----------------------------
# Load data
# -----------------------------
df = pd.read_csv(input_csv)

# -----------------------------
# Compute average ipTM
# -----------------------------
score_cols = [
    "Rep 1 FLS2-flg22 iptm",
    "Rep 2 FLS2-flg22 iptm",
    "Rep 3 FLS2-flg22 iptm",
]

df["avg_iptm"] = df[score_cols].mean(axis=1)

# -----------------------------
# Clean / prepare columns
# -----------------------------
df = df.dropna(subset=["Name", "Known Outcome", "avg_iptm"]).copy()

# Keep only the two expected outcome labels
df = df[df["Known Outcome"].isin(["No perception", "Perception"])].copy()

# Assign subgroup
df["Group"] = df["Name"].apply(
    lambda x: "AtFLS2" if str(x).startswith("AtFLS2") else "Non-AtFLS2"
)

# Desired plotting order
group_order = ["AtFLS2", "Non-AtFLS2"]
outcome_order = ["No perception", "Perception"]

# -----------------------------
# Build plotting data manually
# -----------------------------
positions = [1, 2, 4, 5]
datasets = []
labels = []

for group in group_order:
    for outcome in outcome_order:
        vals = df.loc[
            (df["Group"] == group) & (df["Known Outcome"] == outcome),
            "avg_iptm"
        ].values
        datasets.append(vals)
        labels.append(outcome)

# -----------------------------
# Plot
# -----------------------------
fig, ax = plt.subplots(figsize=(8, 6))

vp = ax.violinplot(
    datasets,
    positions=positions,
    widths=0.8,
    showmeans=False,
    showmedians=False,
    showextrema=False,
)

# Color violins:
# orange for no perception, blue for perception
violin_colors = ["#F4A261", "#A8C5E6", "#F4A261", "#A8C5E6"]

for body, color in zip(vp["bodies"], violin_colors):
    body.set_facecolor(color)
    body.set_edgecolor("none")
    body.set_alpha(0.9)

# Overlay boxplots
bp = ax.boxplot(
    datasets,
    positions=positions,
    widths=0.15,
    patch_artist=True,
    showfliers=False,
    medianprops=dict(color="black", linewidth=1.2),
    boxprops=dict(linewidth=1.0, color="black"),
    whiskerprops=dict(linewidth=1.0, color="black"),
    capprops=dict(linewidth=1.0, color="black"),
)

for patch, color in zip(bp["boxes"], violin_colors):
    patch.set_facecolor(color)
    patch.set_alpha(1.0)

# Overlay jittered points
for pos, vals in zip(positions, datasets):
    if len(vals) == 0:
        continue
    x_jitter = pd.Series(range(len(vals))).sample(frac=1, random_state=1).index
    # simple deterministic jitter
    import numpy as np
    rng = np.random.default_rng(1 + int(pos))
    x = rng.normal(loc=pos, scale=0.05, size=len(vals))
    ax.scatter(x, vals, s=8, color="black", alpha=0.55, linewidths=0)

# -----------------------------
# Statistical tests
# -----------------------------
def format_p_value(p):
    if p < 0.0001:
        return r"$P < 0.0001$"
    return rf"$P = {p:.4f}$"

# AtFLS2
at_no = df.loc[
    (df["Group"] == "AtFLS2") & (df["Known Outcome"] == "No perception"),
    "avg_iptm"
]
at_yes = df.loc[
    (df["Group"] == "AtFLS2") & (df["Known Outcome"] == "Perception"),
    "avg_iptm"
]

# Non-AtFLS2
non_no = df.loc[
    (df["Group"] == "Non-AtFLS2") & (df["Known Outcome"] == "No perception"),
    "avg_iptm"
]
non_yes = df.loc[
    (df["Group"] == "Non-AtFLS2") & (df["Known Outcome"] == "Perception"),
    "avg_iptm"
]

if len(at_no) > 0 and len(at_yes) > 0:
    _, p_at = mannwhitneyu(at_no, at_yes, alternative="two-sided")
    ax.text(1.5, 1.05, format_p_value(p_at), ha="center", va="bottom", fontsize=14)

if len(non_no) > 0 and len(non_yes) > 0:
    _, p_non = mannwhitneyu(non_no, non_yes, alternative="two-sided")
    ax.text(4.5, 1.05, format_p_value(p_non), ha="center", va="bottom", fontsize=14)

# -----------------------------
# Axes / labels / styling
# -----------------------------
ax.set_xticks(positions)
ax.set_xticklabels(labels, fontsize=12)
ax.set_ylabel("ipTM$_{flg22–FLS2}$", fontsize=16)

ax.set_xlim(0.2, 5.8)
ax.set_ylim(0.05, 1.1)

# subgroup labels underneath
ax.text(
    1.5, 0.01, "AtFLS2",
    ha="center", va="top", fontsize=14,
    bbox=dict(boxstyle="round,pad=0.25", facecolor="#A7D8DE", edgecolor="none")
)
ax.text(
    4.5, 0.01, "Non-AtFLS2",
    ha="center", va="top", fontsize=14,
    bbox=dict(boxstyle="round,pad=0.25", facecolor="#9DCCAA", edgecolor="none")
)

# Clean up spines
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.savefig(output_png, dpi=300, bbox_inches="tight")
plt.show()