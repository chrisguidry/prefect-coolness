import asyncio
from datetime import datetime, timedelta

from prefect import flow
from prefect.states import Paused


@flow
async def inspiring_joke():
    print(f"Pausing flow run until {datetime.now() + timedelta(seconds=10)}...")
    return Paused(timeout_seconds=10, message="Chill.")


if __name__ == "__main__":
    asyncio.run(inspiring_joke())
