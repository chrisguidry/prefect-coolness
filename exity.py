import asyncio

from prefect import flow


@flow
async def exity():
    import sys
    sys.exit(42)


if __name__ == "__main__":
    asyncio.run(exity())
