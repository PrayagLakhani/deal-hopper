CREATE TABLE dim_date (
    date_id             DATE PRIMARY KEY,
    day_of_week         VARCHAR(10) NOT NULL,
    is_weekend          BOOLEAN NOT NULL,
    month               INT NOT NULL,
    month_name          VARCHAR(15) NOT NULL,
    quarter             INT NOT NULL,
    year                INT NOT NULL,
    season              VARCHAR(10) NOT NULL,
    is_festive_period   BOOLEAN NOT NULL
);
