from uuid import UUID

import orjson
import pendulum
import rich.console
from websockets.client import connect
from websockets.exceptions import ConnectionClosedError

from prefect.cli import root
from prefect.cli._types import PrefectTyper
from prefect.events.schemas import Event


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

    api_root = f"api/accounts/{account}/workspaces/{workspace}"
    socket_url = f"wss://api.stg.prefect.dev/{api_root}/events/out"
    console.print(socket_url)

    already_seen: set[UUID] = set()

    while True:
        async with connect(
            socket_url, subprotocols=["prefect"], open_timeout=None
        ) as websocket:
            await websocket.send(
                orjson.dumps({"type": "auth", "token": token}).decode()
            )
            message = orjson.loads(await websocket.recv())

            if message["type"] != "auth_success":
                console.print(
                    "Unable to authenticate to the event stream. Please ensure the token you're using is valid for this environment."
                )
                return

            filter_message = {
                "type": "filter",
                "filter": {
                    "occurred": {
                        "since": pendulum.now("UTC").subtract(minutes=5).isoformat(),
                        "until": pendulum.now("UTC").add(years=1).isoformat(),
                    }
                },
            }

            await websocket.send(orjson.dumps(filter_message).decode())

            try:
                while True:
                    message = orjson.loads(await websocket.recv())
                    now = pendulum.now("UTC")
                    event = Event.parse_obj(message["event"])
                    if event.id in already_seen:
                        continue
                    already_seen.add(event.id)

                    console.print(
                        str(event.id).partition("-")[0],
                        f"occurred={(event.occurred - now).total_seconds():>7,.2f}",
                        f"\\[[bold green]{event.event}[/]]",
                        event.resource.id,
                    )
            except ConnectionClosedError:
                console.print("Reconnecting...")
                continue


if __name__ == "__main__":
    app()
