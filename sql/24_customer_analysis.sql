-- Answers: who's profitable, who's discount-dependent, does frequency = profitability?

-- Top 15 most profitable customers
SELECT customer_id, acquisition_channel, subscription_status,
       delivered_orders, ROUND(total_gmv, 0) AS total_gmv,
       ROUND(total_contribution, 0) AS total_contribution,
       promo_usage_rate, avg_order_value
FROM vw_customer_summary
WHERE delivered_orders > 0
ORDER BY total_contribution DESC
LIMIT 15;

-- Discount dependency vs profitability
SELECT
    CASE
        WHEN promo_usage_rate = 0 THEN '0% (never used)'
        WHEN promo_usage_rate <= 0.25 THEN '1-25%'
        WHEN promo_usage_rate <= 0.50 THEN '26-50%'
        WHEN promo_usage_rate <= 0.75 THEN '51-75%'
        ELSE '76-100%'
    END AS discount_dependency_band,
    COUNT(*) AS num_customers,
    ROUND(AVG(delivered_orders), 1) AS avg_orders_per_customer,
    ROUND(AVG(contribution_per_order), 2) AS avg_contribution_per_order,
    ROUND(SUM(total_contribution), 0) AS total_contribution
FROM vw_customer_summary
WHERE delivered_orders >= 3
GROUP BY discount_dependency_band
ORDER BY discount_dependency_band;

-- Does order FREQUENCY predict PROFITABILITY?
WITH scored AS (
    SELECT *,
           NTILE(4) OVER (ORDER BY delivered_orders) AS frequency_quartile
    FROM vw_customer_summary
    WHERE delivered_orders > 0
)
SELECT
    frequency_quartile,
    COUNT(*) AS num_customers,
    ROUND(MIN(delivered_orders), 0) AS min_orders,
    ROUND(MAX(delivered_orders), 0) AS max_orders,
    ROUND(AVG(contribution_per_order), 2) AS avg_contribution_per_order,
    ROUND(AVG(promo_usage_rate), 3) AS avg_promo_usage_rate
FROM scored
GROUP BY frequency_quartile
ORDER BY frequency_quartile;

-- "Growth trap" customers — top-quartile revenue, but bottom-half contribution-per-order RELATIVE to other customers
WITH scored AS (
    SELECT *,
           NTILE(4) OVER (ORDER BY total_gmv) AS gmv_quartile,
           NTILE(4) OVER (ORDER BY contribution_per_order) AS contribution_quartile
    FROM vw_customer_summary
    WHERE delivered_orders > 0
)
SELECT customer_id, acquisition_channel, delivered_orders,
       ROUND(total_gmv, 0) AS total_gmv,
       ROUND(contribution_per_order, 2) AS contribution_per_order,
       ROUND(total_contribution, 0) AS total_contribution,
       promo_usage_rate
FROM scored
WHERE gmv_quartile = 4              -- top 25% by revenue
  AND contribution_quartile = 1     -- but bottom 25% by per-order contribution
ORDER BY total_gmv DESC
LIMIT 15;

-- RFM-style segmentation using NTILE window functions
WITH rfm AS (
    SELECT
        customer_id,
        NTILE(4) OVER (ORDER BY recency_days ASC) AS recency_score,      -- 1 = most recent
        NTILE(4) OVER (ORDER BY delivered_orders DESC) AS frequency_score, -- 1 = most frequent
        NTILE(4) OVER (ORDER BY total_contribution DESC) AS monetary_score -- 1 = most valuable
    FROM vw_customer_summary
    WHERE delivered_orders > 0
),
segmented AS (
    SELECT *,
        CASE
            WHEN recency_score = 1 AND frequency_score = 1 AND monetary_score = 1 THEN 'Champions'
            WHEN frequency_score <= 2 AND monetary_score <= 2 THEN 'Loyal Customers'
            WHEN recency_score >= 3 AND frequency_score <= 2 THEN 'At Risk'
            WHEN recency_score >= 3 AND frequency_score >= 3 THEN 'Lost / Dormant'
            ELSE 'Developing'
        END AS segment
    FROM rfm
)
SELECT segment, COUNT(*) AS num_customers,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_customers
FROM segmented
GROUP BY segment
ORDER BY num_customers DESC;
