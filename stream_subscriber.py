import pendulum
import rich.console
from prefect.cli import root
from prefect.cli._types import PrefectTyper
from prefect.events.clients import get_events_subscriber
from prefect.utilities.services import start_client_metrics_server


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
    async with get_events_subscriber() as subscriber:
        async for event in subscriber:
            now = pendulum.now("UTC")
            console.print(
                str(event.id).partition("-")[0],
                f"{event.occurred.isoformat()}",
                f" ({(event.occurred - now).total_seconds():>6,.2f})",
                f"\\[[bold green]{event.event}[/]]",
                event.resource.id,
            )


if __name__ == "__main__":
    start_client_metrics_server()
    app()
