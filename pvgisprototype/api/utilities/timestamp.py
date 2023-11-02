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
from typing import List
from typing import Sequence
import calendar
import random
# import time
import typer
import zoneinfo
from zoneinfo import ZoneInfo
from rich import print
import numpy as np
from pvgisprototype.constants import TIMESTAMPS_FREQUENCY_DEFAULT


# Random time

def random_day_of_year(days_in_year: int) -> int:
    """
    Generate a random datetime and timezone object
    """
    return random.randint(1, days_in_year)


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


# Time

def now_local_datetimezone():
    """Get current local date and time and zone
    """
    print('[yellow]i[/yellow] Runnning the now_local_datetimezone() function!')
    return datetime.now().astimezone()


# Timezone

def now_utc_datetimezone() -> datetime:
    """Returns the current datetime in UTC.

    Return an aware timestamp using the local system time, however defaulting
    to UTC timezone. 
    """
    return datetime.now(ZoneInfo('UTC'))


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


def attach_requested_timezone(
        timestamp: datetime,
        timezone: ZoneInfo = None
    ) -> datetime:
    """Attaches the requested timezone to a naive datetime."""

    print(f'[green]i[/green] Callback function attach_requested_timezone()')

    if timestamp.tzinfo is not None:  # time zone already set
        print("  [yellow]>[/yellow] The provided timestamp already has a timezone.")  
        print("  [yellow]>[/yellow] Ensure the timestamp is provided as a [yellow]naive[/yellow] datetime object.")
        return timestamp

    if timezone is None:
        timezone_aware_timestamp = timestamp.replace(tzinfo=ZoneInfo('UTC'))
        print(f'  [yellow]i[/yellow] Timezone not requested! Set to [red]{timezone_aware_timestamp.tzinfo}[/red].') 

    else:
        try:
            print(f'[yellow]i[/yellow] Attaching the requested zone [bold]{timezone}[/bold] to {timestamp}')  
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
    print(f'[yellow]i[/yellow] typer.CallbackParam: {param}')
    print(f'  [yellow]>[/yellow] Executing ctx_attach_requested_timezone()')
    timezone = ctx.params.get('timezone')
    print(f'  [yellow]>[/yellow] User requested input parameter [code]timezone[/code] = [bold]{timezone}[/bold]')
    print(f'  [green]>[/green] Callback function returns : {attach_requested_timezone(timestamp, timezone)}')
    return attach_requested_timezone(timestamp, timezone)


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


# Conversions

def convert_hours_to_seconds(hours: float):
    """
    """
    return hours * 3600


def convert_hours_to_datetime_time(value: float) -> time:
    if value < 0 or value > 24:
        raise typer.BadParameter(f'Value {value} is out of the expected range [0, 24] hours.')

    hours = int(value)
    minutes = int((value - hours) * 60)
    seconds = int(((value - hours) * 60 - minutes) * 60)

    return time(hours, minutes, seconds)


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


def timestamp_to_decimal_hours(t):  # NOTE: Integrated in dateclasses
    return t.hour + t.minute / 60 + t.second / 3600 + t.microsecond / 3600000000


def timestamp_to_decimal_hours_time_series(
    timestamps: Union[datetime, Sequence[datetime]]
) -> np.ndarray:
    if isinstance(timestamps, datetime):
        timestamps = [timestamps]

    timestamps_array = np.array(timestamps)
    hours = (timestamps_array.astype('datetime64[h]') - timestamps_array.astype('datetime64[D]')).astype('timedelta64[h]').astype(float)
    minutes = (timestamps_array.astype('datetime64[m]') - timestamps_array.astype('datetime64[h]')).astype('timedelta64[m]').astype(float) / 60
    seconds = (timestamps_array.astype('datetime64[s]') - timestamps_array.astype('datetime64[m]')).astype('timedelta64[s]').astype(float) / 3600
    microseconds = (timestamps_array.astype('datetime64[us]') - timestamps_array.astype('datetime64[s]')).astype('timedelta64[us]').astype(float) / 3600000000

    return hours + minutes + seconds + microseconds


def hour_of_year_to_datetime(year, hour):
    start_of_year = datetime.datetime(year, 1, 1)
    timedelta_hours = datetime.timedelta(hours=hour)
    desired_datetime = start_of_year + timedelta_hours

    return desired_datetime


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


# Single timestamp

