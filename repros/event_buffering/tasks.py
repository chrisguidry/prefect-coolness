from prefect import task
from prefect.task_worker import serve


@task
def square(x):
    return x**2


@task
def neg(x):
    return -x


@task
def summation(nums):
    return sum(nums)


if __name__ == "__main__":
    serve(square, neg, summation)
