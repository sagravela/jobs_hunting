import scrapy
from scrapy.loader import ItemLoader
from urllib3.util import parse_url
from jobs_crawl.items import JobOffer


class LinkedinSpider(scrapy.Spider):
    name = "linkedin_spider"
    allowed_domains = ["linkedin.com"]

    def __init__(self, job: str = None, *args, **kwargs):
        super(LinkedinSpider, self).__init__(*args, **kwargs)

        parsed_url = parse_url(
            f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywordsc={job}&location=argentina&geoId=&trk=public_jobs_jobs-search-bar_search-submit&start="
        )
        # Linkedin only show 10 offer per page and 1000 is the max limit of offers displayed
        self.start_urls = [parsed_url.url + str(i) for i in range(0, 1000, 10)]
        self.logger.info("Starting url: {}0".format(parsed_url.url))

    def parse(self, response):
        for job in response.css("li"):
            loader = ItemLoader(item=JobOffer(), selector=job)

            loader.add_css("title", "h3.base-search-card__title::text")
            # Handle the edgecase where company doesn't have a Linkedin profile
            company = job.css("h4.base-search-card__subtitle a::text").get()
            if not company:
                company = job.css("h4.base-search-card__subtitle::text").get()
            loader.add_value("company", company)
            loader.add_css(
                "location", "div.base-search-card__metadata span:first-child::text"
            )
            loader.add_css("posted_at", "time::attr(datetime)")
            loader.add_css("url", "a:first-of-type::attr(href)")

            yield loader.load_item()
