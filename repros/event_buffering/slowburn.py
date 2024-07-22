import asyncio
from uuid import UUID, uuid4

import pendulum
from prefect.events import Event, Resource, get_events_client


async def main():
    async with get_events_client(checkpoint_every=1) as events:
        prior: UUID | None = None
        for i in range(1_000_000):
            next = uuid4()
            await events.emit(
                Event(
                    occurred=pendulum.now(),
                    event="slow.burn",
                    resource=Resource({"prefect.resource.id": f"slow.burn.{i}"}),
                    id=next,
                    follows=prior,
                )
            )
            prior = next
            try:
                instruction = input(
                    f"Emitted {i+1} events, with last id of {next}.  Enter to keep going, Ctrl-D or 'quit' to cleanly exit."
                )
            except (KeyboardInterrupt, EOFError):
                instruction = "quit"

            if instruction.lower().startswith("q"):
                break


if __name__ == "__main__":
    asyncio.run(main())
