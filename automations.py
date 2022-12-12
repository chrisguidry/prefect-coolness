import asyncio
import time

from httpx import AsyncClient
from prefect import flow, get_run_logger
from prefect.client.orion import get_client


@flow
def stimulus():
    logger = get_run_logger()
    logger.info("A stimulating flow")
    time.sleep(30)


@flow
def response():
    logger = get_run_logger()
    logger.info("A responding flow")


AUTOMATION = {
    "name": "Demo",
    "description": "Demo",
    "trigger": {
        "after": ["prefect.flow-run.Running"],
        "expect": ["prefect.flow-run.*"],
        "for_each": ["prefect.resource.id"],
        "match_related": {
            "prefect.resource.role": "flow",
            "prefect.resource.id": "prefect.flow.a73a9e15-b230-4c0a-ad91-dc1dea6bd97e",
        },
        "posture": "Proactive",
        "threshold": 0,
        "within": 5,
    },
    "actions": [
        {
            "type": "run-deployment",
            "deployment_id": "03fe67f8-37eb-44f2-944b-40d30b527df1",
            "parameters": None,
        },
    ],
}


async def main():
    orion = get_client()
    client: AsyncClient = orion._client

    print("Removing previous automations...")
    response = await client.post("/automations/filter", json={})
    response.raise_for_status()

    for automation in response.json():
        if automation["name"] == AUTOMATION["name"]:
            print("Updating...")
            response = await client.put(
                f"/automations/{automation['id']}", json=AUTOMATION
            )
            response.raise_for_status()
            break
    else:
        print("Creating...")
        response = await client.post(
            "/automations/",
            json=AUTOMATION,
        )
        response.raise_for_status()


if __name__ == "__main__":
    asyncio.run(main())
