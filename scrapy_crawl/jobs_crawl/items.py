# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

from itemloaders.processors import MapCompose, TakeFirst


class JobOffer(scrapy.Item):
    title = scrapy.Field(
        input_processor=MapCompose(lambda x: x.strip()), output_processor=TakeFirst()
    )
    company = scrapy.Field(
        input_processor=MapCompose(lambda x: x.strip()), output_processor=TakeFirst()
    )
    location = scrapy.Field(
        input_processor=MapCompose(lambda x: x.strip()), output_processor=TakeFirst()
    )
    posted_at = scrapy.Field(
        input_processor=MapCompose(lambda x: x.strip()), output_processor=TakeFirst()
    )
    url = scrapy.Field(output_processor=TakeFirst())
