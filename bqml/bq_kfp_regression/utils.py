from google.cloud import bigquery
from google.cloud import storage
import json
import gcsfs

def create_bq_dataset(credential_path:str, project:str, dataset_name:str, region:str, description:str):
    """Create BigQuery dataset

    Args:
        credential_path (str): credential "json" file path
        project (str): GCP project id
        dataset_name (str): bigquery dataset name
        region (str): region
        description (str): dataset description
    """    
    # gcs_file_system = gcsfs.GCSFileSystem()
    # cred = json.load(gcs_file_system.open(credential_path))
    with open(credential_path, "r") as f:
        cred=json.load(f)
    client = bigquery.Client.from_service_account_info(cred)
    # client = bigquery.Client(project=project)
    dataset_id = f"{project}.{dataset_name}"
    ds_info = bigquery.Dataset(dataset_id)
    ds_info.location = region
    ds_info.description = description
    _ = client.create_dataset(ds_info, exists_ok=True)


def upload_sql_to_gcs(bucket_name:str, blob_path:str, file_path:str):
    """Upload sql queries to GCS location from local repository

    Args:
        bucket_name (str): GCS Bucket name
        blob_path (str): GCS Bucket path name
        file_path (str): GCS Bucket file name or blob name

    Returns:
        _type_: _description_
    """    
    # Send base_sql.txt to GCS bucket
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.upload_from_filename(file_path)
    return blob.public_url
