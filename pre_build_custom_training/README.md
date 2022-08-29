# Custom Training with pre-built containers on Vertex AI


### Code Repository
- Under `pre_build_custom_training` directory we have a sub directory named `traincontainer`, `pipeline.py`, `pipeline_config.ini` files. 
- `pipeline_config.ini` is a config file which contains all the parameter inputs required for the pipeline to run `pipeline.py`
- `pipeline.py`: This file contains googles prebuilt operators such as TabularDatasetCreateOp, CustomContainerTrainingJobRunOp, ModelBatchPredictOp responsible for creating Vertex Dataset, train a ML model and perform the Batch Prediction respectively.
- In `traincontainer` direcotry, we have a sub directory called `trainer` which contains the training script `train.py` and `config.py`, input parameters required for `train.py`. 
- In the same directory, we have `Dockerfile`, this is the Docker image file which will be used to create the docker container. Here we copy the scripts, give an entry point to train.py, so it could trigger the script inside the container.

### Usage Example

1. Create Docker container and push to GCR using the following commands into the cloud shell
```
    * gcloud auth activate-service-account SERVICE_ACCOUNT@DOMAIN.COM --key-file=/path/key.json
    * gcloud auth configure-docker
    * PROJECT_ID=<your-project-id>
    * IMAGE_URI="gcr.io/$PROJECT_ID/scikit:v2"
    * docker build ./ -t $IMAGE_URI
    * docker push $IMAGE_URI
```
2. Now, run the docker container `docker run $IMAGE_URI`, because the script is already copied to docker. Please, check Dockerfile for futher details.