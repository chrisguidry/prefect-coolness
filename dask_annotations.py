#!/usr/bin/env python3
from time import sleep

import dask
from prefect import flow, task
from prefect_dask.task_runners import DaskTaskRunner


@task
def show_number(x: int):
    print(x)


@task
def say_hello():
    print("Hello!")
    sleep(4)


@flow(task_runner=DaskTaskRunner(address="tcp://10.0.0.196:8786"))
def example_flow(x):
    show_number.submit(x)
    with dask.annotate(resources={"annotation": 1}):
        say_hello.submit()


if __name__ == "__main__":
    for i in range(6):
        example_flow(i)
