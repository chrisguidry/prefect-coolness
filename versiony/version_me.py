from prefect import flow


@flow
def version_me(foo: str = "bar"):
    print(f"Hello, {foo}!")


if __name__ == "__main__":
    version_me(foo="world")
