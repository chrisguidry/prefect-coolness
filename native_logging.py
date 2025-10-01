import logging

from prefect import flow, task

logger = logging.getLogger("native_logger")


@flow
def native_logging_flow():
    logger.info("Hello, from the %s", "flow")
    native_logging_task()


@task
def native_logging_task():
    logger.info("Hello, from the %s", "task")


if __name__ == "__main__":
    native_logging_flow()
