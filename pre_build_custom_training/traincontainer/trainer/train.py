from sklearn.tree import DecisionTreeClassifier
from google.cloud import bigquery, logging_v2
from google.cloud import storage
from google.oauth2 import service_account
from joblib import dump
import gcsfs
import json

import config
import errno
import logging

import os
import numpy as np




def get_logger(credential_path):
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


def service_credentials(credential_path: str):
    """
    Create service account credential object from json key

    Parameters
    ----------
    credential_path : str
        DESCRIPTION: Service account json key file path

    Returns
    -------
    cred : OBJ
        DESCRIPTION: google auth credential object

    """
    gcs_file_system = gcsfs.GCSFileSystem()
    cred = json.load(gcs_file_system.open(credential_path))
    return cred


log = get_logger(credential_path = config.credential_path)
cred = service_credentials(credential_path = config.credential_path)
bqclient = bigquery.Client.from_service_account_info(cred)
storage_client = storage.Client.from_service_account_info(cred)


def download_table(bq_table_uri: str):
    """
    Download table from bigquery

    Parameters
    ----------
    bq_table_uri : str
        DESCRIPTION: Bigquery table URI

    Returns
    -------
    pandas.DataFrame
        DESCRIPTION: bq table as pandas dataframe

    """
    prefix = "bq://"
    if bq_table_uri.startswith(prefix):
        bq_table_uri = bq_table_uri[len(prefix):]

    table = bigquery.TableReference.from_string(bq_table_uri)
    rows = bqclient.list_rows(
        table,
    )
    return rows.to_dataframe(create_bqstorage_client=False)

log.info("START : custom training")
# These environment variables are from Vertex AI managed datasets
training_data_uri = os.environ["AIP_TRAINING_DATA_URI"]
test_data_uri = os.environ["AIP_TEST_DATA_URI"]
log.info("Training data read initiated")
# Download data into Pandas DataFrames, split into train / test
df = download_table(training_data_uri)
df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.dropna(inplace = True)
log.info("Training data read complete")
log.info("Test data read initiated")
test_df = download_table(test_data_uri)
test_df.replace([np.inf, -np.inf], np.nan, inplace=True)
test_df.dropna(inplace = True)
labels = df.pop("fare").tolist()
data = df.values.tolist()
test_labels = test_df.pop("fare").tolist()
test_data = test_df.values.tolist()
log.info("Test data read complete")

log.info("Training Decision tree initiated")
# Define and train the Scikit model
skmodel = DecisionTreeClassifier()
skmodel.fit(data, labels)
log.info("Training Decision tree completed")
score = skmodel.score(test_data, test_labels)
log.info('Accuracy is:',score)

# Save the model to a local file
dump(skmodel, "model.joblib")

log.info("Model upload initiated")
# Upload the saved model file to GCS
bucket = storage_client.get_bucket(config.BUCKET)
model_directory = os.environ["AIP_MODEL_DIR"]
storage_path = os.path.join(model_directory, "model.joblib")
blob = storage.blob.Blob.from_string(storage_path, client=storage_client)
blob.upload_from_filename("model.joblib")
log.info("Model upload completed")
log.info("FINISH : custom training")