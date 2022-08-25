import os

from kfp.v2 import compiler
from google.cloud import bigquery
import google.cloud.aiplatform as aip

from pipeline import pipeline
from config import (
    PROJECT_ID,
    REGION,
    BUCKET_URI,
    TARGET,
    BQ_TABLE,
    BQ_MODEL_NAME,
    PIPELINE_ROOT,
    MODEL_DIR,
    DATASET_NAME,
    AUTH_KEY,
    TEMPLATE_PATH,
)


def compile_pipeline():
    """Compiles the KF Pipeline and store the JSON to path
    """    
    try:
        compiler.Compiler().compile(pipeline_func=pipeline, package_path=TEMPLATE_PATH)
    except Exception as e:
        raise e


def execute_pipeline():
    """Executes the KF Pipeline on Vertex AI 
    """    
    job = aip.PipelineJob(
        display_name="bqmlautoml",
        template_path=TEMPLATE_PATH,
        pipeline_root=PIPELINE_ROOT,
        parameter_values={
            "bq_table": BQ_TABLE,
            "label": TARGET,
            "dataset": DATASET_NAME,
            "model": BQ_MODEL_NAME,
            "artifact_uri": MODEL_DIR,
            "display_name": "penguins",
            "project": PROJECT_ID,
            "location": "US",
        },
        enable_caching=True,
    )
    job.run()


if __name__ == "__main__":
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = AUTH_KEY
    aip.init(project=PROJECT_ID, location=REGION, staging_bucket=BUCKET_URI)
    bqclient = bigquery.Client()
    compile_pipeline()
    execute_pipeline()
