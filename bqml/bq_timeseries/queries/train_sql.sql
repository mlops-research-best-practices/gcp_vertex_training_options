CREATE OR REPLACE MODEL `{0}.{1}.{2}`
OPTIONS
    (
        model_type = 'ARIMA',
        time_series_timestamp_col = 'date',
        time_series_data_col = 'total_sold_liters',
        auto_arima = TRUE,
        data_frequency = 'AUTO_FREQUENCY'
    ) 
AS 
SELECT * FROM `{0}.{1}.{3}`;