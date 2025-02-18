import os
import logging

from scrapy import logformatter


class PoliteLogFormatter(logformatter.LogFormatter):
    """Custom log formatter for logging. This one overrides the default log for dropped items to DEBUG level, ensuring less verbosity."""
    # override the default dropped item log
    def dropped(self, item, exception, response, spider):
        return {
            "level": logging.DEBUG,  # lowering the level from logging.WARNING
            "msg": "Dropped: %(exception)s" + os.linesep + "%(item)s",
            "args": {
                "exception": exception,
                "item": item,
            },
        }
