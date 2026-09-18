CREATE TABLE dim_promotion (
    promotion_id                INT PRIMARY KEY,
    promotion_name               VARCHAR(100) NOT NULL,
    promotion_type               VARCHAR(30) NOT NULL,
    discount_value                NUMERIC(6,2) NOT NULL,
    max_discount_cap              NUMERIC(6,2),
    min_order_value               NUMERIC(6,2) NOT NULL,
    target_segment                VARCHAR(30) NOT NULL,
    funded_by                     VARCHAR(30) NOT NULL,
    platform_funding_share_pct    NUMERIC(5,1) NOT NULL,
    start_date                    DATE NOT NULL,
    end_date                      DATE NOT NULL,
    planned_budget                NUMERIC(10,2) NOT NULL
);
