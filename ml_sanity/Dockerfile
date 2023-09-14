FROM us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-12.py310:latest

RUN apt update && DEBIAN_FRONTEND=noninteractive apt install tzdata

RUN pip3 install \
    numpy \
    pandas \
    db-dtypes \
    google-cloud-aiplatform \
    google-cloud-bigquery \
    google-cloud-storage \
    tensorflow \
    prefect

COPY ml_sanity.py /ml_sanity.py
