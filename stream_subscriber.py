from uuid import UUID

import pendulum
import rich.console
from prefect.cli import root
from prefect.cli._types import PrefectTyper
from prefect.events.clients import PrefectCloudEventSubscriber
from prefect.events.filters import EventFilter, EventNameFilter


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
async def subscribe(
    account: UUID,
    workspace: UUID,
    token: str,
):
    """Subscribes to the event stream of a workspace, printing each event"""

    api_url = (
        f"https://api.stg.prefect.dev/api/accounts/{account}/workspaces/{workspace}"
    )

    filter = EventFilter(event=EventNameFilter(prefix=["prefect.log.write"]))

    async with PrefectCloudEventSubscriber(api_url, token, filter) as subscriber:
        async for event in subscriber:
            now = pendulum.now("UTC")
            console.print(
                str(event.id).partition("-")[0],
                f"occurred={(event.occurred - now).total_seconds():>7,.2f}",
                f"\\[[bold green]{event.event}[/]]",
                event.resource.id,
            )


if __name__ == "__main__":
    app()
