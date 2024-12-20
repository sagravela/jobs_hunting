from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import argparse
import csv
import logging
import re

class JobSearch:
    def __init__(self) -> None:
        parser = argparse.ArgumentParser(description="Filter jobs based on a role and optionally additional keywords given by 'keywords.txt' file.")
        parser.add_argument('-s', '--search', type=str, required=True, help='Job search keyword')
        parser.add_argument('-l', '--location', type=str, required=True, help='Location to search jobs')

        args = parser.parse_args()
        self.job = args.search
        self.location = args.location
        self.keywords = []
        self.file_name = f'{self.job.replace(" ", "-")}-{self.location.replace(" ", "-")}'.lower()
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
        
        # Read new jobs
        with open(f'{self.file_name}.csv', 'r') as jobs_file:
            jobs = list(csv.DictReader(jobs_file))

        # Read old jobs if provided
        try:
            with open(f'fs-{self.file_name}.csv', 'r') as old_jobs_file:
                old_jobs = list(csv.DictReader(old_jobs_file))
                old_jobs = [(job['title'], job['company'], job['place']) for job in old_jobs if job['applied'] == 'Y']
                logging.info(f"Identified {len(old_jobs)} applied jobs.")
        except FileNotFoundError:
            old_jobs = []
            logging.warning("No old jobs file found. Skipping filtering based on old jobs.")
        
        # Read keywords if provided
        try:
            with open('keywords.txt', 'r') as keywords_file:
                self.keywords = [line.strip() for line in keywords_file.readlines()]
                logging.info(f"Filtering jobs based on keywords: {self.keywords}.")
        except FileNotFoundError:
            logging.warning("No keywords file found. Skipping filtering based on keywords")

        # Filter jobs
        filtered_jobs = self.filter_jobs(jobs, old_jobs)

        # Sort jobs by applicants and date posted
        logging.info("Sorting jobs by applicants and date posted.")
        sorted_jobs = self.sort_jobs(filtered_jobs)
        
        self.save_jobs(sorted_jobs)
        
    def filter_jobs(self, jobs, old_jobs):
        def filter_offer(x):
            # Filter old jobs
            job = (x['title'], x['company'], x['place'])
            if job in old_jobs:
                return False

            # Filter job offers based on keywords
            pattern = r'\b(' + '|'.join(re.escape(keyword) for keyword in self.keywords) + r')\b'
            match = re.search(pattern, x['title'], re.IGNORECASE)
            return bool(match)

        # Remove old jobs from the new jobs
        logging.info("Removing old jobs and filtering by keywords if provided.")
        filtered_jobs = list(filter(filter_offer, jobs))
        logging.info(f"{len(filtered_jobs)} jobs kept out of {len(jobs)}")
        return filtered_jobs

    def sort_jobs(self, jobs):
        # Sort jobs by applicants and date posted
        sorted_jobs = sorted(jobs, key=lambda x: (-int(x['applicants']), x['posted_at']), reverse=True)
        return sorted_jobs

    def save_jobs(self, jobs):
        with open(f'fs-{self.file_name}.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['applied'] + self.fields)
            writer.writeheader()
            for job in jobs:
                job['applied'] = 'N'
                writer.writerow(job)
        
        logging.info(f"Filtered and sorted jobs saved to fs-{self.file_name}.csv")

            
if __name__ == '__main__':
    JobSearch()
