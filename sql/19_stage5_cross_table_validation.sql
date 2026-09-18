-- Row count summary across all tables
SELECT 'dim_city' AS table_name, COUNT(*) AS rows FROM dim_city
UNION ALL SELECT 'dim_customer', COUNT(*) FROM dim_customer
UNION ALL SELECT 'dim_restaurant', COUNT(*) FROM dim_restaurant
UNION ALL SELECT 'dim_product', COUNT(*) FROM dim_product
UNION ALL SELECT 'dim_product_price_history', COUNT(*) FROM dim_product_price_history
UNION ALL SELECT 'dim_promotion', COUNT(*) FROM dim_promotion
UNION ALL SELECT 'dim_date', COUNT(*) FROM dim_date
UNION ALL SELECT 'fact_order', COUNT(*) FROM fact_order
UNION ALL SELECT 'fact_order_item', COUNT(*) FROM fact_order_item;

-- CRITICAL CHECK: any order dated before its own restaurant onboarded?
SELECT o.order_id, o.date_id, r.onboarding_date, r.restaurant_id
FROM fact_order o
JOIN dim_restaurant r ON o.restaurant_id = r.restaurant_id
WHERE o.date_id < r.onboarding_date;
-- Expected: 0 rows

-- Promotion window compliance — order date should fall within the promo's active dates
SELECT o.order_id, o.date_id, p.promotion_id, p.start_date, p.end_date
FROM fact_order o
JOIN dim_promotion p ON o.promotion_id = p.promotion_id
WHERE o.date_id < p.start_date OR o.date_id > p.end_date;
-- Expected: 0 rows

-- Minimum order value compliance — if a discount was allocated, the order's
-- gross value should have met the promotion's min_order_value
SELECT o.order_id, p.min_order_value, SUM(oi.item_price * oi.quantity) AS order_gross_value,
       SUM(oi.item_discount_allocated) AS total_discount
FROM fact_order o
JOIN dim_promotion p ON o.promotion_id = p.promotion_id
JOIN fact_order_item oi ON o.order_id = oi.order_id
GROUP BY o.order_id, p.min_order_value
HAVING SUM(oi.item_discount_allocated) > 0
   AND SUM(oi.item_price * oi.quantity) < p.min_order_value;
-- Expected: 0 rows

-- Structural completeness — every order should have at least one line item
SELECT o.order_id
FROM fact_order o
LEFT JOIN fact_order_item oi ON o.order_id = oi.order_id
WHERE oi.order_item_id IS NULL;
-- Expected: 0 rows

-- High-level business health check
SELECT
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(oi.item_price * oi.quantity)::NUMERIC / COUNT(DISTINCT o.order_id), 2) AS avg_order_value,
    ROUND(SUM(oi.item_discount_allocated)::NUMERIC / SUM(oi.item_price * oi.quantity) * 100, 2) AS overall_discount_pct,
    ROUND(100.0 * SUM(CASE WHEN o.order_status = 'Cancelled' THEN 1 ELSE 0 END) / COUNT(*), 2) AS cancellation_pct,
    ROUND(100.0 * SUM(CASE WHEN o.order_status = 'Refunded' THEN 1 ELSE 0 END) / COUNT(*), 2) AS refund_pct
FROM fact_order o
JOIN fact_order_item oi ON o.order_id = oi.order_id;

-- Informational: what share of customers never placed an order?
SELECT
    (SELECT COUNT(*) FROM dim_customer) AS total_customers,
    (SELECT COUNT(DISTINCT customer_id) FROM fact_order) AS customers_with_orders,
    ROUND(100.0 * (1 - (SELECT COUNT(DISTINCT customer_id) FROM fact_order)::NUMERIC /
          (SELECT COUNT(*) FROM dim_customer)), 1) AS pct_never_ordered;

-- Informational: what share of restaurants never received an order?
SELECT
    (SELECT COUNT(*) FROM dim_restaurant) AS total_restaurants,
    (SELECT COUNT(DISTINCT restaurant_id) FROM fact_order) AS restaurants_with_orders,
    ROUND(100.0 * (1 - (SELECT COUNT(DISTINCT restaurant_id) FROM fact_order)::NUMERIC /
          (SELECT COUNT(*) FROM dim_restaurant)), 1) AS pct_never_ordered;
