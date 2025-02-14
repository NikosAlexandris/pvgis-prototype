"""
Helper functions to generate random timestamps
"""

from calendar import monthrange
from datetime import datetime
from random import choice, randint
from zoneinfo import ZoneInfo, available_timezones


def random_day_of_year(days_in_year: int) -> int:
    """
    Generate a random datetime and timezone object
    """
    return randint(1, days_in_year)


def random_datetimezone() -> tuple:
    """
    Generate a random datetime and timezone object
    """
    year = datetime.now().year
    month = randint(1, 12)
    _, days_in_month = monthrange(year, month)
    day = randint(1, days_in_month)
    hour = randint(0, 23)
    minute = randint(0, 59)
    second = randint(0, 59)
    datetimestamp = datetime(
        year, month, day, hour, minute, second, tzinfo=ZoneInfo("UTC")
    )
    timezone_str = choice(list(available_timezones()))
    timezone = ZoneInfo(timezone_str)

    return datetimestamp, timezone
