import pandas as pd
import numpy as np
from datetime import date, timedelta

np.random.seed(42)

DATA_WINDOW_START = date(2024, 3, 1)
DATA_WINDOW_END = date(2025, 8, 31)  # 18-month order data window

cities = [
    # (city_name, state, region, tier)
    ("Mumbai", "Maharashtra", "West", "Tier 1"),
    ("Delhi", "Delhi", "North", "Tier 1"),
    ("Bengaluru", "Karnataka", "South", "Tier 1"),
    ("Kolkata", "West Bengal", "East", "Tier 1"),
    ("Pune", "Maharashtra", "West", "Tier 2"),
    ("Ahmedabad", "Gujarat", "West", "Tier 2"),
    ("Hyderabad", "Telangana", "South", "Tier 2"),
    ("Chandigarh", "Chandigarh", "North", "Tier 2"),
    ("Indore", "Madhya Pradesh", "Central", "Tier 2"),
    ("Coimbatore", "Tamil Nadu", "South", "Tier 3"),
    ("Bhubaneswar", "Odisha", "East", "Tier 3"),
    ("Bhopal", "Madhya Pradesh", "Central", "Tier 3"),
]

rows = []
for i, (name, state, region, tier) in enumerate(cities, start=1):
    if tier == "Tier 1":
        days_before = np.random.randint(3 * 365, 5 * 365)       # mature: launched 3-5 yrs before window
        market_size = np.random.randint(800, 1500)
    elif tier == "Tier 2":
        days_before = np.random.randint(1 * 365, 2 * 365)       # launched 1-2 yrs before window
        market_size = np.random.randint(300, 600)
    else:  # Tier 3
        days_before = np.random.randint(-180, 365)              # some launch DURING the window (negative = future)
        market_size = np.random.randint(100, 250)

    launch_date = DATA_WINDOW_START - timedelta(days=int(days_before))
    rows.append({
        "city_id": i,
        "city_name": name,
        "state": state,
        "region": region,
        "city_tier": tier,
        "platform_launch_date": launch_date,
        "estimated_market_size": market_size,
    })

dim_city = pd.DataFrame(rows)
dim_city.to_csv("../data/dim_city.csv", index=False)

print(dim_city.to_string(index=False))
print("\n--- Validation: summary by tier ---")
print(dim_city.groupby("city_tier").agg(
    cities=("city_id", "count"),
    avg_market_size=("estimated_market_size", "mean"),
    earliest_launch=("platform_launch_date", "min"),
    latest_launch=("platform_launch_date", "max"),
))
print("\n--- Validation: cities per region ---")
print(dim_city.groupby("region")["city_name"].apply(list))
