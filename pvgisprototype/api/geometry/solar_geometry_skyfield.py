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
from ..utilities.conversions import convert_to_degrees_if_requested
from ..utilities.conversions import convert_to_radians_if_requested
from ..utilities.conversions import convert_to_radians
from ..utilities.timestamp import now_datetime
from ..utilities.timestamp import convert_to_timezone


def calculate_solar_position_skyfield(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        latitude: Annotated[Optional[float], typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_datetime)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Timezone',
            callback=convert_to_timezone)] = None,
        # output_units: Annotated[str, typer.Option(
        #     '-u',
        #     '--units',
        #     show_default=True,
        #     case_sensitive=False,
        #     help="Output units for solar geometry variables (degrees or radians)")] = 'radians',
        ) -> float:
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
    """
    # Handle Me during input validation? -------------------------------------
    try:
        timestamp = timezone.localize(timestamp)
    except Exception:
        logging.warning(f'tzinfo already set for timestamp = {timestamp}')
    # Handle Me during input validation? -------------------------------------

    ephemeris = skyfield.api.load('de421.bsp')
    sun = ephemeris['Sun']
    earth = ephemeris['Earth']
    N = skyfield.api.N
    W = skyfield.api.W
    location = skyfield.api.wgs84.latlon(latitude * N, longitude * W)  # W or E ?

    # the sun position as seen from the observer
    timescale = skyfield.api.load.timescale()
    solar_position = (earth + location).at(timescale.now()).observe(sun).apparent()
    solar_altitude, solar_azimuth, distance_to_sun = solar_position.altaz()

    # in degrees? -> solar_altitude.degrees, solar_azimuth.degrees
    return solar_altitude.radians, solar_azimuth.radians, distance_to_sun
