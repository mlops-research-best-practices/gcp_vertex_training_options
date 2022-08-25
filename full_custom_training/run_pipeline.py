import configparser
import errno
import json
import logging
import os
from os.path import join
from datetime import datetime


from kfp.v2 import compiler
from google.cloud import aiplatform
import gcsfs
from google.cloud import logging_v2
from google.oauth2 import service_account

from pipeline import pipeline

config = configparser.ConfigParser()
current_dir = os.getcwd()
config.read(join(current_dir, "config", "config.ini"))

PROJECT_ID = config["GCP_PROJECT"]["PROJECT_ID"]
REGION = config["GCP_PROJECT"]["REGION"]
CREDENTIAL_PATH = config["GCP_PROJECT"]["CREDENTIAL_PATH"]
EXPERIMENT_NAME=config["GCP_PROJECT"]["EXPERIMENT_NAME"]
PIPELINE_DISPLAY_NAME=config["GCP_PROJECT"]["PIPELINE_DISPLAY_NAME"]
TEMPLATE = config["ML_PIPELINE"]["TEMPLATE"]
CACHE = eval(config["ML_PIPELINE"]["CACHE"])

def get_logger(credential_path=CREDENTIAL_PATH):
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

if __name__=="__main__":
    compiler.Compiler().compile(pipeline_func=pipeline, package_path=TEMPLATE)
    # initialise the aiplatform project
    log.info("initialise the aiplatform project")
    aiplatform.init(project=PROJECT_ID, location=REGION, experiment=EXPERIMENT_NAME)

    TIMESTAMP = datetime.now().strftime("%Y%m%d%H%M%S")
 
    # start the job
    log.info("start the pipeline job")
    run1 = aiplatform.PipelineJob(
        display_name=PIPELINE_DISPLAY_NAME,
        template_path=TEMPLATE,
        job_id=f"pipeline-{TIMESTAMP}",
        enable_caching=CACHE,
    )
    run1.submit()