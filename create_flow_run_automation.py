import asyncio

from httpx import AsyncClient
from prefect.client.orion import get_client

AUTOMATION = {
    "name": "Demo",
    "description": "Logs Flow Run State Changes",
    "trigger": {
        "event": "prefect.flow-run.*",
        "posture": "Reactive",
        "threshold": 1,
        "within": 0,
    },
    "actions": [
        {"type": "log-message", "message": "the first one"},
        {"type": "log-message", "message": "the second one"},
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
