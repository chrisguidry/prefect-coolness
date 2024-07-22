from socket import getaddrinfo, gethostname

import httpx
from prefect import flow, get_run_logger


@flow
def where_am_i():
    logger = get_run_logger()

    hostname = gethostname()
    ip_addresses = getaddrinfo(hostname, None)[0][4][0]

    logger.info(f"The flow ran on host {hostname}")
    logger.info(f"{hostname} has the following IP addresses: {ip_addresses}")

    egress_query = httpx.get("https://ifconfig.me/all.json")
    egress_query.raise_for_status()
    ip_addresses = list(reversed(egress_query.json()["forwarded"].split(",")))
    logger.info(f"{hostname} reaches the internet from: {ip_addresses}")


if __name__ == "__main__":
    where_am_i()
