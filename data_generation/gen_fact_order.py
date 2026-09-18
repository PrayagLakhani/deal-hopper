import pandas as pd
import numpy as np
import bisect
from datetime import date, timedelta

np.random.seed(42)

WINDOW_START = date(2024, 3, 1)
WINDOW_END = date(2025, 8, 31)

dim_customer = pd.read_csv("../data/dim_customer.csv", parse_dates=["signup_date"])
dim_restaurant = pd.read_csv("../data/dim_restaurant.csv")
dim_promotion = pd.read_csv("../data/dim_promotion.csv", parse_dates=["start_date", "end_date"])
dim_date = pd.read_csv("../data/dim_date.csv", parse_dates=["date_id"])
dim_date["date_id"] = dim_date["date_id"].dt.date

# --- Precompute: date -> (season, is_festive) as a plain dict for O(1) lookup ---
date_info = {row.date_id: (row.season, bool(row.is_festive_period)) for row in dim_date.itertuples()}

# --- Precompute: promotion_id -> promotion_type as a plain dict ---
promo_type_dict = dict(zip(dim_promotion["promotion_id"], dim_promotion["promotion_type"]))

# --- Precompute: restaurant lookup by city, sorted by onboarding_date for point-in-time filtering ---
restaurants_by_city = {}
city_min_onboard = {}
for city_id, grp in dim_restaurant.groupby("city_id"):
    grp_sorted = grp.sort_values("onboarding_date")
    onboard_dates = [d.date() if hasattr(d, "date") else d for d in pd.to_datetime(grp_sorted["onboarding_date"])]
    ids = grp_sorted["restaurant_id"].values
    weights = np.exp(grp_sorted["avg_rating"].values)
    restaurants_by_city[city_id] = (onboard_dates, ids, weights)
    city_min_onboard[city_id] = onboard_dates[0]

def restaurants_available_by(city_id, as_of_date):
    """Return (ids, normalized_weights) for restaurants onboarded on or before as_of_date."""
    onboard_dates, ids, weights = restaurants_by_city[city_id]
    idx = bisect.bisect_right(onboard_dates, as_of_date)
    if idx == 0:
        idx = 1  # guard: at least the earliest restaurant is always available from its own onboarding date onward
    avail_ids = ids[:idx]
    avail_weights = weights[:idx]
    return avail_ids, avail_weights / avail_weights.sum()

# --- Precompute: promotions as plain lists of tuples (promotion_id, start_date, end_date) ---
def to_tuples(df):
    return list(zip(df["promotion_id"].values,
                     [d.date() for d in df["start_date"]],
                     [d.date() for d in df["end_date"]]))

all_customer_promos = to_tuples(dim_promotion[dim_promotion["target_segment"] == "All Customers"])
new_customer_promos = to_tuples(dim_promotion[dim_promotion["target_segment"] == "New Customers Only"])
high_freq_promos = to_tuples(dim_promotion[dim_promotion["target_segment"] == "High-Frequency"])
lapsed_promos = to_tuples(dim_promotion[dim_promotion["target_segment"] == "Lapsed/Win-back"])

def active_all_customer_promos_on(d):
    return [pid for pid, s, e in all_customer_promos if s <= d <= e]

# --- Step 1: latent behavioral parameters per customer ---
n_cust = len(dim_customer)
base_rate = np.random.gamma(shape=2.0, scale=0.3, size=n_cust)  # mean ~0.6 orders/month

acq = dim_customer["acquisition_channel"].values
sensitivity = np.empty(n_cust)
beta_params = {
    "Promotional Signup Offer": (4, 2), "Paid Ads": (3, 3),
    "Referral": (2, 4), "Organic": (2, 5),
}
for channel, (a, b) in beta_params.items():
    mask = acq == channel
    sensitivity[mask] = np.random.beta(a, b, size=mask.sum())

sub_mult = np.where(dim_customer["subscription_status"] == "Active", 1.3,
             np.where(dim_customer["subscription_status"] == "Lapsed", 1.05, 1.0))

