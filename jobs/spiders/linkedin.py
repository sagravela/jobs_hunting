import scrapy
from scrapy.loader import ItemLoader
from jobs.items import JobOffer
from urllib3.util import parse_url

class LinkedinSpider(scrapy.spiders.CrawlSpider):
    """
    Spider for Linkedin

    Parameters:
        job (str): Job title
        location (str): Location
    """
    name = 'Linkedin'
    allowed_domains = ['linkedin.com']
    rules = (
        scrapy.spiders.Rule(
            scrapy.linkextractors.LinkExtractor(restrict_css='a.base-card__full-link', allow= r'/jobs'),
            callback='parse',
        ),
    )

    def __init__(self, job: str = None, location: str =None, *args, **kwargs):
        super(LinkedinSpider, self).__init__(*args, **kwargs)
        
        # Search job and location will be received from the command line
        parsed_url = parse_url(f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={job}&location={location}&geoId=&trk=public_jobs_jobs-search-bar_search-submit&start=')
        # Linkedin only show 10 offer per page and 1000 is the max limit of offers displayed
        self.start_urls = [parsed_url.url + str(i) for i in range(0, 1000, 10)] 
        self.logger.info("Linkedin starting base url: {}0".format(parsed_url.url))

    def parse(self, response):
        # scrapy.shell.inspect_response(response, self)
        item = ItemLoader(item=JobOffer(), response=response)
        item.add_css('title', 'h1.top-card-layout__title::text')
        item.add_css('company', 'a.topcard__org-name-link::text')
        item.add_css('place', 'span.topcard__flavor--bullet::text')
        item.add_css('posted_at', 'span.posted-time-ago__text::text')
        item.add_css('applicants', 'h4.top-card-layout__second-subline', re=r'(\d+) applicants')
        item.add_css('description', 'div.show-more-less-html__markup')
        item.add_value('url', response.url)
        yield item.load_item()
