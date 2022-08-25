from datetime import datetime
import configparser
import os
from os.path import join

from kfp.v2 import compiler
from kfp.v2.dsl import pipeline

from google.cloud import aiplatform
from google_cloud_pipeline_components import aiplatform as gcc_aip


config = configparser.ConfigParser()
current_dir = os.getcwd()
config.read(join(current_dir, "pipeline_config.ini"))

BUCKET_NAME = config["PIPELINE_PARAMS"]["BUCKET_NAME"]
PROJECT_ID  = config["PIPELINE_PARAMS"]["PROJECT_ID"]
REGION=config["PIPELINE_PARAMS"]["REGION"]
PIPELINE_ROOT = config["PIPELINE_PARAMS"]["PIPELINE_ROOT"]
credential_path = config["PIPELINE_PARAMS"]["CREDNTIAL_PATH"]
service_account = config["PIPELINE_PARAMS"]["SERVICE_ACCOUNT"]
bq_source = config["PIPELINE_PARAMS"]["BQ_SOURCE"]
TIMESTAMP = datetime.now().strftime("%Y%m%d%H%M%S")


@pipeline(
    name="automl-beans-custom",
    pipeline_root=PIPELINE_ROOT
)
def custom_pipeline(
    bq_source: str = bq_source,
    bucket: str = BUCKET_NAME,
    project: str = PROJECT_ID,
    gcp_region: str = REGION,
    bq_dest: str = "",
    container_uri: str = "",
    batch_destination: str = "",
    service_account: str = ""
):
    """
    

    Parameters
    ----------
    bq_source : str, optional
        DESCRIPTION: BigQuery table URI. The default is bq_source.
    bucket : str, optional
        DESCRIPTION. GCS bucket URI. The default is BUCKET_NAME.
    project : str, optional
        DESCRIPTION: Project ID. The default is PROJECT_ID.
    gcp_region : str, optional
        DESCRIPTION: Prject region. The default is REGION.
    bq_dest : str, optional
        DESCRIPTION: Bigquery destination URI. The default is "".
    container_uri : str, optional
        DESCRIPTION: Container image URI. The default is "".
    batch_destination : str, optional
        DESCRIPTION: Batch prediction output artifact path. The default is "".
    service_account : str, optional
        DESCRIPTION: Service account email. The default is "".

    Returns
    -------
    None.

    """
    dataset_create_op = gcc_aip.TabularDatasetCreateOp(
        display_name="tabular-chicago-dataset",
        bq_source=bq_source,
        project=project,
        location=gcp_region
    )

    training_op = gcc_aip.CustomContainerTrainingJobRunOp(
        display_name="pipeline-chicago-custom-train",
        container_uri=container_uri,
        project=project,
        location=gcp_region,
        dataset=dataset_create_op.outputs["dataset"],
        staging_bucket=bucket,
        training_fraction_split=0.8,
        validation_fraction_split=0.1,
        test_fraction_split=0.1,
        bigquery_destination=bq_dest,
        model_serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.0-24:latest",
        model_display_name="scikit-chicago-model-pipeline",
        machine_type="n1-standard-4",
        service_account = service_account
    )

    batch_predict_op = gcc_aip.ModelBatchPredictOp(
        project=project,
        location=gcp_region,
        job_display_name="chicago-batch-predict",
        model=training_op.outputs["model"],
        gcs_source_uris=["{0}/batch_pred_sample.csv".format(BUCKET_NAME)],
        instances_format="csv",
        gcs_destination_output_uri_prefix=batch_destination,
        machine_type="n1-standard-4"
    )


compiler.Compiler().compile(
    pipeline_func=custom_pipeline, package_path="custom_train_pipeline.json"
)


pipeline_job = aiplatform.PipelineJob(
    display_name="custom-train-pipeline",
    template_path="custom_train_pipeline.json",
    job_id="custom-train-pipeline-{0}".format(TIMESTAMP),
    parameter_values={
        "project": PROJECT_ID,
        "bucket": BUCKET_NAME,
        "bq_dest": "bq://{0}".format(PROJECT_ID),
        "container_uri": "gcr.io/{0}/scikit:v2".format(PROJECT_ID),
        "batch_destination": "{0}/batchpredresults".format(BUCKET_NAME),
        "service_account": service_account
    },
    enable_caching=True,
)

pipeline_job.submit(service_account = service_account)











