import time

from prefect import flow, get_run_logger


@flow(timeout_seconds=1)
def show_timeouts():
    logger = get_run_logger()
    logger.info("I will execute")
    time.sleep(5)
    logger.info("I will not execute")

if __name__ == '__main__':
    show_timeouts()
