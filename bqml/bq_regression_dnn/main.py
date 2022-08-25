import os
import errno
from configparser import ConfigParser
import logging

from google.cloud import bigquery
from google.cloud import logging_v2
from google.oauth2 import service_account

from scripts.bq_utils import (
    create_bq_dataset,
    execute_query,
    execute_query_output,
    get_bq_query,
)

# get the configuration variables for config file
config_parser = ConfigParser()
config_parser.read(os.path.join(os.getcwd(), "configs", "project_configs.config"))
PROJECT = config_parser.get("gcp_variables", "project")
LOCATION = config_parser.get("gcp_variables", "location")
DATASET = config_parser.get("gcp_variables", "dataset")
MODEL = config_parser.get("gcp_variables", "model")
CREDS = config_parser.get("gcp_variables", "credential_path")

LOGGER_NAME = config_parser.get("logger", "log_proj_name")
LOGGER_LVL = config_parser.get("logger", "logger_level")

TRAIN_FILE = config_parser.get("assets", "train_detail_csv")
EVAL_FILE = config_parser.get("assets", "eval_detail_csv")
PRED_FILE = config_parser.get("assets", "prediction_detail_csv")

TRAIN_QUERY = config_parser.get("sql_scripts", "training_query")
TRAIN_INFO_QUERY = config_parser.get("sql_scripts", "training_info_query")
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
        cred_path = os.path.join(os.getcwd(), "configs", CREDS)
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
    log.info(f"creating dataset name : '{DATASET}' in location '{LOCATION}'")
    create_bq_dataset(
        client=bq,
        project=PROJECT,
        dataset_name=DATASET,
        region=LOCATION,
        description="dataset is created for chicago taxi trips prediction",
        log=log,
    )
    log.info("dataset created.")

    log.info("starting DNN model training")
    train_sql = get_bq_query(TRAIN_QUERY, log)
    training_sql = train_sql.format(PROJECT, DATASET, MODEL)
    execute_query(client=bq, query=training_sql, location=LOCATION, log=log)
    log.info("DNN model training completed.")

    log.info(os.getcwd())

    log.info("training information: ")
    train_info = get_bq_query(TRAIN_INFO_QUERY, log)
    train_info_query = train_info.format(PROJECT, DATASET, MODEL)
    execute_query_output(
        client=bq, query=train_info_query, location=LOCATION, name=TRAIN_FILE, log=log
    )

    log.info("starting evaluation")
    eval_sql = get_bq_query(EVAL_QUERY, log)
    evaluation_sql = eval_sql.format(PROJECT, DATASET, MODEL)
    execute_query_output(
        client=bq, query=evaluation_sql, location=LOCATION, name=EVAL_FILE, log=log
    )
    log.info("evaluation completed")

    log.info("making predictions")
    pred_sql = get_bq_query(PRED_QUERY, log)
    prediction_sql = pred_sql.format(PROJECT, DATASET, MODEL)
    execute_query_output(
        client=bq, query=prediction_sql, location=LOCATION, name=PRED_FILE, log=log
    )
    log.info("prediction completed")


if __name__ == "__main__":
    try:
        bq = bigquery.Client(project=PROJECT)
        log.info("bigquery client created successfully")
    except Exception as e:
        log.error(e)

    main(bq)
    log.info("Program completed.")
