import pandas as pd
import numpy as np
from datetime import date

np.random.seed(42)

fact_order = pd.read_csv("../data/fact_order.csv", parse_dates=["date_id"])
fact_order["date_id"] = fact_order["date_id"].dt.date
dim_product = pd.read_csv("../data/dim_product.csv")
dim_price_hist = pd.read_csv("../data/dim_product_price_history.csv",
                              parse_dates=["effective_start_date", "effective_end_date"])
dim_promotion = pd.read_csv("../data/dim_promotion.csv")

# --- Precompute: products by restaurant ---
products_by_restaurant = {}
for rid, grp in dim_product.groupby("restaurant_id"):
    products_by_restaurant[rid] = list(zip(grp["product_id"], grp["category"]))

# --- Precompute: point-in-time price lookup, product_id -> sorted list of periods ---
FAR_FUTURE = date(2100, 1, 1)
price_history = {}
for row in dim_price_hist.itertuples():
    end = row.effective_end_date.date() if pd.notna(row.effective_end_date) else FAR_FUTURE
    price_history.setdefault(row.product_id, []).append(
        (row.effective_start_date.date(), end, row.selling_price, row.ingredient_cost)
    )
for pid in price_history:
    price_history[pid].sort(key=lambda x: x[0])

def get_price(product_id, order_date):
    for start, end, price, cost in price_history[product_id]:
        if start <= order_date <= end:
            return price, cost
    last = price_history[product_id][-1]
    return last[2], last[3]

# --- Precompute: promotion lookup dict ---
promo_lookup = {row.promotion_id: row for row in dim_promotion.itertuples()}

PACKAGING_COST = {
    "Starters": 5, "Main Course": 8, "Biryani & Rice": 8, "Beverages": 3,
    "Desserts": 4, "Snacks": 5, "Combo": 10,
}

N_ITEMS_CHOICES = [1, 2, 3, 4]
N_ITEMS_PROBS = [0.30, 0.35, 0.22, 0.13]
QTY_CHOICES = [1, 2, 3]
QTY_PROBS = [0.80, 0.15, 0.05]

rng = np.random.default_rng(42)
item_rows = []
order_item_id = 1

order_ids = fact_order["order_id"].values
restaurant_ids = fact_order["restaurant_id"].values
order_dates = fact_order["date_id"].values
promo_ids = fact_order["promotion_id"].values

for i in range(len(fact_order)):
    order_id = int(order_ids[i])
    restaurant_id = int(restaurant_ids[i])
    order_date = order_dates[i]
    promo_id = promo_ids[i]
    promo_id = int(promo_id) if pd.notna(promo_id) else None

    products = products_by_restaurant.get(restaurant_id)
    if not products:
        continue

    n_items = int(rng.choice(N_ITEMS_CHOICES, p=N_ITEMS_PROBS))
    n_items = min(n_items, len(products))
    chosen_idx = rng.choice(len(products), size=n_items, replace=False)

    line_items = []
    for idx in chosen_idx:
        product_id, category = products[idx]
        quantity = int(rng.choice(QTY_CHOICES, p=QTY_PROBS))
        price, cost = get_price(product_id, order_date)
        gross_value = price * quantity
        packaging = PACKAGING_COST.get(category, 5) + rng.normal(0, 0.5)
        line_items.append({
            "product_id": product_id, "quantity": quantity,
            "item_price": price, "item_ingredient_cost": cost,
            "gross_value": gross_value, "packaging_cost": round(max(packaging, 1), 2),
        })

    order_gross_value = sum(li["gross_value"] for li in line_items)

    # --- Discount calculation, based on promotion type ---
    total_discount = 0.0
    if promo_id is not None and promo_id in promo_lookup:
        promo = promo_lookup[promo_id]
        if order_gross_value >= promo.min_order_value:
            if promo.promotion_type == "Percentage Off":
                total_discount = order_gross_value * (promo.discount_value / 100)
                if pd.notna(promo.max_discount_cap):
                    total_discount = min(total_discount, promo.max_discount_cap)
            elif promo.promotion_type == "Flat Amount Off":
                total_discount = min(promo.discount_value, order_gross_value)
            elif promo.promotion_type == "Cashback":
                total_discount = min(promo.discount_value, order_gross_value)
            elif promo.promotion_type == "BOGO":
                cheapest = min(li["gross_value"] for li in line_items)
                total_discount = cheapest
                if pd.notna(promo.max_discount_cap):
                    total_discount = min(total_discount, promo.max_discount_cap)
            # Free Delivery: no item-level discount (handled at order level already)

    # --- Allocate discount proportionally to items, fixing rounding remainder on the last item ---
    allocated_so_far = 0.0
    for j, li in enumerate(line_items):
        if order_gross_value > 0 and total_discount > 0:
            if j < len(line_items) - 1:
                share = round(total_discount * (li["gross_value"] / order_gross_value), 2)
            else:
                share = round(total_discount - allocated_so_far, 2)
            allocated_so_far += share
        else:
            share = 0.0

        item_rows.append((
            order_item_id, order_id, li["product_id"], li["quantity"],
            li["item_price"], li["item_ingredient_cost"], share, li["packaging_cost"]
        ))
        order_item_id += 1

COLS = ["order_item_id", "order_id", "product_id", "quantity", "item_price",
        "item_ingredient_cost", "item_discount_allocated", "packaging_cost"]
fact_order_item = pd.DataFrame(item_rows, columns=COLS)
fact_order_item.to_csv("../data/fact_order_item.csv", index=False)

print(f"Total fact_order_item rows generated: {len(fact_order_item):,}")
print(f"Average items per order: {len(fact_order_item) / len(fact_order):.2f}\n")

print("--- Sanity: item_price and item_ingredient_cost stats ---")
print(fact_order_item[["item_price", "item_ingredient_cost"]].describe().round(2))

print("\n--- Sanity: total discount allocated (should be > 0, reflecting promo usage) ---")
print(f"Total discount allocated: Rs {fact_order_item['item_discount_allocated'].sum():,.0f}")

print("\n--- Sanity: unit cost ratio (ingredient_cost / price) should be well under 1.0 ---")
print(f"Average unit cost ratio: {(fact_order_item['item_ingredient_cost'] / fact_order_item['item_price']).mean():.2f}")

print("\n--- Integrity check: unit ingredient_cost should never exceed unit item_price ---")
bad_units = fact_order_item[fact_order_item["item_ingredient_cost"] > fact_order_item["item_price"]]
print(f"Violations found: {len(bad_units)} (should be 0)")
gross = fact_order_item["item_price"] * fact_order_item["quantity"]
bad = fact_order_item[fact_order_item["item_discount_allocated"] > gross]
print(f"Violations found: {len(bad)} (should be 0)")

print("\n--- Integrity check: orders with a Free Delivery promo have zero item-level discount ---")
fd_promo_ids = dim_promotion[dim_promotion["promotion_type"] == "Free Delivery"]["promotion_id"].tolist()
fd_orders = fact_order[fact_order["promotion_id"].isin(fd_promo_ids)]["order_id"]
fd_items = fact_order_item[fact_order_item["order_id"].isin(fd_orders)]
bad2 = fd_items[fd_items["item_discount_allocated"] > 0]
print(f"Violations found: {len(bad2)} (should be 0)")
