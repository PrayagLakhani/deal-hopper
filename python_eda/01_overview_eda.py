# EDA of delivered-order economics and operational metrics.

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

query = """
SELECT
    oe.order_id, oe.order_status, oe.gross_item_value, oe.total_discount,
    oe.contribution_margin, oe.platform_borne_discount,
    fo.delivery_distance_km, fo.actual_delivery_time_min, fo.estimated_delivery_time_min,
    fo.payment_method, fo.order_channel
FROM vw_order_economics oe
JOIN fact_order fo ON oe.order_id = fo.order_id
WHERE oe.order_status = 'Delivered'
"""
df = pd.read_sql(query, engine)
print(f"Loaded {len(df):,} delivered orders\n")

# Basic overview
print("--- Data types and missing values ---")
print(df.info())
print("\n--- Missing value counts ---")
print(df.isnull().sum())

print("\n--- Summary statistics ---")
print(df[["gross_item_value", "total_discount", "contribution_margin", "delivery_distance_km"]].describe().round(2))

# IQR-based outlier detection
def iqr_outlier_bounds(series):
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr

print("\n--- Outlier detection (IQR method) ---")
for col in ["gross_item_value", "contribution_margin", "delivery_distance_km"]:
    low, high = iqr_outlier_bounds(df[col])
    n_outliers = ((df[col] < low) | (df[col] > high)).sum()
    pct = 100 * n_outliers / len(df)
    print(f"{col}: bounds=({low:.2f}, {high:.2f}), outliers={n_outliers:,} ({pct:.2f}%)")

# Distribution plots
fig, axes = plt.subplots(2, 2, figsize=(12, 9))

sns.histplot(df["gross_item_value"], bins=50, ax=axes[0, 0], color="#4C72B0")
axes[0, 0].set_title("Distribution: Order Value (Gross Item Value)")
axes[0, 0].set_xlabel("Gross Item Value (Rs)")

sns.histplot(df["contribution_margin"], bins=50, ax=axes[0, 1], color="#55A868")
axes[0, 1].axvline(0, color="red", linestyle="--", linewidth=1, label="Break-even")
axes[0, 1].set_title("Distribution: Contribution Margin per Order")
axes[0, 1].set_xlabel("Contribution Margin (Rs)")
axes[0, 1].legend()

sns.histplot(df["delivery_distance_km"], bins=40, ax=axes[1, 0], color="#C44E52")
axes[1, 0].set_title("Distribution: Delivery Distance")
axes[1, 0].set_xlabel("Distance (km)")

sns.histplot(df["total_discount"][df["total_discount"] > 0], bins=40, ax=axes[1, 1], color="#8172B2")
axes[1, 1].set_title("Distribution: Discount Amount (orders with a discount only)")
axes[1, 1].set_xlabel("Discount (Rs)")

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "01_distributions.png", dpi=150)
plt.close()
print(f"\nSaved: {OUTPUT_DIR / '01_distributions.png'}")

# Correlation heatmap
corr_cols = ["gross_item_value", "total_discount", "contribution_margin",
             "delivery_distance_km", "platform_borne_discount"]
corr = df[corr_cols].corr()

plt.figure(figsize=(7, 6))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, square=True)
plt.title("Correlation Matrix: Order Economics & Delivery Distance")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "02_correlation_heatmap.png", dpi=150)
plt.close()
print(f"Saved: {OUTPUT_DIR / '02_correlation_heatmap.png'}")

print("\n--- Correlation with contribution_margin (sorted) ---")
print(corr["contribution_margin"].sort_values(ascending=False).round(3))