def parse_timestamp(
    ctx: typer.Context,
    timestamp_string: str,
    param: typer.CallbackParam,
) -> datetime:
    print(f'[yellow]i[/yellow] Context: {ctx}')
    print(f'[yellow]i[/yellow] Context: {ctx.params}')
    print(f'[yellow]i[/yellow] typer.CallbackParam: {param}')
    # if timestamp_string:
    #     formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%Y-%m', '%Y']
    #     for fmt in formats:
    #         try:
    #             return datetime.strptime(timestamp_string, fmt)
    #         except ValueError:
    #             pass
    #     raise ValueError(f"Invalid timestamp format: {timestamp_string}")
    # else:
    #     return None
    from pandas import to_datetime
    return to_datetime(timestamp_string, errors='raise')


# Time series

def get_days_in_year(year):
    """ Calculate the number of days in a given year, accounting for leap years.

    Parameters
    ----------
    year : int
        The year for which to calculate the number of days.

    Returns
    -------
    int
        The number of days in the given year.

    Examples
    --------
    >>> get_days_in_year(2020)
    366

    >>> get_days_in_year(2021)
    365
    """
    start_date = datetime(year, 1, 1)  # First day of the year
    end_date = datetime(year + 1, 1, 1)  # First day of the next year
    return (end_date - start_date).days


def parse_timestamp_series(
    # ctx: typer.Context,
    timestamps: Union[str, datetime, List[datetime]],
    # param: typer.CallbackParam,
):
    # print(f"[yellow]i[/yellow] Context: {ctx}")
    # print(f"[yellow]i[/yellow] Context: {ctx.params}")
    # print(f"[yellow]i[/yellow] typer.CallbackParam: {param}")
    print(f"[yellow]i[/yellow] Executing parse_timestamp_series()")
    # print(f"  Input [yellow]timestamps[/yellow] : {timestamps}")
    # print(f"  Type : {type(timestamps)}")

    if isinstance(timestamps, str):
        datetime_strings = timestamps.strip().split(",")
        # print(f"  Returning : {datetime_strings}")
        return datetime_strings  # List of strings

    if isinstance(timestamps, datetime):
        return_value = [timestamps]
        # print(f"  Returning : {return_value}")
        return [timestamps]  # return a list in case of a single datetime object

    if isinstance(timestamps, list):
        datetime_strings = [string.strip() for string in timestamps]
        # print(f"Returning: {datetime_strings}")
        return datetime_strings


def generate_timestamps_for_a_year(year, frequency_minutes=60):
    start_date = datetime(year, 1, 1)
    days_in_year = get_days_in_year(year)
    end_date = start_date + timedelta(days=days_in_year)
    total_minutes = int((end_date - start_date).total_seconds() // 60)
    intervals = total_minutes // frequency_minutes
    
    return [start_date + timedelta(minutes=(idx * frequency_minutes)) for idx in range(intervals)]


def generate_datetime_series(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    frequency: Optional[str] = TIMESTAMPS_FREQUENCY_DEFAULT,
):
    """
    Example
    -------
    >>> start_time = '2010-06-01 06:00:00'
    >>> end_time = '2010-06-01 08:00:00'
    >>> frequency = 'h'  # 'h' for hourly
    >>> generate_datetime_series(start_time, end_time, frequency)
    array(['2010-06-01T06:00:00', '2010-06-01T07:00:00', '2010-06-01T08:00:00'],
          dtype='datetime64[s]')
    """
    start = np.datetime64(start_time)
    end = np.datetime64(end_time)
    freq = np.timedelta64(1, frequency)
    timestamps = np.arange(start, end + freq, freq)  # +freq to include the end time

    from pandas import DatetimeIndex
    timestamps = DatetimeIndex(timestamps.astype('datetime64[ns]'))
    return timestamps.astype('datetime64[ns]')


def callback_generate_datetime_series(
    ctx: typer.Context,
    timestamps: str,
    # timestamps: List[datetime],
    # value: Union[str, datetime, List[datetime]],
    param: typer.CallbackParam,
):
    print(f'[yellow]i[/yellow] Context: {ctx.params}')
    # print(f'[yellow]i[/yellow] typer.CallbackParam: {param}')
    print("[yellow]i[/yellow] Executing callback_generate_datetime_series()")
    # print(f'  Input [yellow]timestamps[/yellow] : {timestamps}')
    start_time = ctx.params.get('start_time')
    end_time = ctx.params.get('end_time')
    frequency = ctx.params.get('frequency', 'h')

    if start_time is not None and end_time is not None:
        timestamps = generate_datetime_series(start_time, end_time, frequency)
        return timestamps

    else:
        from pandas import to_datetime
        return to_datetime(timestamps, format='mixed')
