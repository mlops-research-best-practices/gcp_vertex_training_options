from kfp.v2.dsl import (
    Output,
    Input,
    Artifact,
    component,
    Model,
    Dataset,
    OutputPath
)

@component(base_image="python:3.7",
           packages_to_install=[ "google-cloud-bigquery", "db-dtypes", "google-cloud-logging==2.7.0",
               "google-cloud==0.34.0","gcsfs==2021.11.1","google-auth==1.35.0",
               "pandas","sklearn"],
           output_component_file="component_artifacts/data_ingestion_comp.yaml")
def read_data(
    credential_path: str,
    bq_query: str,
    train_dataset: Output[Dataset],
    test_dataset: Output[Dataset],
    val_dataset: Output[Dataset],
):
    """
    This is a kubeflow pipeline component to read data from bigquery

    Parameters
    ----------
    credential_path : str
        DESCRIPTION: gcs path for GCP service account credential key 
    bq_query : str
        DESCRIPTION: Query string
    train_dataset : Output[Dataset]
        DESCRIPTION: Output path to store training dataset
    test_dataset : Output[Dataset]
        DESCRIPTION: Output path to store test dataset
    val_dataset : Output[Dataset]
        DESCRIPTION: Output path to store validation dataset

    Raises
    ------
    FileNotFoundError
        DESCRIPTION: Raise error if credential file not found

    Returns
    -------
    None

    """
    from typing import List, Union
    import os
    import gcsfs
    import json
    import errno
    import logging
    
    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split

    from google.cloud import bigquery, logging_v2
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

    def load_raw_data(path: str, bq_query: str):
        """
        Read dara from bigquery

        Parameters
        ----------
        path : str
            DESCRIPTION: credential file path

        Returns
        -------
        df : pandas.DataFrame
            DESCRIPTION: returns pandas dataframe based on the 

        """
        
        gcs_file_system = gcsfs.GCSFileSystem()
        cred = json.load(gcs_file_system.open(path))
        client = bigquery.Client.from_service_account_info(cred)
        job = client.query(bq_query)
        df = job.result().to_dataframe()
        return df

    def pre_processing(df: pd.DataFrame):
        """
        Pre-process the data and split it into train test and validation datasets

        Parameters
        ----------
        df : pd.DataFrame
            DESCRIPTION: Input dataframe

        Returns
        -------
        train_data : pd.DataFrame
            DESCRIPTION: training dataset
        test_data : pd.DataFrame
            DESCRIPTION: test dataset
        val_data : pd.DataFrame
            DESCRIPTION: validation dataset

        """
        train_data, data_eval = train_test_split(df, test_size=0.3, random_state=42)
        val_data, test_data = train_test_split(data_eval, test_size=0.5, random_state=42)
        return train_data, test_data, val_data
    
    dataframe = load_raw_data(credential_path, bq_query)
    dataframe.replace([np.inf, -np.inf], np.nan, inplace=True)
    dataframe.dropna(inplace = True)
    log.info("dataframe shape: ", dataframe.shape)
    log.info("cols= ", dataframe.columns)
    
    train_data, test_data, val_data = pre_processing(
        df= dataframe, 
    )
    log.info("train_data shape:", train_data.shape)
    log.info("test_data shape:", test_data.shape)
    log.info("val_data shape:", val_data.shape)

    train_data.to_csv(f"{train_dataset.uri}.csv", index=False)
    train_dataset.metadata["name"] = "train_data"
    train_dataset.metadata["processed_data_path"] = train_dataset.uri

    test_data.to_csv(f"{test_dataset.uri}.csv", index=False)
    test_dataset.metadata["name"] = "test_data"
    test_dataset.metadata["processed_data_path"] = test_dataset.uri

    val_data.to_csv(f"{val_dataset.uri}.csv", index=False)
    val_dataset.metadata["name"] = "val_data"
    val_dataset.metadata["processed_data_path"] = val_dataset.uri