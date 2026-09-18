CREATE OR REPLACE VIEW vw_customer_summary AS
WITH agg AS (
    SELECT
        c.customer_id,
        c.acquisition_channel,
        c.subscription_status,
        c.signup_date,
        COUNT(oe.order_id) FILTER (WHERE oe.order_status = 'Delivered') AS delivered_orders,
        SUM(oe.gross_item_value) FILTER (WHERE oe.order_status = 'Delivered') AS total_gmv,
        SUM(oe.contribution_margin) AS total_contribution,
        SUM(CASE WHEN oe.promotion_id IS NOT NULL AND oe.order_status = 'Delivered'
                 THEN 1 ELSE 0 END) AS promo_orders,
        MAX(oe.date_id) FILTER (WHERE oe.order_status = 'Delivered') AS last_order_date,
        MIN(oe.date_id) FILTER (WHERE oe.order_status = 'Delivered') AS first_order_date
    FROM dim_customer c
    LEFT JOIN vw_order_economics oe ON c.customer_id = oe.customer_id
    GROUP BY c.customer_id, c.acquisition_channel, c.subscription_status, c.signup_date
)
SELECT
    *,
    ROUND(COALESCE(promo_orders, 0)::NUMERIC / NULLIF(delivered_orders, 0), 3) AS promo_usage_rate,
    ROUND(COALESCE(total_gmv, 0)::NUMERIC / NULLIF(delivered_orders, 0), 2) AS avg_order_value,
    ROUND(COALESCE(total_contribution, 0)::NUMERIC / NULLIF(delivered_orders, 0), 2) AS contribution_per_order,
    (DATE '2025-08-31' - last_order_date) AS recency_days
FROM agg;
