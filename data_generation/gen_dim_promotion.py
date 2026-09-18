import pandas as pd
import numpy as np
from datetime import date, timedelta

np.random.seed(42)

WINDOW_START = date(2024, 3, 1)
WINDOW_END = date(2025, 8, 31)
TOTAL_DAYS = (WINDOW_END - WINDOW_START).days

N_PROMOTIONS = 150

PROMO_TYPE_PROBS = {
    "Percentage Off": 0.35, "Flat Amount Off": 0.25, "Free Delivery": 0.20,
    "Cashback": 0.10, "BOGO": 0.10,
}

TARGET_SEGMENT_PROBS = {
    "All Customers": 0.40, "New Customers Only": 0.25,
    "Lapsed/Win-back": 0.20, "High-Frequency": 0.15,
}

DESCRIPTORS = ["Weekend", "Monsoon", "Summer", "Festive", "Payday", "Flash",
               "Loyalty", "Winback", "Midweek", "Anniversary", "New User", "Late Night"]

NAME_TEMPLATES = {
    "Percentage Off": "{pct}% Off {desc} Sale",
    "Flat Amount Off": "Flat \u20b9{amt} Off {desc} Deal",
    "Free Delivery": "Free Delivery {desc} Days",
    "Cashback": "\u20b9{amt} Cashback {desc} Offer",
    "BOGO": "Buy 1 Get 1 {desc} Fest",
}

rows = []
promo_types = list(PROMO_TYPE_PROBS.keys())
promo_type_weights = list(PROMO_TYPE_PROBS.values())
segments = list(TARGET_SEGMENT_PROBS.keys())
segment_weights = list(TARGET_SEGMENT_PROBS.values())

for promotion_id in range(1, N_PROMOTIONS + 1):
    promo_type = np.random.choice(promo_types, p=promo_type_weights)
    target_segment = np.random.choice(segments, p=segment_weights)

    # Duration: mostly short-to-medium campaigns, occasionally long ones
    duration = int(np.random.choice([7, 14, 21, 30, 45, 60], p=[0.25, 0.25, 0.2, 0.15, 0.1, 0.05]))
    max_start_offset = TOTAL_DAYS - duration
    start_offset = np.random.randint(0, max_start_offset)
    start_date = WINDOW_START + timedelta(days=int(start_offset))
    end_date = start_date + timedelta(days=duration)

    desc = np.random.choice(DESCRIPTORS)

    if promo_type == "Percentage Off":
        discount_value = int(np.random.choice([10, 15, 20, 25, 30, 40]))
        max_discount_cap = float(np.random.choice([75, 100, 125, 150, 200]))
        min_order_value = float(np.random.choice([0, 149, 199, 249, 299]))
        promotion_name = NAME_TEMPLATES[promo_type].format(pct=discount_value, desc=desc)
    elif promo_type == "Flat Amount Off":
        discount_value = float(np.random.choice([50, 75, 100, 125, 150]))
        max_discount_cap = None
        min_order_value = float(discount_value + np.random.choice([49, 99, 149]))
        promotion_name = NAME_TEMPLATES[promo_type].format(amt=int(discount_value), desc=desc)
    elif promo_type == "Free Delivery":
        discount_value = 100.0  # 100% of delivery fee waived
        max_discount_cap = None
        min_order_value = float(np.random.choice([0, 99, 149]))
        promotion_name = NAME_TEMPLATES[promo_type].format(desc=desc)
    elif promo_type == "Cashback":
        discount_value = float(np.random.choice([30, 50, 75, 100]))
        max_discount_cap = None
        min_order_value = float(discount_value + np.random.choice([99, 149, 199]))
        promotion_name = NAME_TEMPLATES[promo_type].format(amt=int(discount_value), desc=desc)
    else:  # BOGO
        discount_value = 100.0  # one item fully free
        max_discount_cap = float(np.random.choice([150, 200, 250]))  # cap on the free item's value
        min_order_value = float(np.random.choice([0, 199, 249]))
        promotion_name = NAME_TEMPLATES[promo_type].format(desc=desc)

    # Funding: 70% platform-only, 30% co-funded with restaurant
    if np.random.rand() < 0.70:
        funded_by = "Platform Only"
        platform_funding_share_pct = 100.0
    else:
        funded_by = "Co-funded with Restaurant"
        platform_funding_share_pct = round(float(np.random.uniform(40, 70)), 1)

    spend_rate_per_day = np.random.uniform(3000, 9000)
    planned_budget = round(duration * spend_rate_per_day, -2)  # round to nearest 100

    rows.append({
        "promotion_id": promotion_id,
        "promotion_name": promotion_name,
        "promotion_type": promo_type,
        "discount_value": discount_value,
        "max_discount_cap": max_discount_cap,
        "min_order_value": min_order_value,
        "target_segment": target_segment,
        "funded_by": funded_by,
        "platform_funding_share_pct": platform_funding_share_pct,
        "start_date": start_date,
        "end_date": end_date,
        "planned_budget": planned_budget,
    })

dim_promotion = pd.DataFrame(rows)
dim_promotion.to_csv("../data/dim_promotion.csv", index=False)

print(f"Total promotions generated: {len(dim_promotion)}\n")

print("--- Promotion type mix ---")
print(dim_promotion["promotion_type"].value_counts(normalize=True).round(3))

print("\n--- Target segment mix ---")
print(dim_promotion["target_segment"].value_counts(normalize=True).round(3))

print("\n--- Funding split ---")
print(dim_promotion["funded_by"].value_counts(normalize=True).round(3))

print("\n--- Duration & budget stats ---")
dim_promotion["duration_days"] = (pd.to_datetime(dim_promotion["end_date"]) - pd.to_datetime(dim_promotion["start_date"])).dt.days
print(dim_promotion[["duration_days", "planned_budget"]].describe().round(0))

print("\n--- Integrity check: all dates within the 18-month window? ---")
bad = dim_promotion[(pd.to_datetime(dim_promotion["start_date"]).dt.date < WINDOW_START) |
                     (pd.to_datetime(dim_promotion["end_date"]).dt.date > WINDOW_END)]
print(f"Violations found: {len(bad)} (should be 0)")

print("\n--- Integrity check: budget scales with duration (correlation) ---")
print(f"Correlation between duration and planned_budget: {dim_promotion['duration_days'].corr(dim_promotion['planned_budget']):.2f} (should be positive)")
