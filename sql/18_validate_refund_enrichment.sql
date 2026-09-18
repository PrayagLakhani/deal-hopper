-- Every Refunded order should now have a non-null refund_amount;
-- every Delivered/Cancelled order should still be NULL.
SELECT order_status,
       COUNT(*) AS orders,
       COUNT(refund_amount) AS orders_with_refund_amount
FROM fact_order
GROUP BY order_status;

-- Spot-check a few refunded orders and their computed amounts
SELECT order_id, order_status, customer_delivery_fee, platform_fee_charged, refund_amount
FROM fact_order
WHERE order_status = 'Refunded'
ORDER BY order_id
LIMIT 10;

-- Sanity range check — refund amounts should be positive and in a believable range
SELECT
    ROUND(MIN(refund_amount), 2) AS min_refund,
    ROUND(AVG(refund_amount), 2) AS avg_refund,
    ROUND(MAX(refund_amount), 2) AS max_refund
FROM fact_order
WHERE order_status = 'Refunded';
