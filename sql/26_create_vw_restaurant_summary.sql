CREATE OR REPLACE VIEW vw_restaurant_summary AS
WITH agg AS (
    SELECT
        r.restaurant_id, r.restaurant_name, r.cuisine_type, r.restaurant_type,
        r.commission_rate, c.city_name, c.city_tier,
        COUNT(oe.order_id) FILTER (WHERE oe.order_status = 'Delivered') AS delivered_orders,
        SUM(oe.gross_item_value) FILTER (WHERE oe.order_status = 'Delivered') AS total_gmv,
        SUM(oe.contribution_margin) AS total_contribution,
        SUM(CASE WHEN oe.promotion_id IS NOT NULL AND oe.order_status = 'Delivered'
                 THEN 1 ELSE 0 END) AS promo_orders
    FROM dim_restaurant r
    JOIN dim_city c ON r.city_id = c.city_id
    LEFT JOIN vw_order_economics oe ON r.restaurant_id = oe.restaurant_id
    GROUP BY r.restaurant_id, r.restaurant_name, r.cuisine_type, r.restaurant_type,
             r.commission_rate, c.city_name, c.city_tier
)
SELECT *,
    ROUND(COALESCE(promo_orders, 0)::NUMERIC / NULLIF(delivered_orders, 0), 3) AS promo_usage_rate,
    ROUND(COALESCE(total_contribution, 0)::NUMERIC / NULLIF(delivered_orders, 0), 2) AS contribution_per_order
FROM agg;
