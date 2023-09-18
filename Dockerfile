FROM prefecthq/prefect:2.13.1-python3.11-kubernetes

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
