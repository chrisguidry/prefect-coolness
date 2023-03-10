import asyncio
import random

from prefect import flow, get_run_logger, task


@flow
async def logtastrophe():
    logger = get_run_logger()
    logger.info("Y'all ready for this?")
    logger.info("Stop me if you've heard it...")
    await bottles.map(range(20, 1, -1))
    logger.info("I guess you were")


@task
async def bottles(n: int):
    logger = get_run_logger()
    logger.info(f"{n} bottles of beer on the wall")
    logger.info(f"{n} bottles of beer!")
    logger.info(f"take one down, pass it around, {n-1} bottles of beer on the wall")
    if random.random() < 0.01:
        raise ValueError("oops, I dropped it")


if __name__ == "__main__":
    asyncio.run(logtastrophe())
