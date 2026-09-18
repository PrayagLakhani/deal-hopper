-- Row count — should be 549 (18-month window)
SELECT COUNT(*) AS total_days FROM dim_date;

-- Season distribution
SELECT season, COUNT(*) AS days
FROM dim_date
GROUP BY season
ORDER BY days DESC;

-- Weekend proportion — should be roughly 2/7 (~28.6%) of all days
SELECT is_weekend, COUNT(*) AS days,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM dim_date
GROUP BY is_weekend;

-- Festive days — list them all
SELECT date_id, day_of_week, season
FROM dim_date
WHERE is_festive_period = TRUE
ORDER BY date_id;

-- Integrity check — is_weekend should always match day_of_week
SELECT date_id, day_of_week, is_weekend
FROM dim_date
WHERE is_weekend <> (day_of_week IN ('Saturday', 'Sunday'));
-- Expected: 0 rows
