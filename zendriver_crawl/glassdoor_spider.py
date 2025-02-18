from bs4 import BeautifulSoup

from utils import logging, parse_to_date
from db_model import setup_db, save_to_db, Job

async def glassdoor(browser, job: str) -> None:
    """Scrape job offers from *Glassdoor* website"""
    logging.info("Connecting to database.")
    conn, cur = setup_db()

    logging.info("Requesting Glassdoor.")
    url = f"https://www.glassdoor.com.ar/Empleo/argentina-{job}-empleos-SRCH_IL.0,9_IN15_KO10,{len(job) + 10}.htm"
    logging.info(f"Starting at {url}.")
    glassdoor = await browser.get(url)
    await glassdoor.sleep(
        10
    )  # Add time to manually click the cloudfare captcha if it appears (only in headless mode disabled)

    # Infinite scrolling to load more content dinamically while closing the popup if it appears
    offers_number = 0
    while True:
        await glassdoor.wait(10)
        pop_up = await glassdoor.query_selector("button.CloseButton")
        if pop_up:
            logging.info("Getting rid of popup.")
            await pop_up.click()
            await glassdoor.wait(5)

        # Get content and parse it with BeautifulSoup
        source_html = await glassdoor.get_content()
        soup = BeautifulSoup(source_html, "html.parser")
        elems = soup.select("div.jobCard")
        offers = []
        for elem in elems[offers_number:]:
            anchor = elem.select_one("a")
            span = elem.select_one("span")
            location = elem.select_one("[id*='job-location']")
            date = elem.select("div")
            data = {
                "company": span.get_text(strip=True),
                "title": anchor.get_text(strip=True),
                "location": location.get_text(strip=True),
                "posted_at": parse_to_date(date[-1].get_text(strip=True)).date(),
                "link": anchor["href"],
            }
            # Check data type and save
            end_data = Job(**data).model_dump()
            offers.append(end_data)

        # Save to database
        save_to_db(conn, cur, offers)
        offers_number += len(offers)
        logging.info(f"Offers scraped: {offers_number}.")

        # Load more content
        next_button = await glassdoor.query_selector("button[data-test='load-more']")
        if not next_button:
            logging.info("Finished.")
            break
        await next_button.click()

    logging.info("Closing spider.")
