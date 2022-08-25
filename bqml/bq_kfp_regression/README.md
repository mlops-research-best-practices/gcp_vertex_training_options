
# BQML Model Training and Deployment on Kubeflow Pipelines

This project demonstrate on Training a machine learning model using BigQuery ML. Deployment of this trained model on Vertex Endpoint. Both, training and deployment pipeline is creating using Kubeflow Pipelines.
## Project Folder Structure

```
├── output_components    # This directory is mananged by KFP. Contains .yaml file for each component.
├── queries              # directory for storing BQML queries
    ├── base_sql.txt     # creating view for generating features from the BigQuery storage
    ├── train_sql.txt    # BQML model training sql
    └── eval_sql.txt     # BQML model evaluation sql
├── notebooks            # directory contain Data Exploration / Analysis .ipynb notebooks
├── main.py              # main program which runs KF KF Pipeline
├── kfp_pipeline.py      # KF Pipeline custom components for BQML
├── configs.py           # project configurations
├── utils.py             # contains the common functions.
└──  README.md
```

## Usage/Examples

1. Update the sql queries available in `queries`. This will include queries for feature generation, model trainig and model evaluation on BQ.
2. Edit the properties in the `configs.py` file as per new project.
3. Run the kubeflow pipeline using command `python3 main.py`. Make sure that your working directory is `bq_kfp_regression`.
`NOTE` : You will have to update the `create_input_view` custom component of the kubeflow in `kfp_pipeline.py` according to the new project.
Below parameters must be set in the `configs.py` file
```
VIEW_NAME : BigQuery view you create for input data to model
DATA_SET_ID : The Data Set ID where the view sits
PROJECT_ID :The Project ID
REGION : e.g. "us-central1"
BQ_REGION : BQ location e.g. 'US'
BUCKET_NAME : GCS Bucket where the queries (e.g. base_sql.txt) file lives. You'll need to make the bucket.  
PIPELINE_ROOT : This is where all pipeline artifacts are sent. You'll need to ensure the bucket is created ahead of time e.g. f'gs://{BUCKET_NAME}'
BQML_MODEL_NAME : Machine Learning Model name which is trained by BQML
MACHINE_TYPE: e.g. "n1-standard-4"
ENDPOINT_DISPLAY_NAME: vertex endpoint display name
MODEL_DISPLAY_NAME: model display name
MAX_REPLICA : maximum replica, property for endpoint deployment
MIN_REPLICA : minimum replica, property for endpoint deployment
BASE_BLOB_PATH : e.g. 'bqml/base_sql.txt'
TRAIN_BLOB_PATH : e.g. 'bqml/train_sql.txt'
EVAL_BLOB_PATH : e.g. 'bqml/eval_sql.txt'
BASE_FILE_PATH : e.g. "queries/base_sql.txt"
TRAIN_FILE_PATH : e.g. "queries/train_sql.txt"
EVAL_FILE_PATH : e.g. "queries/eval_sql.txt"
JSON_FILE_TEMPLATE: Name of JSON file which is created after compiling KFP Pipeline
VERTEX_PIPELINE_NAME : Name to be displayed in vertex pipeline for KF
```

