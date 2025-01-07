# Job Scraper App
The Job Scraper App is a tool designed to connect to various job websites and retrieve job offer information to further analysis and consumption. The app leverages the *Scrapy* framework to efficiently scrape job listings and save them to a PostgreSQL database to further consume data through SQL queries (for instance, filter and sort offers based on user requirements).

## Usage
Help:
```bash
python search_jobs.py --help
```

Searching for jobs:
```bash
python search_jobs.py --search search_term --location location
```
> The command above will run Scrapy with all the spiders already declared.

Where:
- `--search_term` is the job title or keyword to search for.
- `--location` is the location to search for the job.

Spider can be runned standalone by Scrapy CLI:
```bash
scrapy crawl spider_name -a job=job_name -a location=location -O file_name.format
```
This will run only the selected spider standalone.

## Further Improvements
- Add support for different job websites: this can be done adding new spiders by new web site and concatenating the results.
- Improve performance: the app can scrape data faster by decreasing `DOWNLOAD_DELAY` and deactivating `AUTOTHROTTLE_ENABLED` but it will require more resources to avoid getting blocked by the website. For instance, including proxy services. 
