import os
from pathlib import Path

from prefect import flow
from tqdm import tqdm


@flow(log_prints=True)
def test_storage_capacity(
    target_size_gigabytes: float = 20.0,
    chunk_size_megabytes: float = 100.0,
    test_file_path: Path = Path("/tmp/storage_test.bin"),
) -> None:
    target_size_bytes = int(target_size_gigabytes * 1024 * 1024 * 1024)
    chunk_size_bytes = int(chunk_size_megabytes * 1024 * 1024)
    num_chunks = target_size_bytes // chunk_size_bytes

    try:
        print(
            f"Writing {target_size_bytes / 1024 / 1024 / 1024:.1f}GB of data in "
            f"{chunk_size_bytes / 1024 / 1024:.0f}MB chunks..."
        )

        for _ in tqdm(range(num_chunks)):
            with open(test_file_path, "ab") as f:
                f.write(os.urandom(chunk_size_bytes))

            current_size = test_file_path.stat().st_size
            if current_size >= target_size_bytes:
                break

        final_size_gb = test_file_path.stat().st_size / 1024 / 1024 / 1024
        print(f"Finished writing {final_size_gb:.1f}GB")

    finally:
        if test_file_path.exists():
            test_file_path.unlink()
            print("Test file cleaned up")


if __name__ == "__main__":
    test_storage_capacity()
