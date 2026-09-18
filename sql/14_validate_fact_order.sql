-- Row count — should be ~191,700
SELECT COUNT(*) AS total_orders FROM fact_order;

-- Order status mix
SELECT order_status, COUNT(*) AS orders,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM fact_order
GROUP BY order_status
ORDER BY orders DESC;

-- Promotion usage overall
SELECT
    ROUND(100.0 * COUNT(promotion_id) / COUNT(*), 1) AS pct_orders_with_promo
FROM fact_order;

-- KEY BUSINESS LOGIC CHECK: promotion usage rate by acquisition channel.
-- Expect "Promotional Signup Offer" customers to use promos far more than "Organic".
SELECT c.acquisition_channel,
       COUNT(*) AS total_orders,
       ROUND(100.0 * COUNT(o.promotion_id) / COUNT(*), 1) AS pct_with_promo
FROM fact_order o
JOIN dim_customer c ON o.customer_id = c.customer_id
GROUP BY c.acquisition_channel
ORDER BY pct_with_promo DESC;

-- KEY BUSINESS LOGIC CHECK: cancellation rate by payment method.
-- Expect COD noticeably higher than others.
SELECT payment_method,
       COUNT(*) AS total_orders,
       ROUND(100.0 * SUM(CASE WHEN order_status = 'Cancelled' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_cancelled
FROM fact_order
GROUP BY payment_method
ORDER BY pct_cancelled DESC;

-- Integrity check — every order's date must fall inside our 18-month window
SELECT COUNT(*) AS out_of_window_orders
FROM fact_order
WHERE date_id < DATE '2024-03-01' OR date_id > DATE '2025-08-31';
-- Expected: 0

-- Integrity check — Free Delivery promo orders should have customer_delivery_fee = 0
SELECT o.order_id, p.promotion_type, o.customer_delivery_fee
FROM fact_order o
JOIN dim_promotion p ON o.promotion_id = p.promotion_id
WHERE p.promotion_type = 'Free Delivery' AND o.customer_delivery_fee <> 0;
-- Expected: 0 rows
