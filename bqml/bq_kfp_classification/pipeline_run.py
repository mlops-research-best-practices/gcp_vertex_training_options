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
    MIN_REPLICA_COUNT,
    MACHINE_TYPE,
    MAX_REPLICA_COUNT,
    PIPELINE_ROOT,
    MODEL_DIR,
    DATASET_NAME,
    AUTH_KEY,
    TEMPLATE_PATH,
)


def compile_pipeline():
    """ compile KF pipeline and store the json to file
    """
    try:
        compiler.Compiler().compile(pipeline_func=pipeline, package_path=TEMPLATE_PATH)
    except Exception as e:
        raise e


def execute_pipeline():
    """executes the KF pipeline on vertex AI 
    """
    job = aip.PipelineJob(
        display_name="bqml",
        template_path=TEMPLATE_PATH,
        pipeline_root=PIPELINE_ROOT,
        parameter_values={
            "bq_table": BQ_TABLE,
            "label": TARGET,
            "dataset": DATASET_NAME,
            "model": BQ_MODEL_NAME,
            "artifact_uri": MODEL_DIR,
            "display_name": "penguins",
            "machine_type": MACHINE_TYPE,
            "min_replica_count": MIN_REPLICA_COUNT,
            "max_replica_count": MAX_REPLICA_COUNT,
            "project": PROJECT_ID,
            "location": "US",
        },
        enable_caching=True,
    )
    job.run()


if __name__ == "__main__":
    if AUTH_KEY == "" or AUTH_KEY is None:
        raise "Improperly configured. Please check configs.py - 'AUTH_KEY'"
    else:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = AUTH_KEY
    aip.init(project=PROJECT_ID, location=REGION, staging_bucket=BUCKET_URI)
    try:
        bqclient = bigquery.Client()
    except ConnectionError:
        raise ("BigQUery client connection error. Please check IAM policy or BigQuery permissions")
    compile_pipeline()
    execute_pipeline()
