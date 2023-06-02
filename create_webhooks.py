import asyncio

from httpx import AsyncClient
from prefect.client.orchestration import get_client

WEBHOOKS = [
    {
        "name": "Static Demo",
        "description": "Produces a static event",
        "template": """
        {
            "event": "this.is.a.static.event",
            "resource": {
                "prefect.resource.id": "static-resource"
            }
        }
        """,
        "enabled": True,
    },
    {
        "name": "Dynamic Demo",
        "description": "Produces a dynamic event",
        "template": """
        {
            "event": "you.called.{{method}}",
            "resource": {
                "prefect.resource.id": "my.thing.{{ body.object_id }}",
                "prefect.resource.name": "{{ body.object_name }}
            }
        }
        """,
        "enabled": True,
    },
]


async def main():
    orion = get_client()
    client: AsyncClient = orion._client

    response = await client.post("/webhooks/filter", json={})
    response.raise_for_status()

    all_existing = response.json()

    for desired in WEBHOOKS:
        for existing in all_existing:
            if existing["name"] == desired["name"]:
                response = await client.put(
                    f"/webhooks/{existing['id']}",
                    json=desired,
                )
                response.raise_for_status()
                result = existing
                break
        else:
            response = await client.post(
                "/webhooks/",
                json=desired,
            )
            response.raise_for_status()
            result = response.json()

        print(
            f"{result['name']}: https://{client.base_url.host}/hooks/{result['slug']}"
        )


if __name__ == "__main__":
    asyncio.run(main())
