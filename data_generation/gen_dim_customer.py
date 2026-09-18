import pandas as pd
import numpy as np
from datetime import date, timedelta

np.random.seed(42)

DATA_WINDOW_END = date(2025, 8, 31)

dim_city = pd.read_csv("../data/dim_city.csv", parse_dates=["platform_launch_date"])

# How many customers per city, by tier (randomized within a realistic band)
TIER_CUSTOMER_RANGE = {
    "Tier 1": (2200, 2800),
    "Tier 2": (1050, 1350),
    "Tier 3": (500, 700),
}

# Acquisition channel mix, by tier — newer/smaller markets lean more on paid/promo
ACQUISITION_PROBS = {
    "Tier 1": {"Organic": 0.45, "Paid Ads": 0.20, "Referral": 0.20, "Promotional Signup Offer": 0.15},
    "Tier 2": {"Organic": 0.35, "Paid Ads": 0.30, "Referral": 0.20, "Promotional Signup Offer": 0.15},
    "Tier 3": {"Organic": 0.25, "Paid Ads": 0.40, "Referral": 0.15, "Promotional Signup Offer": 0.20},
}

rows = []
customer_id = 1

for _, city in dim_city.iterrows():
    tier = city["city_tier"]
    low, high = TIER_CUSTOMER_RANGE[tier]
    n_customers = np.random.randint(low, high + 1)

    launch = city["platform_launch_date"].date()
    days_available = (DATA_WINDOW_END - launch).days

    probs = ACQUISITION_PROBS[tier]
    channels, weights = list(probs.keys()), list(probs.values())

    for _ in range(n_customers):
        offset = np.random.randint(0, days_available + 1)
        signup_date = launch + timedelta(days=int(offset))
        acquisition_channel = np.random.choice(channels, p=weights)

        tenure_days = (DATA_WINDOW_END - signup_date).days
        # Probability of ever having subscribed grows with tenure, capped at 60%
        p_ever_subscribed = min(0.60, 0.05 + tenure_days / 1500)
        ever_subscribed = np.random.rand() < p_ever_subscribed

        if ever_subscribed:
            subscription_status = "Active" if np.random.rand() < 0.55 else "Lapsed"
            max_offset = max(tenure_days - 1, 0)
            sub_offset = np.random.randint(0, max_offset + 1) if max_offset > 0 else 0
            subscription_start_date = signup_date + timedelta(days=int(sub_offset))
        else:
            subscription_status = "None"
            subscription_start_date = None

        rows.append({
            "customer_id": customer_id,
            "city_id": int(city["city_id"]),
            "signup_date": signup_date,
            "acquisition_channel": acquisition_channel,
            "subscription_status": subscription_status,
            "subscription_start_date": subscription_start_date,
        })
        customer_id += 1

dim_customer = pd.DataFrame(rows)
dim_customer.to_csv("../data/dim_customer.csv", index=False)

print(f"Total customers generated: {len(dim_customer)}\n")

print("--- Customers per city ---")
merged = dim_customer.merge(dim_city[["city_id", "city_name", "city_tier"]], on="city_id")
print(merged.groupby(["city_tier", "city_name"])["customer_id"].count())

print("\n--- Acquisition channel mix, overall ---")
print(dim_customer["acquisition_channel"].value_counts(normalize=True).round(3))

print("\n--- Subscription status, overall ---")
print(dim_customer["subscription_status"].value_counts(normalize=True).round(3))

print("\n--- Integrity check: any signup before city launch? ---")
check = merged.merge(dim_city[["city_id", "platform_launch_date"]], on="city_id")
bad = check[pd.to_datetime(check["signup_date"]) < check["platform_launch_date"]]
print(f"Violations found: {len(bad)} (should be 0)")

print("\n--- Integrity check: any subscription_start_date before signup_date? ---")
sub_check = dim_customer.dropna(subset=["subscription_start_date"])
bad2 = sub_check[pd.to_datetime(sub_check["subscription_start_date"]) < pd.to_datetime(sub_check["signup_date"])]
print(f"Violations found: {len(bad2)} (should be 0)")
