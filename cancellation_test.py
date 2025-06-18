import random
import time
from typing import List

from prefect import flow, task, get_run_logger


@task
def slow_task(task_id: str, sleep_duration: float = 2.0) -> int:
    """A task that sleeps for a configurable duration to test cancellation."""
    logger = get_run_logger()
    logger.info(f"Task {task_id} starting, will sleep for {sleep_duration:.1f}s")
    time.sleep(sleep_duration)
    result = hash(task_id) % 1000 + random.randint(1, 9)
    logger.info(f"Task {task_id} completed with result: {result}")
    return result


@task
def processing_task(data: List[int], task_id: int) -> int:
    """A task that processes data with variable sleep time."""
    logger = get_run_logger()
    sleep_time = random.uniform(1.0, 3.0)
    logger.info(f"Processing task {task_id} starting, processing {len(data)} items, will sleep for {sleep_time:.1f}s")
    time.sleep(sleep_time)
    result = sum(data) + task_id
    logger.info(f"Processing task {task_id} completed with result: {result}")
    return result


@flow
def quick_subflow(subflow_id: int) -> List[int]:
    """A subflow with a few quick tasks."""
    logger = get_run_logger()
    logger.info(f"Quick subflow {subflow_id} starting")
    
    results = []
    for i in range(3):
        task_result = slow_task(f"{subflow_id}_{i}", sleep_duration=random.uniform(0.5, 1.5))
        results.append(task_result)
    
    logger.info(f"Quick subflow {subflow_id} completed with {len(results)} results")
    return results


@flow
def heavy_subflow(subflow_id: int) -> int:
    """A subflow with longer-running tasks."""
    logger = get_run_logger()
    logger.info(f"Heavy subflow {subflow_id} starting")
    
    # Generate some initial data
    initial_tasks = []
    for i in range(4):
        task_result = slow_task(f"{subflow_id}_init_{i}", sleep_duration=random.uniform(2.0, 4.0))
        initial_tasks.append(task_result)
    
    # Process the data
    final_result = processing_task(initial_tasks, subflow_id)
    
    logger.info(f"Heavy subflow {subflow_id} completed with final result: {final_result}")
    return final_result


@flow
def parallel_worker_subflow(worker_id: int, task_count: int = 5) -> List[int]:
    """A subflow that runs multiple tasks in parallel."""
    logger = get_run_logger()
    logger.info(f"Parallel worker {worker_id} starting with {task_count} tasks")
    
    # Submit all tasks for parallel execution
    task_futures = []
    for i in range(task_count):
        future = slow_task.submit(f"{worker_id}_parallel_{i}", sleep_duration=random.uniform(1.0, 2.5))
        task_futures.append(future)
    
    # Collect results
    results = [future.result() for future in task_futures]
    
    logger.info(f"Parallel worker {worker_id} completed with {len(results)} results")
    return results


@flow
def cancellation_test_flow(
    num_quick_subflows: int = 3,
    num_heavy_subflows: int = 2,
    num_parallel_workers: int = 2,
    parallel_tasks_per_worker: int = 4
) -> dict:
    """
    Main flow that orchestrates multiple subflows and tasks for testing cancellation logic.
    
    This flow creates a complex execution graph with:
    - Multiple quick subflows running concurrently
    - Heavy subflows with longer-running tasks
    - Parallel workers executing tasks concurrently
    - Individual long-running tasks
    
    Args:
        num_quick_subflows: Number of quick subflows to run
        num_heavy_subflows: Number of heavy subflows to run  
        num_parallel_workers: Number of parallel worker subflows
        parallel_tasks_per_worker: Number of tasks per parallel worker
    """
    logger = get_run_logger()
    logger.info("🚀 Starting cancellation test flow")
    logger.info(f"Configuration: {num_quick_subflows} quick, {num_heavy_subflows} heavy, {num_parallel_workers} parallel workers")
    
    results = {
        "quick_results": [],
        "heavy_results": [],
        "parallel_results": [],
        "individual_tasks": []
    }
    
    # Run quick subflows concurrently (call them directly as they will run in the current flow context)
    logger.info("🏃 Running quick subflows...")
    for i in range(num_quick_subflows):
        result = quick_subflow(i)
        results["quick_results"].extend(result)
    
    # Run heavy subflows
    logger.info("🔨 Running heavy subflows...")  
    for i in range(num_heavy_subflows):
        result = heavy_subflow(i)
        results["heavy_results"].append(result)
    
    # Run parallel worker subflows
    logger.info("⚡ Running parallel worker subflows...")
    for i in range(num_parallel_workers):
        result = parallel_worker_subflow(i, parallel_tasks_per_worker)
        results["parallel_results"].extend(result)
    
    # Submit some individual long-running tasks for true concurrency
    logger.info("🎯 Running individual long-running tasks...")
    individual_futures = []
    for i in range(3):
        future = slow_task.submit(f"individual_{i}", sleep_duration=random.uniform(3.0, 6.0))
        individual_futures.append(future)
    
    # Collect results from individual tasks
    for future in individual_futures:
        result = future.result()
        results["individual_tasks"].append(result)
    
    # Summary statistics
    total_tasks = (
        len(results["quick_results"]) + 
        len(results["heavy_results"]) + 
        len(results["parallel_results"]) + 
        len(results["individual_tasks"])
    )
    
    logger.info(f"✅ Cancellation test flow completed successfully!")
    logger.info(f"📊 Executed {total_tasks} total tasks across multiple subflows")
    logger.info(f"📈 Results summary: {len(results['quick_results'])} quick, {len(results['heavy_results'])} heavy, {len(results['parallel_results'])} parallel, {len(results['individual_tasks'])} individual")
    
    return results


if __name__ == "__main__":
    # Run with default parameters - creates a complex execution graph perfect for testing cancellation
    result = cancellation_test_flow()
    print(f"Flow completed with {sum(len(v) if isinstance(v, list) else 1 for v in result.values())} total results")