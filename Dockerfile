FROM prefecthq/prefect:2.13.1-python3.11-kubernetes

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir -p /opt/prefect/prefect-coolness
COPY . /opt/prefect/prefect-coolness
