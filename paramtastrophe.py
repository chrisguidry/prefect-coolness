import asyncio
import json

from prefect import flow, get_run_logger


@flow
async def paramtastrophe(params):
    get_run_logger().info(f"size: {len(json.dumps(params))}")

if __name__ == "__main__":
    asyncio.run(paramtastrophe({'hello': 'world' * 1000}))
