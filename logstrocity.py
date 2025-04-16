import sys

from prefect import flow, get_run_logger


@flow
def logstrocity(how_many_logs: int = 10000):
    logger = get_run_logger()
    for i in range(how_many_logs):
        logger.info(f"Logging {i}")


if __name__ == "__main__":
    logstrocity(how_many_logs=int(sys.argv[1]) if len(sys.argv) > 1 else 10000)
