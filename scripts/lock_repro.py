import asyncio

from prefect.client.orchestration import get_client
from prefect.engine import propose_state
from prefect.states import Pending

DEPLOYMENT_ID = "84699c96-0cee-4f7f-94a0-e4c17cc7bd11"


async def main():
    async with get_client() as client:
        # Schedule a flow run
        flow_run = await client.create_flow_run_from_deployment(DEPLOYMENT_ID)
        print(f"Created flow run {flow_run.id!r} ...")

        # Two processes try to update the flow run to PENDING at once.
        # This should raise an ABORT signal.
        results = await asyncio.gather(
            propose_state(
                client=client,
                state=Pending(),
                force=False,
                flow_run_id=flow_run.id,
            ),
            propose_state(
                client=client,
                state=Pending(),
                force=False,
                flow_run_id=flow_run.id,
            ),
        )

    print(f"Result of propose state calls:")
    for state_result in results:
        print(state_result)

    return results


if __name__ == "__main__":
    asyncio.run(main())
