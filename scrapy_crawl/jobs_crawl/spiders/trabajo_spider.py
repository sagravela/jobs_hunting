from urllib3.util import parse_url

import scrapy
from scrapy.loader import ItemLoader

from jobs_crawl.items import JobOffer


class TrabajoSpider(scrapy.Spider):
    name = "trabajo_spider"
    allowed_domains = ["ar.trabajo.org"]

    def __init__(self, job: str = None, *args, **kwargs):
        super(TrabajoSpider, self).__init__(*args, **kwargs)

        parsed_url = parse_url(f"https://ar.trabajo.org/empleo-{job.replace(' ', '+')}")
        self.start_urls = [parsed_url.url]
        self.logger.info("Starting url: {}".format(parsed_url.url))

    def parse(self, response):
        for job in response.css("li.nf-job.list-group-item"):
            loader = ItemLoader(item=JobOffer(), selector=job)

            loader.add_css("title", "h2 a::text")
            loader.add_css("company", "span:has(i.lnr-briefcase)::text")
            loader.add_css("location", "span:has(i.lnr-map-marker)::text")
            loader.add_css("posted_at", "p.text-muted small::text", re="hace (.*)")
            loader.add_css("url", "h2 a::attr(href)")

            yield loader.load_item()
