CREATE OR REPLACE VIEW vw_product_summary AS
SELECT
    p.product_id, p.product_name, p.category, p.restaurant_id, p.is_veg, p.is_combo,
    r.cuisine_type, r.restaurant_type,
    SUM(oi.quantity) AS units_sold,
    ROUND(SUM(oi.item_price * oi.quantity), 2) AS gross_value,
    ROUND(SUM(oi.item_ingredient_cost * oi.quantity), 2) AS total_ingredient_cost,
    ROUND(SUM(oi.packaging_cost), 2) AS total_packaging_cost,
    ROUND(SUM(oi.item_discount_allocated), 2) AS total_discount_allocated,
    ROUND(SUM(oi.item_price * oi.quantity - oi.item_ingredient_cost * oi.quantity - oi.packaging_cost), 2)
        AS restaurant_gross_margin,
    ROUND(100.0 * SUM(oi.item_price * oi.quantity - oi.item_ingredient_cost * oi.quantity - oi.packaging_cost)
          / NULLIF(SUM(oi.item_price * oi.quantity), 0), 2) AS restaurant_margin_pct
FROM dim_product p
JOIN dim_restaurant r ON p.restaurant_id = r.restaurant_id
JOIN fact_order_item oi ON p.product_id = oi.product_id
JOIN fact_order o ON oi.order_id = o.order_id AND o.order_status = 'Delivered'
GROUP BY p.product_id, p.product_name, p.category, p.restaurant_id, p.is_veg, p.is_combo,
         r.cuisine_type, r.restaurant_type;
