from kfp import dsl

from config import PIPELINE_NAME, PROJECT_ID, PIPELINE_ROOT, DATASET_NAME


@dsl.pipeline(name=PIPELINE_NAME, pipeline_root=PIPELINE_ROOT)
def pipeline(
    bq_table: str,
    label: str,
    dataset: str,
    artifact_uri: str,
    model: str,
    project: str = PROJECT_ID,
    location: str = "US"
):
    """AutoML pipeline for classification

    Args:
        bq_table (str): bigquery table where data is present
        label (str): target column or feature to be predicted
        dataset (str): bigquery dataset
        artifact_uri (str): model artifact storage path
        model (str): machine learning model
        project (str, optional): GCP Project ID. Defaults to PROJECT_ID.
        location (str, optional): Bigquery Region. Defaults to "US".
    """    
    from google_cloud_pipeline_components.v1.bigquery import (
        BigqueryCreateModelJobOp,
        BigqueryEvaluateModelJobOp,
        BigqueryExportModelJobOp,
        BigqueryPredictModelJobOp,
        BigqueryQueryJobOp,
    )

    bq_dataset = BigqueryQueryJobOp(
        project=project, location="US", query=f"create schema if not exists {dataset}"
    )
    # make sure to change the `query` argument, if you want to make any changes
    # create bigquery ML model
    bq_model = BigqueryCreateModelJobOp(
        project=project,
        location=location,
        query=f"CREATE OR REPLACE MODEL {dataset}.{model} OPTIONS (MODEL_TYPE='AUTOML_CLASSIFIER', INPUT_LABEL_COLS=['{label}'], BUDGET_HOURS=4.0, OPTIMIZATION_OBJECTIVE='MINIMIZE_LOG_LOSS') AS SELECT * FROM `{bq_table}`",
    ).after(bq_dataset)
    # evaluate bigquery ML model created in last step
    _ = BigqueryEvaluateModelJobOp(
        project=PROJECT_ID, location="US", model=bq_model.outputs["model"]
    ).after(bq_model)
    # perform predictions on bigquery ML model
    _ = BigqueryPredictModelJobOp(
        project=project,
        location=location,
        model=bq_model.outputs["model"],
        table_name=f"`{bq_table}`",
        job_configuration_query={
            "destinationTable": {
                "projectId": PROJECT_ID,
                "datasetId": DATASET_NAME,
                "tableId": "automl_results",
            }
        },
    ).after(bq_model)
    # lastly, upload the BQML model in GCS location
    _ = BigqueryExportModelJobOp(
        project=project,
        location=location,
        model=bq_model.outputs["model"],
        model_destination_path=artifact_uri,
    ).after(bq_model)
