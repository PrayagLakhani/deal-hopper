# Product margin and restaurant economics analysis.

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

products = pd.read_sql("SELECT * FROM vw_product_summary", engine)
restaurants = pd.read_sql("SELECT * FROM vw_restaurant_summary WHERE delivered_orders > 0", engine)
print(f"Loaded {len(products):,} products, {len(restaurants):,} active restaurants\n")

# Product Margin Matrix (volume vs margin, quadrant chart)
median_volume = products["units_sold"].median()
median_margin = products["restaurant_margin_pct"].median()

fig, ax = plt.subplots(figsize=(10, 8))
categories = products["category"].unique()
palette = dict(zip(categories, sns.color_palette("tab10", len(categories))))

for cat in categories:
    sub = products[products["category"] == cat]
    ax.scatter(sub["units_sold"], sub["restaurant_margin_pct"], s=25, alpha=0.5,
               label=cat, color=palette[cat])

ax.axvline(median_volume, color="gray", linestyle="--", linewidth=1)
ax.axhline(median_margin, color="gray", linestyle="--", linewidth=1)

ax.text(0.98, 0.98, "STARS\n(high volume, high margin)\nprotect & promote", transform=ax.transAxes,
        ha="right", va="top", fontsize=9, style="italic", color="#2ca02c")
ax.text(0.02, 0.98, "NICHE\n(low volume, high margin)\ntest wider promotion", transform=ax.transAxes,
        ha="left", va="top", fontsize=9, style="italic", color="#1f77b4")
ax.text(0.98, 0.02, "DANGER ZONE\n(high volume, low margin)\ndo NOT discount further", transform=ax.transAxes,
        ha="right", va="bottom", fontsize=9, style="italic", color="#d62728")
ax.text(0.02, 0.02, "REVIEW\n(low volume, low margin)\ncandidates to drop", transform=ax.transAxes,
        ha="left", va="bottom", fontsize=9, style="italic", color="#7f7f7f")

ax.set_xscale("log")
ax.set_xlabel("Units Sold (log scale)")
ax.set_ylabel("Restaurant Margin %")
ax.set_title("Product Margin Matrix: Volume vs. Margin, by Category")
ax.legend(loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=8)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "08_product_margin_matrix.png", dpi=150)
plt.close()
print(f"Saved: {OUTPUT_DIR / '08_product_margin_matrix.png'}")

# Category margin ranking
cat_summary = products.groupby("category").agg(
    avg_margin=("restaurant_margin_pct", "mean"),
    total_units=("units_sold", "sum")
).sort_values("avg_margin", ascending=True)

plt.figure(figsize=(9, 5))
bars = plt.barh(cat_summary.index, cat_summary["avg_margin"], color=sns.color_palette("RdYlGn", len(cat_summary)))
for i, v in enumerate(cat_summary["avg_margin"]):
    plt.text(v + 0.5, i, f"{v:.1f}%", va="center", fontsize=9)
plt.xlabel("Average Restaurant Margin %")
plt.title("Category Margin Ranking (Realized Sales)")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "09_category_margin_ranking.png", dpi=150)
plt.close()
print(f"Saved: {OUTPUT_DIR / '09_category_margin_ranking.png'}")

# Restaurant volume vs platform contribution
plt.figure(figsize=(11, 7))
cuisines = restaurants["cuisine_type"].unique()
palette2 = dict(zip(cuisines, sns.color_palette("tab20", len(cuisines))))
for cuisine in cuisines:
    sub = restaurants[restaurants["cuisine_type"] == cuisine]
    is_bakery = cuisine == "Bakery & Desserts"
    plt.scatter(sub["delivered_orders"], sub["contribution_per_order"],
                s=60 if is_bakery else 25, alpha=0.9 if is_bakery else 0.4,
                label=cuisine, color=palette2[cuisine],
                edgecolors="black" if is_bakery else "none", linewidths=0.5)

plt.axhline(restaurants["contribution_per_order"].median(), color="gray", linestyle="--", linewidth=1,
            label="Median contribution/order")
plt.xlabel("Delivered Orders (Volume)")
plt.ylabel("Contribution per Order (Rs)")
plt.title("Restaurant Volume vs. Platform Contribution, by Cuisine\n(Bakery & Desserts highlighted — high volume, low platform contribution)")
plt.legend(loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=8)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "10_restaurant_volume_vs_contribution.png", dpi=150)
plt.close()
print(f"Saved: {OUTPUT_DIR / '10_restaurant_volume_vs_contribution.png'}")

print("\n--- Bakery & Desserts vs overall: contribution per order ---")
print(f"Bakery & Desserts avg: Rs {restaurants[restaurants['cuisine_type']=='Bakery & Desserts']['contribution_per_order'].mean():.2f}")
print(f"Overall avg:           Rs {restaurants['contribution_per_order'].mean():.2f}")
