-- Row count check — should be exactly 12
SELECT COUNT(*) AS total_cities FROM dim_city;

-- See all cities
SELECT * FROM dim_city ORDER BY city_tier, city_name;

-- Cities per region — each region should have 2-3 cities
SELECT region, COUNT(*) AS num_cities, STRING_AGG(city_name, ', ') AS cities
FROM dim_city
GROUP BY region
ORDER BY region;

-- Tier-level sanity check — market size and launch maturity should both
--    decrease as we go from Tier 1 -> Tier 3
SELECT
    city_tier,
    COUNT(*) AS num_cities,
    ROUND(AVG(estimated_market_size), 0) AS avg_market_size,
    MIN(platform_launch_date) AS earliest_launch,
    MAX(platform_launch_date) AS latest_launch
FROM dim_city
GROUP BY city_tier
ORDER BY city_tier;
