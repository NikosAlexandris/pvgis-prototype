from devtools import debug
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

from pvgisprototype.api.data_classes import SolarPosition
from pvgisprototype.api.data_classes import SolarAltitude
from pvgisprototype.api.data_classes import SolarAzimuth
from pvgisprototype.api.data_classes import HourAngle
from pvgisprototype.api.data_classes import SolarDeclination
from pvgisprototype.api.data_classes import Latitude
from pvgisprototype.api.data_classes import Longitude

from .input_models import SolarPositionInput
from .input_models import SolarAltitudeInput
from .input_models import HourAngleInput

from .decorators import validate_with_pydantic


@validate_with_pydantic(SolarPositionInput, expand_args=True)
def calculate_solar_position_skyfield(
        longitude: Longitude,
        latitude: Latitude,
        timestamp: datetime,
        timezone: str = None,
        angle_output_units: str = 'radians',
    ) -> SolarPosition:
    """Calculate sun position

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

    ephemeris = skyfield.api.load('de421.bsp')
    sun = ephemeris['Sun']
    earth = ephemeris['Earth']
    N = skyfield.api.N
    W = skyfield.api.W
    location = skyfield.api.wgs84.latlon(latitude.value * N, longitude.value * W)  # W or E ?

    # the sun position as seen from the observer
    timescale = skyfield.api.load.timescale()
    requested_timestamp = timescale.from_datetime(timestamp)
    solar_position = (earth + location).at(requested_timestamp).observe(sun).apparent()

    solar_position = SolarPosition(value=solar_position, unit=angle_output_units)
    return solar_position


@validate_with_pydantic(SolarAltitudeInput, expand_args=True)
def calculate_solar_altitude_azimuth_skyfield(
        longitude: Longitude,
        latitude: Latitude,
        timestamp: datetime,
        timezone: str = None,
        angle_output_units: str = 'radians',
    ) -> Tuple[SolarAltitude, SolarAzimuth]:
    """Calculate sun position

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
    solar_position = calculate_solar_position_skyfield(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            angle_output_units=angle_output_units,
            )
    solar_altitude, solar_azimuth, distance_to_sun = solar_position.value.altaz()

    # # if output_units == 'radians':
    # solar_altitude = solar_altitude.radians
    # solar_azimuth = solar_azimuth.radians

    # if output_units == 'degrees':
    #     solar_altitude = solar_altitude.degrees
    #     solar_azimuth = solar_azimuth.degrees

    solar_altitude = SolarAltitude(
        value=solar_altitude,
        unit=angle_output_units,
    )

    solar_azimuth = SolarAzimuth(
        value=solar_azimuth,
        unit=angle_output_units,
    )

    return solar_altitude, solar_azimuth   # distance_to_sun


@validate_with_pydantic(HourAngleInput)
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

