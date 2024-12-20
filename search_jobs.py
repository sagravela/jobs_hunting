from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import argparse
import csv
import logging
import re
import os


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
        
        if not os.path.exists('output'):
            os.makedirs('output')
        if not os.path.exists(os.path.join('output', self.file_name)):
            os.makedirs(os.path.join('output', self.file_name))

        self.jobs_path = os.path.join('output', self.file_name, 'jobs.csv')
        self.applied_path = os.path.join('output', self.file_name, f'applied_jobs.csv')
        self.fs_path = os.path.join('output', self.file_name, f'filtered_sorted_jobs.csv')
        self.fields = ['title', 'company', 'place', 'posted_at', 'applicants', 'url', 'description']
        self.applied_fields = ['applied'] + self.fields


        # Set up Scrapy Settings
        settings = get_project_settings()
        settings.update({
            'FEEDS': {
                self.jobs_path: {
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
        with open(self.jobs_path, 'r') as jobs_file:
            jobs = list(csv.DictReader(jobs_file))

        # Read old jobs if provided
        try:
            with open(self.fs_path, 'r') as old_jobs_file:
                old_jobs = list(csv.DictReader(old_jobs_file))
            
            applied_jobs = [job for job in old_jobs if job['applied'] == 'Y']
            
            # Save applied jobs to avoid reapplying
            with open(self.applied_path, 'a') as applied_file:
                writer = csv.DictWriter(applied_file, fieldnames=self.applied_fields)
                for job in applied_jobs:
                    writer.writerow(job)

            with open(self.applied_path, 'r') as applied_file:
                full_applied_jobs = [
                    (job['title'], job['company'], job['place']) for job in list(csv.DictReader(applied_file, fieldnames=self.applied_fields))
                ]
            
            logging.info(
                f"Identified {len(applied_jobs)} applied jobs." + \
                f" Saving them to avoid reapplying in {self.applied_path}."
            )
            
        except FileNotFoundError:
            full_applied_jobs = []
            logging.warning("No old jobs file found. Skipping filtering based on old jobs.")
        
        # Read keywords if provided
        try:
            with open('keywords.txt', 'r') as keywords_file:
                lines = [line.strip() for line in keywords_file.readlines() if re.search(r'\w', line)]
                include_index = lines.index('Include:') + 1
                exclude_index = lines.index('Exclude:') + 1
                self.key_include = lines[include_index:exclude_index - 1]
                self.key_exclude = lines[exclude_index:]
                logging.info(f"Keywords to be included: {self.key_include}.")
                logging.info(f"Keywords to be excluded: {self.key_exclude}.")
        except FileNotFoundError:
            logging.warning("No keywords file found. Skipping filtering based on keywords")

        # Filter jobs
        filtered_jobs = self.filter_jobs(jobs, full_applied_jobs)

        # Sort jobs by applicants and date posted
        logging.info("Sorting jobs by applicants and date posted.")
        sorted_jobs = self.sort_jobs(filtered_jobs)
        
        self.save_jobs(sorted_jobs)
        
    def filter_jobs(self, jobs, fa_jobs):
        def filter_offer(x):
            # Filter old jobs
            job = (x['title'], x['company'], x['place'])
            if job in fa_jobs:
                return False

            # Filter job offers based on keywords
            # Include keywords
            pattern_include = r'\b(' + '|'.join(self.key_include) + r')\b'
            match_include = re.search(pattern_include, x['title'], re.IGNORECASE)

            # Exclude keywords
            pattern_exclude = r'\b(' + '|'.join(self.key_exclude) + r')\b'
            match_exclude = re.search(pattern_exclude, x['title'], re.IGNORECASE)

            return bool(match_include and not match_exclude)

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
        with open(self.fs_path, 'w') as file:
            writer = csv.DictWriter(file, fieldnames=self.applied_fields)
            writer.writeheader()
            for job in jobs:
                job['applied'] = 'N'
                writer.writerow(job)
        
        logging.info(f"Filtered and sorted jobs saved to fs-{self.file_name}.csv")

            
if __name__ == '__main__':
    JobSearch()
