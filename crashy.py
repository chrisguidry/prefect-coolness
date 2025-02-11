import os

from prefect import flow


@flow
def crashy():
    print('nah chief')


if os.environ('PREFECT__FLOW_RUN_ID'):
    raise Exception("Why does this always happen to me?")
