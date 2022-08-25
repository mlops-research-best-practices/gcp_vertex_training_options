# NYC citybike trip duration prediction using Bigquery ML

Bigquery public dataset `bigquery-public-data.new_york_citibike.citibike_trips` is used in this project. This project aims to predict the trip duration using XGBoost regression model trained using Bigquery ML. 

### Project Structure
- `assets` : This directory contains csv files which stores the model training, model evaluation and model prediction results.
- `notebooks` : This directory contains the notebooks used for the exploration of the dataset and model building.
- `scripts` : This directory is used to contains commonly used scripts throughout the project.
- `configs` : This directory contained project related `.config` file and serive account credentials(`.json`).
- `main.py` : This file is starting point of entire project. 
- `queries` : This directory stores `.sql` scripts utilized during the model training & training information, model evaluation & model predictions.
- `requirements.txt` : This file contains project dependencies.


### Project Pre-requisites 
1. Active GCP Billing account 
2. New or existing GCP Project
3. Enable Bigquery API service
4. Enable Cloud Logging API service

### Usage
1. To run the project, configure the `project_config.config` file as mentioned above
2. once configuration is complete, run `python3 main.py` in the root directory of the project

