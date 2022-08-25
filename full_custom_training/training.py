from kfp.v2.dsl import (
    Output,
    Input,
    component,
    Model,
    Dataset,
    OutputPath
)

@component(base_image="python:3.7",
           packages_to_install=[ "google-cloud==0.34.0", "gcsfs==2021.11.1", "google-cloud-aiplatform",
               "google-auth==1.35.0", "pandas", "sklearn", "google-cloud-logging==2.7.0"],
           output_component_file="component_artifacts/training_model.yaml")
def training(
    credential_path:str,
    train_dataset: Input[Dataset],
    test_dataset: Input[Dataset],
    model: Output[Model],
    model_metadata_path: OutputPath(str)
):
    """
    Create training component for kubeflow pipeline

    Parameters
    ----------
    credential_path : str
        DESCRIPTION: gcs path for GCP service account credential key 
    train_dataset : Input[Dataset]
        DESCRIPTION: training dataset retrieved from data ingestion component
    test_dataset : Input[Dataset]
        DESCRIPTION: test dataset retrieved from data ingestion component
    model : Output[Model]
        DESCRIPTION: model artifact path for trained model
    model_metadata_path : OutputPath(str)
        DESCRIPTION: metadata path for trained model artifact

    Raises
    ------
    FileNotFoundError
        DESCRIPTION: Raise error if credential file not found

    Returns
    -------
    None

    """

    import errno
    import json
    import logging
    import os
    
    import joblib
    import pandas as pd
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_absolute_error,mean_squared_error

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
        
    target = 'fare' 
    train_df = pd.read_csv(f"{train_dataset.uri}.csv")
    X_train = train_df.drop(target, axis=1)
    y_train = train_df[target]

    test_df = pd.read_csv(f"{test_dataset.uri}.csv")
    X_test = test_df.drop(target, axis=1)
    y_test = test_df[target]

    regr = LinearRegression()
    regr.fit(X_train, y_train)
    y_pred = regr.predict(X_test)
    mae = mean_absolute_error(y_true=y_test,y_pred=y_pred)
    mse = mean_squared_error(y_true=y_test,y_pred=y_pred) 
    rmse = mean_squared_error(y_true=y_test,y_pred=y_pred,squared=False)

    log.info("MAE : ",mae)
    log.info("MSE : ",mse)
    log.info("RMSE : ",rmse)
    
    model_metrics = {
        "MAE":mae,
        "MSE":mse,
        "RMSE":rmse
    }

    log.info("saving model (joblib)")
    joblib.dump(regr, f"{model.path}.joblib")
    
    metadata = {
        "name": "LinearRegressionClf_model",
        "version": model.VERSION,
        "model_path": model.path,
        "model_metrics": model_metrics,
        "model_framework": "scikit learn"
    }
    model.metadata["model_info"] = metadata #json.dumps(metadata)
    model.metadata["name"] = "model"
    
    with open(model_metadata_path, "w") as file_out:
        json.dump(metadata, file_out)