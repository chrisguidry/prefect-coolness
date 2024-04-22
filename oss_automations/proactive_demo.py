import asyncio

from httpx import AsyncClient
from prefect.client.orchestration import get_client

AUTOMATION = {
    "name": "Demo",
    "description": "Demo",
    "trigger": {
        "expect": ["anything"],
        "posture": "Proactive",
        "threshold": 1,
        "within": 10,
    },
    "actions": [
        {
            "type": "do-nothing"
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
