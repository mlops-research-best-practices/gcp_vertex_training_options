
# Vertex AutoML image classification

This is an example code to train a image classification model using AutoML on vertex AI platform. This example contains a repo
with two folder "artifacts" and "config" and two python script "pipeline.py" and "pipeline_run.py".

pipeline.py contains all the pipeline components, whereas pipeline_run.py is used to compile the pipeline and execute it on vertex.

artifacts folder is used to store the json file created by the pipeline execution. This file can be used to recreate the same pipeline
repeatedly.

config folder contains config/project_config.py which holds the static input parameters like project id, region, pipeline root etc... 
These are required to run the pipeline.



### Execution
You can adjust the config parameters in config/project_config.py and execute pipeline_run.py script to invoke the pipeline. Once the pipeline is 
triggered, you can see it in gcp console. Go to vertex AI, and click on the pipeline tab from the left side bar. You will see a pipeline is 
running with the display name you have provided in the config. The pipeline will look something like this - 
 








## Contributing

Contributions are always welcome!

