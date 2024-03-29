CREATE OR REPLACE MODEL `{0}.{1}.{2}`
OPTIONS 
(
    MODEL_TYPE='BOOSTED_TREE_CLASSIFIER',  
    ENABLE_GLOBAL_EXPLAIN=TRUE,  
    INPUT_LABEL_COLS=['Class'], 
    EARLY_STOP=TRUE) 
AS SELECT * FROM `sara-vertex-demos.beans_demo.large_dataset`
WHERE
MOD(ABS(FARM_FINGERPRINT(CONCAT(CAST(Area AS STRING), CAST(Perimeter AS STRING),  CAST(ConvexArea AS STRING)))),10) between 1 and 6