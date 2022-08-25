SELECT
  *
FROM
  ML.ROC_CURVE(MODEL `{0}.{1}.{2}`,
    SELECT * FROM `sara-vertex-demos.beans_demo.large_dataset`
WHERE
MOD(ABS(FARM_FINGERPRINT(CONCAT(CAST(Area AS STRING), CAST(Perimeter AS STRING),  CAST(ConvexArea AS STRING)))),10) 
between 7 and 8
)