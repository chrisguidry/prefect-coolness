import random
import sys
import time

from prefect import flow, task


@task
def random_number() -> int:
    time.sleep(2 * random.random())
    return random.randint(100, 1000)


@task
def add(x: int, y: int) -> int:
    time.sleep(2 * random.random())
    return x + y


@task
def sub(x: int, y: int) -> int:
    time.sleep(2 * random.random())
    return x - y


@flow
def sum_the_pieces(pieces: list[int]) -> int:
    return sum(p for p in pieces)


@flow
def randos(count: int) -> int:
    pieces = [random_number.submit()]

    for _ in range(count):
        pieces.append(add.submit(random.choice(pieces), random_number.submit()))

    pieces += sub.map(pieces, random.choice(pieces))

    answer = sum_the_pieces(pieces)
    assert answer is not None

    # run_deployment(
    #     name="nightnight/agent-nightnight",
    #     parameters={"duration": abs(answer) % 10 + 1},
    # )

    return answer


if __name__ == "__main__":
    count = 10
    if sys.argv[1:]:
        count = int(sys.argv[1])

    print(randos(count))
