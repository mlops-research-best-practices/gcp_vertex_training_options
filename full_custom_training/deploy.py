from typing import NamedTuple
import kfp
from kfp.v2.dsl import (
    Output,
    Input,
    Artifact,
    component,
    Model
)

@component(
    packages_to_install=["google-cloud-aiplatform==1.10.0",
        "google-cloud-logging==2.7.0", "gcsfs==2021.11.1"],
    base_image="python:3.9",
    output_component_file="component_artifacts/model_deploy_comp.yaml")
def deploy_model(
    model: Input[Model],
    credential_path:str,
    project: str,
    region: str,
    serving_img: str,
    vertex_endpoint: Output[Artifact],
    vertex_model: Output[Model],
):
    """
    Model deployment on Vertex AI.

    Parameters
    ----------
    model : Input[Model]
        DESCRIPTION: Take machine learning model as input
    credential_path : str
        DESCRIPTION: gcs path for GCP service account credential key
    project : str
        DESCRIPTION: GCP Project ID
    region : str
        DESCRIPTION: GCP Project Region
    serving_img : str
        DESCRIPTION: Docker container image corresponding to ML Framework
    vertex_endpoint : Output[Artifact]
        DESCRIPTION.
    vertex_model : Output[Model]
        DESCRIPTION: model id deployed on endpoint

    Raises
    ------
    FileNotFoundError
        DESCRIPTION: Raise error if credential file not found

    Returns
    -------
    None

    """
    
    from google.cloud import aiplatform
    import errno
    import json
    import logging
    import os

    import gcsfs
    from google.cloud import bigquery, logging_v2
    from google.oauth2 import service_account

    def get_logger():
        """
        Initialize cloud logger

        Raises
        ------
        FileNotFoundError
            DESCRIPTION: Raise error if credential file not found

        Returns
        -------
        cloud_logger : TYPE
            DESCRIPTION: Logging instance

        """
        try:
            gcs_file_system_object = gcsfs.GCSFileSystem()
            credential = json.load(
                gcs_file_system_object.open(credential_path))
            credentials = service_account.Credentials.from_service_account_info(
                credential)
        except FileNotFoundError:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),
                                    credential_path)

        client_object = logging_v2.client.Client(credentials=credentials)
        google_log_format = logging.Formatter(
            fmt="%(name)s | %(module)s | %(funcName)s | %(message)s",
            datefmt="%Y-%m-$dT%H:%M:%S")
        handler = client_object.get_default_handler()
        handler.setFormatter(google_log_format)

        cloud_logger = logging.getLogger("data-ingestion")
        cloud_logger.setLevel("INFO")
        cloud_logger.addHandler(handler)

        return cloud_logger

    log = get_logger()
    
    gcs_file_system = gcsfs.GCSFileSystem()
    cred = json.load(gcs_file_system.open(credential_path))
    credentials = service_account.Credentials.from_service_account_info(cred)
    aiplatform.init(project=project, location=region, credentials=credentials)
    URI = str(model.uri)
    log.info("artifact_uri= ", URI)
    log.info("upload model to vertex model registry")
    deployed_model = aiplatform.Model.upload(
        display_name="custom-chicago-regression-model",
        artifact_uri=URI.replace("model",""),
        serving_container_image_uri=serving_img,
    )
    log.info("creating model endpoint")
    endpoint = aiplatform.Endpoint.create(
        display_name="chicago-taxi-prediction", project=project, location=region,
    )

    log.info("endpoint.display_name=", endpoint.display_name)
    log.info("endpoint.resource_name=", endpoint.resource_name)

    log.info("creating endpoint and deploying model to endpoint")
    endpoint = deployed_model.deploy(
        endpoint=endpoint,
        machine_type="n1-standard-4", min_replica_count=1, max_replica_count=2
    )
    log.info("Save data to the output params")
    vertex_endpoint.uri = endpoint.resource_name
    vertex_model.uri = deployed_model.resource_name