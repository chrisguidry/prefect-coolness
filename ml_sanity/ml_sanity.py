# Based on the tutorial at:
# https://cloud.google.com/vertex-ai/docs/tutorials/tabular-bq-prediction/create-notebook
import asyncio
import os
import sys
from subprocess import check_call
from typing import cast

import numpy as np
import pandas as pd
from google.cloud import aiplatform, bigquery, storage
from google.cloud.exceptions import NotFound
from prefect import flow, get_run_logger, task
from prefect.artifacts import create_table_artifact
from prefect.blocks.system import Secret

PROJECT_ID = "prefect-sbx-chrisguidry"
REGION = "us-central1"

BUCKET_NAME = "guidry-vertex-ai-tutorial"
BUCKET_URI = f"gs://{BUCKET_NAME}"


BQ_SOURCE = "bigquery-public-data.ml_datasets.penguins"

LABEL_COLUMN = "species"
NA_VALUES = ["NA", "."]

DATASET_NAME = "sample-penguins"


TRAINING_EPOCHS = 20
TRAINING_BATCH_SIZE = 10


REGISTRY = f"{REGION}-docker.pkg.dev/{PROJECT_ID}/model-training"


@task
def prepare_environment() -> None:
    gs_client = storage.Client(project=PROJECT_ID)

    try:
        gs_client.get_bucket(BUCKET_NAME)
    except NotFound:
        gs_client.create_bucket(BUCKET_NAME, location=REGION)

    aiplatform.init(project=PROJECT_ID, location=REGION, staging_bucket=BUCKET_URI)


@task
async def create_dataset() -> aiplatform.TabularDataset:
    bq_client = bigquery.Client(project=PROJECT_ID)

    # Download a table
    table = bq_client.get_table(BQ_SOURCE)
    df: pd.DataFrame = cast(pd.DataFrame, bq_client.list_rows(table).to_dataframe())

    # Drop unusable rows
    df = df.replace(to_replace=NA_VALUES, value=np.NaN).dropna()

    # Convert categorical columns to numeric
    df["island"], island_values = pd.factorize(df["island"])
    df["species"], species_values = pd.factorize(df["species"])
    df["sex"], sex_values = pd.factorize(df["sex"])

    # Split into a training and holdout dataset
    df_train = df.sample(frac=0.8, random_state=100)
    df[~df.index.isin(df_train.index)]

    # Map numeric values to string values
    index_to_island = [{"index": i, "label": v} for i, v in enumerate(island_values)]
    index_to_species = [{"index": i, "label": v} for i, v in enumerate(species_values)]
    index_to_sex = [{"index": i, "label": v} for i, v in enumerate(sex_values)]

    # View the mapped island, species, and sex data
    await create_table_artifact(index_to_island, "penguins--index-to-island")
    await create_table_artifact(index_to_species, "penguins--index-to-species")
    await create_table_artifact(index_to_sex, "penguins--index-to-sex")

    # Create a BigQuery dataset
    bq_dataset_id = f"{PROJECT_ID}.penguins"
    bq_dataset = bigquery.Dataset(bq_dataset_id)
    bq_client.create_dataset(bq_dataset, exists_ok=True)

    # Create a Vertex AI tabular dataset
    for dataset in aiplatform.TabularDataset.list():
        if dataset.display_name == DATASET_NAME:
            assert isinstance(dataset, aiplatform.TabularDataset)
            break
    else:
        dataset = aiplatform.TabularDataset.create_from_dataframe(
            df_source=df_train,
            staging_path=f"bq://{bq_dataset_id}.table-unique",
            display_name=DATASET_NAME,
        )

    return dataset


@task
def download_table(bq_table_uri: str) -> pd.DataFrame:
    bq_client = bigquery.Client(project=PROJECT_ID)

    prefix = "bq://"
    if bq_table_uri.startswith(prefix):
        bq_table_uri = bq_table_uri[len(prefix) :]

    # Download the BigQuery table as a dataframe
    # This requires the "BigQuery Read Session User" role on the custom training
    # service account.
    table = bq_client.get_table(bq_table_uri)
    return bq_client.list_rows(table).to_dataframe()


