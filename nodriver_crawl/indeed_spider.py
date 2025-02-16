import re
import logging
import json
from datetime import datetime, UTC

from glom import glom

from db_model import Job


async def get_indeed(browser, job: str):
    logging.info("Requesting Indeed.")
    # Indeed page
    url = f"https://ar.indeed.com/q-{job}-l-argentina-empleos.html"
    logging.info(f"Starting at {url}.")
    indeed = await browser.get(url, new_tab=True)
    await indeed.sleep(5)
    offers = []

    while True:
        elem = await indeed.wait_for("#mosaic-data", timeout=60)
        elem_html = await elem.get_html()
        pattern = (
            r'window\.mosaic\.providerData\["mosaic-provider-jobcards"\]=(\{.*?\});'
        )
        str_json = re.search(pattern, elem_html, re.DOTALL)
        if not str_json:
            continue
        json_data = json.loads(str_json.group(1))
        results = glom(json_data, "metaData.mosaicProviderJobCardsModel.results")
        for r in results:
            data = {
                "company": r["company"],
                "title": r["displayTitle"],
                "location": r["formattedLocation"],
                "posted_at": datetime.fromtimestamp(r["createDate"] / 1000, UTC).date(),
                "link": "https://ar.indeed.com" + r["link"],
            }
            end_data = Job(**data).model_dump()
            offers.append(end_data)
            if len(offers) % 50 == 0:
                logging.info(f"Indeed offers scraped: {len(offers)}")

        next_button = await indeed.query_selector(
            "a[data-testid='pagination-page-next']"
        )
        if not next_button:
            break
        await next_button.focus()
        await next_button.click()
        await indeed.sleep(5)
    return offers
