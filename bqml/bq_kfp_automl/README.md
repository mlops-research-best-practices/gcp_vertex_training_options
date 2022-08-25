## BQML Model Training and Deployment on Kubeflow Pipelines

This project demonstrate on Training a machine learning model using BigQuery ML. Deployment of this trained model on Vertex Endpoint. Both, training and deployment of pipeline is creating using Kubeflow Pipelines.

## Project Folder Structure

```
├── artifacts          # directory for storing BQML queries
|    ├── images        # images directory for readme.md file
|    └── creds.json    # GCP credentials JSON file
├── config.py          # pipeline configurations
├── pipeline_run.py    # compiles & runs KubeFlow pipeline
├── pipeline.py        # Kubeflow pipelinw
├── requirements.txt   # project dependencies
└── README.md          
```

## Usage
1. Install the project requirements. Go to cloud shell or command line and run `pip3 install requirements.txt`
2. Update `artifacts/creds.json` with your service account credentials
3. Modify the `config.py` file as per the project name and other required variables
4. To compile and sumbmit pipeline to vertex ai, run `python3 pipeline_run.py`

**NOTE:** *It is recommended to create a directory in cloud shell and clone the project repository in this newly created directory. This will avoid any dependency/permission issues.*

In config.py, some of the important variables you must change are shown below:
```
 - PROJECT_ID = "<your-gcp-project-id>"
 - REGION = "us-central1"
 - BUCKET_NAME = "<your-gcs-bucket-name>"
 - BUCKET_URI = f"gs://{BUCKET_NAME}"
 - AUTH_KEY = "<your_abs_path>/artifacts/creds.json" #change <your_abs_path>
 - SERVICE_ACCOUNT = "<your_service_account>.gserviceaccount.com"
```