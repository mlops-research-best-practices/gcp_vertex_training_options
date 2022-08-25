from google.cloud import bigquery
import os


def create_bq_dataset(client, project, dataset_name, region, description, log):
    """To create a dataset in bigquery

    Args:
        client       : bigquery client
        project      : gcp project name
        dataset_name : name of the dataset to be created
        region       : dataset location e.g. US
        description  : short overview about the use of dataset
        log          : cloud logging logger object 
    """
    dataset_id = f"{project}.{dataset_name}"
    ds_info = bigquery.Dataset(dataset_id)
    ds_info.location = region
    ds_info.description = description
    _ = client.create_dataset(ds_info, exists_ok=True)
    log.info("dataset is created.")


def create_bq_table(
    client, query, project_name, dataset_name, table_name, location, log
):
    """ To create table using bigquery in available dataset
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
    try:
        job = client.query(query, location=location, job_config=job_config)
        job.result()
        log.info(f"This query will process {job.total_bytes_processed} bytes.")
        log.info("Query results loaded to the table {}".format(table_id))
    except Exception as e:
        log.error(str(e) + f"Table name {table_id} already exists in {dataset_name}.")


def execute_query(client, query, location, log):
    """ To execute bigquery query

    Args:
        client       : bigquery client
        query        : table creation query
        location     : location of datset & table
        log          : cloud logging logger object
    """
    job_config = bigquery.QueryJobConfig()
    job = client.query(query, location=location, job_config=job_config)
    job.result()
    log.info(f"This query will process {job.total_bytes_processed} bytes.")


def execute_query_output(client, query, location, name, log):
    """ To get the output of bigquery query

    Args:
        client   : bigquery client
        query    : table creation query
        location : location of datset & table
        name     : name of output file to be stored in assets directory
        log      : cloud logging logger object
    """
    job_config = bigquery.QueryJobConfig()
    job = client.query(query, location=location, job_config=job_config)
    job.result()
    log.info(f"This query will process {job.total_bytes_processed} bytes.")
    path = os.path.join(os.getcwd(), "assets", name)
    job.to_dataframe().to_csv(path, index=False)


def list_bq_table(client, dataset_name, log):
    tables = client.list_tables(dataset_name)
    for table in tables:
        log.info(table.table_id)
        print(table.table_id)


def get_bq_query(query_file: str = None, log=None) -> str:
    """To get BigQuery SQL query
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


def get_bq_table_schema(client, dataset_name, log):
    table = client.get_tables(dataset_name)
    for field in table.schema:
        log.info(field)


def get_data_source_name(name, log):
    return f"`{name}`"
