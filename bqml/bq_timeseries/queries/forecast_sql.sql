SELECT * FROM
ML.FORECAST(MODEL `{0}.{1}.{2}`, 
STRUCT(30 AS horizon, 0.8 AS confidence_level));