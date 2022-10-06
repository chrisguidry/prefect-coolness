import re
from datetime import timedelta
from typing import List

import mechanicalsoup
from prefect import flow, get_run_logger, task
from prefect.deployments import Deployment
from prefect.tasks import task_input_hash

NEGATIVE_ENGINEERING = re.compile(r"(negative\s(\w+\s)*engineering)", re.IGNORECASE)
POSITIVE_ENGINEERING = re.compile(r"(positive\s(\w+\s)*engineering)", re.IGNORECASE)


@flow()
def crawl_prefect_blog():
    links = get_front_page_links("https://www.prefect.io/guide/blog/")

    scores = []

    for link in links:
        article = crawl_article.submit(f"https://prefect.io{link}")

        negative_mentions = count_mentions_of_negative_engineering(article)
        positive_mentions = count_mentions_of_positive_engineering(article)

        scores.append(
            compute_net_marvin_score.submit(negative_mentions, positive_mentions)
        )

    scores = [score.result() for score in scores]
    if not scores:
        return

    get_run_logger().info("Average Marvin Score: %f", sum(scores) / len(scores))


@task(cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1))
def get_front_page_links(front_page: str) -> List[str]:
    browser = mechanicalsoup.StatefulBrowser()
    browser.open(front_page)

    links = []

    for anchor in browser.page.select("a"):
        link = anchor.attrs.get("href") or None
        if not link or not link.startswith("/guide/blog"):
            continue

        links.append(link)

    return links


@task(cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1))
def crawl_article(link: str) -> str | None:
    browser = mechanicalsoup.StatefulBrowser()
    browser.open(link)
    main_section = browser.page.select_one("section")
    if not main_section:
        return None
    return str(main_section)


@task
def count_mentions_of_positive_engineering(article: str) -> int:
    if not article:
        return 0

    return len(POSITIVE_ENGINEERING.findall(article))


@task
def count_mentions_of_negative_engineering(article: str) -> int:
    if not article:
        return 0

    return len(NEGATIVE_ENGINEERING.findall(article))


@task
def compute_net_marvin_score(negative_mentions: int, positive_mentions: int) -> float:
    if not positive_mentions:
        return 0.0

    return negative_mentions / positive_mentions


if __name__ == "__main__":
    crawl_prefect_blog()
