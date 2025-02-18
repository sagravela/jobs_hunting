import logging
from datetime import datetime, timedelta
import re

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(funcName)s - %(levelname)s - %(message)s",
)

def parse_to_date(timedelta_str: str) -> datetime:
    """Parse timedelta string to `datetime`."""
    # Extract numbers and units using regex
    pattern = r"(\d+)\s*(d|h|m|s)"
    match = re.search(pattern, timedelta_str)

    # Initialize a timedelta
    delta = timedelta()

    # Map extracted values to timedelta
    value, unit = match.group(1), match.group(2)
    value = int(value)
    if unit == "d":
        delta += timedelta(days=value)
    elif unit == "h":
        delta += timedelta(hours=value)
    elif unit == "m":
        delta += timedelta(minutes=value)
    elif unit == "s":
        delta += timedelta(seconds=value)

    # Get timestamp
    return datetime.now() - delta