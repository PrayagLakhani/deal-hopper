-- Row count and average items per order
SELECT
    (SELECT COUNT(*) FROM fact_order_item) AS total_items,
    (SELECT COUNT(*) FROM fact_order) AS total_orders,
    ROUND((SELECT COUNT(*) FROM fact_order_item)::NUMERIC /
          (SELECT COUNT(*) FROM fact_order), 2) AS avg_items_per_order;

-- Unit economics sanity check — cost ratio by product category.
-- Expect Beverages lowest, Biryani & Rice highest (same pattern as dim_product).
SELECT p.category,
       ROUND(AVG(oi.item_price), 2) AS avg_unit_price,
       ROUND(AVG(oi.item_ingredient_cost / oi.item_price), 2) AS avg_unit_cost_ratio
FROM fact_order_item oi
JOIN dim_product p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY avg_unit_cost_ratio;

-- Total discount allocated, and how it breaks down
SELECT
    ROUND(SUM(item_discount_allocated), 0) AS total_discount_allocated,
    ROUND(SUM(item_price * quantity), 0) AS total_gross_item_value,
    ROUND(100.0 * SUM(item_discount_allocated) / SUM(item_price * quantity), 2) AS overall_discount_pct
FROM fact_order_item;

-- Integrity check — unit ingredient_cost should never exceed unit item_price
SELECT order_item_id, item_price, item_ingredient_cost
FROM fact_order_item
WHERE item_ingredient_cost > item_price;
-- Expected: 0 rows

-- Integrity check — discount allocated to an item should never exceed that item's own value
SELECT order_item_id, item_price, quantity, item_discount_allocated
FROM fact_order_item
WHERE item_discount_allocated > (item_price * quantity);
-- Expected: 0 rows

-- Integrity check — Free Delivery promo orders should have zero item-level discount
SELECT oi.order_item_id
FROM fact_order_item oi
JOIN fact_order fo ON oi.order_id = fo.order_id
JOIN dim_promotion p ON fo.promotion_id = p.promotion_id
WHERE p.promotion_type = 'Free Delivery' AND oi.item_discount_allocated > 0;
-- Expected: 0 rows
