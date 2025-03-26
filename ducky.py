import duckdb
from prefect import flow, task

# Uses the public dataset from Ookla:
# https://registry.opendata.aws/speedtest-global-performance/

OOKLA_FILE_FORMAT = (
    "s3://ookla-open-data/parquet/performance/"
    "type=fixed/"
    "year={year}/"
    "quarter={quarter}/"
    "{year}-{start_month:02d}-01_performance_fixed_tiles.parquet"
)


@flow(log_prints=True)
def analyze_download_speeds():
    filenames = []
    first_year, last_year = 2019, 2024
    for year in range(first_year, last_year + 1):
        for quarter in range(1, 5):
            filenames.append(
                OOKLA_FILE_FORMAT.format(
                    year=year, quarter=quarter, start_month=1 + (quarter - 1) * 3
                )
            )

    biggest_increases_future = get_biggest_increases.submit(
        filenames, first_year, last_year
    )
    biggest_decreases_future = get_biggest_decreases.submit(
        filenames, first_year, last_year
    )

    biggest_increases = biggest_increases_future.result()
    biggest_decreases = biggest_decreases_future.result()

    print(biggest_increases)
    print(biggest_decreases)


@task
def get_biggest_increases(filenames: list[str], first_year: int, last_year: int):
    with duckdb.connect(database=":memory:") as cn:
        cn.sql("""
            INSTALL httpfs;
            INSTALL spatial;
            LOAD httpfs;
            LOAD spatial;

            SET temp_directory = '/tmp';
            SET memory_limit = '15GB';
            SET max_temp_directory_size = '120GB';
        """)

        params = {
            "filenames": filenames,
            "first_year": first_year,
            "last_year": last_year,
        }

        return cn.sql(
            """
            WITH base AS (
                SELECT
                    tile,
                    AVG(avg_d_kbps) / 1000.0 as avg_download_mbps,
                    year,
                    SUM(tests) as total_tests
                FROM read_parquet($filenames)
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
                WHERE a.year = $first_year AND b.year = $last_year
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
            """,
            params=params,
        )


@task
def get_biggest_decreases(filenames: list[str], first_year: int, last_year: int):
    with duckdb.connect(database=":memory:") as cn:
        cn.sql("""
            INSTALL httpfs;
            INSTALL spatial;
            LOAD httpfs;
            LOAD spatial;

            SET temp_directory = '/tmp';
            SET memory_limit = '15GB';
            SET max_temp_directory_size = '120GB';
        """)

        params = {
            "filenames": filenames,
            "first_year": first_year,
            "last_year": last_year,
        }

        return cn.sql(
            """
            WITH base AS (
                SELECT
                    tile,
                    AVG(avg_d_kbps) / 1000.0 as avg_download_mbps,
                    year,
                    SUM(tests) as total_tests
                FROM read_parquet($filenames)
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
                WHERE a.year = $first_year AND b.year = $last_year
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
            """,
            params=params,
        )


if __name__ == "__main__":
    analyze_download_speeds()
