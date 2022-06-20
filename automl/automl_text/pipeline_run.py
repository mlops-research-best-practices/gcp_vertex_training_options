import logging
from google.cloud import aiplatform
from kfp.v2 import compiler
from pipeline import pipeline
import os

from config.setup import (
    PROJECT,
    REGION,
    DISPLAY_NAME,
    TEMPLATE_PATH,
    PIPELINE_ROOT,
    SERVICE_ACCOUNT,
    GCS_DATA_SRC
)


def compile_pipeline():
    """
    to compile pipeline path
    """
    try:
        logging.info(f"Compiling training pipeline and saving file to {TEMPLATE_PATH}")
        compiler.Compiler().compile(
            pipeline_func=pipeline,
            package_path=TEMPLATE_PATH,
        )
    except RuntimeError:
        logging.error(
            f"Error occurred during compiling training pipeline: {RuntimeError} "
        )


def execute_pipeline():
    """
    to execute pipeline on vertex pipelines
    """
    logging.info("Creating Pipeline execution job")
    job = aiplatform.PipelineJob(
        project=PROJECT,
        location=REGION,
        display_name=DISPLAY_NAME,
        template_path=TEMPLATE_PATH,
        pipeline_root=PIPELINE_ROOT,
        parameter_values={
            "gcs_source" : GCS_DATA_SRC,
            "display_name": "automl-text",
            "project": PROJECT,
            "gcp_region": REGION,
            "thresholds_dict_str": '{"auPrc": 0.95}'
        },
        enable_caching=True,
    )
    try:
        logging.info("Running pipeline execution job on vertex pipelines")
        job.submit(service_account=SERVICE_ACCOUNT)
    except RuntimeError:
        logging.error(f"Error occurred while executing pipeline job : {RuntimeError}")


if __name__ == "__main__":
    compile_pipeline()
    execute_pipeline()
