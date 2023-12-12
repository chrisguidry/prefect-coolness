import asyncio
from uuid import uuid4

from prefect.events.clients import PrefectCloudEventsClient
from prefect.events.schemas import Event


async def emit_three_events():
    async with PrefectCloudEventsClient() as client:
        for _ in range(3):
            event = Event(
                event="external.resource.pinged",
                resource={"prefect.resource.id": "my.external.resource"},
                id=uuid4(),
            )
            await client.emit(event)
            print(event.id)


if __name__ == "__main__":
    asyncio.run(emit_three_events())
