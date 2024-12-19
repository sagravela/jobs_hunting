from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import argparse
import csv
import logging
import re

class JobSearch:
    def __init__(self) -> None:
        parser = argparse.ArgumentParser(description="Filter jobs based on a role and optionally additional keywords. Then save it as 'filtered_jobs_offers.csv'.")
        parser.add_argument('-s', '--search', type=str, required=True, help='Job search keyword')
        parser.add_argument('-l', '--location', type=str, required=True, help='Location to search jobs')
        parser.add_argument(
            '-k',
            '--keywords', 
            nargs= '+',
            help='Additional keywords to filter offers. It will select offers if ANY of the job + keywords are in the title + description job offer.'
        )

        args = parser.parse_args()
        self.job = args.search
        self.location = args.location
        self.keywords = args.keywords
        self.file_name = f'{self.job.replace(" ", "-")}-{self.location.replace(" ", "-")}'
        self.fields = ['title', 'company', 'place', 'posted_at', 'applicants', 'url', 'description']

        # Set up Scrapy Settings
        settings = get_project_settings()
        settings.update({
            'FEEDS': {
                f'{self.file_name}.csv': {
                    'format': 'csv',
                    'encoding': 'utf8',
                    'overwrite': True,
                    'store_empty': False,
                    'fields': self.fields,
                },
            },
            # Disable some Scrapy INFO loggers to avoid flooding the console
            'LOG_LEVEL': 'INFO',
        })
        process = CrawlerProcess(settings=settings)

        # Linkedin spider
        logging.info("Starting the crawler process in Linkedin searching for {} in {}".format(self.job, self.location))
        process.crawl("Linkedin", job=self.job, location=self.location)
        # Add more spiders ...

        # Start the crawler
        process.start()
        
        # Filter jobs
        logging.info(f"Filtering jobs based on keywords: {[self.job] + self.keywords}.")
        filtered_jobs = self.filter_jobs()

        # Sort jobs by applicants and date posted
        logging.info("Sorting jobs by applicants and date posted.")
        sorted_jobs = self.sort_jobs(filtered_jobs)
        
        self.save_jobs(sorted_jobs)
        
    def filter_jobs(self):
        with open(f'{self.file_name}.csv', 'r') as file:
            jobs = list(csv.DictReader(file))
        
        def filter_offer(x):
            # Filter job offers based on keywords
            pattern = r'\b(' + '|'.join(re.escape(keyword) for keyword in self.keywords) + r')\b'
            match = re.search(pattern, f"{x['title']} {x['description']}", re.IGNORECASE)
            return bool(match)

        filtered_jobs = list(filter(filter_offer, jobs))
        logging.info(f"{len(filtered_jobs)} jobs kept out of {len(jobs)}")
        return filtered_jobs

    def sort_jobs(self, jobs):
        # Sort jobs by applicants and date posted
        sorted_jobs = sorted(jobs, key=lambda x: (-int(x['applicants']), x['posted_at']), reverse=True)
        return sorted_jobs

    def save_jobs(self, jobs):
        with open(f'fs-{self.file_name}.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=self.fields)
            writer.writeheader()
            for job in jobs:
                writer.writerow(job)
        
        logging.info(f"Filtered and sorted jobs saved to fs-{self.file_name}.csv")

            
if __name__ == '__main__':
    JobSearch()
