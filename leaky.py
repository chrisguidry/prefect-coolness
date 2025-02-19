import resource
import time

from prefect import flow


@flow(log_prints=True)
def leaky():
    oh_the_things_i_love = []
    while True:
        print("leaking a little mo")
        for i in range(10_000_000):
            oh_the_things_i_love.append(str(i * 100_000_000))
        memory_bytes = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
        print(f"Current memory usage: {memory_bytes / 1_000_000:.1f} MB")
        time.sleep(1)


if __name__ == "__main__":
    leaky()
