from prefect import flow
from prefect.task_runners import PrefectTaskRunner
from tasks import neg, square, summation


@flow(task_runner=PrefectTaskRunner())
def example_flow():
    A = square.map(range(10))
    B = neg.map(A)
    total = summation.submit(B)

    return total.result()


if __name__ == "__main__":
    result = example_flow()
    print(result)
