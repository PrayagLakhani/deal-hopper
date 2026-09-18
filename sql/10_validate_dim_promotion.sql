-- Row count — should be 150
SELECT COUNT(*) AS total_promotions FROM dim_promotion;

-- Promotion type mix
SELECT promotion_type, COUNT(*) AS promotions,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM dim_promotion
GROUP BY promotion_type
ORDER BY promotions DESC;

-- Funding split
SELECT funded_by, COUNT(*) AS promotions,
       ROUND(AVG(platform_funding_share_pct), 1) AS avg_platform_share
FROM dim_promotion
GROUP BY funded_by;

-- Duration vs budget — budget should scale up with longer campaigns
SELECT
    (end_date - start_date) AS duration_days,
    planned_budget
FROM dim_promotion
ORDER BY duration_days;

-- Integrity check — no promotion should start or end outside the data window
SELECT promotion_id, start_date, end_date
FROM dim_promotion
WHERE start_date < DATE '2024-03-01' OR end_date > DATE '2025-08-31';
-- Expected: 0 rows
