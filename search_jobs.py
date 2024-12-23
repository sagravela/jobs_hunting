from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import argparse
import logging


def main():
    parser = argparse.ArgumentParser(description="Filter jobs based on a role and optionally additional keywords given by 'keywords.txt' file.")
    parser.add_argument('-s', '--search', type=str, required=True, help='Job search keyword')
    parser.add_argument('-l', '--location', type=str, required=True, help='Location to search jobs')

    args = parser.parse_args()
    job = args.search
    location = args.location

    # Set up Scrapy Settings
    settings = get_project_settings()
    # Disable some Scrapy INFO loggers to avoid flooding the console
    settings.update({'LOG_LEVEL': 'INFO'})
    process = CrawlerProcess(settings=settings)

    # Linkedin spider
    logging.info("Starting the crawler process in Linkedin searching for {} in {}".format(job, location))
    process.crawl("Linkedin", job=job, location=location)
    # Add more spiders ...

    # Start the crawler
    process.start() 


if __name__ == '__main__':
    main()