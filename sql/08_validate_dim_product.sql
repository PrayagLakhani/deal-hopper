-- Row counts
SELECT (SELECT COUNT(*) FROM dim_product) AS total_products,
       (SELECT COUNT(*) FROM dim_product_price_history) AS total_price_rows;

-- Category mix, overall
SELECT category, COUNT(*) AS products,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM dim_product
GROUP BY category
ORDER BY products DESC;

-- Veg/Non-Veg/Egg mix
SELECT is_veg, COUNT(*) AS products,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM dim_product
GROUP BY is_veg
ORDER BY products DESC;

-- Price & cost ratio by category (current prices only) — key business logic check.
-- Expect Beverages to have the LOWEST cost ratio, Biryani & Rice the HIGHEST.
SELECT p.category,
       ROUND(AVG(h.selling_price), 2) AS avg_price,
       ROUND(AVG(h.ingredient_cost / h.selling_price), 2) AS avg_cost_ratio
FROM dim_product p
JOIN dim_product_price_history h ON p.product_id = h.product_id AND h.is_current = TRUE
GROUP BY p.category
ORDER BY avg_cost_ratio;

-- Integrity check — every product should have EXACTLY ONE current price row
SELECT product_id, COUNT(*) AS current_price_rows
FROM dim_product_price_history
WHERE is_current = TRUE
GROUP BY product_id
HAVING COUNT(*) <> 1;
-- Expected: 0 rows

-- How many products have price history (i.e., had a revision)?
SELECT COUNT(DISTINCT product_id) AS products_with_revision
FROM dim_product_price_history
WHERE is_current = FALSE;
