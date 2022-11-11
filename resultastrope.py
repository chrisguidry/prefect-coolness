import anyio
import prefect
from packaging.version import Version
from prefect import flow, get_client


@flow
def hello():
    return "Hello!"


if Version(prefect.__version__) > Version("2.6.0"):
    hello = hello.with_options(persist_result=True)


async def get_state_from_api(flow_run_id):
    async with get_client() as client:
        flow_run = await client.read_flow_run(flow_run_id)
        return flow_run.state


if __name__ == "__main__":
    state = hello(return_state=True)
    assert state.result() == "Hello!"

    api_state = anyio.run(get_state_from_api, state.state_details.flow_run_id)

    from prefect.results import _Result

    result = api_state.result()
    assert isinstance(result, _Result), f"Got {result!r}"
