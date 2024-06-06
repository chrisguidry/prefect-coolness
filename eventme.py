import asyncio
import sys
from uuid import uuid4

from prefect.events import Event
from prefect.events.clients import PrefectCloudEventsClient


async def emit_events(n: int = sys.maxsize):
    async with PrefectCloudEventsClient(checkpoint_every=1) as client:
        for _ in range(n):
            event = Event(
                event="external.resource.pinged",
                resource={"prefect.resource.id": "my.external.resource"},
                id=uuid4(),
            )
            await client.emit(event)
            print(event.id)
            await asyncio.sleep(0.1)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else sys.maxsize
    asyncio.run(emit_events(n))
