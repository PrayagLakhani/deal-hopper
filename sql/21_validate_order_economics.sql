-- Row count should match fact_order exactly
SELECT
    (SELECT COUNT(*) FROM fact_order) AS fact_order_rows,
    (SELECT COUNT(*) FROM vw_order_economics) AS view_rows;

-- Overall platform financial summary
SELECT
    order_status,
    COUNT(*) AS orders,
    ROUND(SUM(gross_item_value), 0) AS total_gmv,
    ROUND(SUM(restaurant_commission_revenue), 0) AS total_commission_revenue,
    ROUND(SUM(platform_borne_discount), 0) AS total_platform_discount,
    ROUND(SUM(contribution_margin), 0) AS total_contribution
FROM vw_order_economics
GROUP BY order_status
ORDER BY order_status;

-- Overall contribution margin % (Delivered orders only, since that's where GMV is real)
SELECT
    ROUND(SUM(CASE WHEN order_status = 'Delivered' THEN gross_item_value ELSE 0 END), 0) AS delivered_gmv,
    ROUND(SUM(contribution_margin), 0) AS total_contribution_all_statuses,
    ROUND(100.0 * SUM(contribution_margin) /
          NULLIF(SUM(CASE WHEN order_status = 'Delivered' THEN gross_item_value ELSE 0 END), 0), 2)
          AS contribution_margin_pct_of_delivered_gmv
FROM vw_order_economics;

-- Sanity check — what % of orders have negative contribution margin, and why?
SELECT
    order_status,
    COUNT(*) AS orders,
    SUM(CASE WHEN contribution_margin < 0 THEN 1 ELSE 0 END) AS negative_contribution_orders,
    ROUND(100.0 * SUM(CASE WHEN contribution_margin < 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_negative
FROM vw_order_economics
GROUP BY order_status;

-- Spot check a few individual orders to eyeball the math makes sense
SELECT order_id, order_status, gross_item_value, total_discount, restaurant_commission_revenue,
       platform_borne_discount, customer_delivery_fee, platform_fee_charged,
       delivery_cost, payment_processing_fee, contribution_margin
FROM vw_order_economics
ORDER BY order_id
LIMIT 10;
