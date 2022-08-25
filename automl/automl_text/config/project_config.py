PROJECT = "your-project-name"
REGION = "us-central1"
DISPLAY_NAME = "automl-text-pipeline-job"
TEMPLATE_PATH = "artifacts/automl_text_pipeline.json"
PIPELINE_ROOT = "gs://<your-bucket-name>/AutoML_Text_Pipeline"
SERVICE_ACCOUNT = (
    "<your-service-acc-name>@<your-project-id>.iam.gserviceaccount.com"
)
PIPELINE_NAME = "automl-text-training"
GCS_DATA_SRC = "gs://cloud-ml-data/NL-classification/happiness.csv"
CREDS="gs://<your-bucket-name>/keys/<your-key>.json"
