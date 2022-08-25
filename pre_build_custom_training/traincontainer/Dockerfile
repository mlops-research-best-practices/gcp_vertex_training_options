FROM gcr.io/deeplearning-platform-release/sklearn-cpu.0-23

# Copies the trainer code to the docker image.
COPY trainer /trainer

WORKDIR /trainer

RUN pip install sklearn google-cloud-bigquery joblib pandas google-cloud-storage gcsfs

# Sets up the entry point to invoke the trainer.
ENTRYPOINT ["python", "-m", "train"]