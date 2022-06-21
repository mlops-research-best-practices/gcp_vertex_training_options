### Use Case
This dataset includes taxi trips from 2013 to the present, reported to the City of Chicago in its role as a regulatory agency. To protect privacy but allow for aggregate analyses, the Taxi ID is consistent for any given taxi medallion number but does not show the number, Census Tracts are suppressed in some cases, and times are rounded to the nearest 15 minutes. Due to the data reporting process, not all trips are reported but the City believes that most are. For more information about this dataset and how it was created.

This public dataset is hosted in Google BigQuery and is included in BigQuery's 1TB/mo of free tier processing. This means that each user receives 1TB of free BigQuery processing every month, which can be used to run queries on this public dataset. Watch this short video to learn how to get started quickly using BigQuery to access public datasets

### Environment Variables
  - `PROJECT`: "your-project-name"
  - `REGION`: e.g."us-central1"
  - `DISPLAY_NAME`: Name 
  - `TEMPLATE_PATH`: <path_to_compile_path>.json
  - `PIPELINE_ROOT`: gs://<your_bucket_name>/<path_name>
  - `SERVICE_ACCOUNT`: <your_service_acc_name>@<your_project_id>.iam.gserviceaccount.com
  - `PIPELINE_NAME` : Give the name you like for your pipeline
  - `BQ_DATA_SRC` : "bq://<project_id>.<bq_dataset>.<bq_table>"
  - `CREDS` : path to your .json credentials file. You can createb from IAM -> Service Account

Ensure all the above variable need to set in `config/setup.py` file. 

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
