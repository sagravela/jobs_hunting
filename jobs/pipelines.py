# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from scrapy.exceptions import DropItem


class PostedAtToDatePipeline:
    """
    A pipeline that processes the 'posted_at' field of an item and converts it to a date.
    """
    def __init__(self):
        # Actual time
        self.now = datetime.now()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter.get('posted_at'):
            quantity, unit, _ = adapter.get('posted_at').split()
            quantity = int(quantity)

            # Handle singular and plural forms of units
            unit = unit.lower().rstrip('s')

            # Map unit to the appropriate timedelta or relativedelta
            if unit in ['week', 'day', 'hour', 'minute', 'second']:
                delta = timedelta(**{unit + 's': quantity})  # Use plural form for timedelta
                adapter['posted_at'] = (self.now - delta).date()
            elif unit in ['month', 'year']:
                delta = relativedelta(**{unit + 's': quantity})  # Use plural form for relativedelta
                adapter['posted_at'] = (self.now - delta).date()
            else:
                adapter['posted_at'] = ''
        return item


class RemoveDuplicatesPipeline:
    """
    A pipeline that removes duplicate items based on the 'title', 'company', and 'place' fields.
    """
    def __init__(self):
        self.offers_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        values = (adapter['title'], adapter['company'], adapter['place'])
        if values in self.offers_seen:
            raise DropItem()
        else:
            self.offers_seen.add(values)
            return item
