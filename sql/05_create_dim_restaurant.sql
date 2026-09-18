CREATE TABLE dim_restaurant (
    restaurant_id      INT PRIMARY KEY,
    restaurant_name    VARCHAR(100) NOT NULL,
    city_id            INT NOT NULL REFERENCES dim_city(city_id),
    cuisine_type       VARCHAR(50) NOT NULL,
    restaurant_type    VARCHAR(30) NOT NULL,
    onboarding_date    DATE NOT NULL,
    commission_rate    NUMERIC(5,3) NOT NULL,
    avg_rating         NUMERIC(2,1) NOT NULL
);
