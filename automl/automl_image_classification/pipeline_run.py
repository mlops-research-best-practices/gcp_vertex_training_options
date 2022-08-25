import logging

from kfp.v2 import compiler
from google.cloud import aiplatform

from pipeline import pipeline
from config.project_config import (
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
    Compile vertex pipeline with kubeflow pipeline compiler

    Returns
    -------
    None.

    """
    try:
        
        logging.info(f"Compiling training pipeline and saving file to {TEMPLATE_PATH}")
        compiler.Compiler().compile(
            pipeline_func=pipeline,
            package_path=TEMPLATE_PATH,
        )
        return
    except RuntimeError:
        logging.error(
            f"Error occurred during compiling training pipeline: {RuntimeError} "
        )
        return

def execute_pipeline():
    """
    Execute compiled kubeflow pipeline

    Returns
    -------
    None.

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
            "display_name": "automl-image",
            "project": PROJECT
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