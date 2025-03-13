from prefect import flow


@flow
def version_me():
    print("Hello, world!")


if __name__ == "__main__":
    version_me()
