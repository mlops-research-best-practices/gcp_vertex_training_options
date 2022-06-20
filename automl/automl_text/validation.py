from typing import NamedTuple
import logging

from kfp.v2.dsl import (
    component,
    Artifact,
    ClassificationMetrics,
    Input,
    Output,
    Metrics,
)


@component(
    base_image="gcr.io/deeplearning-platform-release/tf2-cpu.2-3:latest",
    output_component_file="artifacts/tabular_eval_component.yaml",
    packages_to_install=[
        "google-cloud-aiplatform",
        "google-cloud-logging==2.7.0",
        "gcsfs==2021.11.1",
        "google-auth==1.35.0",],
)
def classification_model_eval_metrics(
    project: str,
    location: str, 
    api_endpoint: str, 
    thresholds_dict_str: str,
    credential_path: str,
    model: Input[Artifact],
    metrics: Output[Metrics],
    metricsc: Output[ClassificationMetrics],
) -> NamedTuple("Outputs", [("dep_decision", str)]):
    """Classification model evaluation metrics

    Args:
        project (str): GCP project
        location (str): GCP region
        api_endpoint (str): {your_region}-aiplatform.googleapis.com
        thresholds_dict_str (str): 
        model (Input[Artifact]):
        metrics (Output[Metrics]):
        metricsc (Output[ClassificationMetrics]):
    Returns:
        NamedTuple: Outputs
    """    

    import json
    import logging
    import errno
    import os

    import gcsfs
    from google.cloud import logging_v2
    from google.oauth2 import service_account
    from google.cloud import aiplatform as aip

    # Fetch model eval info
    def get_eval_info(client, model_name:str):
        """get evaluation information

        Args:
            client (object): client connection
            model_name (str): ml model name

        Returns:
            tuple: ( evaluation.name, metrics_list, metrics_string_list )
        """        
        from google.protobuf.json_format import MessageToDict

        response = client.list_model_evaluations(parent=model_name)
        metrics_list = []
        metrics_string_list = []
        for evaluation in response:
            logging.info("model evaluation")
            logging.info(f" name: {evaluation.name}")
            logging.info(f" metrics_schema_uri: {evaluation.metrics_schema_uri}")
            metrics = MessageToDict(evaluation._pb.metrics)
            for metric in metrics.keys():
                logging.info(f"metric:{metric}, value:{metrics[metric]}")
            metrics_str = json.dumps(metrics)
            metrics_list.append(metrics)
            metrics_string_list.append(metrics_str)

        return (
            evaluation.name,
            metrics_list,
            metrics_string_list,
        )

    # Use the given metrics threshold(s) to determine whether the model is
    # accurate enough to deploy.
    def classification_thresholds_check(metrics_dict:dict, thresholds_dict:dict):
        """ checking classification thresholds

        Args:
            metrics_dict (dict): py dictionary for metrics
            thresholds_dict (dict): py dictionary for thresholds

        Returns:
            bool: True or False
        """        
        for k, v in thresholds_dict.items():
            logging.info("k {}, v {}".format(k, v))
            if k in ["auRoc", "auPrc"]:  # higher is better
                if metrics_dict[k] < v:  # if under threshold, don't deploy
                    logging.info("{} < {}; returning False".format(metrics_dict[k], v))
                    return False
        logging.info("threshold checks passed.")
        return True

    def log_metrics(metrics_list, metricsc):
        test_confusion_matrix = metrics_list[0]["confusionMatrix"]
        logging.info(f'rows: {test_confusion_matrix["rows"]}')

        # log the ROC curve
        fpr = []
        tpr = []
        thresholds = []
        for item in metrics_list[0]["confidenceMetrics"]:
            fpr.append(item.get("falsePositiveRate", 0.0))
            tpr.append(item.get("recall", 0.0))
            thresholds.append(item.get("confidenceThreshold", 0.0))
        logging.info(f"fpr: {fpr}")
        logging.info(f"tpr: {tpr}")
        logging.info(f"thresholds: {thresholds}")
        metricsc.log_roc_curve(fpr, tpr, thresholds)

        # log the confusion matrix
        annotations = []
        for item in test_confusion_matrix["annotationSpecs"]:
            annotations.append(item["displayName"])
        logging.info("confusion matrix annotations: %s", annotations)
        metricsc.log_confusion_matrix(
            annotations,
            test_confusion_matrix["rows"],
        )

        # log textual metrics info as well
        for metric in metrics_list[0].keys():
            if metric != "confidenceMetrics":
                val_string = json.dumps(metrics_list[0][metric])
                metrics.log_metric(metric, val_string)
        metrics.metadata["model_type"] = "AutoML Text classification"

    logging.getLogger().setLevel(logging.INFO)
    aip.init(project=project, location=location)
    # extract the model resource name from the input Model Artifact
    model_resource_path = model.metadata["resourceName"]
    logging.info("model path: %s", model_resource_path)

    client_options = {"api_endpoint": api_endpoint}
    try:
        gcs_file_system_object = gcsfs.GCSFileSystem()
        credential = json.load(gcs_file_system_object.open(credential_path))
        credentials = service_account.Credentials.from_service_account_info(
            credential
        )
    except FileNotFoundError:
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), credential_path
        )
    # Initialize client that will be used to create and send requests.
    client = aip.gapic.ModelServiceClient(client_options=client_options)
    eval_name, metrics_list, metrics_str_list = get_eval_info(
        client, model_resource_path
    )
    logging.info("got evaluation name: %s", eval_name)
    logging.info("got metrics list: %s", metrics_list)
    log_metrics(metrics_list, metricsc)

    thresholds_dict = json.loads(thresholds_dict_str)
    deploy = classification_thresholds_check(metrics_list[0], thresholds_dict)
    if deploy:
        dep_decision = "true"
    else:
        dep_decision = "false"
    logging.info("deployment decision is %s", dep_decision)

    return (dep_decision,)
