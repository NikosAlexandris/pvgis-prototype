from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from rich import print
from skyfield import almanac
from skyfield.api import E, N, W, load, wgs84

from pvgisprototype import Latitude, Longitude
from pvgisprototype.algorithms.skyfield.function_models import (
    CalculateSolarTimeSkyfieldInputModel,
)
from pvgisprototype.log import logger
from pvgisprototype.validation.functions import validate_with_pydantic


@validate_with_pydantic(CalculateSolarTimeSkyfieldInputModel)
def calculate_solar_time_skyfield(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: str = None,
    verbose: int = 0,
) -> datetime:
    # Handle Me during input validation? -------------------------------------
    if timezone != timestamp.tzinfo:
        try:
            timestamp = timestamp.astimezone(timezone)
        except Exception as e:
            logger.warning(f"Error setting tzinfo for timestamp = {timestamp}: {e}")
    # Handle Me during input validation? -------------------------------------

    midnight = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
    next_midnight = midnight + timedelta(days=1)
    timescale = load.timescale()
    midnight_time = timescale.from_datetime(midnight)
    next_midnight_time = timescale.from_datetime(next_midnight)

    planets = load("de421.bsp")
    sun = planets["Sun"]
    if longitude.degrees > 0:
        location = wgs84.latlon(latitude.degrees * N, longitude.degrees * E)
    if longitude.degrees < 0:
        location = wgs84.latlon(
            latitude.degrees * N, longitude.degrees * W
        )  # Correct ?
    if longitude.degrees > 0:
        location = wgs84.latlon(latitude.degrees * N, longitude.degrees * E)
    if longitude.degrees < 0:
        location = wgs84.latlon(
            latitude.degrees * N, longitude.degrees * W
        )  # Correct ?
    else:
        location = wgs84.latlon(latitude.degrees * N, longitude.degrees)  # Correct ?
        location = wgs84.latlon(latitude.degrees * N, longitude.degrees)  # Correct ?

    f = almanac.meridian_transits(planets, sun, location)

    times, events = almanac.find_discrete(midnight_time, next_midnight_time, f)
    times = times[events == 1]  # select transits instead of antitransits
    if not times:
        raise ValueError("No solar noon found in the given time range")

    next_solar_noon = times[0]  # first in `times` is the _next_ solar noon!
    previous_solar_noon = next_solar_noon - timedelta(days=1)

    if timestamp < next_solar_noon.utc_datetime().replace(tzinfo=ZoneInfo("UTC")):
        # if morning : calculate hours until next solar noon
        hours_since_solar_noon = (
            timestamp
            - previous_solar_noon.utc_datetime().replace(tzinfo=ZoneInfo("UTC"))
        ).total_seconds() / 3600
    else:
        # if afternoon : calculate hours since last solar noon
        hours_since_solar_noon = (
            timestamp - next_solar_noon.utc_datetime().replace(tzinfo=ZoneInfo("UTC"))
        ).total_seconds() / 3600

    hours = int(hours_since_solar_noon)
    minutes = int((hours_since_solar_noon - hours) * 60)
    seconds = int(((hours_since_solar_noon - hours) * 60 - minutes) * 60)
    local_solar_time = datetime(  # NOTE gounaol: Maybe wrong implementation
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
        print(f"Local solar time: {local_solar_time}")

        previous_solar_noon_string = previous_solar_noon.astimezone(timezone).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        print(f"Previous solar noon: {previous_solar_noon_string}")

        next_solar_noon_string = next_solar_noon.astimezone(timezone).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        print(f"Next solar noon: {next_solar_noon_string}")

    return local_solar_time
