-- Answers: which promotions drive profitable growth vs. destroy margin?

-- Promotion-level P&L, ranked worst to best by total contribution
SELECT
    p.promotion_id,
    p.promotion_name,
    p.promotion_type,
    p.target_segment,
    p.funded_by,
    COUNT(oe.order_id) AS orders_using_promo,
    ROUND(SUM(oe.gross_item_value), 0) AS gmv,
    ROUND(SUM(oe.platform_borne_discount), 0) AS actual_platform_discount,
    ROUND(SUM(oe.contribution_margin), 0) AS total_contribution,
    ROUND(100.0 * SUM(oe.contribution_margin) / NULLIF(SUM(oe.gross_item_value), 0), 2) AS contribution_margin_pct
FROM dim_promotion p
LEFT JOIN vw_order_economics oe
    ON p.promotion_id = oe.promotion_id AND oe.order_status = 'Delivered'
GROUP BY p.promotion_id, p.promotion_name, p.promotion_type, p.target_segment, p.funded_by
ORDER BY total_contribution ASC NULLS FIRST
LIMIT 15;

-- BEST 15 promotions by total contribution
SELECT
    p.promotion_id,
    p.promotion_name,
    p.promotion_type,
    p.target_segment,
    p.funded_by,
    COUNT(oe.order_id) AS orders_using_promo,
    ROUND(SUM(oe.gross_item_value), 0) AS gmv,
    ROUND(SUM(oe.platform_borne_discount), 0) AS actual_platform_discount,
    ROUND(SUM(oe.contribution_margin), 0) AS total_contribution,
    ROUND(100.0 * SUM(oe.contribution_margin) / NULLIF(SUM(oe.gross_item_value), 0), 2) AS contribution_margin_pct
FROM dim_promotion p
LEFT JOIN vw_order_economics oe
    ON p.promotion_id = oe.promotion_id AND oe.order_status = 'Delivered'
GROUP BY p.promotion_id, p.promotion_name, p.promotion_type, p.target_segment, p.funded_by
ORDER BY total_contribution DESC NULLS LAST
LIMIT 15;

-- Overall — how many promotions are net-positive vs net-negative?
SELECT
    CASE WHEN total_contribution >= 0 THEN 'Net Positive' ELSE 'Net Negative' END AS bucket,
    COUNT(*) AS num_promotions,
    ROUND(SUM(total_contribution), 0) AS combined_contribution
FROM (
    SELECT p.promotion_id,
           SUM(oe.contribution_margin) AS total_contribution
    FROM dim_promotion p
    LEFT JOIN vw_order_economics oe
        ON p.promotion_id = oe.promotion_id AND oe.order_status = 'Delivered'
    GROUP BY p.promotion_id
) t
GROUP BY bucket;

-- Budget adherence — planned vs. actual platform-borne discount spend
SELECT
    p.promotion_id,
    p.promotion_name,
    p.planned_budget,
    ROUND(COALESCE(SUM(oe.platform_borne_discount), 0), 0) AS actual_spend,
    ROUND(COALESCE(SUM(oe.platform_borne_discount), 0) - p.planned_budget, 0) AS variance,
    ROUND(100.0 * COALESCE(SUM(oe.platform_borne_discount), 0) / NULLIF(p.planned_budget, 0), 1) AS pct_of_budget_used
FROM dim_promotion p
LEFT JOIN vw_order_economics oe
    ON p.promotion_id = oe.promotion_id AND oe.order_status = 'Delivered'
GROUP BY p.promotion_id, p.promotion_name, p.planned_budget
ORDER BY pct_of_budget_used DESC NULLS LAST
LIMIT 15;

-- Which promotion MECHANIC performs best on average?
SELECT
    p.promotion_type,
    COUNT(DISTINCT p.promotion_id) AS num_promotions,
    COUNT(oe.order_id) AS total_orders,
    ROUND(SUM(oe.gross_item_value), 0) AS total_gmv,
    ROUND(SUM(oe.contribution_margin), 0) AS total_contribution,
    ROUND(100.0 * SUM(oe.contribution_margin) / NULLIF(SUM(oe.gross_item_value), 0), 2) AS contribution_margin_pct
FROM dim_promotion p
LEFT JOIN vw_order_economics oe
    ON p.promotion_id = oe.promotion_id AND oe.order_status = 'Delivered'
GROUP BY p.promotion_type
ORDER BY contribution_margin_pct DESC;

-- Optimal discount depth for "Percentage Off" promotions
SELECT
    CASE
        WHEN p.discount_value <= 15 THEN '10-15%'
        WHEN p.discount_value <= 25 THEN '20-25%'
        ELSE '30-40%'
    END AS discount_band,
    COUNT(DISTINCT p.promotion_id) AS num_promotions,
    COUNT(oe.order_id) AS total_orders,
    ROUND(SUM(oe.gross_item_value), 0) AS total_gmv,
    ROUND(SUM(oe.contribution_margin), 0) AS total_contribution,
    ROUND(100.0 * SUM(oe.contribution_margin) / NULLIF(SUM(oe.gross_item_value), 0), 2) AS contribution_margin_pct
FROM dim_promotion p
LEFT JOIN vw_order_economics oe
    ON p.promotion_id = oe.promotion_id AND oe.order_status = 'Delivered'
WHERE p.promotion_type = 'Percentage Off'
GROUP BY discount_band
ORDER BY discount_band;

-- Promotions that were never used (0 orders)
SELECT p.promotion_id, p.promotion_name, p.promotion_type, p.target_segment,
       p.start_date, p.end_date, p.planned_budget
FROM dim_promotion p
LEFT JOIN fact_order o ON p.promotion_id = o.promotion_id
WHERE o.order_id IS NULL
ORDER BY p.target_segment, p.promotion_id;
