-- Row count check — should be ~349
SELECT COUNT(*) AS total_restaurants FROM dim_restaurant;

-- Restaurants per city
SELECT c.city_name, c.city_tier, COUNT(*) AS num_restaurants
FROM dim_restaurant r
JOIN dim_city c ON r.city_id = c.city_id
GROUP BY c.city_name, c.city_tier
ORDER BY c.city_tier, num_restaurants DESC;

-- Restaurant type mix
SELECT restaurant_type, COUNT(*) AS restaurants,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM dim_restaurant
GROUP BY restaurant_type
ORDER BY restaurants DESC;

-- Commission rate by restaurant type — this is the key business logic check.
-- Expect: Chain Outlet lowest, Cloud Kitchen highest, Standalone in between.
SELECT restaurant_type,
       ROUND(AVG(commission_rate), 3) AS avg_commission,
       ROUND(MIN(commission_rate), 3) AS min_commission,
       ROUND(MAX(commission_rate), 3) AS max_commission
FROM dim_restaurant
GROUP BY restaurant_type
ORDER BY avg_commission;

-- Rating distribution
SELECT
    ROUND(AVG(avg_rating), 2) AS mean_rating,
    MIN(avg_rating) AS min_rating,
    MAX(avg_rating) AS max_rating
FROM dim_restaurant;

-- Integrity check — no restaurant should onboard before its city launched
SELECT r.restaurant_id, r.onboarding_date, c.platform_launch_date
FROM dim_restaurant r
JOIN dim_city c ON r.city_id = c.city_id
WHERE r.onboarding_date < c.platform_launch_date;
-- Expected: 0 rows
