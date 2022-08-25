import os
import json
import errno
from configparser import ConfigParser
import logging

from google.cloud import bigquery
from google.cloud import logging_v2
from google.oauth2 import service_account


from scripts.bq_utils import (
    create_bq_dataset,
    execute_query,
    create_bq_table,
    execute_query_output,
    get_bq_query,
    upload_sql_to_gcs
)


config_parser = ConfigParser()
config_parser.read(os.path.join(os.getcwd(), "configs", "project_configs.config"))

PROJECT = config_parser.get("gcp_variables", "project")
LOCATION = config_parser.get("gcp_variables", "location")
DATASET = config_parser.get("gcp_variables", "dataset")
CREDS = config_parser.get("gcp_variables", "credential_path")

LOGGER_NAME = config_parser.get("logger", "log_proj_name")
LOGGER_LVL = config_parser.get("logger", "logger_level")

TRAIN_FILE = config_parser.get("assets", "train_detail_csv")
EVAL_FILE = config_parser.get("assets", "eval_detail_csv")
PRED_FILE = config_parser.get("assets", "prediction_detail_csv")
MODEL_NAME = "xgbclassifier"

TRAIN_QUERY = config_parser.get("sql_scripts", "training_query")
EVAL_QUERY = config_parser.get("sql_scripts", "evaluation_query")
PRED_QUERY = config_parser.get("sql_scripts", "prediction_query")


def get_logger():
    """
        Initialize cloud logger

        Returns:
            logger: log object
    """
    try:
        # gcs_file_system_object = gcsfs.GCSFileSystem()
        # cred = json.load(gcs_file_system_object.open(credential_path))
        cred_path = os.path.join(os.getcwd(), CREDS)
        print
        credentials = service_account.Credentials.from_service_account_file(cred_path)
    except FileNotFoundError:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), cred_path)

    # logger client
    client_object = logging_v2.client.Client(credentials=credentials)

    # formatter details
    google_log_format = logging.Formatter(
        fmt="%(name)s | %(module)s | %(funcName)s | %(message)s",
        datefmt="%Y-%m-$dT%H:%M:%S",
    )

    # handler details
    handler = client_object.get_default_handler()
    handler.setFormatter(google_log_format)

    # logger details
    cloud_logger = logging.getLogger(LOGGER_NAME)
    cloud_logger.setLevel(LOGGER_LVL)
    cloud_logger.addHandler(handler)

    return cloud_logger


log = get_logger()


def main(bq):
    log.info(f"create dataset name {DATASET} in location {LOCATION}")
    create_bq_dataset(
        credential_path=os.path.join(os.getcwd(), "configs", "creds.json"),
        project=PROJECT,
        dataset_name=DATASET,
        region=LOCATION,
        description="dataset is created for chicago taxi trip prediction"
    )
    log.info("dataset created.")

    log.info("starting training")
    train_sql_content = get_bq_query(TRAIN_QUERY, log)
    train_sql = train_sql_content.format(PROJECT, DATASET, MODEL_NAME)
    execute_query(client=bq, query=train_sql, location=LOCATION, log=log)
    log.info("training completed.")

    log.info("starting evaluation")
    evaluation_sql_content = get_bq_query(EVAL_QUERY, log)
    eval_sql = evaluation_sql_content.format(PROJECT, DATASET, MODEL_NAME)
    execute_query_output(client=bq, query=eval_sql, location=LOCATION, name=EVAL_FILE, log=log)
    log.info("evaluation completed.")

    log.info("starting predictions")
    prediction_sql_content = get_bq_query(PRED_QUERY, log)
    pred_sql = prediction_sql_content.format(PROJECT, DATASET, MODEL_NAME)
    execute_query_output(client=bq, query=pred_sql, location=LOCATION, name=PRED_FILE, log=log)
    log.info("prediction completed.")

if __name__ == "__main__":
    try:
        credential_path=os.path.join(os.getcwd(), "configs", "creds.json")
        with open(credential_path, "r") as f:
            cred=json.load(f)
        bq_client = bigquery.Client.from_service_account_info(cred)
        # bq = bigquery.Client(project=PROJECT)
        log.info("bigquery client created successfully")
    except Exception as e:
        log.error(e)

    main(bq_client)
    log.info("Program completed.")
