from asyncio import get_event_loop

from prefect import flow, get_run_logger, task


@flow
async def logtastrophe():
    logger = get_run_logger()
    logger.info("Y'all ready for this?")
    logger.info("Stop me if you've heard it...")
    await bottles.map(range(5, 1, -1))
    logger.info("I guess you were")


@task
async def bottles(n: int):
    logger = get_run_logger()
    logger.info(f"{n} bottles of beer on the wall")
    logger.info(f"{n} bottles of beer!")
    logger.info(f"take one down, pass it around, {n-1} bottles of beer on the wall")


if __name__ == "__main__":
    get_event_loop().run_until_complete(logtastrophe())
