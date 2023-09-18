import math
import random
import sys
import time
from datetime import timedelta

from prefect import flow, get_run_logger


@flow
def nightnight(duration: timedelta) -> None:
    """
    A flow that sleeps for the specified duration.
    """
    logger = get_run_logger()
    start = int(time.time())
    end = start + int(duration.total_seconds())
    logger.info(f"Yawn, it's time to snooze for {duration.total_seconds()} seconds...")
    number_of_snores = 10 * math.log(duration.total_seconds(), 10)
    snore_mean = min(max(duration.total_seconds() / number_of_snores, 1), 15)
    while time.time() < end:
        snore_time = snore_mean * random.paretovariate(1.16)
        snore_time = int(min(snore_time, max(end - time.time(), 1)))
        logger.info(f"Z{'z' * (snore_time - 1)}...")
        time.sleep(snore_time)


if __name__ == "__main__":
    try:
        duration = timedelta(seconds=int(sys.argv[1]))
    except (ValueError, IndexError):
        duration = timedelta(seconds=60)
    nightnight(duration)
