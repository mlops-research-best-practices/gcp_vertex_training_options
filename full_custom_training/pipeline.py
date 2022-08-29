import configparser
import os
from os.path import  join
from kfp.v2 import dsl
from kfp.v2.dsl import (
    pipeline
)

from data_ingestion import read_data
from deploy import deploy_model
from training import training
from validation import model_validation

config = configparser.ConfigParser()
current_dir = os.getcwd()
config.read(join(current_dir, "config", "config.ini"))
PROJECT_ID = config['GCP_PROJECT']['PROJECT_ID']
REGION = config["GCP_PROJECT"]["REGION"]
CREDENTIAL_PATH = config["GCP_PROJECT"]["CREDENTIAL_PATH"]
BUCKET_NAME = config["GCP_PROJECT"]["BUCKET_NAME"]

PIPELINE_NAME = config["ML_PIPELINE"]["PIPELINE_NAME"]
PIPELINE_ROOT = config["ML_PIPELINE"]["PIPELINE_ROOT"]
SERVING_IMAGE = config["ML_PIPELINE"]["SERVING_IMAGE"]
BQ_QUERY = config["ML_PIPELINE"]["BQ_QUERY"]
THRESHOLD_DICT= eval(config["ML_PIPELINE"]["THRESHOLD_DICT"])
MACHINE_TYPE = "n1-standard-4"

@pipeline(name=PIPELINE_NAME, pipeline_root=PIPELINE_ROOT, description="pipeline")
def pipeline():
    """
    Create pipeline object which calls all the components and merge them together

    Returns
    -------
    None.

    """
    # reading data
    read_op = read_data(
        credential_path=CREDENTIAL_PATH,
        bq_query=BQ_QUERY,
    )

    # training machine learning model
    training_op = training(
        credential_path=CREDENTIAL_PATH,
        train_dataset = read_op.outputs["train_dataset"],
        test_dataset = read_op.outputs["test_dataset"],
    )

    # validation machine learning model
    validation_op=model_validation(
        credential_path=CREDENTIAL_PATH,
        threshold_dict=THRESHOLD_DICT, 
        model_metadata_path=training_op.outputs["model_metadata_path"]
    )

    condition1 = validation_op.outputs["evaluation_status"] == "True"

    with dsl.Condition(condition1, name="deploy_model"):
        _ = deploy_model(
            credential_path=CREDENTIAL_PATH,
            model=training_op.outputs["model"],
            project=PROJECT_ID,
            region=REGION,
            serving_img=SERVING_IMAGE
        )

