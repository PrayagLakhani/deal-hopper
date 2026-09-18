CREATE TABLE fact_order_item (
    order_item_id               INT PRIMARY KEY,
    order_id                    INT NOT NULL REFERENCES fact_order(order_id),
    product_id                  INT NOT NULL REFERENCES dim_product(product_id),
    quantity                    INT NOT NULL,
    item_price                  NUMERIC(8,2) NOT NULL,   -- unit price at time of sale
    item_ingredient_cost        NUMERIC(8,2) NOT NULL,   -- unit cost at time of sale
    item_discount_allocated     NUMERIC(8,2) NOT NULL,
    packaging_cost              NUMERIC(6,2) NOT NULL
);
