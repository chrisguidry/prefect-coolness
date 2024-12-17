from prefect import flow, task
from prefect_dask import DaskTaskRunner


@flow(task_runner=DaskTaskRunner)
def outer_flow():
    a = task_one.submit()
    b = task_two.submit()
    c = task_three.submit(a, b)
    d = flow_two(c)
    return d


@task
def task_one() -> int:
    return 24


@task
def task_two() -> int:
    return 42


@task
def task_three(a: int, b: int) -> int:
    return a + b


@flow
def flow_two(c: int) -> int:
    return c + 1


if __name__ == "__main__":
    print(outer_flow())
