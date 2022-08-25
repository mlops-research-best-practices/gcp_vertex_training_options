SELECT
    predicted_trip_total as predicted_value,
    trip_total as actual_value
FROM
  ML.PREDICT(MODEL `{0}.{1}.{2}`,
  (
    WITH parameters AS (SELECT 1 as TRAIN, 2 as EVAL, 3 as PRED),
    daynames AS (SELECT ['Sun','Mon','Tues','Wed','Thurs','Fri','Sat'] AS daysofweek),
    chicagotaxitrips AS (
        SELECT 
            trip_seconds, 
            trip_miles, 
            trip_total, 
            payment_type, 
            EXTRACT(HOUR FROM trip_start_timestamp) AS hourofday,
            ML.BUCKETIZE(EXTRACT(HOUR FROM trip_start_timestamp), [0, 6, 12, 18, 24]) AS bucket_hourofday,
            daysofweek[ORDINAL(EXTRACT(DAYOFWEEK FROM trip_start_timestamp))] AS dayofweek,
            EXTRACT(WEEK FROM trip_start_timestamp) AS week,
            EXTRACT(MONTH FROM trip_start_timestamp) as month,
            IFNULL (pickup_census_tract,-1) AS pickup_census_tract,
            IFNULL(company,"") AS company,
            IFNULL(dropoff_census_tract,-1) AS dropoff_census_tract,
            IFNULL(pickup_community_area,-1) AS pickup_community_area, 
            IFNULL(dropoff_community_area,-1) AS dropoff_community_area,  
            ST_DISTANCE(ST_GEOGPOINT(pickup_longitude, pickup_latitude), ST_GEOGPOINT(dropoff_longitude, dropoff_latitude)) AS trip_distance,
            IF(company IN ("Blue Ribbon Taxi Association Inc.", "Suburban Dispatch LLC"),1,0) as is_luxury,
            CASE  
                WHEN (pickup_community_area IN (56, 64, 76)) OR (dropoff_community_area IN (56, 64, 76)) 
                THEN 1 else 0 
            END AS is_airport
        FROM
            `bigquery-public-data.chicago_taxi_trips.taxi_trips`, daynames, parameters
            WHERE trip_miles > 0 AND trip_seconds > 0 AND trip_total BETWEEN 1 AND 100 
            AND pickup_longitude IS NOT NULL AND dropoff_longitude IS NOT NULL
            AND pickup_latitude IS NOT NULL AND dropoff_latitude IS NOT NULL
            AND MOD(ABS(FARM_FINGERPRINT(CAST(trip_start_timestamp AS STRING))),1000) = parameters.PRED
            ) 
            SELECT * FROM chicagotaxitrips
        )
    )	