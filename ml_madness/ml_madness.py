# Based on the tutorial at:
# https://cloud.google.com/vertex-ai/docs/tutorials/tabular-bq-prediction/create-notebook
import os
import sys
from subprocess import check_call
from typing import cast

import numpy as np
import pandas as pd
from google.cloud import aiplatform, bigquery, storage
from google.cloud.exceptions import NotFound

PROJECT_ID = "prefect-sbx-chrisguidry"
REGION = "us-central1"

BUCKET_NAME = "guidry-vertex-ai-tutorial"
BUCKET_URI = f"gs://{BUCKET_NAME}"


def prepare_environment() -> None:
    gs_client = storage.Client(project=PROJECT_ID)

    try:
        gs_client.get_bucket(BUCKET_NAME)
    except NotFound:
        gs_client.create_bucket(BUCKET_NAME, location=REGION)

    aiplatform.init(project=PROJECT_ID, location=REGION, staging_bucket=BUCKET_URI)


BQ_SOURCE = "bigquery-public-data.ml_datasets.penguins"

LABEL_COLUMN = "species"
NA_VALUES = ["NA", "."]

DATASET_NAME = "sample-penguins"


def create_dataset() -> aiplatform.TabularDataset:
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
    index_to_island = dict(enumerate(island_values))
    index_to_species = dict(enumerate(species_values))
    index_to_sex = dict(enumerate(sex_values))

    # View the mapped island, species, and sex data
    print(index_to_island)
    print(index_to_species)
    print(index_to_sex)

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


EPOCHS = 20
BATCH_SIZE = 10


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

    bq_client = bigquery.Client(project=PROJECT_ID)

    def download_table(bq_table_uri: str):
        prefix = "bq://"
        if bq_table_uri.startswith(prefix):
            bq_table_uri = bq_table_uri[len(prefix) :]

        # Download the BigQuery table as a dataframe
        # This requires the "BigQuery Read Session User" role on the custom training
        # service account.
        table = bq_client.get_table(bq_table_uri)
        return bq_client.list_rows(table).to_dataframe()

    df_train = download_table(training_data_uri)
    df_validation = download_table(validation_data_uri)
    download_table(test_data_uri)

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

    dataset_train = dataset_train.batch(BATCH_SIZE)
    dataset_validation = dataset_validation.batch(BATCH_SIZE)

    model.fit(dataset_train, epochs=EPOCHS, validation_data=dataset_validation)

    tf.saved_model.save(model, model_dir)


REGISTRY = f"{REGION}-docker.pkg.dev/{PROJECT_ID}/model-training"


def build_and_push_container() -> str:
    IMAGE_URI = f"{REGISTRY}/penguins:latest"
    check_call(
        ["gcloud", "auth", "configure-docker", f"{REGION}-docker.pkg.dev", "--quiet"]
    )
    check_call(["docker", "build", "-t", IMAGE_URI, "."])
    check_call(["docker", "push", IMAGE_URI])
    return IMAGE_URI


def create_training_job(container_uri: str) -> aiplatform.CustomContainerTrainingJob:
    job = aiplatform.CustomContainerTrainingJob(
        display_name="train-penguins",
        container_uri=container_uri,
        command=["python3", "ml_madness.py", "train"],
        model_serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/tf-cpu.2-12.py310:latest",
    )
    return job


if __name__ == "__main__":
    if sys.argv[1:] == ["train"]:
        # when invoked with "train", we're _inside_ Vertex AI running the training job
        train_model()
    else:
        # when invoked without parameters, we're running locally and orchestrating the
        # training and deployment
        prepare_environment()
        dataset = create_dataset()

        container_uri = build_and_push_container()

        job = create_training_job(container_uri)
        model = job.run(
            dataset=dataset,
            model_display_name="penguins-model",
            bigquery_destination=f"bq://{PROJECT_ID}",
        )
        print(model)
