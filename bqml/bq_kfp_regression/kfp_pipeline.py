from typing import Dict, Optional

from kfp import dsl
from kfp.v2.dsl import (
    Artifact,
    Model,
    Output,
    OutputPath,
    component,
)

from config import (
    PROJECT_ID,
    DATASET_ID,
    BUCKET_NAME,
    EVAL_BLOB_PATH,
    TRAIN_BLOB_PATH,
    ENDPOINT_DISPLAY_NAME,
    MODEL_DISPLAY_NAME,
    BQML_MODEL_NAME,
    REGION,
    PIPELINE_ROOT,
    VERTEX_PIPELINE_NAME,
    MACHINE_TYPE,
    MAX_REPLICA,
    MIN_REPLICA,
    CREDENTIAL_PATH
)


@component(
    # this component builds a regression model with BigQuery ML
    packages_to_install=[
        "google-cloud-aiplatform",
        "google-cloud-bigquery",
        "google-cloud-storage",
        "gcsfs==2021.11.1"
    ],
    base_image="python:3.9",
    output_component_file="output_component/create_bqml_model.yaml",
)
def build_bqml_model(
    credential_path:str,
    project_id: str,
    data_set_id: str,
    model_name: str,
    bucket_name: str,
    blob_path: str,
):
    """build bigquery machine learning model 

    Args:
        project_id (str): GCP Project ID
        data_set_id (str): GCP dataset
        model_name (str): BQML model name, user defined
        training_view (str): bigquery view name used for training
        bucket_name (str): GCS Bucket name
        blob_path (str): GCS file path, user defined

    """
    from google.cloud import bigquery
    import json
    import gcsfs
    # client = bigquery.Client(project=project_id)
    gcs_file_system = gcsfs.GCSFileSystem()
    cred = json.load(gcs_file_system.open(credential_path))
    bq_client=bigquery.Client.from_service_account_info(cred)

    def get_sql(bucket_name, blob_path):
        from google.cloud import storage
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.get_blob(blob_path)
        content = blob.download_as_string()
        content = str(content, "utf-8")
        return content

    content = get_sql(bucket_name, blob_path)
    model_build_query = content.format(
        project_id, data_set_id, model_name
    )

    bq_client.query(model_build_query)  


@component(
    # this component evaluations Logistic Regression
    packages_to_install=[
        "google-cloud-bigquery",
        "pandas",
        "gcsfs==2021.11.1",
        "pyarrow",
        "matplotlib",
        "db-dtypes",
        "google-cloud-storage",
    ],
    base_image="python:3.9",
    output_component_file="output_component/evaluate_bqml_model.yaml",
)
def evaluate_bqml_model(
    credential_path:str,
    project_id: str,
    data_set_id: str,
    model_name: str,
    bucket_name: str,
    blob_path: str,
    meta_data_path: OutputPath("Dataset"),
):
    """_summary_

    Args:
        project_id (str): GCP project ID
        data_set_id (str): Bigquery dataset id
        model_name (str): BQML model name, user defined
        bucket_name (str): GCS Bucket name
        blob_path (str): GCS bucket path, user defined
        logistic_data_path (OutputPath): Vertex Path for artifact storage

    """
    from google.cloud import bigquery
    from google.cloud.exceptions import NotFound
    import pandas as pd
    import pyarrow
    import matplotlib as plt
    import time, json
    import gcsfs

    gcs_file_system = gcsfs.GCSFileSystem()
    cred = json.load(gcs_file_system.open(credential_path))
    bq_client=bigquery.Client.from_service_account_info(cred)
    # bq_client = bigquery.Client(project=project_id)

    # wait to ensure the model exists.  check 5 times with a minute wait between.
    _model_name = project_id + "." + data_set_id + "." + model_name

    for _ in range(0, 5):
        try:
            bq_client.get_model(_model_name)  # Make an API request.
            # print(f"Model {model_name} already exists.")
            break  # if here, the model exists so we exit the loop
        except:
            # print(f"Model {model_name} is not found. Attempt #: {i}")
            time.sleep(60)

    def get_sql(bucket_name, blob_path):
        from google.cloud import storage
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.get_blob(blob_path)
        content = blob.download_as_string()
        content = str(content, "utf-8")
        return content

    content = get_sql(bucket_name, blob_path)
    eval_model_query = content.format(
        project_id, data_set_id, model_name
    )

    query_job = bq_client.query(
        eval_model_query
    )

    df_evaluation= query_job.result()
    df_evaluation = df_evaluation.to_dataframe()
    df_evaluation.to_csv(meta_data_path)
    graph = df_evaluation.plot(
        x="threshold", y=["precision", "recall"]
    ).get_figure()
    graph.savefig(meta_data_path)

