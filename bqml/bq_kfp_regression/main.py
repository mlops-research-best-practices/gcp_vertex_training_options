from datetime import datetime

from kfp.v2 import compiler
from google.cloud.aiplatform import pipeline_jobs

from utils import create_bq_dataset, upload_sql_to_gcs
from kfp_pipeline import pipeline
from config import (
    PROJECT_ID,
    DATASET_ID,
    BUCKET_NAME,
    BQ_REGION,
    VERTEX_PIPELINE_NAME,
    EVAL_BLOB_PATH,
    EVAL_FILE_PATH,
    TRAIN_BLOB_PATH,
    TRAIN_FILE_PATH,
    JSON_FILE_TEMPLATE,
    CRED
)

if __name__ == "__main__":
    # 1. create dataset
    create_bq_dataset( credential_path=CRED,
        project=PROJECT_ID, dataset_name=DATASET_ID, region=BQ_REGION, description=None
    )
    # 2. upload SQL queries

    blob_url1 = upload_sql_to_gcs(
        bucket_name=BUCKET_NAME, blob_path=TRAIN_BLOB_PATH, file_path=TRAIN_FILE_PATH
    )
    blob_url2 = upload_sql_to_gcs(
        bucket_name=BUCKET_NAME, blob_path=EVAL_BLOB_PATH, file_path=EVAL_FILE_PATH
    )
    # 3. compile KFP
    compiler.Compiler().compile(pipeline_func=pipeline, package_path=JSON_FILE_TEMPLATE)
    TIMESTAMP = datetime.now().strftime("%Y%m%d%H%M%S")
    # 4. create job
    job = pipeline_jobs.PipelineJob(
        display_name=VERTEX_PIPELINE_NAME,
        template_path=JSON_FILE_TEMPLATE,
        job_id="regression-job-{0}".format(TIMESTAMP),
        enable_caching=False,
    )
    # 5. run pipeline
    job.run()
