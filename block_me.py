import asyncio

from prefect import flow, task
from prefect.blocks.webhook import Webhook


@flow
async def block_me():
    block = Webhook(method="GET", url="https://example.com/")
    await block.save("my-webhook", overwrite=True)

    block = await Webhook.load("my-webhook")

    await hook_it()


@task
async def hook_it():
    block = Webhook(method="GET", url="https://example.com/")
    await block.save("my-webhook", overwrite=True)

    block = await Webhook.load("my-webhook")


if __name__ == "__main__":
    asyncio.run(block_me())
