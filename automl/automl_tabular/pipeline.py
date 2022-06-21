from google.cloud import aiplatform
from google_cloud_pipeline_components import aiplatform as gcc_aip
from kfp.v2 import dsl
from kfp.v2.dsl import pipeline

from deploy import model_deploy
from config.setup import PIPELINE_ROOT, PIPELINE_NAME, CREDS

@pipeline(
    name=PIPELINE_NAME,
    pipeline_root= PIPELINE_ROOT,
)
def pipeline(
    bq_source: str,
    display_name: str,
    project: str,
    gcp_region: str = "us-central1"
):
    """ Vertex Pipelines for AutoML Tabular Classification use case

    Args:
        bq_source (str): bigquery uri 
        display_name (str): display name
        project (str): GCP project id
        gcp_region (str, optional): GCP region. Defaults to "us-central1"
    """    
    dataset_create_op = gcc_aip.TabularDatasetCreateOp(
        project=project,
        display_name=display_name,
        bq_source=bq_source
    )

    training_op = gcc_aip.AutoMLTabularTrainingJobRunOp(
        project=project,
        display_name=display_name,
        target_column="trip_total",
        training_fraction_split=0.6,
        validation_fraction_split=0.2,
        test_fraction_split=0.2,
        budget_milli_node_hours=1000,
        optimization_prediction_type='regression',
        optimization_objective="minimize-rmse",
        dataset=dataset_create_op.outputs["dataset"],
    )

    endpoint_op = gcc_aip.EndpointCreateOp(
        project=project,
        location=gcp_region,
        display_name="train-automl-tabular",
    )

    model_deploy(
        endpoint_artifact=endpoint_op.outputs["endpoint"],
        model_artifact=training_op.outputs["model"],
    )
