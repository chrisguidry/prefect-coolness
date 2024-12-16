from prefect import flow, get_run_logger


@flow
def say_hello():
    get_run_logger().info("Hello, world!")


if __name__ == "__main__":
    say_hello()
