from prefect import flow


@flow
def ping():
    return "ping"


if __name__ == "__main__":
    print(ping())
