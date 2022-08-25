from kfp import dsl

from config import PIPELINE_NAME, PROJECT_ID, PIPELINE_ROOT, DATASET_NAME, DEPLOY_IMAGE

@dsl.pipeline(name=PIPELINE_NAME, pipeline_root=PIPELINE_ROOT)
def pipeline(
    bq_table: str,
    label: str,
    dataset: str,
    model: str,
    artifact_uri: str,
    machine_type: str,
    min_replica_count: int,
    max_replica_count: int,
    display_name: str,
    accelerator_type: str = "",
    accelerator_count: int = 0,
    project: str = PROJECT_ID,
    location: str = "US",
    region: str = "us-central1",
):
    """Machine Learning Classification Kubeflow Pipeline

    Args:
        bq_table (str): bigquery table where data is available
        label (str): target column or feature to be predicted
        dataset (str): bigquery dataset
        model (str): machine learning model
        artifact_uri (str): ML model storage artiacts path
        machine_type (str): e.g. n1-standard-2, n1-standard-4
        min_replica_count (int): integer, minimum 1
        max_replica_count (int): interger, minimum 1
        display_name (str): display name
        accelerator_type (str, optional): GPU type. Defaults to "".
        accelerator_count (int, optional): number of GPUs . Defaults to 0.
        project (str, optional): GCP Project ID. Defaults to PROJECT_ID.
        location (str, optional): BQ Location . Defaults to "US".
        region (str, optional): GCP Region. Defaults to "us-central1".
    """
    from google_cloud_pipeline_components.types import artifact_types
    from google_cloud_pipeline_components.v1.bigquery import (
        BigqueryCreateModelJobOp,
        BigqueryEvaluateModelJobOp,
        BigqueryExportModelJobOp,
        BigqueryPredictModelJobOp,
        BigqueryQueryJobOp,
    )
    from google_cloud_pipeline_components.v1.endpoint import (
        EndpointCreateOp,
        ModelDeployOp,
    )
    from google_cloud_pipeline_components.v1.model import ModelUploadOp
    from kfp.v2.components import importer_node

    # create the dataset if not already created
    bq_dataset = BigqueryQueryJobOp(
        project=project, location="US", query=f"create schema if not exists {dataset}"
    )
    # create a bigquery ML model
    bq_model = BigqueryCreateModelJobOp(
        project=project,
        location=location,
        query=f"CREATE OR REPLACE MODEL {dataset}.{model} OPTIONS (MODEL_TYPE='LOGISTIC_REG', ENABLE_GLOBAL_EXPLAIN=TRUE, INPUT_LABEL_COLS=['{label}'], EARLY_STOP=TRUE) AS SELECT * FROM `{bq_table}`",
    ).after(bq_dataset)
    # evaluation of newly create bq model
    _ = BigqueryEvaluateModelJobOp(
        project=PROJECT_ID, location="US", model=bq_model.outputs["model"]
    ).after(bq_model)
    # predictions from the ML model
    _ = BigqueryPredictModelJobOp(
        project=project,
        location=location,
        model=bq_model.outputs["model"],
        table_name=f"`{bq_table}`",
        job_configuration_query={
            "destinationTable": {
                "projectId": PROJECT_ID,
                "datasetId": DATASET_NAME,
                "tableId": "results_1",
            }
        },
    ).after(bq_model)
    # export the trained model to gcs location
    bq_export = BigqueryExportModelJobOp(
        project=project,
        location=location,
        model=bq_model.outputs["model"],
        model_destination_path=artifact_uri,
    ).after(bq_model)
    # import the model artifact from the gcs location
    import_unmanaged_model_task = importer_node.importer(
        artifact_uri=artifact_uri,
        artifact_class=artifact_types.UnmanagedContainerModel,
        metadata={"containerSpec": {"imageUri": DEPLOY_IMAGE,},},
    ).after(bq_export)
    # upload the model to vertex models
    model_upload = ModelUploadOp(
        project=project,
        display_name=display_name,
        unmanaged_container_model=import_unmanaged_model_task.outputs["artifact"],
    ).after(import_unmanaged_model_task)
    # create the vertex endpoint
    endpoint = EndpointCreateOp(
        project=project, location=region, display_name=display_name,
    ).after(model_upload)
    # deploying model to endpoint with infra
    _ = ModelDeployOp(
        model=model_upload.outputs["model"],
        endpoint=endpoint.outputs["endpoint"],
        dedicated_resources_min_replica_count=min_replica_count,
        dedicated_resources_max_replica_count=max_replica_count,
        dedicated_resources_machine_type=machine_type,
        dedicated_resources_accelerator_type=accelerator_type,
        dedicated_resources_accelerator_count=accelerator_count,
        traffic_split={"0": 100},
    )
