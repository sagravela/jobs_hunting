# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from scrapy.exceptions import DropItem
import psycopg2

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
            raise DropItem("Job offer duplicated.")
        else:
            self.offers_seen.add(values)
            return item


class SavingToSQLPipeline:

    def __init__(self):

        # Connect to my database
        self.conn = psycopg2.connect(
            host = 'localhost',
            user='scraper',
            password='1234',
            dbname = 'jobs'
        )

        ## Create cursor, used to execute commands
        self.cur = self.conn.cursor()
        
        ## Create jobs table if none exists
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS jobs(
            id SERIAL PRIMARY KEY,                               -- Primary key for unique identification
            applied BOOLEAN DEFAULT FALSE,                       -- Flag to indicate if the job was applied to (it will be used later)
            title VARCHAR(255) NOT NULL,                         -- Job title
            company VARCHAR(255) NOT NULL,                       -- Company name
            place VARCHAR(255) NOT NULL,                         -- Job location
            posted_at DATE NOT NULL,                             -- Date when the job was posted
            applicants INT DEFAULT 0,                            -- Number of applicants
            description TEXT,                                    -- Job description
            url VARCHAR(2083) NOT NULL,                          -- URL of the job listing
            date_added DATE DEFAULT CURRENT_DATE,                -- Date when the job was added, default to current date
            CONSTRAINT unique_job UNIQUE (title, company, place) -- Unique constraint for job identification
            )"""
        )
        self.conn.commit()


    def process_item(self, item, spider):

        ## Define insert statement
        self.cur.execute("""
            INSERT INTO jobs (title, company, place, posted_at, applicants, description, url, date_added) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_DATE)
            ON CONFLICT (title, company, place) 
            DO UPDATE SET 
            posted_at = EXCLUDED.posted_at,
            applicants = EXCLUDED.applicants,
            description = EXCLUDED.description,
            url = EXCLUDED.url,
            date_added = CURRENT_DATE
            """, (
            item.get('title', None),        # Default to None if key doesn't exist
            item.get('company', None), 
            item.get('place', None), 
            item.get('posted_at', None), 
            item.get('applicants', 0),     # Default to 0 if 'applicants' is missing
            item.get('description', None), 
            item.get('url', None)
            )
        )


        ## Execute insert of data into database
        self.conn.commit()

    
    def close_spider(self, spider):

        ## Close cursor & connection to database 
        self.cur.close()
        self.conn.close()
