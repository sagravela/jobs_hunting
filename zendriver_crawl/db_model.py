from datetime import datetime
import os

from pydantic import BaseModel, HttpUrl
import psycopg2
from dotenv import load_dotenv


class Job(BaseModel):
    company: str
    title: str
    location: str
    posted_at: datetime
    link: HttpUrl


def setup_db():
    """Connect to the database"""
    load_dotenv()

    # Database URL
    PSQL_CONFIG = {
        "user": os.getenv("PSQL_USER"),
        "password": os.getenv("PSQL_PASSWORD"),
        "host": os.getenv("PSQL_HOST"),
        "dbname": os.getenv("PSQL_DB"),
    }

    # Connect to my database
    conn = psycopg2.connect(**PSQL_CONFIG)

    # Create cursor, used to execute commands
    cur = conn.cursor()

    # Create jobs table if none exists
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs(
        id SERIAL PRIMARY KEY,                                       -- Primary key for unique identification
        viewed BOOLEAN DEFAULT FALSE,                                -- Flag to indicate if the job was applied to (it will be used later)
        title VARCHAR(255) NOT NULL,                                 -- Job title
        company VARCHAR(255),                                        -- Company name
        location VARCHAR(255),                                       -- Job location
        posted_at DATE,                                              -- Date when the job was posted
        added_at DATE DEFAULT CURRENT_DATE,                          -- Date when the jobs was added to the database
        url VARCHAR(2083) NOT NULL,                                  -- URL of the job listing
        CONSTRAINT job UNIQUE (title, company, location) -- Unique constraint for job identification
        )"""
    )
    conn.commit()
    return conn, cur


def save_to_db(conn, cur, offers) -> None:
    """Save offers to database"""
    for offer in offers:
        cur.execute(
            """
            INSERT INTO jobs(title, company, location, posted_at, url) 
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (title, company, location) 
            DO UPDATE SET 
                added_at = CURRENT_DATE,
                url = EXCLUDED.url;
            """,
            (
                offer.get("title"),
                offer.get("company", None),
                offer.get("location", None),
                offer.get("posted_at", None),
                str(offer.get("link")),
            ),
        )
    conn.commit()
