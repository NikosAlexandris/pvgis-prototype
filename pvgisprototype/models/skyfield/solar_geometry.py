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
from typing import NamedTuple
from pvgisprototype.api.named_tuples import generate


def calculate_solar_position_skyfield(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        latitude: Annotated[Optional[float], typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Timezone',
            callback=convert_to_timezone)] = None,
        output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar geometry variables (degrees or radians)")] = 'radians',
        ) -> NamedTuple:
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
    location = skyfield.api.wgs84.latlon(latitude * N, longitude * W)  # W or E ?

    # the sun position as seen from the observer
    timescale = skyfield.api.load.timescale()
    requested_timestamp = timescale.from_datetime(timestamp)
    solar_position = (earth + location).at(requested_timestamp).observe(sun).apparent()

    solar_position = generate(
        'solar_position',
        (solar_position, angle_output_units),                   # NOTE: Is this unit correct? It is not used anywhere
    )
    debug(locals())
    return solar_position


def calculate_solar_altitude_azimuth_skyfield(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        latitude: Annotated[Optional[float], typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Timezone',
            callback=convert_to_timezone)] = None,
        output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar geometry variables (degrees or radians)")] = 'radians',
        ) -> Tuple[NamedTuple, NamedTuple]:
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
            longitude,
            latitude,
            timestamp,
            timezone,
            output_units,
            )
    solar_altitude, solar_azimuth, distance_to_sun = solar_position.value.altaz()       # TODO: Must be tested

    # if output_units == 'radians':
    solar_altitude = solar_altitude.radians
    solar_azimuth = solar_azimuth.radians

    # if output_units == 'degrees':
    #     solar_altitude = solar_altitude.degrees
    #     solar_azimuth = solar_azimuth.degrees

    solar_altitude = generate(
        'solar_altitude',
        (solar_altitude, angle_output_units),
    )

    solar_azimuth = generate(
        'solar_azimuth',
        (solar_azimuth, angle_output_units),
    )

    debug(locals())
    return solar_altitude, solar_azimuth   # distance_to_sun


def calculate_hour_angle_skyfield(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        latitude: Annotated[Optional[float], typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Timezone',
            callback=convert_to_timezone)] = None,
        output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar geometry variables (degrees or radians)")] = 'radians',
        ) -> float:
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
            output_units,
            )
    hour_angle, solar_declination, distance_to_sun = solar_position.hadec()

    if output_units == 'minutes':
        hour_angle = hour_angle.minutes
        solar_declination = solar_declination.minutes

    if output_units == 'hours':
        hour_angle = hour_angle.hours
        solar_declination = solar_declination.hours

    if output_units == 'radians':
        hour_angle = hour_angle.radians
        solar_declination = solar_declination.radians

    return hour_angle, solar_declination, output_units

