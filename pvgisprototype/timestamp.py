import typer
from typing import Annotated
from typing import Optional
from datetime import datetime
import pytz

import time
from datetime import datetime
from datetime import timezone
import pytz # $ pip install pytz
from tzlocal import get_localzone # $ pip install tzlocal


def now_datetime():
    """
    """
    return datetime.now().astimezone()


def timestamp_to_decimal_hours(timestamp, timezone='UTC'):
    dt = datetime.fromtimestamp(timestamp, pytz.timezone(timezone))
    decimal_hours = dt.hour + dt.minute / 60 + dt.second / 3600

    return decimal_hours


def convert_hours_to_seconds(hours: float):
    """
    """
    return hours * 3600



def convert_to_timezone( ctx: typer.Context, param: typer.CallbackParam, value: str):
    """Convert string to `tzinfo` timezone object
    """
    if value == "local":
        try:
            tzinfo = get_localzone()
        except Exception:
            tzinfo = pytz.timezone('UTC')
            typer.echo("Unable to determine local timezone. Defaulting to UTC.")
    elif value is None:
        tzinfo = pytz.timezone('UTC')
    else:
        try:
            tzinfo = pytz.timezone(value)
        except pytz.UnknownTimeZoneError:
            typer.echo(f"Unknown timezone: {value}. Please input a valid timezone.")
            raise typer.Exit(code=1)

    return tzinfo


def attach_timezone(
        value: Optional[str] = None,
        timezone: Optional[pytz.timezone] = None
        ) -> datetime:
    """Convert datetime object to timezone-aware.
    """
    local_tz = get_localzone() 

    if value == 'UTC':
        timestamp_utc = datetime.utcfromtimestamp(timestamp)

    local_now = utc_now.replace(tzinfo=pytz.utc).astimezone(local_tz) # utc -> local
    assert local_now.replace(tzinfo=None) == now
    if value is None:
        timestamp = datetime.now(tz=timezone)
    else:
        datetimestamp_naive = datetime.strptime(value, '%Y-%m-%d')
        datetimestamp = timezone.localize(datetimestamp_naive)

    return datetimestamp


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
