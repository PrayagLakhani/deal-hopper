import pandas as pd
import numpy as np
from datetime import date, timedelta

np.random.seed(42)

DATA_WINDOW_END = date(2025, 8, 31)

dim_city = pd.read_csv("../data/dim_city.csv", parse_dates=["platform_launch_date"])

# How many restaurants per city, by tier
TIER_RESTAURANT_RANGE = {
    "Tier 1": (35, 55),
    "Tier 2": (20, 30),
    "Tier 3": (10, 20),
}

CUISINES = [
    "North Indian", "South Indian", "Chinese", "Biryani & Mughlai",
    "Pizza & Italian", "Burgers & American", "Momos & Tibetan",
    "Rolls & Wraps", "Bakery & Desserts", "Cafe & Beverages", "Multi-cuisine",
]

RESTAURANT_TYPE_PROBS = {"Cloud Kitchen": 0.40, "Standalone Restaurant": 0.45, "Chain Outlet": 0.15}

# Commission rate ranges — chains negotiate lower rates due to bargaining power
COMMISSION_RANGE = {
    "Chain Outlet": (0.12, 0.18),
    "Cloud Kitchen": (0.18, 0.28),
    "Standalone Restaurant": (0.15, 0.25),
}

# Fictional chain brands — reused across cities, since a chain shares its brand name
CHAIN_BRANDS = [
    "Spice Route Express", "Urban Tadka", "Curry Culture", "Wok & Roll Co.",
    "The Combo Company", "Flame & Fork", "Bite Society", "Craveable Kitchens",
]

NAME_PREFIXES = ["Spice", "Urban", "Royal", "Tasty", "Golden", "Zaika", "The Daily",
                  "Flavour", "Hungry", "Fresh", "Local", "Grand", "Corner"]
NAME_SUFFIXES = ["Kitchen", "House", "Junction", "Hub", "Corner", "Express", "Bites",
                  "Point", "Kart", "Diner", "Studio", "Deli"]

rows = []
restaurant_id = 1

for _, city in dim_city.iterrows():
    tier = city["city_tier"]
    low, high = TIER_RESTAURANT_RANGE[tier]
    n_restaurants = np.random.randint(low, high + 1)

    launch = city["platform_launch_date"].date()
    days_available = (DATA_WINDOW_END - launch).days

    types = list(RESTAURANT_TYPE_PROBS.keys())
    type_weights = list(RESTAURANT_TYPE_PROBS.values())

    for _ in range(n_restaurants):
        restaurant_type = np.random.choice(types, p=type_weights)
        cuisine = np.random.choice(CUISINES)

        if restaurant_type == "Chain Outlet":
            restaurant_name = np.random.choice(CHAIN_BRANDS)
        else:
            restaurant_name = f"{np.random.choice(NAME_PREFIXES)} {np.random.choice(NAME_SUFFIXES)}"

        offset = np.random.randint(0, days_available + 1)
        onboarding_date = launch + timedelta(days=int(offset))

        c_low, c_high = COMMISSION_RANGE[restaurant_type]
        commission_rate = round(np.random.uniform(c_low, c_high), 3)

        avg_rating = np.clip(np.random.normal(3.9, 0.4), 2.5, 5.0)
        avg_rating = round(avg_rating, 1)

        rows.append({
            "restaurant_id": restaurant_id,
            "restaurant_name": restaurant_name,
            "city_id": int(city["city_id"]),
            "cuisine_type": cuisine,
            "restaurant_type": restaurant_type,
            "onboarding_date": onboarding_date,
            "commission_rate": commission_rate,
            "avg_rating": avg_rating,
        })
        restaurant_id += 1

dim_restaurant = pd.DataFrame(rows)
dim_restaurant.to_csv("../data/dim_restaurant.csv", index=False)

print(f"Total restaurants generated: {len(dim_restaurant)}\n")

merged = dim_restaurant.merge(dim_city[["city_id", "city_name", "city_tier"]], on="city_id")
print("--- Restaurants per city ---")
print(merged.groupby(["city_tier", "city_name"])["restaurant_id"].count())

print("\n--- Restaurant type mix ---")
print(dim_restaurant["restaurant_type"].value_counts(normalize=True).round(3))

print("\n--- Commission rate by restaurant type (should show Chain < Standalone < Cloud Kitchen) ---")
print(dim_restaurant.groupby("restaurant_type")["commission_rate"].agg(["mean", "min", "max"]).round(3))

print("\n--- Rating distribution ---")
print(dim_restaurant["avg_rating"].describe().round(2))

print("\n--- Integrity check: any restaurant onboarded before city launch? ---")
check = merged.merge(dim_city[["city_id", "platform_launch_date"]], on="city_id")
bad = check[pd.to_datetime(check["onboarding_date"]) < check["platform_launch_date"]]
print(f"Violations found: {len(bad)} (should be 0)")
