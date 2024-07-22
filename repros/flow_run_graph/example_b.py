"""
https://github.com/PrefectHQ/prefect/issues/11456
"""

from prefect import flow, task
from prefect.task_runners import SequentialTaskRunner


@flow
def upstream_flow():
    @task
    def upstream_flow_task():
        print("upstream flow")

    upstream_flow_task()


@flow
def downstream_flow():
    @task
    def downstream_flow_task():
        print("downstream flow")

    downstream_flow_task()


@task
def upstream_task():
    print("upstream task")


@task
def downstream_task():
    print("downstream task")


@flow(task_runner=SequentialTaskRunner())
def main_flow():
    uf_future = upstream_flow(return_state=True)
    ut_future = upstream_task(return_state=True)

    _test = downstream_flow(wait_for=[uf_future, ut_future])

    downstream_task(wait_for=[_test])


if __name__ == "__main__":
    main_flow()
