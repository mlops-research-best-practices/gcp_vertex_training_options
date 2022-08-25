from google.cloud import aiplatform as aip
from google_cloud_pipeline_components import aiplatform as gcc_aip
from kfp.v2 import dsl
from kfp.v2.dsl import pipeline

from config.project_config import PIPELINE_ROOT, PIPELINE_NAME


@pipeline(
    name=PIPELINE_NAME,
    pipeline_root= PIPELINE_ROOT,
)
def pipeline(
    gcs_source: str,
    display_name: str,
    project: str,
    gcp_region: str = "us-central1"
):
    """
    

    Parameters
    ----------
    gcs_source : str
        DESCRIPTION: gcs bucket uri  
    display_name : str
        DESCRIPTION: pipeline display name
    project : str
        DESCRIPTION: GCP project id
    gcp_region : str, optional
        DESCRIPTION: Pipeline region. The default is "us-central1".
    api_endpoint : str, optional
        DESCRIPTION: endpoint uri. The default is "us-central1-aiplatform.googleapis.com".
    thresholds_dict_str : str, optional
        DESCRIPTION: Tthreshold parformance matrix value. The default is '{"auPrc": 0.92}'.

    Returns
    -------
    None.

    """
    from google_cloud_pipeline_components.v1.endpoint import (EndpointCreateOp,
                                                              ModelDeployOp)

    dataset_create_op  = gcc_aip.ImageDatasetCreateOp(
            project=project,
            display_name=display_name,
            gcs_source=gcs_source,
            import_schema_uri=aip.schema.dataset.ioformat.image.single_label_classification,
        )
    training_op = gcc_aip.AutoMLImageTrainingJobRunOp(
        project=project,
        display_name="automl-image-train",
        prediction_type="classification",
        model_type="CLOUD",
        dataset=dataset_create_op.outputs["dataset"],
        model_display_name="automl-image-train",
        training_fraction_split=0.6,
        validation_fraction_split=0.2,
        test_fraction_split=0.2,
        budget_milli_node_hours=8000,
    )

    endpoint_op = EndpointCreateOp(
    project=project,
    location=gcp_region,
    display_name="automl-image-train",
)

    ModelDeployOp(
    model=training_op.outputs["model"],
    endpoint=endpoint_op.outputs["endpoint"],
    automatic_resources_min_replica_count=1,
    automatic_resources_max_replica_count=1,
)
