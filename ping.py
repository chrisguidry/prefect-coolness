from prefect import flow


@flow(log_prints=True)
def ping(value: str = "ping"):
    print(value)
    return value


if __name__ == "__main__":
    print(ping())
