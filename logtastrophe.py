import random

from prefect import flow, get_run_logger, task


@flow
def logtastrophe():
    logger = get_run_logger()
    logger.info("Y'all ready for this?")
    logger.info("Stop me if you've heard it...")
    futures = bottles.map(range(99, 1, -1))
    for future in futures:
        future.wait()
    logger.info("I guess you were")


@task
def bottles(n: int):
    logger = get_run_logger()
    logger.info(f"{n} bottles of beer on the wall")
    logger.info(f"{n} bottles of beer!")
    logger.info(f"take one down, pass it around, {n-1} bottles of beer on the wall")
    if random.random() < 0.10:
        raise ValueError("oops, I dropped it")


if __name__ == "__main__":
    logtastrophe()
