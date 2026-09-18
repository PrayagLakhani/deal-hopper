-- KEY BUSINESS LOGIC:
--  Platform revenue = restaurant commission (on GROSS price) + delivery fee + platform fee
--  Platform costs   = discount the PLATFORM absorbs (per funded_by split) + delivery cost + payment fee

CREATE OR REPLACE VIEW vw_order_economics AS
WITH item_agg AS (
    SELECT
        oi.order_id,
        SUM(oi.item_price * oi.quantity) AS gross_item_value,
        SUM(oi.item_discount_allocated) AS total_discount
    FROM fact_order_item oi
    GROUP BY oi.order_id
)
SELECT
    o.order_id,
    o.customer_id,
    o.restaurant_id,
    o.date_id,
    o.promotion_id,
    o.order_status,
    o.payment_method,
    o.order_channel,
    ia.gross_item_value,
    ia.total_discount,
    r.commission_rate,
    ROUND(ia.gross_item_value * r.commission_rate, 2) AS restaurant_commission_revenue,
    COALESCE(p.platform_funding_share_pct, 100) AS platform_funding_share_pct,
    ROUND(ia.total_discount * COALESCE(p.platform_funding_share_pct, 100) / 100.0, 2) AS platform_borne_discount,
    o.customer_delivery_fee,
    o.platform_fee_charged,
    o.delivery_cost,
    o.payment_processing_fee,
    o.refund_amount,
    CASE
        WHEN o.order_status = 'Cancelled' THEN 0
        WHEN o.order_status = 'Refunded' THEN
            ROUND(-1 * (o.delivery_cost + o.payment_processing_fee), 2)
        ELSE
            ROUND(
                (ia.gross_item_value * r.commission_rate)
                + o.customer_delivery_fee
                + o.platform_fee_charged
                - (ia.total_discount * COALESCE(p.platform_funding_share_pct, 100) / 100.0)
                - o.delivery_cost
                - o.payment_processing_fee
            , 2)
    END AS contribution_margin
FROM fact_order o
JOIN item_agg ia ON o.order_id = ia.order_id
JOIN dim_restaurant r ON o.restaurant_id = r.restaurant_id
LEFT JOIN dim_promotion p ON o.promotion_id = p.promotion_id;
