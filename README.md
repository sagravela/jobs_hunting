# Job Hunting App

The **Job Hunting App** is a powerful tool designed to simplify the job search process by connecting to popular job websites and retrieving relevant job listings for easy access and application.  
The app uses the **Scrapy** framework to efficiently scrape job listings from publicly available websites with minimal protection. For more challenging sites, such as those protected by Cloudflare, the app utilizes the **Zendriver** package to automate browser interactions and bypass security measures.
Scraped job data is stored in a local **PostgreSQL** database, making it available for easy consumption through the **Streamlit** web application.  
With features like job filtering, sorting, and tracking previously viewed jobs, the app ensures you never apply for the same job twice. This streamlined process helps users save time and apply more effectively.
> **Important**: Currently, the app is available for job searches only in *Argentina*. The location cannot be changed at this time due to     differences in how job websites display listings based on geographic location.  
Linkedin spider is the only one that currently supports looking for jobs in other regions. To run that spider standalone:
```bash
cd scrapy_crawl/
scrapy crawl linkedin_spider -a job=JOB -a location=LOCATION
```

## Usage
First of all, scrape for jobs in websites pulling data with the following command:  
```bash
./run_spiders.sh JOB
```

After jobs are saved to the database, run the application: 
```bash
./run_app.sh
```

