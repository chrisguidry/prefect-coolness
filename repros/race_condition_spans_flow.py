import asyncio
import time
from prefect import flow, task, get_run_logger

@task
def simple_task(step: int):
    logger = get_run_logger()
    logger.info(f"Executing step {step}")
    return f"step_{step}_result"


@flow(name="Race Condition Spans Flow")
async def race_condition_spans_flow():
    logger = get_run_logger()

    # Execute first two tasks
    simple_task(1)
    simple_task(2)

    # Small sleep to simulate some work
    await asyncio.sleep(1)

    # Execute remaining tasks close to flow completion
    simple_task(3)
    simple_task(4)

    logger.info("Flow completed")
    # Exit immediately after tasks to maximize race condition potential


if __name__ == "__main__":
    asyncio.run(race_condition_spans_flow())