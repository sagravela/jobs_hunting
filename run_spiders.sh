#!/bin/bash

JOB=${1:-'data science'}

# Set up the env
source .venv/bin/activate

# Start postgresql db
sudo service postgresql start

# Run the automated browser with nodriver
python zendriver_crawl/main.py -s "$JOB"

# Go to scrapy project folder
cd scrapy_crawl/

# Run the Scrapy spiders
scrapy crawl trabajo_spider -a job="$JOB"
scrapy crawl linkedin_spider -a job="$JOB"
