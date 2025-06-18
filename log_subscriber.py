import pendulum
import rich.console
from prefect.cli import root
from prefect.cli._types import PrefectTyper
from prefect.logs.clients import get_logs_subscriber


def setup_console(app: PrefectTyper) -> rich.console.Console:
    console = rich.console.Console()
    setattr(app, "console", console)
    setattr(root.app, "console", console)
    return console


app = PrefectTyper(
    no_args_is_help=True,
    help=(
        """
A performance harness for benchmarking Event streaming subscribers
"""
    ),
)

console = setup_console(app)


@app.command()
async def subscribe():
    """Subscribes to the event stream of a workspace, printing each event"""
    async with get_logs_subscriber() as subscriber:
        async for log in subscriber:
            now = pendulum.now("UTC")
            console.print(
                str(log.id).partition("-")[0],
                f"{log.timestamp.isoformat()}",
                f" ({(log.timestamp - now).total_seconds():>6,.2f})",
                f"\\[[bold green]{log.message}[/]]",
                log.flow_run_id,
            )


if __name__ == "__main__":
    app()
