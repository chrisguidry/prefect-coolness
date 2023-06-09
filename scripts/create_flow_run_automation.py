import asyncio

from httpx import AsyncClient
from prefect.client.orion import get_client

AUTOMATION = {
    "name": "Demo",
    "description": "Demo",
    "trigger": {
        "expect": ["prefect.flow-run.Completed"],
        "match_related": {
            "prefect.resource.role": "flow",
            "prefect.name": "response",
        },
        "posture": "Reactive",
        "threshold": 1,
        "within": 10,
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
