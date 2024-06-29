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

from pvgisprototype.log import logger
from pandas import DatetimeIndex, Timestamp
from pandas import date_range
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
from random import randint
from random import choice
# import time
import typer
import zoneinfo
from zoneinfo import ZoneInfo
from rich import print
import numpy as np
from pvgisprototype.constants import TIMESTAMPS_FREQUENCY_DEFAULT
import time
from functools import wraps


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"'{func.__name__}' executed in {elapsed_time:.6f} seconds (or {elapsed_time:.2f} seconds).")
        return result
    return wrapper


# Random time

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
    _, days_in_month = calendar.monthrange(year, month)
    day = randint(1, days_in_month)
    hour = randint(0, 23)
    minute = randint(0, 59)
    second = randint(0, 59)
    datetimestamp = datetime(year, month, day, hour, minute, second, tzinfo=ZoneInfo('UTC'))
    timezone_str = choice(list(zoneinfo.available_timezones()))
    timezone = ZoneInfo(timezone_str)

    return datetimestamp, timezone


# Time

def now_datetime() -> datetime:
    """Returns the current datetime in UTC.

    Return an aware timestamp using the local system time, however defaulting
    to UTC timezone. 
    """
    return datetime.now()


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


def convert_to_timezone(timezone: str) -> ZoneInfo:
    """Convert string to ZoneInfo object."""
    # print(f'[yellow]i[/yellow] Executing convert_to_timezone()')

    if timezone is None:
        # print(f'  [yellow]>[/yellow] No timezone requested [red]?[/red]')  # Convert to warning!
        # print(f'  [yellow]>[/yellow] Setting timezone to [red]UTC[/red]')
        return ZoneInfo('UTC')

    else:
        try:
            if timezone == 'local':
                return datetime.now().astimezone(None).tzinfo

            else:
                return ZoneInfo(timezone)

        except (zoneinfo.ZoneInfoNotFoundError, Exception):
            print(f"  [yellow]>[/yellow] Requested zone {timezone} not found. Setting it to [red]UTC[/red].")
            return ZoneInfo('UTC')


def attach_timezone(
        timestamp: Optional[datetime] = None,
        timezone: Optional[str] = None
) -> datetime:
    """Convert datetime object to timezone-aware."""
    if timestamp is None:
        timestamp = datetime.now(ZoneInfo('UTC'))  # Default to UTC

    if isinstance(timezone, str):
        try:
            tzinfo = convert_to_timezone(timezone)
            timestamp = timestamp.replace(tzinfo=tzinfo)
        except Exception as e:
            raise ValueError(f"Could not convert timezone: {e}")

    return timestamp


def attach_requested_timezone(
    timestamp: Union[Timestamp, datetime],
    timezone: ZoneInfo = None,
) -> Timestamp:
    """
    Attaches the requested timezone to a naive datetime. Attention : Defaults to UTC if no timezone requested!
    """
    # print(f'[green]i[/green] Callback function attach_requested_timezone()')

    if timestamp.tzinfo is not None:
        raise ValueError(f"  [yellow]>[/yellow] The provided timestamp '{timestamp}' already has a timezone!  Expected a [yellow]naive[/yellow] [bold]datetime[/bold] or [bold]Timestamp[/bold] object.")

    if timezone:
        try:
            # print(f'[yellow]i[/yellow] Attaching the requested zone [bold]{timezone}[/bold] to {timestamp}')  
            return timestamp.tz_localize(timezone)
        except Exception as e:
            print(f'[red]x[/red] Failed to attach the requested timezone \'{timezone}\' to the timestamp: {e}!')
    else:
        zoneinfo_utc = ZoneInfo('UTC')
        print(f"  [yellow]i[/yellow] Timezone not requested! Setting to [red]{zoneinfo_utc}[/red].") 
        return timestamp.tz_localize(zoneinfo_utc)
    

