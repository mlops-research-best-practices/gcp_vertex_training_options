### Use Case
This dataset includes taxi trips from 2013 to the present, reported to the City of Chicago in its role as a regulatory agency. To protect privacy but allow for aggregate analyses, the Taxi ID is consistent for any given taxi medallion number but does not show the number, Census Tracts are suppressed in some cases, and times are rounded to the nearest 15 minutes. Due to the data reporting process, not all trips are reported but the City believes that most are. For more information about this dataset and how it was created.

This public dataset is hosted in Google BigQuery and is included in BigQuery's 1TB/mo of free tier processing. This means that each user receives 1TB of free BigQuery processing every month, which can be used to run queries on this public dataset. Watch this short video to learn how to get started quickly using BigQuery to access public datasets

### Create BigQuery Dataset

- Create a BigQuery dataset for babyweight if it doesn't exist
``` bash
  datasetexists=$(bq ls -d | grep -w vertex_automl)

  if [ -n "$datasetexists" ]; then
      echo -e "BigQuery dataset already exists!"

  else
      echo "Creating BigQuery dataset titled: vertex_automl"

      bq --location=US mk --dataset \
          --description "chicago taxi trip data" \
          $PROJECT:vertex_automl
      echo "Here are your current datasets:"
      bq ls
  fi
```
- Run the below query to update the table in the above dataset.
```bash
CREATE TABLE vertex_automl.taxi_trips as
 WITH daynames AS (SELECT ['Sun','Mon','Tues','Wed','Thurs','Fri','Sat'] AS daysofweek),
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
    SQRT(POW((pickup_longitude - dropoff_longitude),2)) AS longitude,
    SQRT(POW((pickup_latitude - dropoff_latitude), 2)) AS latitude
FROM
    `bigquery-public-data.chicago_taxi_trips.taxi_trips`, daynames
    WHERE trip_miles > 0 AND trip_seconds > 0 AND trip_total BETWEEN 1 AND 100 
    AND pickup_longitude IS NOT NULL AND dropoff_longitude IS NOT NULL
    AND pickup_latitude IS NOT NULL AND dropoff_latitude IS NOT NULL
    AND MOD(ABS(FARM_FINGERPRINT(CAST(trip_start_timestamp AS STRING))),1000) = 1
) SELECT * FROM chicagotaxitrips
```
**NOTE**: Here, dataset name is `vertex_automl`, and bigquert table name is `taxi_trips`. Feel free to change it and make the samilar changes in `config/project_config.py` file

### Environment Variables
  - `PROJECT`: "your-project-name"
  - `REGION`: e.g."us-central1"
  - `DISPLAY_NAME`: Name 
  - `TEMPLATE_PATH`: <path_to_compile_path>.json
  - `PIPELINE_ROOT`: "gs://<your_bucket_name>/<path_name>"
  - `SERVICE_ACCOUNT`: "<your_service_acc_name>@<your_project_id>.iam.gserviceaccount.com"
  - `PIPELINE_NAME` : Give the name you like for your pipeline
  - `BQ_DATA_SRC` : "bq://<project_id>.<bq_dataset>.<bq_table>"
  - `CREDS` : path to your .json credentials file. You can createb from IAM -> Service Account

Ensure all the above variable need to set in `config/project_config.py` file. 

**NOTE**
: Create a google cloud storage bucket. Also, give minimun `Editor` permission/role to your service account.

###  Usage
  1. After, you have done the setup, to run pipeline : 
  ```
    python3 pipeline_run.py
  ```
  2. You can got to **Vertex AI** -> **Training**, select your pipeline to see the below screen. Job might take 5 - 6 hrs to complete.
<img
  src="https://github.com/mlops-research-best-practices/gcp_vertex_training_options/blob/feature-automl-text/automl/automl_tabular/artifacts/images/dataset_analyze.png"
  alt="Model Evaluation Image"
  title="Model Evaluation"
  width="600"
  height="400"
/>

<img
  src="https://github.com/mlops-research-best-practices/gcp_vertex_training_options/blob/feature-automl-text/automl/automl_tabular/artifacts/images/training_pipe.PNG"
  alt="Vertex Pipeline Image"
  title="Vertex Pipeline"
  width="600"
  height="400"
/>

<img
  src="https://github.com/mlops-research-best-practices/gcp_vertex_training_options/blob/feature-automl-text/automl/automl_tabular/artifacts/images/model_eval.PNG"
  alt="Model Prediction Image"
  title="Model Predictions"
  width="600"
  height="400"
/>


<img
  src="https://github.com/mlops-research-best-practices/gcp_vertex_training_options/blob/feature-automl-text/automl/automl_tabular/artifacts/images/deploy_test.png"
  alt="ROC-AUC Image"
  title="ROC AUC Metrics"
  width="600"
  height="400"
/>
