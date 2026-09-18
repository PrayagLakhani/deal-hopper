CREATE TABLE dim_city (
    city_id                 INT PRIMARY KEY,
    city_name               VARCHAR(100) NOT NULL,
    state                   VARCHAR(100) NOT NULL,
    region                  VARCHAR(20)  NOT NULL,
    city_tier               VARCHAR(10)  NOT NULL,
    platform_launch_date    DATE         NOT NULL,
    estimated_market_size   INT          NOT NULL
);

