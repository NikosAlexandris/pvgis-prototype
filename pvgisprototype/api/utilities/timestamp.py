import typer
from typing import Annotated
from typing import Optional

from datetime import datetime
from datetime import timedelta
from datetime import timezone
import pytz
from tzlocal import get_localzone
import calendar
import time
import random


def now_datetime():
    """
    """
    return datetime.now().astimezone()


def random_datetimezone():
    """
    Generate a random datetime and timezone object
    """
    year = datetime.now().year
    month = random.randint(1, 12)
    _, days_in_month = calendar.monthrange(year, month)
    day = random.randint(1, days_in_month)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    datetimestamp = datetime(year, month, day, hour, minute, second)
    timezone_str = random.choice(pytz.all_timezones)
    timezone = pytz.timezone(timezone_str)
    # datetimezone = timezone.localize(datetimestamp)

    return datetimestamp, timezone


def timestamp_to_decimal_hours(timestamp, timezone='UTC'):
    dt = datetime.fromtimestamp(timestamp, pytz.timezone(timezone))
    decimal_hours = dt.hour + dt.minute / 60 + dt.second / 3600

    return decimal_hours


def convert_hours_to_seconds(hours: float):
    """
    """
    return hours * 3600


def convert_to_timezone(string: str):
    """Convert string to `tzinfo` timezone object
    """
    if string is None:
        tzinfo = pytz.timezone('UTC')

    elif isinstance(string, str):
        if string == "local":
            try:
                tzinfo = get_localzone()
            except Exception:
                tzinfo = pytz.timezone('UTC')
                typer.echo("Unable to determine local timezone. Defaulting to UTC.")
        else:
            try:
                tzinfo = pytz.timezone(string)
            except pytz.UnknownTimeZoneError:
                typer.echo(f"Unknown timezone: {string}. Please input a valid timezone.")
                raise typer.Exit(code=1)
    # if input is not a string, it _should_ be a `tzinfo` object
    else:  
        tzinfo = string

    return tzinfo


def ctx_convert_to_timezone( ctx: typer.Context, param: typer.CallbackParam, value: str):
    """Convert string to `tzinfo` timezone object
    """
    return convert_to_timezone(value)


def attach_timezone(
        timestamp: Optional[datetime] = None,
        timezone: Optional[str] = None
        ) -> datetime:
    """Convert datetime object to timezone-aware.
    """
    if timestamp is None:
        timestamp = datetime.utcnow()  # Default to UTC

    if isinstance(timezone, str):
        try:
            tzinfo = convert_to_timezone(timezone)
        except Exception as e:
            raise ValueError(f"Could not convert timezone: {e}")
    else:  # If timezone is not a string, it should be a datetime.tzinfo object
        tzinfo = timezone
    
    timestamp = timestamp.replace(tzinfo=pytz.UTC).astimezone(tzinfo)

    return timestamp


def get_day_from_hour_of_year(year: int, hour_of_year: int):
    """Get day of year from hour of year."""
    start_of_year = np.datetime64(f'{year}-01-01')
    date_and_time = start_of_year + np.timedelta64(hour_of_year, 'h')
    date_and_time = date_and_time.astype(datetime.datetime)
    day_of_year = int(date_and_time.strftime('%j'))
    # month = int(date_and_time.strftime('%m'))  # Month
    # day_of_month = int(date_and_time.strftime('%d'))
    # hour_of_day = int(date_and_time.strftime('%H'))

    return day_of_year


def hour_of_year_to_datetime(year, hour):
    start_of_year = datetime.datetime(year, 1, 1)
    timedelta_hours = datetime.timedelta(hours=hour)
    desired_datetime = start_of_year + timedelta_hours

    return desired_datetime