@flow
def train_model() -> None:
    import tensorflow as tf

    training_data_uri = os.getenv("AIP_TRAINING_DATA_URI")
    assert training_data_uri

    validation_data_uri = os.getenv("AIP_VALIDATION_DATA_URI")
    assert validation_data_uri

    test_data_uri = os.getenv("AIP_TEST_DATA_URI")
    assert test_data_uri

    model_dir = os.getenv("AIP_MODEL_DIR")
    assert model_dir

    df_train = download_table(training_data_uri)
    assert df_train is not None

    df_validation = download_table(validation_data_uri)
    assert df_validation is not None

    df_test = download_table(test_data_uri)
    assert df_test is not None

    def convert_dataframe_to_dataset(
        df_train: pd.DataFrame,
        df_validation: pd.DataFrame,
    ) -> tuple[tf.data.Dataset, tf.data.Dataset]:
        df_train_x, df_train_y = df_train, df_train.pop(LABEL_COLUMN)
        df_validation_x, df_validation_y = df_validation, df_validation.pop(
            LABEL_COLUMN
        )

        y_train = tf.convert_to_tensor(np.asarray(df_train_y).astype("float32"))
        y_validation = tf.convert_to_tensor(
            np.asarray(df_validation_y).astype("float32")
        )

        # Convert to numpy representation
        x_train = tf.convert_to_tensor(np.asarray(df_train_x).astype("float32"))
        x_test = tf.convert_to_tensor(np.asarray(df_validation_x).astype("float32"))

        # Convert to one-hot representation
        num_species = len(df_train_y.unique())
        y_train = tf.keras.utils.to_categorical(y_train, num_classes=num_species)
        y_validation = tf.keras.utils.to_categorical(
            y_validation, num_classes=num_species
        )

        dataset_train = tf.data.Dataset.from_tensor_slices((x_train, y_train))
        dataset_validation = tf.data.Dataset.from_tensor_slices((x_test, y_validation))
        return (dataset_train, dataset_validation)

    dataset_train, dataset_validation = convert_dataframe_to_dataset(
        df_train, df_validation
    )

    dataset_train = cast(tf.data.Dataset, dataset_train.shuffle(len(df_train)))

    def create_model(num_features: int) -> tf.keras.Sequential:
        Dense = tf.keras.layers.Dense
        model = tf.keras.Sequential(
            [
                Dense(
                    100,
                    activation=tf.nn.relu,
                    kernel_initializer="uniform",
                    input_dim=num_features,
                ),
                Dense(75, activation=tf.nn.relu),
                Dense(50, activation=tf.nn.relu),
                Dense(25, activation=tf.nn.relu),
                Dense(3, activation=tf.nn.softmax),
            ]
        )

        optimizer = tf.keras.optimizers.RMSprop(lr=0.001)
        model.compile(
            loss="categorical_crossentropy",
            metrics=["accuracy"],
            optimizer=optimizer,
        )

        return model

    model = create_model(num_features=dataset_train._flat_shapes[0].dims[0].value)

    dataset_train = dataset_train.batch(TRAINING_BATCH_SIZE)
    dataset_validation = dataset_validation.batch(TRAINING_BATCH_SIZE)

    model.fit(dataset_train, epochs=TRAINING_EPOCHS, validation_data=dataset_validation)

    tf.saved_model.save(model, model_dir)


@task
def build_and_push_container() -> str:
    IMAGE_URI = f"{REGISTRY}/penguins-sanity:latest"
    check_call(
        ["gcloud", "auth", "configure-docker", f"{REGION}-docker.pkg.dev", "--quiet"]
    )
    check_call(["docker", "build", "-t", IMAGE_URI, "."])
    check_call(["docker", "push", IMAGE_URI])
    return IMAGE_URI


@task
def create_training_job(container_uri: str) -> aiplatform.CustomContainerTrainingJob:
    job = aiplatform.CustomContainerTrainingJob(
        display_name="train-penguins",
        container_uri=container_uri,
        command=["python3", "ml_sanity.py", "train"],
        model_serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/tf-cpu.2-12.py310:latest",
    )
    return job


@flow
async def submit_training() -> None:
    prepare_environment()
    dataset = await create_dataset()

    container_uri = build_and_push_container()

    j = aiplatform.CustomJob()
    j.run()
    job = create_training_job(container_uri)

    api_key: Secret = await Secret.load("coolness-api-key")
    api_url: Secret = await Secret.load("coolness-api-url")

    model = job.run(
        dataset=dataset,
        model_display_name="penguins-model",
        bigquery_destination=f"bq://{PROJECT_ID}",
        environment_variables={
            "PREFECT_API_URL": api_url.get(),
            "PREFECT_API_KEY": api_key.get(),
        },
    )
    assert model

    get_run_logger().info("Model: %s (%s)", model.resource_name, model.uri)


if __name__ == "__main__":
    if sys.argv[1:] == ["train"]:
        # when invoked with "train", we're _inside_ Vertex AI running the training job
        train_model()
    else:
        # when invoked without parameters, we're running locally and orchestrating the
        # training and deployment
        asyncio.run(submit_training())
