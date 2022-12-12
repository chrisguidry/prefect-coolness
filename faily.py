import asyncio

from prefect import flow


@flow
async def faily():
    raise Exception("Why does this always happen to me?")


if __name__ == "__main__":
    asyncio.run(faily())
