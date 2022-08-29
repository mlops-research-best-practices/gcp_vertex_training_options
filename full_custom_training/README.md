# Custom Training on Vertex AI

### Code Repo Explanation
- `data_ingestion.py`: reads the data from bigquery and bring it to the pipeline for downstream consumption
- `training.py`: trains the ML model
- `validation.py`: validated the trained model
- `deploy.py`: deploys the trained and validated model
- `pipeline.py`: contains the compilation of the components 
- `run_pipeline.py`: executes the pipeline.
- `config`: sub directory contains `config.ini` which holds all the input parameters required for running the pipeline. 
- `component_artifacts`: directory is an output directory where yaml files for each component will be stored. 
- `pipeline_artifacts`: sub-directory is created to contain the json file that is created by the pipeline execution. This json file can be used to recreate the pipeline again. 

### Usage
```
    1. Fire up the cloud shell & git clone the repository
    2. Navigate to `full_custom_training` directory
    3. Go to `config/config.ini` file and make necessary changes such as PROJECT, REGION, CREDENTIAL PATH etc.
    4. Run `python3 run_pipeline.py` command
    5. Go to Vertex AI to check for the pipeline execution and status
```


