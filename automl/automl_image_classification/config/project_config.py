"""
Static configuration parameters to run the kfp pipeline
"""
PROJECT = ""
REGION = "us-central1"
CREDS = "gs://<your_credential_filepath>.json"
PIPELINE_ROOT = "gs://<root_path>f"
PIPELINE_NAME = "automl-image-training"
GCS_DATA_SRC = "gs://cloud-samples-data/vision/automl_classification/flowers/all_data_v2.csv"
SERVICE_ACCOUNT = (
    "<your_service_account>"
)
DISPLAY_NAME = "automl-image-pipeline-job"
TEMPLATE_PATH = "artifacts/automl_image_pipeline.json"