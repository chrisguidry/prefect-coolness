from prefect import flow, get_run_logger


@flow
def say_hello(name: str = "World"):
    get_run_logger().info(f"Hello, {name}!")


if __name__ == "__main__":
    say_hello()
