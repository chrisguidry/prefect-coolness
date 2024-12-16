import sys

from prefect import flow, task
from prefect.task_runners import ConcurrentTaskRunner


@task
def map_me(x):
    return x


@flow(task_runner=ConcurrentTaskRunner())
def map_flow(N):
    return sum(r.result() for r in map_me.map([i for i in range(N)]))


if __name__ == "__main__":
    count = 10
    if sys.argv[1:]:
        count = int(sys.argv[1])

    print(map_flow(count))
