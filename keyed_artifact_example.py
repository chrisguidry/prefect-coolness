import json
from typing import Any

from prefect import flow, task
from prefect.artifacts import create_table_artifact


@task
def generate_large_row_data() -> list[dict[str, str]]:
    """Generate approximately 2MB of row data as list of dictionaries."""
    rows = []
    row_size_estimate = 200  # Approximate bytes per row with our field structure
    target_rows = 2_000_000 // row_size_estimate  # ~10,000 rows for 2MB
    
    for i in range(target_rows):
        row = {
            "id": str(i),
            "name": f"User_{i:06d}",
            "email": f"user_{i}@example.com",
            "department": f"Department_{i % 10}",
            "status": "active" if i % 3 == 0 else "inactive",
            "created_date": f"2025-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}",
            "description": f"This is a sample description for user {i} with some additional text to increase row size and reach our target data volume.",
        }
        rows.append(row)
    
    return rows


@task
def create_keyed_artifact(data: list[dict[str, str]], artifact_key: str) -> str:
    """Create a keyed Prefect artifact with the provided data."""
    # Create table artifact with key
    artifact_id = create_table_artifact(
        key=artifact_key,
        table=data,
        description=f"Large dataset artifact with {len(data):,} rows (~2MB)"
    )
    
    return artifact_id


@flow(name="Keyed Artifact Example")
def keyed_artifact_flow(artifact_key: str = "large-dataset-v1") -> str:
    """Flow that creates a keyed artifact with 2MB of row data."""
    
    # Generate the large dataset
    row_data = generate_large_row_data()
    
    # Verify data size
    data_size_mb = len(json.dumps(row_data)) / (1024 * 1024)
    print(f"Generated {len(row_data):,} rows (~{data_size_mb:.2f} MB)")
    
    # Create the keyed artifact
    artifact_id = create_keyed_artifact(row_data, artifact_key)
    
    print(f"Created keyed artifact '{artifact_key}' with ID: {artifact_id}")
    return artifact_id


if __name__ == "__main__":
    result = keyed_artifact_flow()
    print(f"Flow completed. Artifact ID: {result}")