def ctx_attach_requested_timezone(
        ctx: typer.Context,
        timestamp: str,
        param: typer.CallbackParam
    ) -> datetime:
    """Returns the current datetime in the user-requested timezone."""

    # print(f'[yellow]i[/yellow] Context: {ctx.params}')
    # print(f'[yellow]i[/yellow] typer.CallbackParam: {param}')
    # print(f'  [yellow]>[/yellow] Executing ctx_attach_requested_timezone()')
    timezone = ctx.params.get('timezone')
    # print(f'  [yellow]>[/yellow] User requested input parameter [code]timezone[/code] = [bold]{timezone}[/bold]')
    # print(f'  [green]>[/green] Callback function returns : {attach_requested_timezone(timestamp, timezone)}')

    from pandas import to_datetime
    return attach_requested_timezone(to_datetime(timestamp), timezone)


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
    """
    """
    if isinstance(timestamps, datetime):
        timestamps = [timestamps]

    timestamps_array = np.array(timestamps)
    hours = (timestamps_array.astype('datetime64[h]') - timestamps_array.astype('datetime64[D]')).astype('timedelta64[h]').astype(float)
    minutes = (timestamps_array.astype('datetime64[m]') - timestamps_array.astype('datetime64[h]')).astype('timedelta64[m]').astype(float) / 60
    seconds = (timestamps_array.astype('datetime64[s]') - timestamps_array.astype('datetime64[m]')).astype('timedelta64[s]').astype(float) / 3600
    microseconds = (timestamps_array.astype('datetime64[us]') - timestamps_array.astype('datetime64[s]')).astype('timedelta64[us]').astype(float) / 3600000000

    return hours + minutes + seconds + microseconds


def hour_of_year_to_datetime(year, hour):
    """
    """
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


def get_days_in_years(years):
    """ Calculate the number of days in a given year, accounting for leap years.

    Parameters
    ----------
    years : DatetimeIndex
        The years series for which to calculate the number of days.

    Returns
    -------
    DatetimeIndex :
        The number of days series for the given years series

    Examples
    --------
    >>> get_days_in_years_series(pd.DatetimeIndex(['2000-12-22 21:12:12', '2001-11-11 11:11:11']))
    Index([366, 365], dtype='int64')
    """
    import pandas as pd
    end_dates = pd.to_datetime(years, format='%Y') + pd.offsets.YearEnd(0)
    start_dates = end_dates - pd.DateOffset(years=1)

    # Cannot serialise an index ! -------------------------------
    # from pvgisprototype.validation.hashing import generate_hash
    # output_hash = generate_hash((end_dates - start_dates).days)
    # print(
    #     "Days in Years Series : get_days_in_years_series() |",
    #     f"Data Type : [bold]{end_dates.dtype}[/bold] |",
    #     f"Data Type : [bold]{start_dates.dtype}[/bold] |",
    #     f"Output Hash : [code]{output_hash}[/code]",
    # )
    # ------------------------------ Cannot serialise an index !

    return (end_dates - start_dates).days


def parse_timestamp_series(
    timestamps: str,
) -> 'DatetimeIndex | DatetimeScalar | NaTType | None':
    """
    Parse an input of type string and generate a Pandas Timestamp or
    DatetimeIndex [1]_.

    either `str`ings or `datetime.datetime` objects and generate a NumPy
    datetime64 array [1]_

    Parameters
    ----------
    timestamps : `str`
            A single `str`ing (i.e. '2111-11-11' or '2121-12-12 12:12:12')

    Returns
    -------
    timestamps :
        Pandas Timestamp or DatetimeIndex

    Notes
    -----
    .. [1] https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Timestamp.html#pandas-timestamp
    .. [2] https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DatetimeIndex.html
    """
    from pandas import to_datetime
    if isinstance(timestamps, str):
        # return to_datetime(timestamps.split(','), format='mixed', utc=True)
        return to_datetime(timestamps.split(','), format='mixed')
    else:
        raise ValueError("The `timestamps` input must be a string of datetime or datetimes separated by comma as expected by Pandas `to_datetime()` function")


