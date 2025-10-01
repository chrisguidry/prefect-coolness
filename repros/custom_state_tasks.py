import time
from typing import Literal
from prefect import flow, task
from prefect.states import State, StateType, Completed, Failed


CustomStateType = Literal[
    "Scheduled", "Late", "Resuming", "AwaitingRetry", "AwaitingConcurrencySlot",
    "Pending", "Paused", "Suspended", "Running", "Retrying",
    "Completed", "Cached", "Cancelled", "Cancelling", "Crashed", "Failed", "TimedOut"
]


@task
def custom_state_task(state_type: CustomStateType) -> None:
    """
    Task that returns one of 17 custom states based on the state_type parameter.

    Maps custom state names to their corresponding state types according to Prefect's state model.
    """
    state_configs = {
        # Scheduled type states
        "Scheduled": State(type=StateType.SCHEDULED, name="Scheduled", message="Task is scheduled"),
        "Late": State(type=StateType.SCHEDULED, name="Late", message="Task is running late"),
        "Resuming": State(type=StateType.SCHEDULED, name="Resuming", message="Task is resuming"),
        "AwaitingRetry": State(type=StateType.SCHEDULED, name="AwaitingRetry", message="Task is awaiting retry"),
        "AwaitingConcurrencySlot": State(type=StateType.SCHEDULED, name="AwaitingConcurrencySlot", message="Task is awaiting concurrency slot"),

        # Pending type states
        "Pending": State(type=StateType.PENDING, name="Pending", message="Task is pending"),

        # Paused type states
        "Paused": State(type=StateType.PAUSED, name="Paused", message="Task is paused"),
        "Suspended": State(type=StateType.PAUSED, name="Suspended", message="Task is suspended"),

        # Running type states
        "Running": State(type=StateType.RUNNING, name="Running", message="Task is running"),
        "Retrying": State(type=StateType.RUNNING, name="Retrying", message="Task is retrying"),

        # Completed type states
        "Completed": Completed(name="Completed", message="Task completed successfully"),
        "Cached": State(type=StateType.COMPLETED, name="Cached", message="Task result was cached"),

        # Cancelled type states
        "Cancelled": State(type=StateType.CANCELLED, name="Cancelled", message="Task was cancelled"),

        # Cancelling type states
        "Cancelling": State(type=StateType.CANCELLING, name="Cancelling", message="Task is being cancelled"),

        # Crashed type states
        "Crashed": State(type=StateType.CRASHED, name="Crashed", message="Task crashed"),

        # Failed type states
        "Failed": Failed(name="Failed", message="Task failed"),
        "TimedOut": State(type=StateType.FAILED, name="TimedOut", message="Task timed out"),
    }

    return state_configs[state_type]


@flow
def custom_states_flow(iterations: int = 1, pause_seconds: int = 5):
    """
    Flow that demonstrates 17 different custom state name/type combinations.

    Args:
        iterations: Number of batches to run (default: 1)
        pause_seconds: Seconds to wait between each batch (default: 5)
    """
    all_states = [
        "Scheduled", "Late", "Resuming", "AwaitingRetry", "AwaitingConcurrencySlot",
        "Pending", "Paused", "Suspended", "Running", "Retrying",
        "Completed", "Cached", "Cancelled", "Cancelling", "Crashed", "Failed", "TimedOut"
    ]

    for iteration in range(iterations):
        print(f"Running iteration {iteration + 1} of {iterations}")

        # Submit all 17 tasks for this iteration
        for state_name in all_states:
            custom_state_task(state_name)

        # Pause between iterations (except after the last one)
        if iteration < iterations - 1:
            print(f"Pausing for {pause_seconds} seconds...")
            time.sleep(pause_seconds)

    print(f"Flow completed! Ran {len(all_states) * iterations} tasks total.")


if __name__ == "__main__":
    # Example usage
    custom_states_flow(iterations=2, pause_seconds=3)

