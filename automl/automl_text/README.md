
### Use Case
**Happy Moments** sample dataset is used to train a model. The resulting model classifies happy moments into categories that reflect the causes of happiness.

### Environment Variables
  - `PROJECT`: "your-project-name"
  - `REGION`: e.g."us-central1"
  - `DISPLAY_NAME`: Name 
  - `TEMPLATE_PATH`: <path_to_compile_path>.json
  - `PIPELINE_ROOT`: gs://<your_bucket_name>/<path_name>
  - `SERVICE_ACCOUNT`: <your_service_acc_name>@<your_project_id>.iam.gserviceaccount.com
  - `PIPELINE_NAME` 
  - `GCS_DATA_SRC`
  - `CREDS`

Ensure all the above variable need to set in `config/setup.py` file. 

**NOTE**
: Create a google cloud storage bucket

###  Usage

1. After, you have done the setup, to run pipeline, 
  ```
    python3 pipeline_run.py
  ```
  2. You can got to **Vertex AI** -> **Training**, select your pipeline to see the below screen. Job might take 5 - 6 hrs to complete.

<img
  src="https://github.com/mlops-research-best-practices/gcp_vertex_training_options/blob/feature-automl-text/automl/automl_text/artifacts/images/pipe.PNG"
  alt="Vertex Pipeline Image"
  title="Vertex Pipeline"
  width="800"
  height="600"
/>

  3.  Once, pipeline run is successful, you can visit to **Vertex AI** -> **Model**, check for `Evaluate` tab

<img
  src="https://github.com/mlops-research-best-practices/gcp_vertex_training_options/blob/feature-automl-text/automl/automl_text/artifacts/images/eval.PNG"
  alt="Model Evaluation Image"
  title="Model Evaluation"
  width="800"
  height="600"
/>

<img
  src="https://github.com/mlops-research-best-practices/gcp_vertex_training_options/blob/feature-automl-text/automl/automl_text/artifacts/images/roc.PNG"
  alt="ROC-AUC Image"
  title="ROC AUC Metrics"
  width="800"
  height="600"
/>


  4. You can also make prediction from GCP console in Deploy & Test tab or else from the REST API request.
  
<img
  src="https://github.com/mlops-research-best-practices/gcp_vertex_training_options/blob/feature-automl-text/automl/automl_text/artifacts/images/pred.PNG"
  alt="Model Prediction Image"
  title="Model Predictions"
  width="800"
  height="600"
/>