def generate_datetime_series(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    periods: Optional[str] = None,
    frequency: Optional[str] = TIMESTAMPS_FREQUENCY_DEFAULT,
    timezone: Optional[str] = None,
    name: Optional[str] = None,
):
    """Generate a fixed frequency DatetimeIndex

    Generates a range of equally spaced timestamps wrapping over Pandas'
    date_range() function. The timestamps satisfy `start_time <[=] x <[=]
    end_time`, where the first and last stamps fall on the boundary of the
    requested ``frequency`` string. The difference between any two timestamps
    is specified by the requested ``frequency``.

    If exactly one of ``start_time``, ``end_time``, or ``frequency`` is *not*
    specified, it can be computed by the ``periods``, the number of timesteps
    in the range.

    Parameters
    ----------
    start_time : str, datetime, date, pandas.Timestamp, or period-like, default None
        The starting time (if str in ISO format), also described as the left
        bound for generating periods.
    end_time : str, datetime, date, pandas.Timestamp, or period-like, default None
        The ending time in ISO format. In Pandas described as the right bound
        for generating periods.
    periods : int, default None
        Number of periods to generate.
    frequency : str or DateOffset, optional
        Frequency alias of the timestamps to generate, e.g., 'h' for hourly.
        By default the frequency is taken from start_time or
        end_time if those are Period objects. Otherwise, the default is "h" for
        hourly frequency.
    name : str, default None
        Name of the resulting PeriodIndex.

    Returns
    -------
    DatetimeIndex
        A Pandas DatetimeIndex at the specified frequency.

    See Also
    --------
    pandas.date_range
        Return a fixed frequency DatetimeIndex.

    Notes
    -----
    Of the four parameters ``start_time``, ``end_time``, ``periods``, and
    ``frequency``, exactly three must be specified. If ``frequency`` is
    omitted, the resulting ``DatetimeIndex`` will have ``periods`` linearly
    spaced elements between ``start`` and ``end`` (closed on both sides).

    Common time series frequencies are indexed via a set of string (also
    referred to as offset) aliases described at 
    <https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases>`__.

    Example
    -------
    >>> start_time = '2010-06-01 06:00:00'
    >>> end_time = '2010-06-01 08:00:00'
    >>> frequency = 'h'  # 'h' for hourly
    >>> generate_datetime_series(start_time, end_time, frequency)
    DatetimeIndex(['2010-06-01 06:00:00', '2010-06-01 07:00:00', '2010-06-01 08:00:00'], dtype='datetime64[ns]', freq=None)

    Using the periods input parameter to define the number of timesteps to generate : 

    >>> generate_datetime_series(start_time=start_time, periods=4, frequency=frequency)
    DatetimeIndex(['2010-06-01 06:00:00', '2010-06-01 07:00:00',
               '2010-06-01 08:00:00', '2010-06-01 09:00:00'],
              dtype='datetime64[ns]', freq='H')
    """
    timestamps = date_range(
        start=start_time,
        end=end_time,
        periods=periods,
        freq=frequency,
        tz=timezone,
        name=name,
    )

    return timestamps


def callback_generate_datetime_series(
    ctx: typer.Context,
    timestamps: DatetimeIndex,
    # timestamps: List[datetime],
    # value: Union[str, datetime, List[datetime]],
    # param: typer.CallbackParam,
):
    # print(f'[yellow]i[/yellow] Context: {ctx.params}')
    # print(f'[yellow]i[/yellow] typer.CallbackParam: {param}')
    # print("[yellow]i[/yellow] Executing callback_generate_datetime_series()")
    # print(f'  Input [yellow]timestamps[/yellow] : {timestamps}')
    start_time=ctx.params.get('start_time')
    end_time=ctx.params.get('end_time')
    if start_time == end_time:
        logger.warning(
            (
                f"[yellow bold]The start and end time are the same and will generate a single time stamp![/yellow bold]"
            )
        )
    periods=ctx.params.get('periods', None) 
    frequency=ctx.params.get('frequency', TIMESTAMPS_FREQUENCY_DEFAULT) if not periods else None
    if start_time is not None and end_time is not None:
        timestamps = generate_datetime_series(
            start_time=start_time,
            end_time=end_time,
            periods=periods,
            frequency=frequency,
            timezone=ctx.params.get('timezone'),
            name=ctx.params.get('datetimeindex_name', None)
        )
    # from pandas import to_datetime
    # -----------------------------------------------------------------------
    # If we do the following, we need to take care of external naive time series!
    # timezone_aware_timestamps = [
    #     attach_requested_timezone(timestamp, timezone) for timestamp in timestamps
    # ]
    # return to_datetime(timezone_aware_timestamps, format="mixed")
    # -----------------------------------------------------------------------
    return timestamps


def callback_generate_naive_datetime_series(
    ctx: typer.Context,
    timestamps: str,
):
    start_time=ctx.params.get('start_time')
    end_time=ctx.params.get('end_time')
    periods=ctx.params.get('periods', None) 
    frequency=ctx.params.get('frequency', TIMESTAMPS_FREQUENCY_DEFAULT) if not periods else None
    if start_time is not None and end_time is not None:
        timestamps = generate_datetime_series(
            start_time=start_time,
            end_time=end_time,
            periods=periods,
            frequency=frequency,
            timezone=None,
            name=ctx.params.get('datetimeindex_name', None)
        )
    return timestamps
