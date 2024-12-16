import requests
from prefect import flow, get_run_logger


@flow(name="Hello [*✨World✨*]")
def say_hello(name: str):
    get_run_logger().info("Hello, %s", name)


def get_deployment():
    response = requests.get(
        "https://api.prefect.dev/api/accounts/257bc8f1-6997-4088-bb5e-6ec1cfbe28a9/workspaces/948362f2-21e1-4794-b0b0-651f5bc68ace/deployments/name/Hello [*✨World✨*]/[Say ✨ my ✨ name]",
        headers={"Authorization": "Bearer pnu_U0ZCIdceuVo3jFKN76UZMR7Ps9h66604ohJK"},
    )
    print(response.status_code)
    print(response.text)
    print(response.json())


if __name__ == "__main__":
    # say_hello("World")
    print(get_deployment())
