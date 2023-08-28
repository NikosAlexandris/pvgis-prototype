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
from datetime import time
from typing import Annotated
from typing import Optional
from typing import Union
import calendar
import random
# import time
import typer
import zoneinfo
from zoneinfo import ZoneInfo
from rich import print

from pvgisprototype.api.named_tuples import generate


def parse_timestamp(timestamp_string):
    if timestamp_string:
        formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%Y-%m', '%Y']
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_string, fmt)
            except ValueError:
                pass
        raise ValueError(f"Invalid timestamp format: {timestamp_string}")
    else:
        return None


def now_local_datetimezone():
    """Get current local date and time and zone
    """
    print('[yellow]i[/yellow] Runnning the now_local_datetimezone() function!')
    return datetime.now().astimezone()


def now_utc_datetimezone() -> datetime:
    """Returns the current datetime in UTC.

    Return an aware timestamp using the local system time, however defaulting
    to UTC timezone. 
    """
    return datetime.now(ZoneInfo('UTC'))


def attach_requested_timezone(
        timestamp: datetime,
        timezone: ZoneInfo = None
    ) -> datetime:
    """Attaches the requested timezone to a naive datetime."""

    print(f'[green]i[/green] Callback function attach_requested_timezone()')

    if timestamp.tzinfo is not None:
        print("  [yellow]>[/yellow] The provided timestamp already has a timezone.")  
        print("  [yellow]>[/yellow] Ensure the timestamp is provided as a [yellow]naive[/yellow] datetime object.")
        return timestamp

    if timezone is None:
        timezone_aware_timestamp = timestamp.replace(tzinfo=ZoneInfo('UTC'))
        print(f'  [yellow]i[/yellow] Timezone not requested! Set to [red]{timezone_aware_timestamp.tzinfo}[/red].') 

    else:
        try:
            print(f'[yellow]i[/yellow] Attaching the {timezone} to the {timestamp}')  
            timezone_aware_timestamp = timestamp.replace(tzinfo=timezone)

        except Exception as e:
            print(f'[red]x[/red] Failed to attach the requested timezone \'{timezone}\' to the timestamp: {e}!')
            print("[red]Defaulting to UTC timezone.[/red]")
            timezone_aware_timestamp = timestamp.replace(tzinfo=ZoneInfo('UTC'))

    return timezone_aware_timestamp


def ctx_attach_requested_timezone(
        ctx: typer.Context,
        timestamp: datetime,
        param: typer.CallbackParam
    ) -> datetime:
    """Returns the current datetime in the user-requested timezone."""

    print(f'[yellow]i[/yellow] Context: {ctx.params}')
    print(f'  [yellow]>[/yellow] Executing ctx_attach_requested_timezone()')
    timezone = ctx.params.get('timezone')
    print(f'  [yellow]>[/yellow] User defined input parameter `timezone` = {timezone}')
    print(f'  [green]>[/green] Callback function sets : {attach_requested_timezone(timestamp, timezone)}')
    return attach_requested_timezone(timestamp, timezone)


# def ctx_attach_requested_timezone(
#         ctx: typer.Context,
#         timestamp: datetime,
#         param: typer.CallbackParam,
#         # verbose: bool = False,
#     ) -> datetime:
#     """Returns the current datetime in the user-requested timezone."""

#     # if verbose:
#     print(f'[yellow]i[/yellow] Executing `ctx_attach_requested_timezone()`')
#     timezone = ctx.params.get('timezone')

#     if timestamp.tzinfo is not None:
#         # --------------------------------------------------------------------
#         print("WARNING: The provided timestamp already has a timezone.")  # Convert to warning!
#         print("Please ensure the timestamp is provided as a naive datetime object.")
#         print("Usage example: YYYY-MM-DDTHH:MM:SS or YYYY-MM-DD")
#         # --------------------------------------------------------------------
#         return timestamp

#     if timezone is None:
#         # --------------------------------------------------------------------
#         print(f'[yellow]No timezone requested! Set to[/yellow] [red]UTC[/red].')  # Convert to warning!
#         # --------------------------------------------------------------------
#         timezone_aware_timestamp = timestamp.replace(tzinfo=ZoneInfo('UTC'))

