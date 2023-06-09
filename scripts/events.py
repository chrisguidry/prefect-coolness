import asyncio

from prefect.events import Event
from prefect.events.clients import PrefectCloudEventsClient

PREFECT_API_URL = "https://api.stg.prefect.dev/api/accounts/257bc8f1-6997-4088-bb5e-6ec1cfbe28a9/workspaces/948362f2-21e1-4794-b0b0-651f5bc68ace"
PREFECT_API_KEY = "pnu_axYBk7lyRYNtztD4BjH6k1FMPYtG0Y0FMmU7"


async def main():
    async with PrefectCloudEventsClient(PREFECT_API_URL, PREFECT_API_KEY) as client:
        await client.emit(
            Event(
                event="guidry.did.things",
                resource={"prefect.resource.id": "guidrytime"},
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
