#!/usr/bin/env python3

import random
import time
from datetime import datetime

from prefect import flow, task
from prefect.logging import get_run_logger


@task
def initialize_data() -> dict[str, str]:
    logger = get_run_logger()
    logger.info("Initializing data processing...")

    # Random delay between 5-10 seconds
    delay = random.uniform(5, 10)
    logger.info(f"Setting up data structures (will take {delay:.1f}s)")
    time.sleep(delay)

    data = {
        "batch_id": f"batch_{datetime.now().strftime('%H%M%S')}",
        "status": "initialized",
        "records": str(random.randint(500, 2000))
    }

    logger.info(f"Initialized batch {data['batch_id']} with {data['records']} records")
    return data


@task
def validate_records(data: dict[str, str]) -> dict[str, str]:
    logger = get_run_logger()
    logger.info(f"Validating {data['records']} records from {data['batch_id']}")

    # Simulate validation taking time proportional to record count
    base_time = 8
    record_factor = int(data['records']) / 300
    delay = base_time + record_factor + random.uniform(0, 4)

    logger.info(f"Running validation checks (estimated {delay:.1f}s)")
    time.sleep(delay)

    # Randomly fail some validation
    if random.random() < 0.3:
        logger.warning("Found data quality issues, applying corrections...")
        time.sleep(random.uniform(3, 8))
        data["corrections_applied"] = "true"

    data["status"] = "validated"
    logger.info(f"Validation complete for batch {data['batch_id']}")
    return data


@task
def process_chunk(chunk_id: int, data: dict[str, str]) -> dict[str, str]:
    logger = get_run_logger()
    logger.info(f"Processing chunk {chunk_id} from batch {data['batch_id']}")

    # Each chunk takes a different amount of time
    base_delay = random.uniform(5, 12)
    complexity_factor = random.choice([0.8, 1.0, 1.3, 1.8])  # Some chunks are more complex
    total_delay = base_delay * complexity_factor

    if complexity_factor > 1.2:
        logger.info(f"Chunk {chunk_id} requires additional processing ({total_delay:.1f}s)")
    else:
        logger.info(f"Processing chunk {chunk_id} ({total_delay:.1f}s)")

    # Add progress updates during long processing
    if total_delay > 8:
        time.sleep(total_delay * 0.4)
        logger.info(f"Chunk {chunk_id}: 40% complete...")
        time.sleep(total_delay * 0.3)
        logger.info(f"Chunk {chunk_id}: 70% complete...")
        time.sleep(total_delay * 0.3)
    else:
        time.sleep(total_delay)

    result = {
        "chunk_id": str(chunk_id),
        "batch_id": data["batch_id"],
        "processed_at": datetime.now().isoformat(),
        "complexity": "high" if complexity_factor > 1.2 else "normal"
    }

    logger.info(f"Chunk {chunk_id} processing complete")
    return result


@task
def aggregate_results(results: list[dict[str, str]], data: dict[str, str]) -> dict[str, str]:
    logger = get_run_logger()
    logger.info(f"Aggregating results from {len(results)} chunks")

    # Aggregation takes time based on number of chunks
    delay = 5 + (len(results) * 1.2) + random.uniform(0, 4)
    logger.info(f"Computing aggregations and statistics ({delay:.1f}s)")

    # Progress updates for long aggregation
    if delay > 8:
        time.sleep(delay * 0.3)
        logger.info("Computing statistical measures...")
        time.sleep(delay * 0.4)
        logger.info("Building summary reports...")
        time.sleep(delay * 0.3)
    else:
        time.sleep(delay)

    high_complexity_count = sum(1 for r in results if r.get("complexity") == "high")

    summary = {
        "batch_id": data["batch_id"],
        "total_chunks": str(len(results)),
        "high_complexity_chunks": str(high_complexity_count),
        "status": "aggregated",
        "completed_at": datetime.now().isoformat()
    }

    logger.info(f"Aggregation complete: {high_complexity_count}/{len(results)} high-complexity chunks")
    return summary


@task
def quality_assurance(summary: dict[str, str]) -> dict[str, str]:
    logger = get_run_logger()
    logger.info(f"Running quality assurance on batch {summary['batch_id']}")

    # QA checks take significant time
    delay = random.uniform(6, 12)
    logger.info(f"Performing comprehensive QA checks ({delay:.1f}s)")

    # Multi-stage QA process
    time.sleep(delay * 0.25)
    logger.info("QA: Data integrity checks...")
    time.sleep(delay * 0.25)
    logger.info("QA: Statistical validation...")
    time.sleep(delay * 0.25)
    logger.info("QA: Cross-referencing results...")
    time.sleep(delay * 0.25)

    # Occasionally find issues that need fixing
    if random.random() < 0.15:
        logger.warning("QA: Minor inconsistencies detected, applying fixes...")
        time.sleep(random.uniform(3, 6))
        summary["qa_fixes_applied"] = "true"

    summary["qa_status"] = "passed"
    logger.info("Quality assurance complete")
    return summary