#     else:
#         try:
#             # --------------------------------------------------------------------
#             print(f'Attaching the {timezone} to the {timestamp}')  # Convert to warning!
#             # --------------------------------------------------------------------
#             timezone_aware_timestamp = timestamp.replace(tzinfo=timezone)

#         except Exception as e:
#             print(f'Failed to attach the requested timezone \'{timezone}\' to the timestamp: {e}')
#             print("Defaulting to UTC timezone.")
#             timezone_aware_timestamp = timestamp.replace(tzinfo=ZoneInfo('UTC'))

#     # if verbose:
#     #     print(f'Input timestamp    : {timestamp}')
#     #     print(f'Requested timezone : {timezone} of type \'{type(timezone)}\'')
#     #     # add verbosity...
#     return timezone_aware_timestamp


def random_day_of_year(days_in_a_year) -> int:
    """
    Generate a random datetime and timezone object
    """
    day = random.randint(1, days_in_a_year)

    return days_in_a_year


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
    timezone_str = random.choice(list(zoneinfo.available_timezones()))
    timezone = ZoneInfo(timezone_str)

    return datetimestamp, timezone


def convert_to_timezone(timezone_string: str) -> ZoneInfo:
    """Convert string to ZoneInfo object."""
    print(f'[yellow]i[/yellow] Executing convert_to_timezone()')

    if timezone_string is None:
        print(f'  [yellow]>[/yellow] No timezone requested [red]?[/red]')  # Convert to warning!
        print(f'  [yellow]>[/yellow] Setting timezone to [red]UTC[/red]')
        return ZoneInfo('UTC')

    else:
        try:
            if timezone == 'local':
                return datetime.now().astimzone(None).tzinfo

            else:
                return ZoneInfo(timezone_string)

        except (zoneinfo.ZoneInfoNotFoundError, Exception):
            print(f"  [yellow]>[/yellow] Requested zone {timezone} not found. Setting it to [red]UTC[/red].")
            return ZoneInfo('UTC')


def ctx_convert_to_timezone(ctx: typer.Context, param: typer.CallbackParam, value: str):
    """Convert string to `tzinfo` timezone object
    """
    return convert_to_timezone(value)


def attach_timezone(
        timestamp: Optional[datetime] = None,
        timezone_string: Optional[str] = None
) -> datetime:
    """Convert datetime object to timezone-aware."""
    if timestamp is None:
        timestamp = datetime.now(ZoneInfo('UTC'))  # Default to UTC

    if isinstance(timezone_string, str):
        try:
            tzinfo = convert_to_timezone(timezone_string)
            timestamp = timestamp.replace(tzinfo=tzinfo)
        except Exception as e:
            raise ValueError(f"Could not convert timezone: {e}")

    return timestamp


def convert_hours_to_seconds(hours: float):
    """
    """
    return hours * 3600


def datetime_to_decimal_hours(timestamp: float, timezone_string: str = 'UTC') -> float:
    dt = datetime.fromtimestamp(timestamp, ZoneInfo(timezone_string))
    decimal_hours = dt.hour + dt.minute / 60 + dt.second / 3600

    return decimal_hours


def convert_hours_to_datetime_time(value: float) -> time:
    if value < 0 or value > 24:
        raise typer.BadParameter(f'Value {value} is out of the expected range [0, 24] hours.')

    hours = int(value)
    minutes = int((value - hours) * 60)
    seconds = int(((value - hours) * 60 - minutes) * 60)

    return time(hours, minutes, seconds)


def timestamp_to_decimal_hours(t):
    return t.hour + t.minute / 60 + t.second / 3600 + t.microsecond / 3600000000


def timestamp_to_minutes(timestamp: datetime) -> float:
    """Convert a datetime object to minutes.

    Parameters
    ----------
    timestamp : datetime
        A datetime object.

    Returns
    -------
    float
        The equivalent number of minutes.
    """
    total_seconds = timestamp.hour * 3600 + timestamp.minute * 60 + timestamp.second
    return total_seconds / 60


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
