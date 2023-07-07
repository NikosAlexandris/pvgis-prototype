import typer
from typing import Annotated
from typing import Optional
"""
Date, time and zones
--------------------

By default, input timestamps will default to the Coordinated Universal Time
(UTC) unless a user explicitly requests another or the system's local time and
zone. Regardless, all timestamps will convert internally to UTC. The rationale
behind this design decision is:

- UTC provides an unambiguous reference point as it does not observe Daylight
Saving Time (DST) which may bring in various complexities.

- UTC is a standard used worldwide, making it a safer choice for
interoperability.

- Using UTC can avoid issues when a server/system's local time zone may not be
  under control.

- While the software allows users to to specify their time zone if they wish,
  internally all timestamps will convert to UTC internally and only convert
  back to the user's time zone when displaying the time to the user.


Things to keep in mind:

> From: https://blog.ganssle.io/articles/2022/04/naive-local-datetimes.html

- The local offset may change during the course of the interpreter run.

- You can use datetime.astimezone with None to convert a naïve time into an
  aware datetime with a fixed offset representing the current system local
  time.

- All arithmetic operations should be applied to naïve datetimes when working
  in system local civil time — only call .astimezone(None) when you need to
  represent an absolute time, e.g. for display or comparison with aware
  datetimes.[3]


Read also:

- https://peps.python.org/pep-0615/
"""

from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Annotated
from typing import Optional
from tzlocal import get_localzone
import calendar
import random
import time
import typer
import zoneinfo
from zoneinfo import ZoneInfo
from rich import print


app = typer.Typer()


def now_datetime() -> datetime:
    """Returns the current datetime in UTC.

    Return an aware timestamp using the local system time, however defaulting
    to UTC timezone. 
    """
    return datetime.now(ZoneInfo('UTC'))


def ctx_attach_requested_timezone(
        ctx: typer.Context,
        timestamp: datetime,
        param: typer.CallbackParam,
        # verbose: bool = False,
    ) -> datetime:
    """Returns the current datetime in the user-requested timezone."""

    timezone = ctx.params.get('timezone')
    if timestamp.tzinfo is not None:
        # --------------------------------------------------------------------
        print("WARNING: The provided timestamp already has a timezone.")  # Convert to warning!
        print("Please ensure the timestamp is provided as a naive datetime object.")
        print("Usage example: YYYY-MM-DDTHH:MM:SS or YYYY-MM-DD")
        # --------------------------------------------------------------------
        return timestamp

    if timezone is None:
        # --------------------------------------------------------------------
        print('No timezone requested. Setting timezone to UTC.')  # Convert to warning!
        # --------------------------------------------------------------------
        timezone_aware_timestamp = timestamp.replace(tzinfo=ZoneInfo('UTC'))

    else:
        try:
            # --------------------------------------------------------------------
            print(f'Attaching the {timezone} to the {timestamp}')  # Convert to warning!
            # --------------------------------------------------------------------
            timezone_aware_timestamp = timestamp.replace(tzinfo=timezone)

        except Exception as e:
            print(f'Failed to attach the requested timezone \'{timezone}\' to the timestamp: {e}')
            print("Defaulting to UTC timezone.")
            timezone_aware_timestamp = timestamp.replace(tzinfo=ZoneInfo('UTC'))
    # if verbose:
    #     print(f'Input timestamp    : {timestamp}')
    #     print(f'Requested timezone : {timezone} of type \'{type(timezone)}\'')
    #     # add verbosity...
    return timezone_aware_timestamp


def random_datetimezone() -> tuple:
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
    datetimestamp = datetime(year, month, day, hour, minute, second, tzinfo=ZoneInfo('UTC'))
    timezone_str = random.choice(list(ZoneInfo.available_timezones()))
    timezone = ZoneInfo(timezone_str)

    return datetimestamp, timezone


def convert_to_timezone(timezone_string: str) -> ZoneInfo:
    """Convert string to ZoneInfo object."""


    if timezone_string is None:
        print(f'Setting timezone to UTC')
        return ZoneInfo('UTC')

    else:
        try:
            if timezone == 'local':
                return datetime.now().astimzone(None).tzinfo

            else:
                return ZoneInfo(timezone_string)

        except (zoneinfo.ZoneInfoNotFoundError, Exception):
            print(f"Requested zone {timezone} not found. Setting it to UTC.")
            return ZoneInfo('UTC')


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


def convert_hours_to_seconds(hours: float):
    """
    """
    return hours * 3600


def timestamp_to_decimal_hours(timestamp: float, timezone_string: str = 'UTC') -> float:
    dt = datetime.fromtimestamp(timestamp, ZoneInfo(timezone_string))
    decimal_hours = dt.hour + dt.minute / 60 + dt.second / 3600

    return decimal_hours


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
