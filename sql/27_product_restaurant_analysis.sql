-- Highest-margin products
SELECT product_name, category, cuisine_type, units_sold, gross_value, restaurant_margin_pct
FROM vw_product_summary
WHERE units_sold >= 20
ORDER BY restaurant_margin_pct DESC
LIMIT 15;

-- High-sales but LOW-margin products 
WITH scored AS (
    SELECT *,
           NTILE(4) OVER (ORDER BY units_sold) AS volume_quartile,
           NTILE(4) OVER (ORDER BY restaurant_margin_pct) AS margin_quartile
    FROM vw_product_summary
)
SELECT product_name, category, units_sold, gross_value, restaurant_margin_pct, total_discount_allocated
FROM scored
WHERE volume_quartile = 4   -- top 25% by sales volume
  AND margin_quartile <= 2  -- bottom 50% by margin
ORDER BY units_sold DESC
LIMIT 15;

-- Category-level margin, on ACTUAL realized sales (not just listed menu prices)
SELECT category,
       COUNT(DISTINCT product_id) AS num_products,
       SUM(units_sold) AS total_units_sold,
       ROUND(SUM(gross_value), 0) AS total_gross_value,
       ROUND(AVG(restaurant_margin_pct), 2) AS avg_margin_pct,
       ROUND(100.0 * SUM(total_discount_allocated) / NULLIF(SUM(restaurant_gross_margin), 0), 1)
           AS discount_as_pct_of_margin
FROM vw_product_summary
GROUP BY category
ORDER BY avg_margin_pct DESC;

-- Top restaurants by total platform contribution
SELECT restaurant_name, cuisine_type, restaurant_type, city_name, city_tier,
       delivered_orders, ROUND(total_gmv, 0) AS total_gmv,
       ROUND(total_contribution, 0) AS total_contribution,
       promo_usage_rate
FROM vw_restaurant_summary
WHERE delivered_orders > 0
ORDER BY total_contribution DESC
LIMIT 15;

-- Restaurants MOST dependent on promotions
SELECT restaurant_name, cuisine_type, restaurant_type, delivered_orders,
       promo_usage_rate, contribution_per_order, ROUND(total_contribution, 0) AS total_contribution
FROM vw_restaurant_summary
WHERE delivered_orders >= 20
ORDER BY promo_usage_rate DESC
LIMIT 15;

-- High volume but POOR unit economics restaurants
WITH scored AS (
    SELECT *,
           NTILE(4) OVER (ORDER BY delivered_orders) AS volume_quartile,
           NTILE(4) OVER (ORDER BY contribution_per_order) AS contribution_quartile
    FROM vw_restaurant_summary
    WHERE delivered_orders > 0
)
SELECT restaurant_name, cuisine_type, restaurant_type, delivered_orders,
       contribution_per_order, promo_usage_rate, ROUND(total_contribution, 0) AS total_contribution
FROM scored
WHERE volume_quartile = 4    -- top 25% by order volume
  AND contribution_quartile = 1  -- bottom 25% by per-order contribution
ORDER BY delivered_orders DESC
LIMIT 15;
