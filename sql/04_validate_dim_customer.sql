-- Row count check — should be ~17,800
SELECT COUNT(*) AS total_customers FROM dim_customer;

-- Customers per city
SELECT c.city_name, c.city_tier, COUNT(*) AS num_customers
FROM dim_customer cu
JOIN dim_city c ON cu.city_id = c.city_id
GROUP BY c.city_name, c.city_tier
ORDER BY c.city_tier, num_customers DESC;

-- Acquisition channel mix, overall
SELECT acquisition_channel, COUNT(*) AS customers,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM dim_customer
GROUP BY acquisition_channel
ORDER BY customers DESC;

-- Subscription status breakdown
SELECT subscription_status, COUNT(*) AS customers,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM dim_customer
GROUP BY subscription_status
ORDER BY customers DESC;

-- Integrity check — no customer should have signed up before their city launched
SELECT cu.customer_id, cu.signup_date, ci.platform_launch_date
FROM dim_customer cu
JOIN dim_city ci ON cu.city_id = ci.city_id
WHERE cu.signup_date < ci.platform_launch_date;
-- Expected: 0 rows

-- Integrity check — no subscription should start before signup
SELECT customer_id, signup_date, subscription_start_date
FROM dim_customer
WHERE subscription_start_date IS NOT NULL
  AND subscription_start_date < signup_date;
-- Expected: 0 rows
