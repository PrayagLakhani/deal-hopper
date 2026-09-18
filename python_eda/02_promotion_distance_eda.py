# EDA of promotion impact and distance-margin relationships.

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from pathlib import Path
from db_utils import get_engine

OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
sns.set_style("whitegrid")

engine = get_engine()

query = """
SELECT
    oe.order_id, oe.contribution_margin, oe.promotion_id,
    fo.delivery_distance_km,
    p.promotion_type
FROM vw_order_economics oe
JOIN fact_order fo ON oe.order_id = fo.order_id
LEFT JOIN dim_promotion p ON oe.promotion_id = p.promotion_id
WHERE oe.order_status = 'Delivered'
"""
df = pd.read_sql(query, engine)
df["has_promotion"] = df["promotion_id"].notna().map({True: "With Promotion", False: "No Promotion"})
print(f"Loaded {len(df):,} delivered orders\n")

# STATISTICAL TEST: does promotion usage significantly affect contribution margin?
with_promo = df[df["has_promotion"] == "With Promotion"]["contribution_margin"]
without_promo = df[df["has_promotion"] == "No Promotion"]["contribution_margin"]

t_stat, p_value = stats.ttest_ind(with_promo, without_promo, equal_var=False)  # Welch's t-test
pooled_std = np.sqrt((with_promo.std()**2 + without_promo.std()**2) / 2)
cohens_d = (with_promo.mean() - without_promo.mean()) / pooled_std

print("--- Independent t-test: Contribution Margin, With vs Without Promotion ---")
print(f"With promotion:    mean = Rs {with_promo.mean():.2f}, n = {len(with_promo):,}")
print(f"Without promotion: mean = Rs {without_promo.mean():.2f}, n = {len(without_promo):,}")
print(f"Difference: Rs {with_promo.mean() - without_promo.mean():.2f}")
print(f"t-statistic = {t_stat:.2f}, p-value = {p_value:.2e}")
print(f"Cohen's d (effect size) = {cohens_d:.3f}")
if p_value < 0.001:
    print("=> Highly statistically significant (p < 0.001).")
print()

# PLOT 1: Boxplot + violin — contribution margin with vs without promotion
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
sns.boxplot(data=df, x="has_promotion", y="contribution_margin", ax=axes[0], hue="has_promotion",
            palette=["#C44E52", "#55A868"], legend=False)
axes[0].axhline(0, color="black", linestyle="--", linewidth=0.8)
axes[0].set_title("Contribution Margin: With vs Without Promotion")
axes[0].set_xlabel("")

promo_only = df[df["has_promotion"] == "With Promotion"]
order = promo_only.groupby("promotion_type")["contribution_margin"].median().sort_values(ascending=False).index
sns.boxplot(data=promo_only, x="promotion_type", y="contribution_margin", order=order, ax=axes[1],
            hue="promotion_type", palette="Set2", legend=False)
axes[1].axhline(0, color="black", linestyle="--", linewidth=0.8)
axes[1].set_title("Contribution Margin by Promotion Type")
axes[1].tick_params(axis="x", rotation=30)
axes[1].set_xlabel("")

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "03_promotion_boxplots.png", dpi=150)
plt.close()
print(f"Saved: {OUTPUT_DIR / '03_promotion_boxplots.png'}")

# PLOT 2: Distance vs margin
df["distance_bin"] = pd.cut(df["delivery_distance_km"], bins=np.arange(0, 15.5, 1))
binned = df.groupby("distance_bin", observed=True)["contribution_margin"].agg(["mean", "sem", "count"]).reset_index()
binned["distance_mid"] = binned["distance_bin"].apply(lambda x: x.mid).astype(float)
binned["ci95"] = 1.96 * binned["sem"]

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].scatter(df["delivery_distance_km"], df["contribution_margin"], alpha=0.05, s=8, color="#4C72B0")
axes[0].set_title("Raw Scatter: Distance vs Contribution Margin\n(individual orders — looks noisy)")
axes[0].set_xlabel("Delivery Distance (km)")
axes[0].set_ylabel("Contribution Margin (Rs)")

axes[1].errorbar(binned["distance_mid"], binned["mean"], yerr=binned["ci95"],
                  marker="o", capsize=3, color="#C44E52", linewidth=2)
axes[1].set_title("Binned Average (1km bins) with 95% CI\n(the real pattern, hidden by noise above)")
axes[1].set_xlabel("Delivery Distance (km)")
axes[1].set_ylabel("Avg Contribution Margin (Rs)")

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "04_distance_margin_relationship.png", dpi=150)
plt.close()
print(f"Saved: {OUTPUT_DIR / '04_distance_margin_relationship.png'}")

print("\n--- Binned distance summary ---")
print(binned[["distance_bin", "mean", "count"]].round(2).to_string(index=False))
