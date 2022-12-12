from prefect import flow, task
from prefect.task_runners import ConcurrentTaskRunner


@task
def map_me(x):
    return x


@flow(task_runner=ConcurrentTaskRunner())
def map_flow(N):
    return map_me.map([i for i in range(N)])


if __name__ == "__main__":
    map_flow(100)
