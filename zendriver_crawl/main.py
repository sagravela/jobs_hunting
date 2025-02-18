import asyncio
import argparse

import zendriver as zd

from utils import logging
from glassdoor_spider import glassdoor
from indeed_spider import indeed

async def main(job: str) -> None:
    """Run the spiders asynchronously."""
    browser = await zd.start(
        headless=False
    )  # Enable headless mode if the website doesn't block you
    job = job.replace(" ", "-")
    await asyncio.gather(glassdoor(browser, job), indeed(browser, job))
    await browser.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the spiders scraping for jobs in each web site through an automated browser. Location is set to Argentina."
    )
    parser.add_argument(
        "-s", "--search", type=str, required= True, help="Job search keyword"
    )
    args = parser.parse_args()
    job = args.search

    logging.info("Running Program ...")
    logging.info(f"Looking for {job} in Argentina.")
    zd.loop().run_until_complete(main(job))
