import argparse
import asyncio
import sys

from prefect import flow, task


@task
async def sleep_task():
    await asyncio.sleep(60)


@flow
async def sleep_flow():
    await sleep_task()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "N", type=int, nargs="?", default=1, help="Number of flows to run in parallel"
    )
    parser.add_argument(
        "--actually-run",
        action="store_true",
        help="Actually run the flow in this process",
    )
    args = parser.parse_args()

    if args.actually_run:
        # Run the flow in this process
        asyncio.run(sleep_flow())
    else:
        # Create subprocesses that run the flow
        async def run_flows():
            # Create subprocess for each flow
            processes = []
            for _ in range(args.N):
                proc = await asyncio.create_subprocess_exec(
                    sys.executable, __file__, "--actually-run"
                )
                processes.append(proc)

            # Wait for all subprocesses to complete
            await asyncio.gather(*[proc.wait() for proc in processes])

        asyncio.run(run_flows())
