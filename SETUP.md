# Deal Hopper — Margin Drain Intelligence

## Project Structure

```
deal_hopper/
├── README.md                              # Project overview
├── SETUP.md                               # Detailed setup and reproduction guide
├── requirements.txt                       # Python dependencies
├── .env.example                           # PostgreSQL configuration template
├── Power_BI_Dashboard.pbix                # Power BI dashboard
│
├── data_generation/                       # Synthetic dataset generation scripts
│   ├── gen_dim_city.py                    # Generates dim_city.csv
│   ├── gen_dim_customer.py                # Generates dim_customer.csv
│   ├── gen_dim_date.py                    # Generates dim_date.csv
│   ├── gen_dim_product.py                 # Generates dim_product.csv + dim_product_price_history.csv
│   ├── gen_dim_promotion.py               # Generates dim_promotion.csv
│   ├── gen_dim_restaurant.py              # Generates dim_restaurant.csv
│   ├── gen_fact_order.py                  # Generates fact_order.csv
│   └── gen_fact_order_item.py             # Generates fact_order_item.csv
│
├── data/                                  # Generated CSV dataset
│   ├── dim_city.csv                       # 12 cities
│   ├── dim_customer.csv                   # ~17,800 customers
│   ├── dim_date.csv                       # 549 calendar days
│   ├── dim_product.csv                    # ~6,210 products
│   ├── dim_product_price_history.csv      # ~7,570 SCD Type 2 price-history rows
│   ├── dim_promotion.csv                  # 150 promotions
│   ├── dim_restaurant.csv                 # ~349 restaurants
│   ├── fact_order.csv                     # ~191,700 orders
│   └── fact_order_item.csv                # ~418,000 order-item rows
│
├── sql/                                   # PostgreSQL schema, validation, views & analysis
│   ├── 01_create_dim_city.sql             # Creates dim_city
│   ├── 02_validate_dim_city.sql           # Validates dim_city
│   ├── 03_create_dim_customer.sql         # Creates dim_customer
│   ├── 04_validate_dim_customer.sql       # Validates dim_customer
│   ├── 05_create_dim_restaurant.sql       # Creates dim_restaurant
│   ├── 06_validate_dim_restaurant.sql     # Validates dim_restaurant
│   ├── 07_create_dim_product.sql          # Creates dim_product + price history
│   ├── 08_validate_dim_product.sql       # Validates product tables
│   ├── 09_create_dim_promotion.sql        # Creates dim_promotion
│   ├── 10_validate_dim_promotion.sql      # Validates dim_promotion
│   ├── 11_create_dim_date.sql              # Creates dim_date
│   ├── 12_validate_dim_date.sql            # Validates dim_date
│   ├── 13_create_fact_order.sql            # Creates fact_order
│   ├── 14_validate_fact_order.sql          # Validates fact_order
│   ├── 15_create_fact_order_item.sql       # Creates fact_order_item
│   ├── 16_validate_fact_order_item.sql     # Validates fact_order_item
│   ├── 17_enrich_refund_amount.sql         # Populates refund_amount
│   ├── 18_validate_refund_enrichment.sql   # Validates refund enrichment
│   ├── 19_stage5_cross_table_validation.sql # Cross-table validation
│   ├── 20_create_vw_order_economics.sql    # Creates order economics view
│   ├── 21_validate_order_economics.sql     # Validates order economics
│   ├── 22_promotion_analysis.sql           # Promotion performance analysis
│   ├── 23_create_vw_customer_summary.sql   # Creates customer summary view
│   ├── 24_customer_analysis.sql            # Customer profitability & RFM analysis
│   ├── 25_create_vw_product_summary.sql    # Creates product summary view
│   ├── 26_create_vw_restaurant_summary.sql # Creates restaurant summary view
│   ├── 27_product_restaurant_analysis.sql  # Product & restaurant analysis
│   ├── 28_cohort_retention_analysis.sql    # Cohort & retention analysis
│   ├── 29_operations_delivery_analysis.sql # Delivery & operational analysis
│   ├── 30_create_vw_margin_drain_score.sql # Creates margin-drain scoring view
│   └── 31_validate_margin_drain_score.sql  # Validates margin-drain scores
│
├── python_eda/                             # Statistical analysis & visualization
│   ├── 01_overview_eda.py                 # Distributions, correlations & outliers
│   ├── 02_promotion_distance_eda.py       # Promotion impact & distance analysis
│   ├── 03_customer_segmentation_eda.py    # Customer dependency & RFM analysis
│   ├── 04_product_restaurant_eda.py       # Product margin & restaurant analysis
│   ├── db_utils.py                         # Shared PostgreSQL connection helper
│   └── outputs/                            # Generated EDA visualizations
│       ├── 01_distributions.png
│       ├── 02_correlation_heatmap.png
│       ├── 03_promotion_boxplots.png
│       ├── 04_distance_margin_relationship.png
│       ├── 05_discount_dependency.png
│       ├── 06_frequency_and_rfm_segments.png
│       ├── 07_rfm_bubble_chart.png
│       ├── 08_product_margin_matrix.png
│       ├── 09_category_margin_ranking.png
│       └── 10_restaurant_volume_vs_contribution.png
│
├── power_bi/                               # Power BI documentation & measures
│   └── dax_measures.txt                   # DAX measures used in dashboard
│
└── docs/                                   # Supporting project documentation
    └── schema_erd.png                     # PostgreSQL schema ER diagram

```

