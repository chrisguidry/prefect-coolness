from pathlib import Path

import duckdb
from prefect import cache_policies, flow, task


@flow(log_prints=True)
def analyze_download_speeds():
    Path("ookla").mkdir(parents=True, exist_ok=True)

    futures = []
    first_year, last_year = 2019, 2024
    for year in range(first_year, last_year + 1):
        for quarter in range(1, 5):
            futures.append(download_ookla_file.submit(year, quarter))

    files = [file.result() for file in futures]
    print(files)

    with duckdb.connect(database=":memory:") as cn:
        cn.sql(
            """
            INSTALL spatial;
            LOAD spatial;
            """
        )

        biggest_increases = cn.sql(
            f"""
            WITH base AS (
                SELECT
                    tile,
                    AVG(avg_d_kbps) / 1000.0 as avg_download_mbps,
                    year,
                    SUM(tests) as total_tests
                FROM read_parquet('ookla/sources/*.parquet')
                WHERE ST_IsValid(tile::GEOMETRY)
                GROUP BY tile, year
                HAVING total_tests >= 100
            ),
            changes AS (
                SELECT
                    a.tile,
                    a.avg_download_mbps as speed_first_year,
                    b.avg_download_mbps as speed_last_year,
                    b.avg_download_mbps - a.avg_download_mbps as speed_change_mbps
                FROM base a
                JOIN base b ON a.tile = b.tile
                WHERE a.year = {first_year} AND b.year = {last_year}
            )
            SELECT
                tile::GEOMETRY as geometry,
                speed_first_year,
                speed_last_year,
                speed_change_mbps
            FROM changes
            WHERE speed_change_mbps > 0
            ORDER BY speed_change_mbps DESC
            LIMIT 10
            """
        )
        print(biggest_increases)

        biggest_decreases = cn.sql(
            f"""
            WITH base AS (
                SELECT
                    tile,
                    AVG(avg_d_kbps) / 1000.0 as avg_download_mbps,
                    year,
                    SUM(tests) as total_tests
                FROM read_parquet('ookla/sources/*.parquet')
                WHERE ST_IsValid(tile::GEOMETRY)
                GROUP BY tile, year
                HAVING total_tests >= 100
            ),
            changes AS (
                SELECT
                    a.tile,
                    a.avg_download_mbps as speed_prev_year,
                    b.avg_download_mbps as speed_last_year,
                    b.avg_download_mbps - a.avg_download_mbps as speed_change_mbps
                FROM base a
                JOIN base b ON a.tile = b.tile
                WHERE a.year = {last_year - 1} AND b.year = {last_year}
            )
            SELECT
                tile::GEOMETRY as geometry,
                speed_prev_year,
                speed_last_year,
                speed_change_mbps
            FROM changes
            WHERE speed_change_mbps < 0
            ORDER BY speed_change_mbps ASC
            LIMIT 10
            """
        )
        print(biggest_decreases)


OOKLA_FILE_FORMAT = (
    "s3://ookla-open-data/parquet/performance/"
    "type=fixed/"
    "year={year}/"
    "quarter={quarter}/"
    "{year}-{start_month:02d}-01_performance_fixed_tiles.parquet"
)


@task(log_prints=True, cache_policy=cache_policies.INPUTS)
def download_ookla_file(year: int, quarter: int) -> Path:
    downloads = Path("ookla") / "sources"
    downloads.mkdir(parents=True, exist_ok=True)

    start_month = 1 + (quarter - 1) * 3
    source_file = OOKLA_FILE_FORMAT.format(
        year=year, quarter=quarter, start_month=start_month
    )
    local_file = downloads / f"{year}-Q{quarter}.parquet"

    print(f"Downloading {year}-Q{quarter} data...")
    with duckdb.connect(database=":memory:") as cn:
        cn.sql(
            f"COPY (SELECT * FROM '{source_file}') to '{local_file}' (FORMAT PARQUET)"
        )
    print("Done!")
    return local_file


if __name__ == "__main__":
    analyze_download_speeds()
