from typing import NamedTuple
from kfp.v2.dsl import (
    Output,
    component,
    ClassificationMetrics
)

@component(
    base_image="python:3.7",
    packages_to_install=[
        "google-cloud-aiplatform==1.10.0",
        "google-cloud-logging==2.7.0", "gcsfs==2021.11.1", "google-auth==1.35.0"
    ],
    output_component_file="component_artifacts/model_validation.yaml")
def model_validation(
    credential_path:str,
    metrics: Output[ClassificationMetrics],
    threshold_dict: dict, 
    model_metadata_path: str
) -> NamedTuple("Outputs", [("evaluation_status", str)]):
    """
    Validate trained model performace with threshold values from user input
    
    Parameters
    ----------
    credential_path : str
        DESCRIPTION: gcs path for GCP service account credential key 
    metrics : Output[ClassificationMetrics]
        DESCRIPTION: path to model performace matrices
    threshold_dict : dict
        DESCRIPTION: dictionary of threshold values for model performance matrices (user input)
    model_metadata_path: str
        DESCRIPTION: GCS Path of model metadata
    val_dataset : Output[Dataset]
        DESCRIPTION: Output path to store validation dataset

    Raises
    ------
    FileNotFoundError
        DESCRIPTION: Raise error if credential file not found

    Returns
    -------
    NamedTuple("Outputs", [("evaluation_status", str)]): returns "True" if model performance exceeds threshold values, "False" otherwise
    
    """
    
    import errno
    import json
    import logging
    import os

    import gcsfs
    from google.cloud import logging_v2
    from google.oauth2 import service_account

    def get_logger():
        """
        Create logging object for pipeline logging

        Raises
        ------
        FileNotFoundError
            DESCRIPTION: Raise error if credential file not found

        Returns
        -------
        cloud_logger : OBJ
            DESCRIPTION: logging instance

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

    model_metadata = json.loads(model_metadata_path)
    log.info("model_metadata= ", model_metadata)
    condition1 = model_metadata["model_metrics"]["MAE"] < threshold_dict["MAE"]
    condition2 = model_metadata["model_metrics"]["MSE"] < threshold_dict["MSE"]
    condition3 = model_metadata["model_metrics"]["RMSE"] < threshold_dict["RMSE"]
    if condition1 and condition2 and condition3:
        evaluation_status = "True"
    else:
        evaluation_status= "False"
    return (evaluation_status, )