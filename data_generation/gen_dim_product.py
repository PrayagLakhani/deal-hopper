import pandas as pd
import numpy as np
from datetime import date, timedelta

np.random.seed(42)

DATA_WINDOW_END = date(2025, 8, 31)

dim_restaurant = pd.read_csv("../data/dim_restaurant.csv", parse_dates=["onboarding_date"])

CATEGORIES = ["Starters", "Main Course", "Biryani & Rice", "Beverages",
              "Desserts", "Snacks", "Combo"]

# Category probability weights, by cuisine. Each list aligns to CATEGORIES order.
CATEGORY_WEIGHTS_BY_CUISINE = {
    "North Indian":        [0.15, 0.35, 0.05, 0.15, 0.10, 0.10, 0.10],
    "South Indian":        [0.15, 0.20, 0.05, 0.15, 0.10, 0.30, 0.05],
    "Chinese":             [0.25, 0.25, 0.00, 0.15, 0.05, 0.25, 0.05],
    "Biryani & Mughlai":   [0.10, 0.15, 0.45, 0.10, 0.05, 0.05, 0.10],
    "Pizza & Italian":     [0.15, 0.35, 0.00, 0.15, 0.10, 0.10, 0.15],
    "Burgers & American":  [0.15, 0.30, 0.00, 0.15, 0.05, 0.20, 0.15],
    "Momos & Tibetan":     [0.20, 0.10, 0.00, 0.15, 0.05, 0.45, 0.05],
    "Rolls & Wraps":       [0.10, 0.10, 0.00, 0.15, 0.05, 0.55, 0.05],
    "Bakery & Desserts":   [0.05, 0.00, 0.00, 0.20, 0.55, 0.20, 0.00],
    "Cafe & Beverages":    [0.05, 0.00, 0.00, 0.45, 0.30, 0.20, 0.00],
    "Multi-cuisine":       [0.15, 0.25, 0.10, 0.15, 0.10, 0.15, 0.10],
}

VEG_PROB_BY_CUISINE = {
    "North Indian": 0.55, "South Indian": 0.80, "Chinese": 0.45,
    "Biryani & Mughlai": 0.25, "Pizza & Italian": 0.60, "Burgers & American": 0.45,
    "Momos & Tibetan": 0.50, "Rolls & Wraps": 0.40, "Bakery & Desserts": 0.90,
    "Cafe & Beverages": 0.90, "Multi-cuisine": 0.55,
}

# (price_low, price_high), (cost_ratio_low, cost_ratio_high) per category
PRICE_AND_COST_BY_CATEGORY = {
    "Starters":       ((100, 280), (0.28, 0.38)),
    "Main Course":    ((150, 380), (0.32, 0.42)),
    "Biryani & Rice": ((180, 450), (0.35, 0.45)),
    "Beverages":      ((40, 130), (0.12, 0.22)),
    "Desserts":       ((60, 190), (0.22, 0.32)),
    "Snacks":         ((60, 160), (0.25, 0.35)),
    "Combo":          ((250, 550), (0.28, 0.36)),
}

NAME_WORDS = {
    "Starters": ["Paneer Tikka", "Chicken 65", "Spring Rolls", "Kebab Platter", "Cheese Balls"],
    "Main Course": ["Butter Chicken", "Paneer Butter Masala", "Dal Makhani", "Kadai Chicken", "Veg Kolhapuri"],
    "Biryani & Rice": ["Hyderabadi Chicken Biryani", "Veg Biryani", "Mutton Biryani", "Egg Biryani", "Fried Rice Bowl"],
    "Beverages": ["Cold Coffee", "Masala Chai", "Fresh Lime Soda", "Mango Shake", "Iced Tea"],
    "Desserts": ["Gulab Jamun", "Chocolate Brownie", "Rasmalai", "Ice Cream Sundae", "Kheer"],
    "Snacks": ["Veg Momos", "Chicken Roll", "French Fries", "Samosa Plate", "Vada Pav"],
    "Combo": ["Meal Combo for 1", "Family Feast Combo", "Biryani + Drink Combo", "Burger Meal Combo"],
}

product_rows = []
price_rows = []
product_id = 1
price_id = 1