median_base_rate = np.median(base_rate)
is_high_freq_pool = base_rate > median_base_rate

observable_start = dim_customer["signup_date"].clip(lower=pd.Timestamp(WINDOW_START))
tenure_days = (pd.Timestamp(WINDOW_END) - observable_start).dt.days.values
expected_orders = base_rate * (tenure_days / 30) * sub_mult * (1 + 0.3 * sensitivity)
n_orders = np.random.poisson(np.clip(expected_orders, 0, None))

print(f"Target check -- total expected orders: {expected_orders.sum():,.0f}")
print(f"Actual total orders (after Poisson draw): {n_orders.sum():,}\n")

HOUR_WEIGHTS = np.array([1,1,1,1,1,2,4,6,8,7,5,6,10,12,8,6,7,9,11,14,15,10,5,2], dtype=float)
HOUR_WEIGHTS = HOUR_WEIGHTS / HOUR_WEIGHTS.sum()
HOURS = np.arange(24)

customer_ids = dim_customer["customer_id"].values
city_ids = dim_customer["city_id"].values
signup_dates = dim_customer["signup_date"].dt.date.values

order_rows = []
order_id = 1
rng = np.random.default_rng(42)

for i in range(n_cust):
    n = n_orders[i]
    if n == 0:
        continue

    customer_id = int(customer_ids[i])
    city_id = int(city_ids[i])
    signup = signup_dates[i]
    if city_id not in city_min_onboard:
        continue
    # Orders can't be recorded before our data window, AND can't happen before
    obs_start = max(signup, WINDOW_START, city_min_onboard[city_id])
    sens = sensitivity[i]

    qualifying = []
    for pid, s, e in all_customer_promos:
        os_, oe_ = max(obs_start, s), min(WINDOW_END, e)
        if os_ <= oe_:
            qualifying.append((pid, os_, oe_))
    new_cust_window_end = min(signup + timedelta(days=45), WINDOW_END)
    for pid, s, e in new_customer_promos:
        os_, oe_ = max(obs_start, s), min(new_cust_window_end, e)
        if os_ <= oe_:
            qualifying.append((pid, os_, oe_))
    pool = high_freq_promos if is_high_freq_pool[i] else lapsed_promos
    for pid, s, e in pool:
        os_, oe_ = max(obs_start, s), min(WINDOW_END, e)
        if os_ <= oe_:
            qualifying.append((pid, os_, oe_))

    used_restaurants = []
    orders_this_customer = []
    promo_trigger_prob = sens * 0.5
    span_full = (WINDOW_END - obs_start).days

    for _ in range(n):
        promo_id = None
        if qualifying and rng.random() < promo_trigger_prob:
            pid, s, e = qualifying[rng.integers(len(qualifying))]
            span = (e - s).days
            order_date = s + timedelta(days=int(rng.integers(0, span + 1)))
            promo_id = pid
        else:
            order_date = obs_start + timedelta(days=int(rng.integers(0, span_full + 1)))
            if rng.random() < 0.10:
                active = active_all_customer_promos_on(order_date)
                if active:
                    promo_id = int(active[rng.integers(len(active))])
        orders_this_customer.append((order_date, promo_id))

    orders_this_customer.sort(key=lambda x: x[0])

    for order_date, promo_id in orders_this_customer:
        if used_restaurants and rng.random() < 0.40:
            restaurant_id = int(used_restaurants[rng.integers(len(used_restaurants))])
        else:
            avail_ids, avail_weights = restaurants_available_by(city_id, order_date)
            restaurant_id = int(rng.choice(avail_ids, p=avail_weights))
            used_restaurants.append(restaurant_id)

        order_hour = int(rng.choice(HOURS, p=HOUR_WEIGHTS))
        order_channel = "App" if rng.random() < 0.85 else "Website"
        pm_roll = rng.random()
        if pm_roll < 0.50:
            payment_method, payment_processing_fee = "UPI", 2.0
        elif pm_roll < 0.75:
            payment_method, payment_processing_fee = "Card", 6.0
        elif pm_roll < 0.90:
            payment_method, payment_processing_fee = "Wallet", 3.0
        else:
            payment_method, payment_processing_fee = "COD", 0.0

        delivery_distance_km = round(float(np.clip(rng.exponential(3.0), 0.5, 15.0)), 1)
        delivery_cost = max(round(15 + delivery_distance_km * 8 + rng.normal(0, 3), 2), 10.0)

        base_delivery_fee = 20 + min(delivery_distance_km, 10) * 2
        is_free_delivery_promo = promo_id is not None and promo_type_dict.get(promo_id) == "Free Delivery"
        customer_delivery_fee = 0.0 if is_free_delivery_promo else round(base_delivery_fee, 2)

        pf_roll = rng.random()
        platform_fee_charged = 5.0 if pf_roll < 0.4 else 6.0 if pf_roll < 0.7 else 7.0 if pf_roll < 0.9 else 8.0

        season, is_festive = date_info.get(order_date, ("Summer", False))
        estimated_delivery_time_min = round(20 + delivery_distance_km * 3, 1)
        delay_factor = rng.normal(1.05, 0.15)
        if season == "Monsoon":
            delay_factor += 0.15
        if is_festive:
            delay_factor += 0.10
        actual_delivery_time_min = round(estimated_delivery_time_min * max(delay_factor, 0.8), 1)

        cancel_prob = 0.06 + (0.06 if payment_method == "COD" else 0.0)
        refund_prob = 0.03 + (0.04 if actual_delivery_time_min > estimated_delivery_time_min * 1.3 else 0.0)
        roll = rng.random()
        if roll < cancel_prob:
            order_status = "Cancelled"
            cr_roll = rng.random()
            cancellation_reason = ("Customer Cancelled" if cr_roll < 0.5
                                    else "Restaurant Rejected" if cr_roll < 0.8
                                    else "Delivery Partner Unavailable")
        elif roll < cancel_prob + refund_prob:
            order_status, cancellation_reason = "Refunded", None
        else:
            order_status, cancellation_reason = "Delivered", None

        order_rows.append((
            order_id, customer_id, restaurant_id, order_date, order_hour, order_channel,
            payment_method, payment_processing_fee, promo_id, delivery_distance_km,
            estimated_delivery_time_min, actual_delivery_time_min, delivery_cost,
            customer_delivery_fee, platform_fee_charged, order_status, cancellation_reason, None
        ))
        order_id += 1

