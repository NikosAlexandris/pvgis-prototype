import typer
from typing import Annotated
from typing import Optional
from datetime import datetime
from datetime import time as datetime_time
from datetime import timedelta
from zoneinfo import ZoneInfo
from skyfield import almanac
from skyfield.api import Topos
from skyfield.api import load
from skyfield.api import N
from skyfield.api import W
from skyfield.api import E
from skyfield.api import wgs84
from skyfield.api import load
from ...api.utilities.conversions import convert_to_radians
from ...api.utilities.conversions import convert_to_degrees
from ...api.utilities.timestamp import now_utc_datetimezone
from ...api.utilities.timestamp import ctx_convert_to_timezone

from pvgisprototype.api.data_classes import SolarTime
from pvgisprototype.api.data_classes import Latitude
from pvgisprototype.api.data_classes import Longitude

from .input_models import CalculateTrueSolarTimeSkyfieldInput
from .decorators import validate_with_pydantic


# @validate_with_pydantic(CalculateTrueSolarTimeSkyfieldInputModel)
# def calculate_solar_time_skyfield(
#         longitude: Annotated[float, typer.Argument(
#             callback=convert_to_degrees,
#             min=-180, max=180)],
#         latitude: Annotated[float, typer.Argument(
#             callback=convert_to_degrees,
#             min=-90, max=90)],
#         timestamp: Annotated[Optional[datetime], typer.Argument(
#             help='Timestamp',
#             default_factory=now_utc_datetimezone)],
#         timezone: Annotated[Optional[str], typer.Option(
#             help='Timezone',
#             callback=ctx_convert_to_timezone)] = None,
#         verbose: bool = False,
#         ):
#     """
#     Returns
#     -------
#     (decimal_hours, units): float, str
#     """
#     # Handle Me during input validation? -------------------------------------
#     if timezone != timestamp.tzinfo:
#         try:
#             timestamp = timestamp.astimezone(timezone)
#         except Exception as e:
#             logging.warning(f'Error setting tzinfo for timestamp = {timestamp}: {e}')
#     # Handle Me during input validation? -------------------------------------

#     midnight = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
#     next_midnight = midnight + timedelta(days=1)
#     timescale = load.timescale()
#     midnight_time = timescale.from_datetime(midnight)
#     next_midnight_time = timescale.from_datetime(next_midnight)

#     ephemeris = load('de421.bsp')
#     sun = ephemeris['Sun']
#     # location = wgs84.latlon(latitude * N, longitude * W)
#     location = wgs84.latlon(latitude * N, longitude * E)
#     f = almanac.meridian_transits(ephemeris, sun, location)
#     times, events = almanac.find_discrete(midnight_time, next_midnight_time, f)
    
#     times = times[events == 1]  # select transits instead of antitransits
#     if not times:
#         raise ValueError("No solar noon found in the given time range")

#     next_solar_noon = times[0]  # first time in `times` is the next solar noon!
#     previous_solar_noon = next_solar_noon - timedelta(days=1)

#     if timestamp < next_solar_noon.utc_datetime().replace(tzinfo=ZoneInfo('UTC')):
#         # If it's morning, calculate the hours until the next solar noon.
#         hours_since_solar_noon = (timestamp - previous_solar_noon.utc_datetime().replace(tzinfo=ZoneInfo('UTC'))).total_seconds() / 3600
#     else:
#         # If it's afternoon, calculate the hours since the last solar noon.
#         hours_since_solar_noon = (timestamp - next_solar_noon.utc_datetime().replace(tzinfo=ZoneInfo('UTC'))).total_seconds() / 3600

#     hours = int(hours_since_solar_noon)
#     minutes = int((hours_since_solar_noon - hours) * 60)
#     seconds = int(((hours_since_solar_noon - hours) * 60 - minutes) * 60)
#     local_solar_time = datetime_time(hours, minutes, seconds)

#     # solar_noon_string = str(solar_noon.astimezone(timezone))[:19]
#     # solar_noon_datetime = solar_noon.utc_datetime().replace(tzinfo=ZoneInfo('UTC'))

#     # local_solar_time_delta = timestamp - solar_noon_datetime.astimezone(timezone)
#     # total_seconds = int(local_solar_time_delta.total_seconds())
#     # local_solar_datetime = datetime.utcfromtimestamp(total_seconds)
#     # local_solar_timestamp = datetime.utcfromtimestamp(total_seconds).time()

#     return local_solar_time


@validate_with_pydantic(CalculateTrueSolarTimeSkyfieldInput, expand_args=True)
def calculate_solar_time_skyfield(
        longitude: Longitude,
        latitude: Latitude,
        timestamp: datetime,
        timezone: str = None,
        verbose: bool = False,
    ) -> SolarTime:

    # Handle Me during input validation? -------------------------------------
    if timezone != timestamp.tzinfo:
        try:
            timestamp = timestamp.astimezone(timezone)
        except Exception as e:
            logging.warning(f'Error setting tzinfo for timestamp = {timestamp}: {e}')
    # Handle Me during input validation? -------------------------------------

    midnight = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
    next_midnight = midnight + timedelta(days=1)
    timescale = load.timescale()
    midnight_time = timescale.from_datetime(midnight)
    next_midnight_time = timescale.from_datetime(next_midnight)

    ephemeris = load('de421.bsp')
    sun = ephemeris['Sun']
    # location = wgs84.latlon(latitude * N, longitude * W) ? ----------------
    location = wgs84.latlon(latitude.value * N, longitude.value * E)
    f = almanac.meridian_transits(ephemeris, sun, location)
    times, events = almanac.find_discrete(midnight_time, next_midnight_time, f)
    
    times = times[events == 1]  # select transits instead of antitransits
    if not times:
        raise ValueError("No solar noon found in the given time range")

    next_solar_noon = times[0]  # first time in `times` is the next solar noon!
    previous_solar_noon = next_solar_noon - timedelta(days=1)

    if timestamp < next_solar_noon.utc_datetime().replace(tzinfo=ZoneInfo('UTC')):
        # if morning : calculate hours until next solar noon
        hours_since_solar_noon = (timestamp - previous_solar_noon.utc_datetime().replace(tzinfo=ZoneInfo('UTC'))).total_seconds() / 3600
    else:
        # if afternoon : calculate hours since last solar noon
        hours_since_solar_noon = (timestamp - next_solar_noon.utc_datetime().replace(tzinfo=ZoneInfo('UTC'))).total_seconds() / 3600

    local_solar_time = previous_solar_noon.utc_datetime() + timedelta(hours=hours_since_solar_noon)

    # if verbose:
        
    previous_solar_noon_string = previous_solar_noon.astimezone(timezone).strftime('%Y-%m-%d %H:%M:%S')
    # typer.echo(f'Previous solar noon: {previous_solar_noon_string}')

    next_solar_noon_string = next_solar_noon.astimezone(timezone).strftime('%Y-%m-%d %H:%M:%S')
    # typer.echo(f'Next solar noon: {next_solar_noon_string}')
    # typer.echo(f'Local solar time: {local_solar_time}')

    return SolarTime(value=local_solar_time, unit='decimal hours') 