for _, rest in dim_restaurant.iterrows():
    cuisine = rest["cuisine_type"]
    n_products = np.random.randint(10, 26)
    weights = np.array(CATEGORY_WEIGHTS_BY_CUISINE[cuisine])
    weights = weights / weights.sum()
    veg_prob = VEG_PROB_BY_CUISINE[cuisine]
    creation_date = rest["onboarding_date"].date()

    for _ in range(n_products):
        category = np.random.choice(CATEGORIES, p=weights)
        is_veg = "Veg" if np.random.rand() < veg_prob else np.random.choice(["Non-Veg", "Egg"], p=[0.85, 0.15])
        is_combo = category in ("Main Course", "Biryani & Rice") and np.random.rand() < 0.12
        product_name = np.random.choice(NAME_WORDS[category])

        product_rows.append({
            "product_id": product_id,
            "restaurant_id": int(rest["restaurant_id"]),
            "product_name": product_name,
            "category": category,
            "is_veg": is_veg,
            "is_combo": is_combo,
        })

        # --- Price history (SCD Type 2) ---
        price_low, price_high = PRICE_AND_COST_BY_CATEGORY[category][0]
        cost_low, cost_high = PRICE_AND_COST_BY_CATEGORY[category][1]

        selling_price_v1 = round(np.random.uniform(price_low, price_high), 0)
        cost_ratio_v1 = np.random.uniform(cost_low, cost_high)
        ingredient_cost_v1 = round(selling_price_v1 * cost_ratio_v1, 2)

        days_available = (DATA_WINDOW_END - creation_date).days
        has_revision = days_available > 120 and np.random.rand() < 0.25

        if has_revision:
            revision_offset = np.random.randint(90, days_available - 30)
            revision_date = creation_date + timedelta(days=int(revision_offset))

            # v1 row: active from creation to just before revision
            price_rows.append({
                "price_id": price_id, "product_id": product_id,
                "selling_price": selling_price_v1, "ingredient_cost": ingredient_cost_v1,
                "effective_start_date": creation_date,
                "effective_end_date": revision_date - timedelta(days=1),
                "is_current": False,
            })
            price_id += 1

            # v2 row: price bumped 5-15%, cost scaled proportionally (+ small noise)
            bump = np.random.uniform(1.05, 1.15)
            selling_price_v2 = round(selling_price_v1 * bump, 0)
            ingredient_cost_v2 = round(ingredient_cost_v1 * np.random.uniform(1.03, bump), 2)

            price_rows.append({
                "price_id": price_id, "product_id": product_id,
                "selling_price": selling_price_v2, "ingredient_cost": ingredient_cost_v2,
                "effective_start_date": revision_date,
                "effective_end_date": None,
                "is_current": True,
            })
            price_id += 1
        else:
            price_rows.append({
                "price_id": price_id, "product_id": product_id,
                "selling_price": selling_price_v1, "ingredient_cost": ingredient_cost_v1,
                "effective_start_date": creation_date,
                "effective_end_date": None,
                "is_current": True,
            })
            price_id += 1

        product_id += 1

dim_product = pd.DataFrame(product_rows)
dim_product_price_history = pd.DataFrame(price_rows)

dim_product.to_csv("../data/dim_product.csv", index=False)
dim_product_price_history.to_csv("../data/dim_product_price_history.csv", index=False)

print(f"Total products generated: {len(dim_product)}")
print(f"Total price-history rows: {len(dim_product_price_history)} "
      f"({(dim_product_price_history.shape[0] - dim_product.shape[0])} products got a price revision)\n")

print("--- Category mix, overall ---")
print(dim_product["category"].value_counts(normalize=True).round(3))

print("\n--- Veg/Non-Veg/Egg mix, overall ---")
print(dim_product["is_veg"].value_counts(normalize=True).round(3))

print("\n--- Price & cost ratio sanity check, by category (current prices only) ---")
current_prices = dim_product_price_history[dim_product_price_history["is_current"]]
check = dim_product.merge(current_prices, on="product_id")
check["cost_ratio"] = check["ingredient_cost"] / check["selling_price"]
print(check.groupby("category")[["selling_price", "cost_ratio"]].mean().round(2))

print("\n--- Integrity check: every product has exactly one is_current=True row ---")
current_counts = dim_product_price_history[dim_product_price_history["is_current"]].groupby("product_id").size()
bad = current_counts[current_counts != 1]
print(f"Products with != 1 current price row: {len(bad)} (should be 0)")

print("\n--- Integrity check: revision dates fall after creation and before window end ---")
rev_rows = dim_product_price_history[~dim_product_price_history["is_current"]]
merged_check = rev_rows.merge(dim_product[["product_id", "restaurant_id"]], on="product_id")
merged_check = merged_check.merge(dim_restaurant[["restaurant_id", "onboarding_date"]], on="restaurant_id")
bad2 = merged_check[pd.to_datetime(merged_check["effective_start_date"]) < merged_check["onboarding_date"]]
print(f"Violations found: {len(bad2)} (should be 0)")
