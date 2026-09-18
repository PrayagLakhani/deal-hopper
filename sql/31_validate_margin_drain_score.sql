-- Top 10 highest-drain promotions (worst offenders)
SELECT promotion_id, promotion_name, promotion_type, target_segment, funded_by,
       contribution_margin_pct, discount_efficiency, pct_of_budget_used,
       refund_cancel_rate_pct, avg_customer_dependency, margin_drain_score
FROM vw_promotion_margin_drain_score
ORDER BY margin_drain_score DESC
LIMIT 10;

-- Top 10 lowest-drain (best) promotions
SELECT promotion_id, promotion_name, promotion_type, target_segment, funded_by,
       contribution_margin_pct, discount_efficiency, pct_of_budget_used,
       refund_cancel_rate_pct, avg_customer_dependency, margin_drain_score
FROM vw_promotion_margin_drain_score
ORDER BY margin_drain_score ASC
LIMIT 10;

-- Sanity check — does the score correlate sensibly with contribution margin %?
SELECT
    CASE
        WHEN margin_drain_score >= 75 THEN 'Severe Drain (75-100)'
        WHEN margin_drain_score >= 50 THEN 'Moderate Drain (50-75)'
        WHEN margin_drain_score >= 25 THEN 'Low Drain (25-50)'
        ELSE 'Healthy (0-25)'
    END AS drain_tier,
    COUNT(*) AS num_promotions,
    ROUND(AVG(contribution_margin_pct), 2) AS avg_margin_pct,
    ROUND(AVG(total_contribution), 0) AS avg_total_contribution
FROM vw_promotion_margin_drain_score
GROUP BY drain_tier
ORDER BY MIN(margin_drain_score) DESC;

-- Score distribution by promotion type (should show BOGO skewing high-drain, Free Delivery skewing low-drain, matching Stage 6 findings)
SELECT promotion_type,
       ROUND(AVG(margin_drain_score), 1) AS avg_drain_score,
       COUNT(*) AS num_promotions
FROM vw_promotion_margin_drain_score
GROUP BY promotion_type
ORDER BY avg_drain_score DESC;