@component(
    # this component deploys the model
    packages_to_install=[
        "google-cloud-aiplatform",
        "google-cloud-storage",
        "db-dtypes",
    ],
    base_image="python:3.9",
    output_component_file="output_component/deploying_bqml_model.yaml",
)
def deploy_bqml_model(
    project_id: str,
    location: str,
    model_name: str,
    endpoint_display_name: str,
    machine_type: str,
    vertex_endpoint: Output[Artifact],
    vertex_model: Output[Model],
    deployed_model_display_name: Optional[str] = None,
    traffic_percentage: Optional[int] = 0,
    traffic_split: Optional[Dict[str, int]] = None,
    min_replica_count: int = 1,
    max_replica_count: int = 2,
    accelerator_type: Optional[str] = None,
    accelerator_count: Optional[int] = None,
    # explanation_metadata: Optional[explain.ExplanationMetadata] = None,
    # explanation_parameters: Optional[explain.ExplanationParameters] = None,
    # metadata: Optional[Sequence[Tuple[str, str]]] = (),
    sync: bool = True,
):
    """deploying the bqml model on vertex endpoint

    Args:
        project_id (str): GCP Project ID
        location (str): GCP Region
        model_name (str): BQML model name
        endpoint_display_name (str): vertex endpoint display name
        machine_type (str): e.g. n1-standard-2, n1-standard-4
        vertex_endpoint (Output[Artifact]): vertex endpoint, output artifact
        vertex_model (Output[Model]): vertex model, output artifact
        deployed_model_display_name (Optional[str], optional): _description_. Defaults to None.
        traffic_percentage (Optional[int], optional):  Defaults to 0.
        traffic_split (Optional[Dict[str, int]], optional): Defaults to None.
        min_replica_count (int, optional): minimum replication . Defaults to 1.
        max_replica_count (int, optional): maximum replication. Defaults to 2.
        accelerator_type (Optional[str], optional): GPU Type. Defaults to None.
        accelerator_count (Optional[int], optional): No. of GPUs. Defaults to None.
        sync (bool, optional): Defaults to True.
    """
    from google.cloud import aiplatform
    from google.cloud.aiplatform import explain

    # aiplatform initialization
    aiplatform.init(project=project_id, location=location)

    # Getting Vertex Model
    model = aiplatform.Model(model_name=model_name)

    # Creating Vertex Endpoint
    lr_endpoint = aiplatform.Endpoint.create(
        display_name=endpoint_display_name, project=project_id, location=location,
    )

    # Deploying model to endpoint
    endpoint = model.deploy(
        endpoint=lr_endpoint,
        deployed_model_display_name=deployed_model_display_name,
        traffic_percentage=traffic_percentage,
        traffic_split=traffic_split,
        machine_type=machine_type,
        min_replica_count=min_replica_count,
        max_replica_count=max_replica_count,
        accelerator_type=accelerator_type,
        accelerator_count=accelerator_count,
        # explanation_metadata=explanation_metadata,
        # explanation_parameters=explanation_parameters,
        # metadata=metadata,
        sync=sync,
    )

    model.wait()
    vertex_endpoint.uri = endpoint.resource_name
    vertex_model.uri = model.resource_name


@dsl.pipeline(
    # Default pipeline root. You can override it when submitting the pipeline.
    pipeline_root=PIPELINE_ROOT,
    # A name for the pipeline.
    name=VERTEX_PIPELINE_NAME,
    description="Propensity BigQuery ML Test",
)
def pipeline():
    """kubeflow pipeline for vertex AI
    """

    # bq_dataset_op = BigqueryQueryJobOp(
    #     project=PROJECT_ID, location="US", query=f"create schema if not exists {DATASET_ID}"
    # )

    build_bqml_model_op = build_bqml_model(
        credential_path=CREDENTIAL_PATH,
        project_id=PROJECT_ID,
        data_set_id=DATASET_ID,
        model_name=BQML_MODEL_NAME,
        bucket_name=BUCKET_NAME,
        blob_path=TRAIN_BLOB_PATH,
    )

    evaluate_bqml_model_op = evaluate_bqml_model(
        credential_path=CREDENTIAL_PATH,
        project_id=PROJECT_ID,
        data_set_id=DATASET_ID,
        model_name=BQML_MODEL_NAME,
        bucket_name=BUCKET_NAME,
        blob_path=EVAL_BLOB_PATH,
    )

    deploy_bqml_model_op = deploy_bqml_model(
        project_id=PROJECT_ID,
        location=REGION,
        model_name=BQML_MODEL_NAME,
        endpoint_display_name=ENDPOINT_DISPLAY_NAME,
        deployed_model_display_name=MODEL_DISPLAY_NAME,
        machine_type=MACHINE_TYPE,
        traffic_percentage=100,
        min_replica_count=MIN_REPLICA,
        max_replica_count=MAX_REPLICA,
    )

    # joining the indivudual component to create a pipeline
    # build_bqml_model_op.after(bq_dataset_op)
    evaluate_bqml_model_op.after(build_bqml_model_op)
    deploy_bqml_model_op.after(evaluate_bqml_model_op)
