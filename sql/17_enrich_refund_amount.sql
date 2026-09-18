-- Logic: refund_amount = (sum of item price*qty - discount allocated) + customer_delivery_fee + platform_fee_charged

UPDATE fact_order fo
SET refund_amount = sub.net_value
FROM (
    SELECT
        oi.order_id,
        SUM(oi.item_price * oi.quantity - oi.item_discount_allocated)
            + MAX(f.customer_delivery_fee) + MAX(f.platform_fee_charged) AS net_value
    FROM fact_order_item oi
    JOIN fact_order f ON oi.order_id = f.order_id
    GROUP BY oi.order_id
) sub
WHERE fo.order_id = sub.order_id
  AND fo.order_status = 'Refunded';
