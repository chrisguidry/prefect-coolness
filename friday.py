from prefect import flow


@flow(log_prints=True)
def im_in_love():
    print("It's Friday, I'm in love")
