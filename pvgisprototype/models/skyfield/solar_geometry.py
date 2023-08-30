import logging
import typer
from typing import Annotated
from typing import Optional
import skyfield
# from skyfield import api
# from skyfield import almanac
from datetime import datetime
from datetime import timedelta
import dateutil.parser
from calendar import monthrange
from ...api.utilities.conversions import convert_to_degrees_if_requested
from ...api.utilities.conversions import convert_to_radians_if_requested
from ...api.utilities.conversions import convert_to_radians
from ...api.utilities.timestamp import now_utc_datetimezone
from ...api.utilities.timestamp import convert_to_timezone
from typing import Tuple

from pvgisprototype.models.skyfield.decorators import validate_with_pydantic
from pvgisprototype.models.skyfield.function_models import CalculateSolarPositionSkyfieldInputModel
from pvgisprototype.models.skyfield.function_models import CalculateSolarAltitudeAzimuthSkyfieldInputModel
from pvgisprototype.models.skyfield.function_models import CalculateHourAngleSkyfieldInput

from pvgisprototype.api.models import SolarPosition
from pvgisprototype.api.models import SolarAltitude
from pvgisprototype.api.models import SolarAzimuth
from pvgisprototype.api.models import HourAngle
from pvgisprototype.api.models import SolarDeclination
from pvgisprototype.api.models import Latitude
from pvgisprototype.api.models import Longitude


@validate_with_pydantic(CalculateSolarPositionSkyfieldInputModel)
def calculate_solar_position_skyfield(
        longitude: Longitude,
        latitude: Latitude,
        timestamp: datetime,
        timezone: str = None,
        angle_output_units: str = 'radians',
    ) -> SolarPosition:
    """Calculate sun position above the local horizon using Skyfield.

    Returns
    -------
    solar_altitude:
        Altitude measures the angle above or below the horizon. The
        zenith is at +90°, an object on the horizon’s great circle is at 0°,
        and the nadir beneath your feet is at −90°.

    solar_azimuth:
        Azimuth measures the angle around the sky from the north pole: 0° means
        exactly north, 90° is east, 180° is south, and 270° is west.

    Notes
    -----

    For the implementation, see also:
    https://techoverflow.net/2022/06/19/how-to-compute-position-of-sun-in-the-sky-in-python-using-skyfield/

    Factors influencing the accuracy of the calculation using Skyfield:

    - Skyfield considers:

        - The slight shift in position caused by light speed
        - The very very slight shift in position caused by earth’s gravity

    - Skyfield does not consider:

        - Atmospheric distortions shifting the sun’s position
        - The extent of the sun’s disk causing the sun to emanate not from a
          point but apparently from an area

    Notes
    -----

    To consider:

    - https://rhodesmill.org/skyfield/almanac.html#elevated-vantage-points
    - The `Time` class in Skyfield (i.e. `timescale()`) only uses UTC for input
      and output
    - https://rhodesmill.org/skyfield/time.html#utc-and-your-timezone
    - https://rhodesmill.org/skyfield/time.html#utc-and-leap-seconds
    """
    # # Handle Me during input validation? -------------------------------------
    # try:
    #     timestamp = timezone.localize(timestamp)
    # except Exception:
    #     logging.warning(f'tzinfo already set for timestamp = {timestamp}')
    # # Handle Me during input validation? -------------------------------------
    planets = skyfield.api.load('de421.bsp')
    sun = planets['Sun']
    earth = planets['Earth']
    N = skyfield.api.N
    W = skyfield.api.W
    E = skyfield.api.E

    if longitude.value < 0:
        location = skyfield.api.wgs84.latlon(latitude.value * N, longitude.value * W)  # W or E ?
    if longitude.value > 0:
        location = skyfield.api.wgs84.latlon(latitude.value * N, longitude.value * E)  # W or E ?
    else:
        location = skyfield.api.wgs84.latlon(latitude.value * N, longitude.value)  # ?

    # sun position seen from observer location
    timescale = skyfield.api.load.timescale()
    requested_timestamp = timescale.from_datetime(timestamp)
    solar_position = (earth + location).at(requested_timestamp).observe(sun).apparent()

    # solar_position = SolarPosition(value=solar_position, unit=angle_output_units)
    return solar_position


@validate_with_pydantic(CalculateSolarAltitudeAzimuthSkyfieldInputModel)
def calculate_solar_altitude_azimuth_skyfield(
        longitude: Longitude,
        latitude: Latitude,
        timestamp: datetime,
        timezone: str = None,
        angle_output_units: str = 'radians',
    ) -> Tuple[SolarAltitude, SolarAzimuth]:
    """Calculate sun position"""
    solar_position = calculate_solar_position_skyfield(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        angle_output_units=angle_output_units,
    )
    solar_altitude, solar_azimuth, distance_to_sun = solar_position.altaz()

    solar_altitude = SolarAltitude(
        value=solar_altitude.radians,
        unit='radians',
    )
    solar_altitude = convert_to_degrees_if_requested(
        solar_altitude,
        angle_output_units,
        )

    solar_azimuth = SolarAzimuth(
        value=solar_azimuth.radians,
        unit='radians',
    )
    solar_azimuth = convert_to_degrees_if_requested(
        solar_azimuth,
        angle_output_units,
        )

    return solar_altitude, solar_azimuth   # distance_to_sun


@validate_with_pydantic(CalculateHourAngleSkyfieldInput)
def calculate_hour_angle_skyfield(
        longitude: Longitude,
        latitude: Latitude,
        timestamp: datetime,
        timezone: str = None,
        angle_output_units: str = 'radians',
    ) -> Tuple[HourAngle, SolarDeclination]:
    """Calculate the hour angle ω'

    Parameters
    ----------


    Returns
    --------

    hour_angle: float
        Hour angle is the angle (ω) at any instant through which the earth has
        to turn to bring the meridian of the observer directly in line with the
        sun's rays measured in radian.
    """
    solar_position = calculate_solar_position_skyfield(
            longitude,
            latitude,
            timestamp,
            timezone,
            angle_output_units,
            )
    hour_angle, solar_declination, distance_to_sun = solar_position.hadec()

    if angle_output_units == 'minutes':
        hour_angle = hour_angle.minutes
        solar_declination = solar_declination.minutes

    if angle_output_units == 'hours':
        hour_angle = hour_angle.hours
        solar_declination = solar_declination.hours

    if angle_output_units == 'radians':
        hour_angle = hour_angle.radians
        solar_declination = solar_declination.radians

    hour_angle = HourAngle(value=hour_angle, unit=angle_output_units)
    solar_declination = SolarDeclination(value=solar_declination, unit=angle_output_units)

    return hour_angle, solar_declination
