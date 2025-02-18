# Job Hunting App

The **Job Hunting App** is a powerful tool designed to simplify the job search process by connecting to popular job websites and retrieving relevant job listings for easy access and application.  
The app uses the **Scrapy** framework to efficiently scrape job listings from publicly available websites with minimal protection. For more challenging sites, such as those protected by Cloudflare, the app utilizes the **Zendriver** package to automate browser interactions and bypass security measures.
Scraped job data is stored in a local **PostgreSQL** database, making it available for easy consumption through the **Streamlit** web application.  
With features like job filtering, sorting, and tracking previously viewed jobs, the app ensures you never apply for the same job twice. This streamlined process helps users save time and apply more effectively.  
![Job Hunting App in Action](assets/jobs_hunting_demo.gif)  

> **Important**: Currently, the app is available for job searches only in *Argentina*. The location cannot be changed at this time due to     differences in how job websites display listings based on geographic location.  
Linkedin spider is the only one that currently supports looking for jobs in other regions. To run that spider standalone:
```bash
cd scrapy_crawl/
scrapy crawl linkedin_spider -a job=JOB -a location=LOCATION
```

## Usage
Set up a PostgreSQL database and add the credentials to the `.env` file. Names are: `PSQL_USER`, `PSQL_PASSWORD`, `PSQL_DB`, `PSQL_HOST`. Other types of databases are not supported.  
Scrape for jobs in websites pulling data with the following command:  
```bash
./run_spiders.sh JOB
```
> It is possible to run each spider separately, inspect `run_spiders.sh` for details.

After jobs are saved to the database, run the application: 
```bash
./run_app.sh
```
Follow the output instructions to open the app.
