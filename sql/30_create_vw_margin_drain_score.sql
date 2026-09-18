CREATE OR REPLACE VIEW vw_promotion_margin_drain_score AS
WITH promo_orders AS (
    SELECT o.promotion_id, o.order_id, o.order_status, o.customer_id
    FROM fact_order o
    WHERE o.promotion_id IS NOT NULL
),
promo_financials AS (
    SELECT
        p.promotion_id, p.promotion_name, p.promotion_type, p.target_segment,
        p.funded_by, p.planned_budget,
        COUNT(oe.order_id) FILTER (WHERE oe.order_status = 'Delivered') AS delivered_orders,
        SUM(oe.gross_item_value) FILTER (WHERE oe.order_status = 'Delivered') AS gmv,
        SUM(oe.contribution_margin) AS total_contribution,
        SUM(oe.platform_borne_discount) FILTER (WHERE oe.order_status = 'Delivered') AS actual_platform_discount,
        ROUND(100.0 * SUM(oe.contribution_margin) /
              NULLIF(SUM(oe.gross_item_value) FILTER (WHERE oe.order_status = 'Delivered'), 0), 2)
              AS contribution_margin_pct
    FROM dim_promotion p
    LEFT JOIN vw_order_economics oe ON p.promotion_id = oe.promotion_id
    GROUP BY p.promotion_id, p.promotion_name, p.promotion_type, p.target_segment, p.funded_by, p.planned_budget
),
promo_ops AS (
    SELECT promotion_id,
           COUNT(*) AS total_orders_attempted,
           SUM(CASE WHEN order_status IN ('Refunded', 'Cancelled') THEN 1 ELSE 0 END) AS refund_cancel_count
    FROM promo_orders
    GROUP BY promotion_id
),
promo_customer_dependency AS (
    SELECT po.promotion_id, AVG(cs.promo_usage_rate) AS avg_customer_dependency
    FROM (SELECT DISTINCT promotion_id, customer_id FROM promo_orders) po
    JOIN vw_customer_summary cs ON po.customer_id = cs.customer_id
    GROUP BY po.promotion_id
),
combined AS (
    SELECT
        pf.*,
        ROUND(pf.total_contribution / NULLIF(pf.actual_platform_discount, 0), 3) AS discount_efficiency,
        ROUND(100.0 * pf.actual_platform_discount / NULLIF(pf.planned_budget, 0), 1) AS pct_of_budget_used,
        ROUND(100.0 * po.refund_cancel_count / NULLIF(po.total_orders_attempted, 0), 2) AS refund_cancel_rate_pct,
        ROUND(pcd.avg_customer_dependency, 3) AS avg_customer_dependency
    FROM promo_financials pf
    LEFT JOIN promo_ops po ON pf.promotion_id = po.promotion_id
    LEFT JOIN promo_customer_dependency pcd ON pf.promotion_id = pcd.promotion_id
),
ranking_input AS (
    SELECT *,
        CASE
            WHEN actual_platform_discount IS NULL OR actual_platform_discount = 0
                THEN CASE WHEN total_contribution >= 0 THEN 999999 ELSE -999999 END
            ELSE discount_efficiency
        END AS discount_efficiency_for_ranking
    FROM combined
),
scored AS (
    SELECT *,
        PERCENT_RANK() OVER (ORDER BY contribution_margin_pct DESC)               AS pr_margin,      -- worst margin = lowest value = last = ~1
        PERCENT_RANK() OVER (ORDER BY discount_efficiency_for_ranking DESC)       AS pr_efficiency,   -- worst efficiency = lowest value = last = ~1
        PERCENT_RANK() OVER (ORDER BY pct_of_budget_used ASC)                     AS pr_budget,       -- worst = highest overspend = last = ~1
        PERCENT_RANK() OVER (ORDER BY refund_cancel_rate_pct ASC)                 AS pr_refund,       -- worst = highest refund rate = last = ~1
        PERCENT_RANK() OVER (ORDER BY avg_customer_dependency ASC)                AS pr_dependency    -- worst = highest dependency = last = ~1
    FROM ranking_input
)
SELECT *,
    ROUND((100 * (
        0.40 * pr_margin
      + 0.25 * pr_efficiency
      + 0.15 * pr_budget
      + 0.10 * pr_refund
      + 0.10 * pr_dependency
    ))::NUMERIC, 1) AS margin_drain_score
FROM scored;
