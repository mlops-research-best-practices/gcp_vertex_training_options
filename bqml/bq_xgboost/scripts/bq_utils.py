import os, json
from google.cloud import bigquery
from google.cloud import storage

# def create_bq_dataset(client, project, dataset_name, region, description, log):
#     """
#     to create a dataset in bigquery
#     Args:
#         client       : bigquery client
#         project      : gcp project name
#         dataset_name : name of the dataset to be created
#         region       : dataset location e.g. US
#         description  : short overview about the use of dataset
#         log          : cloud logging logger object 
#     """
#     dataset_id = f"{project}.{dataset_name}"
#     ds_info = bigquery.Dataset(dataset_id)
#     ds_info.location = region
#     ds_info.description = description
#     ds = client.create_dataset(ds_info, exists_ok=True)

def create_bq_dataset( credential_path, project, dataset_name, region, description):
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


def create_bq_table(
    client, query, project_name, dataset_name, table_name, location, log
):
    """
    To create table using bigquery in available dataset
    Args:
        client       : bigquery client
        query        : table creation query
        project_name : gcp project name
        dataset_name : name of the dataset to be created
        table_name   : table name to be created within dataset
        location     : location of datset & table
        log          : cloud logging logger object
    """
    table_id = f"{project_name}.{dataset_name}.{table_name}"
    job_config = bigquery.QueryJobConfig(destination=table_id)
    job = client.query(query, job_config=job_config)
    job.result()
    log.info(f"This query will process {job.total_bytes_processed} bytes.")
    log.info("Query results loaded to the table {}".format(table_id))


def execute_query(client, query, location, log):
    """
    To execute bigquery query
    Args:
        client       : bigquery client
        query        : table creation query
        location     : location of datset & table
        log          : cloud logging logger object
    """
    job_config = bigquery.QueryJobConfig()
    job = client.query(query, job_config)
    job.result()
    log.info(f"This query will process {job.total_bytes_processed} bytes.")


def execute_query_output(client, query, location, name, log):
    """
    To execute bigquery query
    Args:
        client   : bigquery client
        query    : table creation query
        location : location of datset & table
        name     : name of output file to be stored in assets directory
        log      : cloud logging logger object
    """
    job_config = bigquery.QueryJobConfig()
    job = client.query(query, job_config=job_config)
    job.result()
    log.info(f"This query will process {job.total_bytes_processed} bytes.")
    path = os.path.join(os.getcwd(), "assets", name)
    job.to_dataframe().to_csv(path, index=False)


def upload_sql_to_gcs(bucket_name, blob_path, file_path):
    # Send base_sql.txt to GCS bucket
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.upload_from_filename(file_path)
    return blob.public_url



def get_bq_query(query_file: str = None, log=None) -> str:
    """
    to get bq query
    Args: query_file (str, required): file location for sql script. Defaults is None
    Returns:
        str: file read as string
    """
    sql_path = os.path.join(os.getcwd(), "queries", query_file)
    try:
        with open(sql_path) as file:
            query_string = file.read()
        return query_string
    except FileNotFoundError:
        log.error(f"File is not found at {sql_path}")
        raise f"File is not found at {sql_path}"


def list_bq_table(client, dataset_name, log):
    tables = client.list_tables(dataset_name)
    for table in tables:
        print(table.table_id)


def get_bq_table_schema(client, dataset_name, log):
    table = client.get_tables(dataset_name)
    for field in table.schema:
        print(field)


def get_data_source_name(name, log):
    return f"`{name}`"


# from google.cloud import bigquery
# client = bigquery.Client()
# gcs_uri = 'gs://cloud-samples-data/bigquery/us-states/us-states.json'
# dataset = client.create_dataset('us_states_dataset')
# table = dataset.table('us_states_table')
# job_config = bigquery.job.LoadJobConfig()
# job_config.schema = [
#     bigquery.SchemaField('name', 'STRING'),
#     bigquery.SchemaField('post_abbr', 'STRING'),
# ]
# job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
# load_job = client.load_table_from_uri(gcs_uri, table, job_config=job_config)
# print('JSON file loaded to BigQuery')


# from google.cloud import bigquery

# # Construct a BigQuery client object.
# client = bigquery.Client()

# # TODO(developer): Set model_id to the ID of the model to fetch.
# # model_id = 'your-project.your_dataset.your_model'

# model = client.get_model(model_id)  # Make an API request.

# full_model_id = "{}.{}.{}".format(model.project, model.dataset_id, model.model_id)
# friendly_name = model.friendly_name
# print(
#     "Got model '{}' with friendly_name '{}'.".format(full_model_id, friendly_name)
# )
