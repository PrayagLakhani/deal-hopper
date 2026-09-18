-- Run this AFTER dim_city exists (it references dim_city via a foreign key).
CREATE TABLE dim_customer (
    customer_id                INT PRIMARY KEY,
    city_id                    INT NOT NULL REFERENCES dim_city(city_id),
    signup_date                DATE NOT NULL,
    acquisition_channel        VARCHAR(30) NOT NULL,
    subscription_status        VARCHAR(10) NOT NULL,
    subscription_start_date    DATE
);
