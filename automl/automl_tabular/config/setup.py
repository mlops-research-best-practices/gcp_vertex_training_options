PROJECT = "your-project-name"
REGION = "us-central1"
DISPLAY_NAME = "automl-tabular-data-pipeline"
TEMPLATE_PATH = "artifacts/automl_tabular_pipeline.json"
PIPELINE_ROOT = "gs://<your-bucket-name>/AutoML_Tabular_Pipeline"
SERVICE_ACCOUNT = (
    "<your-service-acc-name>@<your-project-id>.iam.gserviceaccount.com"
)
PIPELINE_NAME = "automl-text-training"
BQ_DATA_SRC= "bq://<project-id>.<bq_dataset>.<bq_table_namee>"
CREDS="gs://<your-bucket-name>/keys/<your-key>.json"
