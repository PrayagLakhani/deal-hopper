-- Full cohort retention table
WITH customer_cohort AS (
    SELECT customer_id, DATE_TRUNC('month', signup_date)::date AS cohort_month
    FROM dim_customer
    WHERE signup_date >= DATE '2024-03-01'
),
cohort_sizes AS (
    SELECT cohort_month, COUNT(*) AS cohort_size
    FROM customer_cohort
    GROUP BY cohort_month
),
customer_activity AS (
    SELECT DISTINCT o.customer_id, DATE_TRUNC('month', o.date_id)::date AS activity_month
    FROM fact_order o
    WHERE o.order_status = 'Delivered'
),
joined AS (
    SELECT cc.customer_id, cc.cohort_month, ca.activity_month,
           (EXTRACT(YEAR FROM ca.activity_month) - EXTRACT(YEAR FROM cc.cohort_month)) * 12
           + (EXTRACT(MONTH FROM ca.activity_month) - EXTRACT(MONTH FROM cc.cohort_month)) AS months_since_signup
    FROM customer_cohort cc
    JOIN customer_activity ca ON cc.customer_id = ca.customer_id
    WHERE ca.activity_month >= cc.cohort_month
),
retention AS (
    SELECT cohort_month, months_since_signup, COUNT(DISTINCT customer_id) AS active_customers
    FROM joined
    GROUP BY cohort_month, months_since_signup
)
SELECT r.cohort_month, cs.cohort_size, r.months_since_signup, r.active_customers,
       ROUND(100.0 * r.active_customers / cs.cohort_size, 1) AS retention_pct,
       ROUND(100.0 * r.active_customers / cs.cohort_size, 1) -
           LAG(ROUND(100.0 * r.active_customers / cs.cohort_size, 1)) OVER (
               PARTITION BY r.cohort_month ORDER BY r.months_since_signup
           ) AS pct_point_change_vs_prev_month
FROM retention r
JOIN cohort_sizes cs ON r.cohort_month = cs.cohort_month
ORDER BY r.cohort_month, r.months_since_signup;

-- Blended retention curve
WITH customer_cohort AS (
    SELECT customer_id, DATE_TRUNC('month', signup_date)::date AS cohort_month
    FROM dim_customer
    WHERE signup_date >= DATE '2024-03-01'
),
customer_activity AS (
    SELECT DISTINCT o.customer_id, DATE_TRUNC('month', o.date_id)::date AS activity_month
    FROM fact_order o
    WHERE o.order_status = 'Delivered'
),
joined AS (
    SELECT cc.customer_id, cc.cohort_month,
           (EXTRACT(YEAR FROM ca.activity_month) - EXTRACT(YEAR FROM cc.cohort_month)) * 12
           + (EXTRACT(MONTH FROM ca.activity_month) - EXTRACT(MONTH FROM cc.cohort_month)) AS months_since_signup
    FROM customer_cohort cc
    JOIN customer_activity ca ON cc.customer_id = ca.customer_id
    WHERE ca.activity_month >= cc.cohort_month
)
SELECT months_since_signup,
       COUNT(DISTINCT customer_id) AS active_customers,
       (SELECT COUNT(*) FROM customer_cohort) AS total_cohort_customers,
       ROUND(100.0 * COUNT(DISTINCT customer_id) / (SELECT COUNT(*) FROM customer_cohort), 1) AS blended_retention_pct
FROM joined
WHERE months_since_signup BETWEEN 0 AND 6  
GROUP BY months_since_signup
ORDER BY months_since_signup;

