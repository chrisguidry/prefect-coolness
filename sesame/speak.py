#!/usr/bin/env python
import asyncio

from prefect.events import Event
from prefect.events.clients import PrefectCloudEventsClient


async def speak(word: str):
    async with PrefectCloudEventsClient() as client:
        await client.emit(
            Event(
                event="speak",
                resource={
                    "prefect.resource.id": f"word.{word}",
                    "word": word
                },
            )
        )

async def main():
    nth = "first"
    try:
        while True:
            word = input(f"Speak thy {nth} word: ")
            nth = "next"
            if word == "give up":
                return
            await speak(word)
    except (KeyboardInterrupt, EOFError):
        print()

if __name__ == '__main__':
    asyncio.run(main())
