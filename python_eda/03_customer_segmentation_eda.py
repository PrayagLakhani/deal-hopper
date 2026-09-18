# Customer segmentation and profitability analysis.

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from db_utils import get_engine

OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
sns.set_style("whitegrid")

engine = get_engine()

# Pull customer summary and apply RFM segmentation.
query = """
WITH rfm AS (
    SELECT customer_id, delivered_orders, total_contribution, promo_usage_rate,
           contribution_per_order, recency_days,
           NTILE(4) OVER (ORDER BY recency_days ASC) AS recency_score,
           NTILE(4) OVER (ORDER BY delivered_orders DESC) AS frequency_score,
           NTILE(4) OVER (ORDER BY total_contribution DESC) AS monetary_score
    FROM vw_customer_summary
    WHERE delivered_orders > 0
)
SELECT *,
    CASE
        WHEN recency_score = 1 AND frequency_score = 1 AND monetary_score = 1 THEN 'Champions'
        WHEN frequency_score <= 2 AND monetary_score <= 2 THEN 'Loyal Customers'
        WHEN recency_score >= 3 AND frequency_score <= 2 THEN 'At Risk'
        WHEN recency_score >= 3 AND frequency_score >= 3 THEN 'Lost / Dormant'
        ELSE 'Developing'
    END AS segment
FROM rfm
"""
df = pd.read_sql(query, engine)
print(f"Loaded {len(df):,} customers with at least one delivered order\n")

# Discount dependency vs profitability (binned trend + boxplot)
df["dependency_band"] = pd.cut(
    df["promo_usage_rate"], bins=[-0.01, 0, 0.25, 0.5, 0.75, 1.0],
    labels=["0%", "1-25%", "26-50%", "51-75%", "76-100%"]
)

binned = df.groupby("dependency_band", observed=True)["contribution_per_order"].agg(["mean", "sem"]).reset_index()
binned["ci95"] = 1.96 * binned["sem"]

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].errorbar(range(len(binned)), binned["mean"], yerr=binned["ci95"],
                  marker="o", capsize=4, color="#C44E52", linewidth=2, markersize=8)
axes[0].set_xticks(range(len(binned)))
axes[0].set_xticklabels(binned["dependency_band"])
axes[0].set_title("Discount Dependency vs. Avg Contribution/Order\n(with 95% CI)")
axes[0].set_xlabel("Promo Usage Rate Band")
axes[0].set_ylabel("Avg Contribution per Order (Rs)")

sns.boxplot(data=df, x="dependency_band", y="contribution_per_order", ax=axes[1],
            hue="dependency_band", palette="Reds_r", legend=False, showfliers=False)
axes[1].set_title("Contribution/Order Distribution by Dependency Band\n(outliers hidden for readability)")
axes[1].set_xlabel("Promo Usage Rate Band")

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "05_discount_dependency.png", dpi=150)
plt.close()
print(f"Saved: {OUTPUT_DIR / '05_discount_dependency.png'}")

# Frequency vs profitability
df["frequency_quartile"] = pd.qcut(df["delivered_orders"], 4, labels=["Q1 (Lowest)", "Q2", "Q3", "Q4 (Highest)"])

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

sns.boxplot(data=df, x="frequency_quartile", y="contribution_per_order", ax=axes[0],
            hue="frequency_quartile", palette="Blues", legend=False, showfliers=False)
axes[0].set_title("Contribution/Order by Frequency Quartile\n(flat -> frequency doesn't predict profitability)")
axes[0].set_xlabel("Order Frequency Quartile")

segment_counts = df["segment"].value_counts().sort_values(ascending=True)
colors = sns.color_palette("viridis", len(segment_counts))
axes[1].barh(segment_counts.index, segment_counts.values, color=colors)
for i, v in enumerate(segment_counts.values):
    axes[1].text(v + 50, i, f"{v:,} ({100*v/len(df):.1f}%)", va="center", fontsize=9)
axes[1].set_title("Customer Base by RFM Segment")
axes[1].set_xlabel("Number of Customers")
axes[1].set_xlim(0, segment_counts.max() * 1.25)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "06_frequency_and_rfm_segments.png", dpi=150)
plt.close()
print(f"Saved: {OUTPUT_DIR / '06_frequency_and_rfm_segments.png'}")

# RFM bubble chart — frequency vs monetary, colored by segment
plt.figure(figsize=(9, 7))
segments = df["segment"].unique()
palette = dict(zip(segments, sns.color_palette("Set2", len(segments))))
for seg in segments:
    sub = df[df["segment"] == seg]
    plt.scatter(sub["delivered_orders"], sub["total_contribution"], s=15, alpha=0.4,
                label=seg, color=palette[seg])
plt.xlabel("Delivered Orders (Frequency)")
plt.ylabel("Total Contribution (Rs) (Monetary)")
plt.title("Customer Segments: Frequency vs. Monetary Value")
plt.legend(markerscale=3, title="RFM Segment")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "07_rfm_bubble_chart.png", dpi=150)
plt.close()
print(f"Saved: {OUTPUT_DIR / '07_rfm_bubble_chart.png'}")

print("\n--- Segment sizes ---")
print(df["segment"].value_counts())
print("\n--- Avg contribution per order by dependency band ---")
print(df.groupby("dependency_band", observed=True)["contribution_per_order"].mean().round(2))