## Prerequisites (one-time setup)

1. **Python 3.10+** — [python.org/downloads](https://www.python.org/downloads/)
2. **PostgreSQL** (server) — [postgresql.org/download](https://www.postgresql.org/download/)
3. **pgAdmin 4** — usually bundled with the PostgreSQL installer, or standalone at [pgadmin.org/download](https://www.pgadmin.org/download/)

---

## Step 1 — Set Up Your Python Environment

Open a terminal in this project folder and run:

```bash
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
---

## Prerequisites (one-time setup)

1. **Python 3.10+** — [python.org/downloads](https://www.python.org/downloads/)
2. **PostgreSQL** (server) — [postgresql.org/download](https://www.postgresql.org/download/)
3. **pgAdmin 4** — usually bundled with the PostgreSQL installer, or standalone at [pgadmin.org/download](https://www.pgadmin.org/download/)

---

## Step 1 — Set Up Your Python Environment

Open a terminal in this project folder and run:

```bash
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

## Step 2 — Generate the Data

```bash
python data_generation/gen_dim_city.py
```

This creates/overwrites `data/dim_city.csv` and prints a validation summary
to your terminal (city list, counts by tier, cities per region).

## Step 3 — Create the Database in pgAdmin 4

1. Open pgAdmin 4 and connect to your local PostgreSQL server (it'll ask for
   the password you set during installation).
2. Right-click **Databases** → **Create** → **Database...**
3. Name it `deal_hopper` → **Save**.

## Step 4 — Create the Table

1. Click on the `deal_hopper` database, then open the **Query Tool**
   (toolbar icon, or right-click the DB → Query Tool).
2. Open `sql/01_create_dim_city.sql` (File → Open, in the Query Tool),
   or just paste its contents in.
3. Click **Execute** (the ▶ play button, or F5).
4. You should see `CREATE TABLE` with no errors. Refresh the database tree
   on the left (right-click `deal_hopper` → Refresh) — you'll now see
   `dim_city` under **Schemas → public → Tables**.

## Step 5 — Import the CSV

1. Right-click the `dim_city` table → **Import/Export Data...**
2. Toggle to **Import**.
3. **Filename**: browse to `data/dim_city.csv`.
4. **Format**: csv
5. Go to the **Options** tab → make sure **Header** is turned ON
   (the CSV's first row is column names, not data).
6. Click **OK**. It should report success and the row count (12).

## Step 6 — Validate

1. Back in the **Query Tool** on `deal_hopper`, open
   `sql/02_validate_dim_city.sql` and run it (F5).
2. Check that:
   - Total city count = 12
   - Every region shows 2-3 cities
   - Tier 1 has the largest average market size and earliest launch dates,
     decreasing through Tier 2 and Tier 3

If all of that checks out, `dim_city` is fully set up and validated on your
machine — ready for the next table.

---

## Table 2: `dim_customer`

Same pattern as above, run in order:

1. **Generate**: `python data_generation/gen_dim_customer.py`
   (run this from inside the `data_generation/` folder, since it reads
   `../data/dim_city.csv` — so `dim_city.csv` must already exist)
2. **Create table**: run `sql/03_create_dim_customer.sql` in the Query Tool
   (this has a foreign key to `dim_city`, so `dim_city` must be created and
   populated first)
3. **Import**: right-click `dim_customer` in pgAdmin 4 → Import/Export Data →
   import `data/dim_customer.csv` (Header = ON, same as before)
4. **Validate**: run `sql/04_validate_dim_customer.sql` and confirm:
   - Total customers ≈ 17,800
   - Tier 1 cities show the most customers, Tier 3 the fewest
   - Both integrity checks (queries 5 and 6) return **0 rows**

---

## Table 3: `dim_restaurant`

1. **Generate**: `python data_generation/gen_dim_restaurant.py`
   (run from inside `data_generation/`, since it reads `../data/dim_city.csv`)
2. **Create table**: run `sql/05_create_dim_restaurant.sql` (FK to `dim_city`,
   so `dim_city` must exist first)
3. **Import**: import `data/dim_restaurant.csv` into `dim_restaurant`
   (Header = ON)
4. **Validate**: run `sql/06_validate_dim_restaurant.sql` and confirm:
   - Total restaurants ≈ 349
   - Commission rate ordering: Chain Outlet < Standalone < Cloud Kitchen
   - Integrity check (query 6) returns **0 rows**

---

## Table 4: `dim_product` + `dim_product_price_history`

This one creates **two** tables together (identity + SCD Type 2 price history).

1. **Generate**: `python data_generation/gen_dim_product.py`
   (run from inside `data_generation/`, reads `../data/dim_restaurant.csv`)
2. **Create tables**: run `sql/07_create_dim_product.sql` (creates both
   tables; FK to `dim_restaurant`, so that must exist first)
3. **Import**: import `data/dim_product.csv` into `dim_product`, then
   `data/dim_product_price_history.csv` into `dim_product_price_history`
   (Header = ON for both — do `dim_product` first since price history
   references it)
4. **Validate**: run `sql/08_validate_dim_product.sql` and confirm:
   - ~6,210 products, ~7,570 price-history rows
   - Beverages show the lowest cost ratio, Biryani & Rice the highest
   - Integrity check (query 5) returns **0 rows** — every product has
     exactly one current price

---

## Table 5: `dim_promotion`

No foreign key dependencies — can be created any time.

1. **Generate**: `python data_generation/gen_dim_promotion.py`
2. **Create table**: run `sql/09_create_dim_promotion.sql`
3. **Import**: import `data/dim_promotion.csv` into `dim_promotion`
   (Header = ON)
4. **Validate**: run `sql/10_validate_dim_promotion.sql` and confirm:
   - Total promotions = 150
   - Funding split roughly 70% Platform Only / 30% Co-funded
   - Integrity check (query 5) returns **0 rows**

---

## Table 6: `dim_date`

No foreign key dependencies — can be created any time.

1. **Generate**: `python data_generation/gen_dim_date.py`
2. **Create table**: run `sql/11_create_dim_date.sql`
3. **Import**: import `data/dim_date.csv` into `dim_date` (Header = ON)
4. **Validate**: run `sql/12_validate_dim_date.sql` and confirm:
   - Total days = 549
   - Weekend days ≈ 28.6% of total
   - Integrity check (query 5) returns **0 rows**

---

## All Dimension Tables Complete

At this point you should have 6 dimension tables fully loaded and validated:
`dim_city`, `dim_customer`, `dim_restaurant`, `dim_product` (+
`dim_product_price_history`), `dim_promotion`, `dim_date`. Next come the two
fact tables (`fact_order`, `fact_order_item`), which reference all of these.

---

## Table 7: `fact_order` (order header)

This is the big one — ~191,700 orders, generated using latent per-customer
behavioral traits (order frequency, discount sensitivity) so the resulting
patterns are genuinely discoverable, not just random.

**Important**: `refund_amount` is left NULL in this file. It genuinely
depends on the order's total value, which only exists once
`fact_order_item` is built — we'll run a short enrichment script to fill it
in once that table exists. This is normal and expected for now.

1. **Generate**: `python data_generation/gen_fact_order.py`
   (run from inside `data_generation/`; reads `dim_customer.csv`,
   `dim_restaurant.csv`, `dim_promotion.csv`, `dim_date.csv` — all must
   already be generated)
2. **Create table**: run `sql/13_create_fact_order.sql` in the Query Tool
   (FKs to `dim_customer`, `dim_restaurant`, `dim_date`, `dim_promotion` —
   all four must exist and be populated first)
3. **Import**: import `data/fact_order.csv` into `fact_order` (Header = ON).
   Note: the `refund_amount` column will import as blank/NULL for every
   row — that's expected at this stage.
4. **Validate**: run `sql/14_validate_fact_order.sql` and confirm:
   - Total orders ≈ 191,700
   - Order status roughly 90% Delivered / 6.6% Cancelled / 3.5% Refunded
   - Query 4: "Promotional Signup Offer" customers show a noticeably
     higher promo-usage rate than "Organic" customers
   - Query 5: COD shows a noticeably higher cancellation rate than other
     payment methods
   - Queries 6 and 7 (integrity checks) return **0 rows**

---

## Table 8: `fact_order_item` (order line items — the last table!)

~418,000 rows, one per product per order, with point-in-time pricing (SCD
Type 2 lookup) and proportionally-allocated discounts.

1. **Generate**: `python data_generation/gen_fact_order_item.py`
   (run from inside `data_generation/`; reads `fact_order.csv`,
   `dim_product.csv`, `dim_product_price_history.csv`, `dim_promotion.csv`)
2. **Create table**: run `sql/15_create_fact_order_item.sql` (FKs to
   `fact_order` and `dim_product` — both must exist first)
3. **Import**: import `data/fact_order_item.csv` into `fact_order_item`
   (Header = ON)
4. **Validate**: run `sql/16_validate_fact_order_item.sql` and confirm:
   - ~418,000 items, ~2.18 items/order
   - Cost ratio ordering: Beverages lowest, Biryani & Rice highest
   - All three integrity checks (queries 4-6) return **0 rows**

### Enrichment Step: Populate `refund_amount`

Now that order totals exist, run the enrichment we flagged back when we
built `fact_order`:

1. Run `sql/17_enrich_refund_amount.sql` (an `UPDATE ... FROM` — a good SQL
   pattern to recognize: it fills in a header field using an aggregate
   computed from the detail table)
2. Run `sql/18_validate_refund_enrichment.sql` and confirm:
   - Every `Refunded` order now has a non-null `refund_amount`; every
     `Delivered`/`Cancelled` order stays NULL
   - Refund amounts fall in a believable range (tens to a few thousand ₹)

---

## 🎉 Data Generation Complete

All 8 tables are built, loaded, and validated: `dim_city`, `dim_customer`,
`dim_restaurant`, `dim_product` (+ `dim_product_price_history`),
`dim_promotion`, `dim_date`, `fact_order`, `fact_order_item` — roughly
**625,000 total rows** across the fact tables, all internally consistent
and tied to real business logic (commission economics, cost ratios,
discount-dependency behavior, COD cancellation risk, and more). This
dataset is now ready for SQL analysis, Python EDA, and the Power BI
dashboard.

---

## Stage 5: Cross-Table Data Validation

Beyond the per-table checks above, run one more holistic pass now that
every table is loaded:

1. Run `sql/19_stage5_cross_table_validation.sql`
2. Confirm:
   - The row-count summary matches: `dim_city`=12, `dim_customer`≈17,808,
     `dim_restaurant`≈349, `dim_product`≈6,210,
     `dim_product_price_history`≈7,570, `dim_promotion`=150, `dim_date`=549,
     `fact_order`≈191,699, `fact_order_item`≈418,085
   - Query 2 (order dated before its restaurant onboarded) returns **0 rows**
   - Query 3 (promotion window compliance) returns **0 rows**
   - Query 4 (minimum order value compliance) returns **0 rows**
   - Query 5 (every order has at least one item) returns **0 rows**
   - Query 6 (business health): AOV around ₹500-550, discount % in the
     low single digits, cancellation ~6-7%, refund ~3-4%
   - Queries 7-8 (informational): a small single-digit % of customers
     never ordered, and well under 1% of restaurants never got an order —
     both expected, not bugs

**Note on regenerated files**: `gen_fact_order.py` and `gen_fact_order_item.py`
were both corrected during Stage 5 (a restaurant could previously be
assigned to an order dated before that restaurant had actually onboarded —
found and fixed via the cross-table checks above). If you generated these
two files before this fix, re-run both scripts and reload `fact_order.csv`
and `fact_order_item.csv` to pick up the correction.

## Stage 7: Python EDA

This stage connects directly to your Postgres database (rather than
re-reading CSVs) so Python and SQL analysis stay perfectly in sync.

### One-time setup

1. Copy `.env.example` to `.env` (same folder, project root) and fill in
   your real pgAdmin 4 / Postgres password:
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=deal_hopper
   DB_USER=postgres
   DB_PASSWORD=<your real password>
   ```
   **Never commit the real `.env` file** — only `.env.example` should be
   shared/version-controlled.
2. Make sure `sql/20_create_vw_order_economics.sql` has been run (Python
   reads from this view).

### Part 1: Overview, Distributions, Outliers

Run from inside `python_eda/`:
```bash
python 01_overview_eda.py
```

This prints data types, missing-value counts, summary statistics, and IQR-based
outlier detection to your terminal, and saves two charts to
`python_eda/outputs/`:
- `01_distributions.png` — order value, contribution margin, delivery
  distance, and discount amount distributions
- `02_correlation_heatmap.png` — correlation matrix between order economics
  and delivery distance

**A genuinely important finding from this step**: the raw correlation
between `delivery_distance_km` and `contribution_margin` is only -0.21,
much weaker than the dramatic pattern SQL found (₹89 → ₹15 across distance
bands). This isn't a contradiction — `gross_item_value` correlates 0.83
with margin and has ~0 correlation with distance, so its variance dilutes
the pairwise correlation. Grouped/binned analysis (like the SQL distance
bands) can reveal real effects that a single correlation coefficient hides.

---

## Known Limitations (Documented Honestly)

- **Retention/cohort curves are shallow and don't differ meaningfully by
  acquisition channel.** This is a property of the generator, not a real
  finding: `acquisition_channel` affects per-order discount sensitivity
  (validated strongly — 40.4% vs 22.7% promo usage) but the generator never
  modeled month-over-month churn/attrition explicitly. Total order count
  per customer is a single Poisson draw over their whole tenure, not a
  decaying month-by-month process. A real improvement here would be adding
  an explicit churn mechanism so retention curves reflect genuine behavioral
  decay rather than mostly tenure-censoring effects.
- **Cohort "Month 0" reads artificially low compared to Month 1** in any
  cohort table — this is a known methodological artifact (partial first
  calendar month depending on signup day), not a data bug.

- **Business model**: Marketplace/aggregator (independent restaurant
  partners, platform owns delivery + funds most promotions)
- **Primary stakeholder**: Head of Product/Strategy (balances growth vs.
  profitability)
- **Fact table grain**: Order-item level (one row per product per order)
- **Time window**: 18 months (Mar 2024 – Aug 2025)
- **Cities**: 12 (4 Tier-1, 5 Tier-2, 3 Tier-3), spanning all 5 regions
  (North/South/East/West/Central) with 2-3 cities each
- **Target scale**: ~18,000 customers, ~350 restaurants, ~6,300 products,
  ~150 promotions, ~200,000 orders, ~440,000 order-item rows
- **Database**: PostgreSQL (via pgAdmin 4, run locally)
- **Random seed**: All generation scripts use `np.random.seed(42)` for
  full reproducibility

---

## Stage 8: The Margin Drain Score

A composite 0-100 score per promotion (higher = more drain) combining five
percentile-ranked factors: contribution margin % (40% weight), discount
efficiency (25%), budget overrun (15%), refund/cancellation rate (10%), and
average discount-dependency of the customers it reaches (10%).

1. Run `sql/30_create_vw_margin_drain_score.sql`
2. Run `sql/31_validate_margin_drain_score.sql` and confirm:
   - The "Severe Drain" tier shows **negative** average margin %, and
     "Healthy" shows solidly **positive** average margin % (if these are
     reversed, the percentile-rank sort directions are inverted — see the
     note below)
   - BOGO shows the highest average drain score; Free Delivery shows the
     lowest — matching the Stage 6/7 findings

**A bug worth knowing about if you ever build a similar score**:
`PERCENT_RANK() OVER (ORDER BY x ASC)` gives the *smallest* x a percentile
near 0 and the *largest* x a percentile near 1. If "worse" means a small
value for some factor (like margin %) and a large value for another (like
refund rate), each one needs the *opposite* sort direction to consistently
land "worse = higher percentile" before you sum them into one score. Getting
this backwards silently produces a score that's exactly inverted — it still
runs without error, so the only way to catch it is validating the result
against ground truth you already trust (which is exactly what
`31_validate...sql` does, by comparing against the Stage 6/7 findings).

---

## Stage 9: Power BI Dashboard

See `power_bi/README_power_bi_setup.md` for the full connection, modeling,
and DAX setup guide, and `power_bi/dax_measures.txt` for the complete
measure library. Architecture: 8 raw star-schema tables imported directly
(DAX-driven, per your Option B decision) plus `vw_promotion_margin_drain_score`
imported as a supplementary table (its PERCENT_RANK-based logic isn't worth
replicating natively in DAX).

**Validate before building any visuals** — Total Orders (191,699), Delivered
Orders (172,282), Gross Item Value (~₹8.76 crore), Total Discount, Delivered
only (~₹32.28 lakh), Total Contribution Margin (~₹1.29 crore), and
Contribution Margin % (~14.70%) should all match the SQL/Python numbers
from Stage 6/7 (see `power_bi/dax_measures.txt` for the full checklist and
an important note on why "Total Discount" differs from an unfiltered sum
across all order statuses). If they don't, check the `fact_order` →
`fact_order_item` relationship first — it's the one most likely to be
missed by Power BI's auto-detect.

---

## Stage 9 Finale: Styling & Polish

See `power_bi/deal_hopper_theme.json` (import via View -> Themes -> Browse
for themes) and `power_bi/styling_polish_checklist.md` for the full,
ordered checklist covering: theme application, measure display formats,
the deferred Page 1/2 conditional formatting, a consistent header banner
across pages, multi-select card formatting, and final alignment cleanup.
