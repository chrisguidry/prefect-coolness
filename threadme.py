from threading import current_thread

from prefect import flow, task


@task
def say_hello():
    thread = current_thread()
    print(f"Task running on thread: {thread.ident}, {thread.name}")


@flow
def check_task_thread():
    thread = current_thread()
    print(f"Flow running on thread: {thread.ident}, {thread.name}")
    say_hello()
    say_hello.submit().result()


if __name__ == "__main__":
    thread = current_thread()
    print(f"Program running on thread: {thread.ident}, {thread.name}")
    check_task_thread()
