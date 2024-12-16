from prefect import flow


@flow
def slay(who: str):
    print(f"Slay, {who}!")


if __name__ == "__main__":
    slay.serve(name="serving", tags=["killing", "it"])
