import re
import json
from datetime import datetime, UTC

from glom import glom

from utils import logging
from db_model import setup_db, save_to_db, Job

async def indeed(browser, job: str) -> None:
    """Scrape data from *Indeed* website"""
    logging.info("Connecting to database.")
    conn, cur = setup_db()

    logging.info("Requesting Indeed.")
    # Indeed page
    url = f"https://ar.indeed.com/q-{job}-l-argentina-empleos.html"
    logging.info(f"Starting at {url}.")
    indeed = await browser.get(url, new_tab=True)
    await indeed.sleep(
        15
    )  # Add time to manually click the cloudfare captcha if it appears (only in headless mode disabled)

    # Paginate while scraping jobs data
    offers_number = 0
    while True:
        await indeed.wait(10)
        try:
            # Look for the json data
            elem = await indeed.wait_for("script#mosaic-data", timeout=60)
        except TimeoutError:
            logging.warning("Timeout reached looking for json data.")
            break

        # Get json data
        elem_html = await elem.get_html()
        pattern = (
            r'window\.mosaic\.providerData\["mosaic-provider-jobcards"\]=(\{.*?\});'
        )
        str_json = re.search(pattern, elem_html, re.DOTALL)
        if not str_json:
            continue
        json_data = json.loads(str_json.group(1))
        results = glom(json_data, "metaData.mosaicProviderJobCardsModel.results")
        offers = []
        for r in results:
            data = {
                "company": r["company"],
                "title": r["displayTitle"],
                "location": r["formattedLocation"],
                "posted_at": datetime.fromtimestamp(r["createDate"] / 1000, UTC).date(),
                "link": "https://ar.indeed.com" + r["link"],
            }
            # Check data type and save
            end_data = Job(**data).model_dump()
            offers.append(end_data)

        # Save to database
        save_to_db(conn, cur, offers)
        offers_number += len(offers)
        logging.info(f"Offers scraped: {offers_number}.")

        # Next page
        next_button = await indeed.query_selector(
            "a[data-testid='pagination-page-next']"
        )
        if not next_button:
            logging.info("Finished.")
            break
        await next_button.click()

    logging.info("Closing spider.")
