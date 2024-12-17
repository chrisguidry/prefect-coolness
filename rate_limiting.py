import asyncio
from uuid import UUID

from prefect import flow, get_client


@flow
async def rate_limited_flow():
    started_event = asyncio.Event()
    finished_event = asyncio.Event()

    async def lotta_requests():
        c = get_client()
        started_event.set()

        errors = 0
        for future in asyncio.as_completed(
            [
                c.read_flow_run(UUID("7d0aa6d9-2e43-43b2-b987-7bc533d84c38"))
                for _ in range(1000)
            ]
        ):
            try:
                result = await future
                print("got result", result.name)
            except asyncio.CancelledError:
                print("got cancelled")
                return
            except Exception as e:
                print("got exception", str(e))
                errors += 1
                if errors > 20:
                    finished_event.set()
                    return

    task = asyncio.create_task(lotta_requests())
    await started_event.wait()
    await finished_event.wait()
    try:
        task.cancel()
        await task
    except asyncio.CancelledError:
        pass
    return


if __name__ == "__main__":
    asyncio.run(rate_limited_flow())
