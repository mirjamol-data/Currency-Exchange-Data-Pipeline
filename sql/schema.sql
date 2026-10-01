--CREATE DATABASE CurrencyExchange
--GO
--USE CurrencyExchange


-- BRONZE LAYER
CREATE TABLE raw_rates (
    fetch_date DATE,
    base_currency VARCHAR(3),
    raw_json NVARCHAR(MAX), -- NVARCHAR(MAX) is used for JSON in SQL Server
    inserted_at DATETIME2 DEFAULT GETDATE()
);


-- SILVER LAYER
CREATE TABLE cleaned_rates (
    date DATE,
    base_currency VARCHAR(3),
    target_currency VARCHAR(3),
    exchange_rate DECIMAL(18, 6),
    load_timestamp DATETIME2 DEFAULT GETDATE()
);


-- GOLD LAYER (Dimensions)
CREATE TABLE dim_currencies (
    currency_code VARCHAR(3) PRIMARY KEY,
    name VARCHAR(50),
    symbol NVARCHAR(5),
    country VARCHAR(50)
);

CREATE TABLE dim_dates (
    date DATE PRIMARY KEY,
    year INT,
    month INT,
    day INT,
    is_weekday BIT
);

-- Insert starting dimension data
INSERT INTO dim_currencies (currency_code, name, symbol, country)
VALUES 
    ('USD', 'US Dollar', '$', 'United States'),
    ('EUR', 'Euro', '€', 'Eurozone'),
    ('GBP', 'British Pound', '£', 'United Kingdom'),
    ('RUB', 'Russian Ruble', '₽', 'Russia'),
    ('UZS', 'Uzbekistani Som', 'лв', 'Uzbekistan');
GO


-- TO POPULATE dim_dates table

--DECLARE @CurrentDate DATE = '2024-01-01';
--DECLARE @EndDate DATE = '2027-12-31';

---- Loop through each day and insert it into the dimension table
--WHILE @CurrentDate <= @EndDate
--BEGIN
--    INSERT INTO dim_dates (date, year, month, day, is_weekday)
--    VALUES (
--        @CurrentDate,
--        YEAR(@CurrentDate),
--        MONTH(@CurrentDate),
--        DAY(@CurrentDate),
--        -- Check if it's a weekend (Saturday or Sunday)
--        CASE WHEN DATENAME(dw, @CurrentDate) IN ('Saturday', 'Sunday') THEN 0 ELSE 1 END
--    );
    
--    -- Move to the next day
--    SET @CurrentDate = DATEADD(DAY, 1, @CurrentDate);
--END
--GO
