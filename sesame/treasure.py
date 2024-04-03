#!/usr/bin/env python
import asyncio
import random
from typing import Any

from prefect import flow, get_client

JEWELS = "🔹🔸🔶🔷💠♦️♢💎💍👑🪙"


async def create_or_replace_automation(automation: dict[str, Any]) -> dict[str, Any]:
    async with get_client() as prefect:
        # Clean up any older automations with the same name prefix
        response = await prefect._client.post("/automations/filter")
        response.raise_for_status()
        for existing in response.json():
            if str(existing["name"]).startswith(automation["name"]):
                print(
                    f'Deleting old automation {existing["name"]} ({existing["id"]})',
                )
                await prefect._client.delete(f"/automations/{existing['id']}")

        response = await prefect._client.post("/automations", json=automation)
        response.raise_for_status()

        automation = response.json()
        print(f'Created automation {automation["name"]} ({automation["id"]})')

        print("Waiting 5s for the automation to be loaded the triggers services")
        await asyncio.sleep(5)

        return automation

async def magical_lock():
    event_template = {
        "type": "event",
        "posture": "Reactive",
        "expect": ["speak"],
        "threshold": 1,
        "within": 0,
    }
    await create_or_replace_automation(
        {
            "name": "magic-words",
            "trigger": {
                "type": "sequence",
                "within": 60,
                "triggers": [
                    {
                        "type": "compound",
                        "require": "any",
                        "within": 20,
                        "triggers": [
                            {
                                **event_template,
                                "match": {'word': 'abracadabra'},
                            },
                            {
                                **event_template,
                                "match": {'word': 'abbracaddabbra'},
                            }
                        ]
                    },
                    {
                        "type": "compound",
                        "require": 2,
                        "within": 20,
                        "triggers": [
                            {
                                **event_template,
                                "match": {'word': 'hocus'},
                            },
                            {
                                **event_template,
                                "match": {'word': 'pocus'},
                            },
                            {
                                **event_template,
                                "match": {'word': 'focus'},
                            }
                        ]
                    },
                    {
                        "type": "sequence",
                        "within": 20,
                        "triggers": [
                            {
                                **event_template,
                                "match": {'word': 'open'},
                            },
                            {
                                **event_template,
                                "match": {'word': 'sesame'},
                            }
                        ]
                    }
                ],
            },
            "actions": [
                {
                    "type": "run-deployment",
                    "deployment_id": "98220084-9ba5-4f5d-a2b4-ae198b8934f3",
                }
            ],
        }
    )

@flow
def treasure():
    print("\n" * 5)
    print("The chest opens to reveal:\n\n")
    for i in range(random.randrange(500, 800)):
        print(random.choice(JEWELS), end="")
    print("\n" * 5)

async def main():
    await magical_lock()
    await treasure.serve("chest")

if __name__ == '__main__':
    asyncio.run(main())
