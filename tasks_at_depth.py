from prefect import flow, get_run_logger, task


@flow
def shallow():
    get_run_logger().info("shallow")
    for i in range(5):
        deep(i)


@task
def deep(i: int):
    get_run_logger().info("deep at depth %s", i)
    for j in range(5):
        abyssal(i, j)


@task
def abyssal(i: int, j: int):
    get_run_logger().info("abyssal at depth %s %s", i, j)


if __name__ == "__main__":
    shallow()