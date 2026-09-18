-- Delivery distance vs. contribution margin
SELECT
    CASE
        WHEN fo.delivery_distance_km < 2 THEN '0-2km'
        WHEN fo.delivery_distance_km < 4 THEN '2-4km'
        WHEN fo.delivery_distance_km < 6 THEN '4-6km'
        WHEN fo.delivery_distance_km < 8 THEN '6-8km'
        WHEN fo.delivery_distance_km < 10 THEN '8-10km'
        ELSE '10km+'
    END AS distance_band,
    COUNT(*) AS orders,
    ROUND(AVG(fo.delivery_distance_km), 2) AS avg_distance_km,
    ROUND(AVG(fo.delivery_cost), 2) AS avg_delivery_cost,
    ROUND(AVG(fo.customer_delivery_fee), 2) AS avg_customer_fee,
    ROUND(AVG(fo.customer_delivery_fee - fo.delivery_cost), 2) AS avg_delivery_net,
    ROUND(AVG(oe.contribution_margin), 2) AS avg_contribution_margin
FROM fact_order fo
JOIN vw_order_economics oe ON fo.order_id = oe.order_id
WHERE fo.order_status = 'Delivered'
GROUP BY distance_band
ORDER BY MIN(fo.delivery_distance_km);

-- Financial impact of cancellations & refunds
SELECT
    order_status,
    COUNT(*) AS orders,
    ROUND(SUM(contribution_margin), 0) AS actual_contribution,
    ROUND(COUNT(*) * (SELECT AVG(contribution_margin) FROM vw_order_economics WHERE order_status = 'Delivered'), 0)
        AS contribution_if_delivered_normally,
    ROUND(COUNT(*) * (SELECT AVG(contribution_margin) FROM vw_order_economics WHERE order_status = 'Delivered')
          - SUM(contribution_margin), 0) AS total_margin_impact
FROM vw_order_economics
WHERE order_status IN ('Cancelled', 'Refunded')
GROUP BY order_status;

-- Which payment-method x daypart combos are structurally loss-making?
SELECT
    fo.payment_method,
    CASE
        WHEN fo.order_hour BETWEEN 6 AND 10 THEN 'Breakfast'
        WHEN fo.order_hour BETWEEN 11 AND 15 THEN 'Lunch'
        WHEN fo.order_hour BETWEEN 16 AND 19 THEN 'Evening/Snacks'
        WHEN fo.order_hour BETWEEN 20 AND 23 THEN 'Dinner'
        ELSE 'Late Night'
    END AS daypart,
    COUNT(*) AS orders,
    ROUND(AVG(oe.contribution_margin), 2) AS avg_contribution_margin
FROM fact_order fo
JOIN vw_order_economics oe ON fo.order_id = oe.order_id
WHERE fo.order_status = 'Delivered'
GROUP BY fo.payment_method, daypart
ORDER BY avg_contribution_margin ASC
LIMIT 15;

-- Does delivery delay predict refund rate and margin impact?
SELECT
    CASE WHEN fo.actual_delivery_time_min > fo.estimated_delivery_time_min * 1.3
         THEN 'Delayed 30%+' ELSE 'On-time / minor delay' END AS delay_bucket,
    COUNT(*) AS orders,
    ROUND(100.0 * SUM(CASE WHEN fo.order_status = 'Refunded' THEN 1 ELSE 0 END) / COUNT(*), 2) AS refund_rate_pct,
    ROUND(AVG(oe.contribution_margin), 2) AS avg_contribution_margin
FROM fact_order fo
JOIN vw_order_economics oe ON fo.order_id = oe.order_id
GROUP BY delay_bucket;

-- Season / festive period impact on delay, refunds, and margin
SELECT
    d.season, d.is_festive_period,
    COUNT(*) AS orders,
    ROUND(AVG(fo.actual_delivery_time_min - fo.estimated_delivery_time_min), 2) AS avg_delay_min,
    ROUND(100.0 * SUM(CASE WHEN fo.order_status = 'Refunded' THEN 1 ELSE 0 END) / COUNT(*), 2) AS refund_rate_pct,
    ROUND(AVG(oe.contribution_margin), 2) AS avg_contribution_margin
FROM fact_order fo
JOIN dim_date d ON fo.date_id = d.date_id
JOIN vw_order_economics oe ON fo.order_id = oe.order_id
GROUP BY d.season, d.is_festive_period
ORDER BY d.season, d.is_festive_period;