@task
def generate_reports(summary: dict[str, str]) -> dict[str, str]:
    logger = get_run_logger()
    logger.info(f"Generating reports for batch {summary['batch_id']}")

    # Report generation is time-consuming
    delay = random.uniform(8, 15)
    logger.info(f"Creating detailed reports ({delay:.1f}s)")

    # Multi-stage report generation
    time.sleep(delay * 0.2)
    logger.info("Generating executive summary...")
    time.sleep(delay * 0.3)
    logger.info("Creating detailed analytics report...")
    time.sleep(delay * 0.2)
    logger.info("Building data visualizations...")
    time.sleep(delay * 0.2)
    logger.info("Compiling final documentation...")
    time.sleep(delay * 0.1)

    summary["reports_generated"] = "true"
    summary["report_count"] = str(random.randint(3, 7))
    logger.info(f"Generated {summary['report_count']} reports successfully")
    return summary


@task
def backup_results(summary: dict[str, str]) -> dict[str, str]:
    logger = get_run_logger()
    logger.info(f"Backing up results for batch {summary['batch_id']}")

    # Backup process with potential retries
    delay = random.uniform(4, 8)
    logger.info(f"Creating backup archives ({delay:.1f}s)")

    time.sleep(delay * 0.6)

    # Sometimes backup needs retry
    if random.random() < 0.1:
        logger.warning("Backup connection timeout, retrying...")
        time.sleep(random.uniform(2, 4))

    logger.info("Verifying backup integrity...")
    time.sleep(delay * 0.4)

    summary["backup_status"] = "completed"
    logger.info("Backup process completed successfully")
    return summary


@task
def finalize_processing(summary: dict[str, str]) -> str:
    logger = get_run_logger()
    logger.info(f"Finalizing processing for batch {summary['batch_id']}")

    # Final cleanup and reporting
    delay = random.uniform(3, 8)
    logger.info(f"Final cleanup and archival ({delay:.1f}s)")

    time.sleep(delay * 0.4)
    logger.info("Cleaning up temporary files...")
    time.sleep(delay * 0.3)
    logger.info("Updating process logs...")
    time.sleep(delay * 0.3)

    # Sometimes there's additional work
    if random.random() < 0.2:
        logger.info("Performing final compliance checks...")
        time.sleep(random.uniform(4, 8))

    final_status = f"Batch {summary['batch_id']} completed successfully"
    logger.info(final_status)
    return final_status


@flow(log_prints=True)
def serious_business_flow() -> str:
    logger = get_run_logger()
    logger.info("Starting serious business processing flow")

    # Initial setup delay
    setup_delay = random.uniform(2, 5)
    logger.info(f"Flow initialization ({setup_delay:.1f}s)")
    time.sleep(setup_delay)

    # Initialize data
    data = initialize_data()

    # Flow-level processing delay
    logger.info("Preparing for validation phase...")
    time.sleep(random.uniform(2, 4))

    # Validate the data
    validated_data = validate_records(data)

    # Another flow-level delay
    logger.info("Setting up parallel processing...")
    time.sleep(random.uniform(2, 3))

    # Process multiple chunks in parallel (more chunks now)
    chunk_count = random.randint(6, 10)
    logger.info(f"Processing {chunk_count} chunks in parallel")

    chunk_results = []
    for i in range(chunk_count):
        result = process_chunk(i + 1, validated_data)
        chunk_results.append(result)

    # Flow coordination delay
    logger.info("All chunks complete, preparing aggregation...")
    time.sleep(random.uniform(2, 4))

    # Aggregate results
    summary = aggregate_results(chunk_results, validated_data)

    # New post-processing phase
    logger.info("Beginning post-processing phase...")
    time.sleep(random.uniform(2, 3))

    # Quality assurance
    qa_summary = quality_assurance(summary)

    # Flow delay before reports
    logger.info("Preparing report generation...")
    time.sleep(random.uniform(1, 3))

    # Generate reports
    report_summary = generate_reports(qa_summary)

    # Flow delay before backup
    logger.info("Initiating backup procedures...")
    time.sleep(random.uniform(1, 2))

    # Backup results
    backup_summary = backup_results(report_summary)

    # Final flow delay
    logger.info("Preparing finalization...")
    time.sleep(random.uniform(2, 4))

    # Finalize
    result = finalize_processing(backup_summary)

    logger.info("Flow completed successfully")
    return result


if __name__ == "__main__":
    serious_business_flow()