COLS = ["order_id", "customer_id", "restaurant_id", "date_id", "order_hour", "order_channel",
        "payment_method", "payment_processing_fee", "promotion_id", "delivery_distance_km",
        "estimated_delivery_time_min", "actual_delivery_time_min", "delivery_cost",
        "customer_delivery_fee", "platform_fee_charged", "order_status", "cancellation_reason",
        "refund_amount"]
fact_order = pd.DataFrame(order_rows, columns=COLS)
fact_order["promotion_id"] = fact_order["promotion_id"].astype("Int64")  # nullable int, avoids "76.0" in CSV
fact_order.to_csv("../data/fact_order.csv", index=False)

print(f"Total fact_order rows generated: {len(fact_order):,}\n")
print("--- Order status mix ---")
print(fact_order["order_status"].value_counts(normalize=True).round(3))
print("\n--- Promotion usage rate ---")
print(f"{fact_order['promotion_id'].notna().mean():.1%} of orders used a promotion")
print("\n--- Payment method mix ---")
print(fact_order["payment_method"].value_counts(normalize=True).round(3))
print("\n--- Cancellation rate by payment method (COD should be highest) ---")
print(fact_order.groupby("payment_method")["order_status"].apply(lambda s: (s == "Cancelled").mean()).round(3))
print("\n--- Promotion usage rate by customer acquisition channel ---")
fo_cust = fact_order.merge(dim_customer[["customer_id", "acquisition_channel"]], on="customer_id")
print(fo_cust.groupby("acquisition_channel")["promotion_id"].apply(lambda s: s.notna().mean()).round(3))
