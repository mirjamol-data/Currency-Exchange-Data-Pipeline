-- GOLD LAYER (Views)
CREATE VIEW vw_gold_aggregated_rates AS
SELECT 
    c.date,
    d.is_weekday,
    c.base_currency,
    c.target_currency,
    cur.name AS currency_name,
    c.exchange_rate,
    
    -- Day-over-Day Percentage Change
    ((c.exchange_rate - LAG(c.exchange_rate) OVER (PARTITION BY c.target_currency ORDER BY c.date)) 
    / LAG(c.exchange_rate) OVER (PARTITION BY c.target_currency ORDER BY c.date)) * 100 AS rate_change_pct,
    
    -- 7-Day Rolling Average
    AVG(c.exchange_rate) OVER (
        PARTITION BY c.target_currency 
        ORDER BY c.date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS seven_day_avg

FROM cleaned_rates c
JOIN dim_dates d ON c.date = d.date
JOIN dim_currencies cur ON c.target_currency = cur.currency_code;
GO