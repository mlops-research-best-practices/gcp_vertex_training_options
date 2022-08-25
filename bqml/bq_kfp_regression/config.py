PROJECT_ID = "hackathon1-183523"  # The Project ID
REGION = "us-central1"
BQ_REGION = "US"
# TABLE_NAME = "taxi_data"  # BigQuery view you create for input data to model
DATASET_ID = "taxi_regression"  # The Data Set ID where the view sits
BUCKET_NAME = "hackathon1-183523"  # Bucket where the base_sql.txt file lives. You'll need to make the bucket.
CRED= f"artifacts/creds.json"
CREDENTIAL_PATH=f"gs://{BUCKET_NAME}/keys/creds.json"
PIPELINE_ROOT = f"gs://{BUCKET_NAME}"  # This is where all pipeline artifacts are sent. You'll need to ensure the bucket is created ahead of time
JSON_FILE_TEMPLATE = "artifacts/pipeline.json"
VERTEX_PIPELINE_NAME = "dnn-regression-bqml-pipeine"

BQML_MODEL_NAME = "bqml_dnn_reg_ml_model"
BLOB_PATH = "bqml/"  # The actual path where base_sql will be sent to GCS 
PRED_BLOB_PATH = "bqml/pred_sql.txt"
TRAIN_BLOB_PATH = "bqml/train_sql.txt"
EVAL_BLOB_PATH = "bqml/eval_sql.txt"
PRED_FILE_PATH = "queries/pred_sql.txt"
TRAIN_FILE_PATH = "queries/train_sql.txt"
EVAL_FILE_PATH = "queries/eval_sql.txt"

MACHINE_TYPE = "n1-standard-4"
ENDPOINT_DISPLAY_NAME = "dnn_reg_endpoint"
MODEL_DISPLAY_NAME = "dnn_reg_model"
MAX_REPLICA = 2
MIN_REPLICA = 1
