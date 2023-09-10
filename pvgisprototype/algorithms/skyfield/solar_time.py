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
from pvgisprototype.api.utilities.conversions import convert_to_radians
from pvgisprototype.api.utilities.conversions import convert_to_degrees
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.api.utilities.timestamp import ctx_convert_to_timezone
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.algorithms.skyfield.function_models import CalculateSolarTimeSkyfieldInputModel
from pvgisprototype import SolarTime
from pvgisprototype import Latitude
from pvgisprototype import Longitude


@validate_with_pydantic(CalculateSolarTimeSkyfieldInputModel)
def calculate_solar_time_skyfield(
        longitude: Longitude,
        latitude: Latitude,
        timestamp: datetime,
        timezone: str = None,
        verbose: int = 0,
    ):

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

    planets = load('de421.bsp')
    sun = planets['Sun']
    if longitude.value > 0:
        location = wgs84.latlon(latitude.value * N, longitude.value * E)
    if longitude.value < 0:
        location = wgs84.latlon(latitude.value * N, longitude.value * W)  # Correct ?
    else:
        location = wgs84.latlon(latitude.value * N, longitude.value)  # Correct ?

    f = almanac.meridian_transits(planets, sun, location)

    times, events = almanac.find_discrete(midnight_time, next_midnight_time, f)
    times = times[events == 1]  # select transits instead of antitransits
    if not times:
        raise ValueError("No solar noon found in the given time range")

    next_solar_noon = times[0]  # first in `times` is the _next_ solar noon!
    previous_solar_noon = next_solar_noon - timedelta(days=1)

    if timestamp < next_solar_noon.utc_datetime().replace(tzinfo=ZoneInfo('UTC')):
        # if morning : calculate hours until next solar noon
        hours_since_solar_noon = (timestamp - previous_solar_noon.utc_datetime().replace(tzinfo=ZoneInfo('UTC'))).total_seconds() / 3600
    else:
        # if afternoon : calculate hours since last solar noon
        hours_since_solar_noon = (timestamp - next_solar_noon.utc_datetime().replace(tzinfo=ZoneInfo('UTC'))).total_seconds() / 3600

    hours = int(hours_since_solar_noon)
    minutes = int((hours_since_solar_noon - hours) * 60)
    seconds = int(((hours_since_solar_noon - hours) * 60 - minutes) * 60)
    # local_solar_time = datetime_time(hours, minutes, seconds)
    local_solar_time = datetime(
            year=timestamp.year,
            month=timestamp.month,
            day=timestamp.day,
            hour=int(hours),
            minute=int(minutes),
            second=int(seconds),
            tzinfo=timestamp.tzinfo,
    )
    # local_solar_time = previous_solar_noon.utc_datetime() + timedelta(hours=hours_since_solar_noon)

    if verbose:
        typer.echo(f'Local solar time: {local_solar_time}')

        previous_solar_noon_string = previous_solar_noon.astimezone(timezone).strftime('%Y-%m-%d %H:%M:%S')
        typer.echo(f'Previous solar noon: {previous_solar_noon_string}')
        
        next_solar_noon_string = next_solar_noon.astimezone(timezone).strftime('%Y-%m-%d %H:%M:%S')
        typer.echo(f'Next solar noon: {next_solar_noon_string}')

    return local_solar_time
