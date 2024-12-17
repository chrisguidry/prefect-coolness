import asyncio
from uuid import UUID

from prefect import get_client


async def rate_limiting_abuser(queue: asyncio.Queue[UUID]):
    id = UUID("7d0aa6d9-2e43-43b2-b987-7bc533d84c38")
    while True:
        await queue.put(id)


async def consumer(queue: asyncio.Queue[UUID]):
    c = get_client()
    while True:
        id = await queue.get()
        try:
            result = await c.read_flow_run(id)
            print("got result", result.name)
        except Exception as e:
            print("got exception", str(e))


async def main():
    queue = asyncio.Queue(maxsize=10000)
    await asyncio.gather(
        rate_limiting_abuser(queue), *[consumer(queue) for _ in range(100)]
    )


if __name__ == "__main__":
    asyncio.run(main())
