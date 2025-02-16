import asyncio
import logging
import argparse

import zendriver as zd

from db_model import setup_db, save_to_db
from glassdoor_spider import get_glassdoor
from indeed_spider import get_indeed


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def main(job: str):
    conn, cur = setup_db()
    browser = await zd.start(headless=True)
    job = job.replace(" ", "-")
    glassdoor_offers, indeed_offers = await asyncio.gather(
        get_glassdoor(browser, job), get_indeed(browser, job)
    )

    logging.info(f"Glassdoor offers scraped: {len(glassdoor_offers)}.")
    save_to_db(conn, cur, glassdoor_offers)
    logging.info(f"Indeed offers scraped: {len(indeed_offers)}.")
    save_to_db(conn, cur, indeed_offers)

    browser.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the spiders scraping for jobs in each web site."
    )
    parser.add_argument(
        "-s", "--search", type=str, default="data science", help="Job search keyword"
    )
    args = parser.parse_args()
    job = args.search

    logging.info("Running Program ...")
    logging.info(f"Looking for {job} in Argentina.")
    zd.loop().run_until_complete(main(job))
