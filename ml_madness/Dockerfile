FROM us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-12.py310:latest

RUN pip3 install \
    numpy \
    pandas \
    db-dtypes \
    google-cloud-aiplatform \
    google-cloud-bigquery \
    google-cloud-storage \
    tensorflow

COPY ml_madness.py /ml_madness.py
