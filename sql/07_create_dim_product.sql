CREATE TABLE dim_product (
    product_id      INT PRIMARY KEY,
    restaurant_id   INT NOT NULL REFERENCES dim_restaurant(restaurant_id),
    product_name    VARCHAR(100) NOT NULL,
    category        VARCHAR(30) NOT NULL,
    is_veg          VARCHAR(10) NOT NULL,
    is_combo        BOOLEAN NOT NULL
);

-- SCD Type 2: one or more rows per product
CREATE TABLE dim_product_price_history (
    price_id                INT PRIMARY KEY,
    product_id              INT NOT NULL REFERENCES dim_product(product_id),
    selling_price           NUMERIC(8,2) NOT NULL,
    ingredient_cost         NUMERIC(8,2) NOT NULL,
    effective_start_date    DATE NOT NULL,
    effective_end_date      DATE,             
    is_current              BOOLEAN NOT NULL
);