-- Pivoted cohort grid, Month 0 - Month 5
WITH customer_cohort AS (
    SELECT customer_id, DATE_TRUNC('month', signup_date)::date AS cohort_month
    FROM dim_customer
    WHERE signup_date >= DATE '2024-03-01'
),
cohort_sizes AS (
    SELECT cohort_month, COUNT(*) AS cohort_size
    FROM customer_cohort
    GROUP BY cohort_month
),
customer_activity AS (
    SELECT DISTINCT o.customer_id, DATE_TRUNC('month', o.date_id)::date AS activity_month
    FROM fact_order o
    WHERE o.order_status = 'Delivered'
),
joined AS (
    SELECT cc.customer_id, cc.cohort_month,
           (EXTRACT(YEAR FROM ca.activity_month) - EXTRACT(YEAR FROM cc.cohort_month)) * 12
           + (EXTRACT(MONTH FROM ca.activity_month) - EXTRACT(MONTH FROM cc.cohort_month)) AS months_since_signup
    FROM customer_cohort cc
    JOIN customer_activity ca ON cc.customer_id = ca.customer_id
    WHERE ca.activity_month >= cc.cohort_month
)
SELECT
    cs.cohort_month, cs.cohort_size,
    ROUND(100.0 * COUNT(DISTINCT j.customer_id) FILTER (WHERE j.months_since_signup = 0) / cs.cohort_size, 1) AS m0,
    ROUND(100.0 * COUNT(DISTINCT j.customer_id) FILTER (WHERE j.months_since_signup = 1) / cs.cohort_size, 1) AS m1,
    ROUND(100.0 * COUNT(DISTINCT j.customer_id) FILTER (WHERE j.months_since_signup = 2) / cs.cohort_size, 1) AS m2,
    ROUND(100.0 * COUNT(DISTINCT j.customer_id) FILTER (WHERE j.months_since_signup = 3) / cs.cohort_size, 1) AS m3,
    ROUND(100.0 * COUNT(DISTINCT j.customer_id) FILTER (WHERE j.months_since_signup = 4) / cs.cohort_size, 1) AS m4,
    ROUND(100.0 * COUNT(DISTINCT j.customer_id) FILTER (WHERE j.months_since_signup = 5) / cs.cohort_size, 1) AS m5
FROM cohort_sizes cs
JOIN joined j ON cs.cohort_month = j.cohort_month
GROUP BY cs.cohort_month, cs.cohort_size
ORDER BY cs.cohort_month;

-- Does discount-driven acquisition retain WORSE than organic?
WITH customer_cohort AS (
    SELECT customer_id, acquisition_channel, DATE_TRUNC('month', signup_date)::date AS cohort_month
    FROM dim_customer
    WHERE signup_date >= DATE '2024-03-01'
),
customer_activity AS (
    SELECT DISTINCT o.customer_id, DATE_TRUNC('month', o.date_id)::date AS activity_month
    FROM fact_order o
    WHERE o.order_status = 'Delivered'
),
joined AS (
    SELECT cc.customer_id, cc.acquisition_channel,
           (EXTRACT(YEAR FROM ca.activity_month) - EXTRACT(YEAR FROM cc.cohort_month)) * 12
           + (EXTRACT(MONTH FROM ca.activity_month) - EXTRACT(MONTH FROM cc.cohort_month)) AS months_since_signup
    FROM customer_cohort cc
    JOIN customer_activity ca ON cc.customer_id = ca.customer_id
    WHERE ca.activity_month >= cc.cohort_month
),
channel_totals AS (
    SELECT acquisition_channel, COUNT(*) AS total FROM customer_cohort GROUP BY acquisition_channel
)
SELECT j.acquisition_channel, j.months_since_signup,
       COUNT(DISTINCT j.customer_id) AS active_customers,
       ct.total AS cohort_total,
       ROUND(100.0 * COUNT(DISTINCT j.customer_id) / ct.total, 1) AS retention_pct
FROM joined j
JOIN channel_totals ct ON j.acquisition_channel = ct.acquisition_channel
WHERE j.months_since_signup BETWEEN 0 AND 4
GROUP BY j.acquisition_channel, j.months_since_signup, ct.total
ORDER BY j.acquisition_channel, j.months_since_signup;
