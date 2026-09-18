# Deal Hopper — Power BI Setup Guide (Stage 9)

## Architecture Decision

- **8 raw star-schema tables** imported directly (DAX-driven, not
  pre-aggregated) — `dim_city`, `dim_customer`, `dim_restaurant`,
  `dim_product`, `dim_product_price_history`, `dim_promotion`, `dim_date`,
  `fact_order`, `fact_order_item`
- **1 supplementary table**: `vw_promotion_margin_drain_score` — imported
  as-is, since replicating its `PERCENT_RANK()`-based percentile logic
  natively in DAX would be considerably more complex for no real analytical
  benefit. Every other measure in this project is genuine DAX over the raw
  tables.

---

## Step 1 — Connect Power BI Desktop to Postgres

1. Power BI Desktop needs the **Npgsql** driver to talk to Postgres — it
   will prompt you to install this automatically the first time you
   connect, if it's missing.
2. **Get Data → More → Database → PostgreSQL database**
3. Server: `localhost`. Database: `deal_hopper`.
4. Choose **Import** mode (not DirectQuery).
5. Enter your Postgres username/password.
6. In the Navigator window, check all 9 tables (8 raw + the one view) and
   click **Load**.

---

## Step 2 — Verify/Build Model Relationships

Go to **Model view** and verify all relationships are one-to-many, single
filter direction (dimension → fact). Power BI's auto-detect is not
reliable for the fact-to-fact link (`fact_order` → `fact_order_item`) —
always check this one manually.

**This schema has two independent "diamond" ambiguities** that must each
have exactly one relationship deactivated to resolve (see the main
README's "Known Issues" section for the full diagnosis):
- Deactivate `dim_city → dim_customer` (keep `dim_city → dim_restaurant`
  active for regional reporting)
- Deactivate `dim_restaurant → dim_product` (keep `dim_restaurant →
  fact_order` active — this one is essential and must NOT be the one you
  turn off)

---

## Step 3 — Add the DAX Measures

See `dax_measures.txt` in this folder. Copy each measure into a **New
measure** one at a time, roughly in the order they appear (later measures
reference earlier ones).

---

## Step 4 — Validate Against Known Numbers

| Measure | Expected Value |
|---|---|
| Total Orders (all statuses) | 191,699 |
| Delivered Orders | 172,282 |
| Gross Item Value (GMV) | ~₹8.76 crore (87,611,447) |
| Total Discount (Delivered only) | ~₹32.28 lakh (3,227,839) |
| Total Contribution Margin | ~₹1.29 crore (12,876,481) |
| Contribution Margin % | ~14.70% |

If these don't match, check the `fact_order → fact_order_item`
relationship first.

---

## Step 5 — Build Dashboard Pages

1. Executive Overview
2. Promotion Intelligence
3. Customer Intelligence
4. Product & Menu Analytics
5. Restaurant Analytics
6. Operations & Delivery

See the main README's Stage 9 section for the detailed build notes on
each page, including the calculated-table DAX patterns used for pages
3-5 and the RANKX-based quartile/segmentation logic.
