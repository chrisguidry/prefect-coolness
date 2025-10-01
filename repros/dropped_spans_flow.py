import asyncio
from prefect import flow, task, pause_flow_run, get_run_logger

@task
def simple_task(step: int):
    logger = get_run_logger()
    logger.info(f"Executing step {step}")
    return f"step_{step}_result"


@flow(name="Dropped Spans Flow")
async def dropped_spans_flow():
    logger = get_run_logger()

    # Execute first two tasks
    simple_task(1)
    simple_task(2)

    # Pause for user input
    await pause_flow_run()

    # Execute remaining tasks
    simple_task(3)
    simple_task(4)

    logger.info("Flow completed")


if __name__ == "__main__":
    asyncio.run(dropped_spans_flow())