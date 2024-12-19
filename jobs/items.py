# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags

class JobOffer(scrapy.Item):
    title = scrapy.Field(input_processor= MapCompose(lambda x: x.strip()), output_processor=TakeFirst())
    company = scrapy.Field(input_processor= MapCompose(lambda x: x.strip()), output_processor=TakeFirst())
    place  = scrapy.Field(input_processor= MapCompose(lambda x: x.strip()), output_processor=TakeFirst())
    posted_at = scrapy.Field(input_processor= MapCompose(lambda x: x.strip()), output_processor=TakeFirst())
    applicants = scrapy.Field(input_processor=MapCompose(lambda x: int(x)), output_processor=TakeFirst())
    description = scrapy.Field(input_processor= MapCompose(remove_tags, lambda x: x.strip()), output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
