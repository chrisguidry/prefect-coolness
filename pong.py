from prefect import flow


@flow
def pong(value: str = "pong"):
    print(value)
    return value


if __name__ == "__main__":
    print(pong())
