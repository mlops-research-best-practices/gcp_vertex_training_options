SELECT
    predicted_Class as predicted_value,
    Class as actual_value
FROM
  ML.PREDICT(MODEL `{0}.{1}.{2}`,
  ( AS SELECT * FROM `sara-vertex-demos.beans_demo.large_dataset`
    WHERE
    MOD(ABS(FARM_FINGERPRINT(CONCAT(
        CAST(Area AS STRING), 
        CAST(Perimeter AS STRING),  
        CAST(ConvexArea AS STRING)))),10) between 9 and 10