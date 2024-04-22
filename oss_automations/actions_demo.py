import asyncio
import random
import sys

from prefect import flow, get_run_logger
from prefect.events import DeploymentEventTrigger, Event, Posture
from prefect.events.clients import PrefectEventsClient


@flow
def add_some_stuff(x: int, y: int):
    logger = get_run_logger()

    logger.info(f"Adding {x} and {y} gives you {x + y}")


async def serve_deployment():
    try:
        await add_some_stuff.serve(
            name="actions-demo",
            triggers=[
                DeploymentEventTrigger(
                    expect={"a.fine.event"},
                    posture=Posture.Reactive,
                    threshold=1,
                    parameters={
                        "x": "{{ event.payload.x }}",
                        "y": "{{ event.payload.y }}",
                    },
                )
            ],
        )
    except asyncio.CancelledError:
        return
    except Exception as e:
        print(f"Deployment failed: {e}")
        sys.exit(1)


async def main():
    deployment_task = asyncio.create_task(serve_deployment())

    print("waiting a bit to make sure the deployment is serving...")
    await asyncio.sleep(5)

    print("emitting events...")
    async with PrefectEventsClient() as events:
        for i in range(3):
            await events.emit(
                Event(
                    event="a.fine.event",
                    resource={
                        "prefect.resource.id": "1234",
                        "prefect.resource.name": "A Resource",
                    },
                    payload={
                        "x": random.randint(42, 420),
                        "y": random.randint(42, 420),
                    },
                )
            )

    print("waiting a while for the deployments to run...")
    await asyncio.sleep(60)

    deployment_task.cancel()
    await deployment_task


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
