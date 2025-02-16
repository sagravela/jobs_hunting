import re
import logging
from datetime import datetime, timedelta

from bs4 import BeautifulSoup

from db_model import Job


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def parse_duration(duration_str):
    # Extract numbers and units using regex
    pattern = r"(\d+)\s*(d|h|m|s)"
    match = re.search(pattern, duration_str)

    # Initialize a timedelta
    delta = timedelta()

    # Map extracted values to timedelta
    value, unit = match.group(1), match.group(2)
    value = int(value)
    if unit == "d":
        delta += timedelta(days=value)
    elif unit == "h":
        delta += timedelta(hours=value)
    elif unit == "m":
        delta += timedelta(minutes=value)
    elif unit == "s":
        delta += timedelta(seconds=value)

    # Get timestamp
    return datetime.now() - delta


async def get_glassdoor(browser, job: str):
    logging.info("Requesting Glassdoor.")

    # This only works for Argentina
    url = f"https://www.glassdoor.com.ar/Empleo/argentina-{job}-empleos-SRCH_IL.0,9_IN15_KO10,{len(job) + 10}.htm"
    logging.info(f"Starting at {url}.")
    glassdoor = await browser.get(url)
    await glassdoor.sleep(5)

    # Infinite scrolling to load more content dinamically while closing the popup
    while True:
        button = await glassdoor.query_selector("button[data-test='load-more']")
        if not button:
            break
        await button.click()
        await glassdoor.sleep(5)
        pop_up = await glassdoor.query_selector("button.CloseButton")
        if pop_up:
            await pop_up.click()
            await glassdoor.sleep(2)

    source_html = await glassdoor.get_content()
    soup = BeautifulSoup(source_html, "html.parser")
    elems = soup.select("div.jobCard")
    offers = []
    logging.info(f"Found {len(elems)} offers.")
    for i, elem in enumerate(elems):
        anchor = elem.select_one("a")
        span = elem.select_one("span")
        location = elem.select_one("[id*='job-location']")
        date = elem.select("div")
        data = {
            "company": span.get_text(strip=True),
            "title": anchor.get_text(strip=True),
            "location": location.get_text(strip=True),
            "posted_at": parse_duration(date[-1].get_text(strip=True)).date(),
            "link": anchor["href"],
        }
        end_data = Job(**data).model_dump()
        if i % 50 == 0:
            logging.info(f"Glassdoor offers scraped: {i}")
        offers.append(end_data)
    return offers
