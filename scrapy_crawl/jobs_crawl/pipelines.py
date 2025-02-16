# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import psycopg2
from dotenv import load_dotenv


class PostedAtToDatePipeline:
    """
    A pipeline that processes the 'posted_at' field of an item and converts it to a date.
    """

    def __init__(self):
        # Actual time
        self.now = datetime.now()

        self.spain_names = {
            "año": "year",
            "mes": "month",
            "semana": "week",
            "día": "day",
            "hora": "hour",
            "minuto": "minute",
            "segundo": "second",
        }

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if spider.name == "linkedin_spider":
            adapter["posted_at"] = datetime.strptime(
                adapter["posted_at"], "%Y-%m-%d"
            ).date()
        else:
            quantity, unit = adapter.get("posted_at").split()
            quantity = int(quantity)

            # Handle singular and plural forms of units
            unit = unit.lower().rstrip("s")

            # Translate spanish units names
            if unit in self.spain_names.keys():
                unit = self.spain_names[unit]

            # Map unit to the appropriate timedelta or relativedelta
            if unit in ["week", "day", "hour", "minute", "second"]:
                delta = timedelta(
                    **{unit + "s": quantity}
                )  # Use plural form for timedelta
                adapter["posted_at"] = (self.now - delta).date()
            else:
                delta = relativedelta(
                    **{unit + "s": quantity}
                )  # Use plural form for relativedelta
                adapter["posted_at"] = (self.now - delta).date()
        return item


class RemoveDuplicatesPipeline:
    """
    A pipeline that removes duplicate items based on the 'title', 'company', and 'location' fields.
    """

    def __init__(self):
        self.offers_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        values = (adapter["title"], adapter["company"], adapter["location"])
        if values in self.offers_seen:
            raise DropItem("Job offer duplicated.")
        else:
            self.offers_seen.add(values)
            return item


class SavingToSQLPipeline:
    def __init__(self):
        load_dotenv()

        # Database URL
        PSQL_CONFIG = {
            "user": os.getenv("PSQL_USER"),
            "password": os.getenv("PSQL_PASSWORD"),
            "host": os.getenv("PSQL_HOST"),
            "dbname": os.getenv("PSQL_DB"),
        }

        # Connect to my database
        self.conn = psycopg2.connect(**PSQL_CONFIG)

        ## Create cursor, used to execute commands
        self.cur = self.conn.cursor()

        ## Create jobs table if none exists
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs(
            id SERIAL PRIMARY KEY,                               -- Primary key for unique identification
            viwed BOOLEAN DEFAULT FALSE,                         -- Flag to indicate if the job was applied to (it will be used later)
            title VARCHAR(255) NOT NULL,                         -- Job title
            company VARCHAR(255) NOT NULL,                       -- Company name
            location VARCHAR(255) NOT NULL,                      -- Job location
            posted_at DATE NOT NULL,                             -- Date when the job was posted
            added_at DATE DEFAULT CURRENT_DATE,                   -- Date when the jobs was added to the database
            url VARCHAR(2083) NOT NULL,                          -- URL of the job listing
            CONSTRAINT job UNIQUE (title, company, location)     -- Unique constraint for job identification
            )"""
        )
        self.conn.commit()

    def process_item(self, item, spider):
        ## Define insert statement
        self.cur.execute(
            """
            INSERT INTO jobs(title, company, location, posted_at, url) 
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (title, company, location) 
            DO UPDATE SET 
                added_at = CURRENT_DATE,
                url = EXCLUDED.url;
            """,
            (
                item.get("title"),
                item.get("company"),
                item.get("location"),
                item.get("posted_at"),
                item.get("url"),
            ),
        )

        ## Execute insert of data into database
        self.conn.commit()

    def close_spider(self, spider):
        ## Close cursor & connection to database
        self.cur.close()
        self.conn.close()
