from prefect import flow


@flow
def pong():
    return "pong"


if __name__ == "__main__":
    print(pong())
