# Google Cloud's Machine Learning Training Options

1. automl
    - In this directory, there are three different use cases that are covered namely, text, image & tabular data.
    - [Image classification](https://github.com/mlops-research-best-practices/gcp_vertex_training_options/tree/main/automl/automl_image_classification) use case takes flower dataset for demonstrating auto ML for image data
    - [Text classification](https://github.com/mlops-research-best-practices/gcp_vertex_training_options/tree/main/automl/automl_text) study uses happiness dataset to show case auto ML for text data 
    - chicago taxi dataset is used for demonstrating auto ML for [tabular](https://github.com/mlops-research-best-practices/gcp_vertex_training_options/tree/main/automl/automl_tabular) data

2. bqml
    - In this directory, there are total six different uses cases which demonstrate the usage of bigquery ML in various scenarios.
    - Three uses cases for BigQuery [AutoML](https://github.com/mlops-research-best-practices/gcp_vertex_training_options/tree/main/bqml/bq_kfp_automl), [Classification](https://github.com/mlops-research-best-practices/gcp_vertex_training_options/tree/main/bqml/bq_kfp_classification) and [Regression](https://github.com/mlops-research-best-practices/gcp_vertex_training_options/tree/main/bqml/bq_kfp_regression) are show cased using Vertex pipelines and google's newly launch BigQuery Operators.
    - Remaining three use cases are demonstarted using Google Cloud SDK and BigQuery SDK. This uses cases are [Deep Neural Network](https://github.com/mlops-research-best-practices/gcp_vertex_training_options/tree/main/bqml/bq_regression_dnn) for Regression, [Boosted Tree](https://github.com/mlops-research-best-practices/gcp_vertex_training_options/tree/main/bqml/bq_xgboost) for Classification and [Time Series](https://github.com/mlops-research-best-practices/gcp_vertex_training_options/tree/main/bqml/bq_timeseries).

3. [full custom training](https://github.com/mlops-research-best-practices/gcp_vertex_training_options/tree/main/full_custom_training)
    - Perform custom training on Vertex AI to run your own ML training code in the cloud.

4. [pre-built custom training](https://github.com/mlops-research-best-practices/gcp_vertex_training_options/tree/main/pre_build_custom_training)
    - Vertex AI provides Docker container images that you run as pre-built containers for custom training. These containers include common dependencies that you might want to use in training code.