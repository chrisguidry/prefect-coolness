"""
https://github.com/PrefectHQ/prefect/issues/11456
"""

from prefect import flow, task


@task
def task_one():
    return 1


@flow
def my_sub_flow():
    pass


@flow
def my_flow():
    one1 = task_one.submit()
    flow1 = my_sub_flow(wait_for=[one1])
    one2 = task_one.submit()
    flow2 = my_sub_flow(wait_for=[flow1])
    flow3 = my_sub_flow(wait_for=[flow2, one2])


if __name__ == "__main__":
    my_flow()
