from google.cloud import aiplatform
from google_cloud_pipeline_components import aiplatform as gcc_aip
from kfp.v2 import dsl
from kfp.v2.dsl import pipeline

from deploy import model_deploy
from validation import classification_model_eval_metrics

from config.setup import PIPELINE_ROOT, PIPELINE_NAME, CREDS

@pipeline(
    name=PIPELINE_NAME,
    pipeline_root= PIPELINE_ROOT,
)
def pipeline(
    gcs_source: str,
    display_name: str,
    project: str,
    gcp_region: str = "us-central1",
    api_endpoint: str = "us-central1-aiplatform.googleapis.com",
    thresholds_dict_str: str = '{"auPrc": 0.95}',
):
    """ Vertex Pipelines for AutoML Text Classification use case

    Args:
        gcs_source (str): GCS for data path
        display_name (str): display name
        project (str): GCP project id
        gcp_region (str, optional): GCP region. Defaults to "us-central1".
        api_endpoint (str, optional): API endpoint. Defaults to "us-central1-aiplatform.googleapis.com".
        thresholds_dict_str (_type_, optional): threshold dictionary with parameters. 
                                                Defaults to '{"auPrc": 0.95}'.
    """    
    dataset_create_op = gcc_aip.TextDatasetCreateOp(
        project=project,
        display_name=display_name,
        gcs_source=gcs_source,
        import_schema_uri=aiplatform.schema.dataset.ioformat.text.single_label_classification,
    )

    training_op = gcc_aip.AutoMLTextTrainingJobRunOp(
        project=project,
        display_name=display_name,
        prediction_type="classification",
        dataset=dataset_create_op.outputs["dataset"],
    )

    model_eval_task = classification_model_eval_metrics(
        project,
        gcp_region,
        api_endpoint,
        credential_path=CREDS,
        thresholds_dict_str,
        training_op.outputs["model"],
    )

    with dsl.Condition(
        model_eval_task.outputs["dep_decision"] == "true",
        name="deploy_decision",
    ):
        endpoint_op = gcc_aip.EndpointCreateOp(
            project=project,
            location=gcp_region,
            display_name="train-automl-text",
        )

        model_deploy(
            endpoint_artifact=endpoint_op.outputs["endpoint"],
            model_artifact=training_op.outputs["model"],
        )
