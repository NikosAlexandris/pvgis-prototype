import typer
from typing import Annotated
from typing import Optional
from datetime import datetime
from datetime import timedelta
from zoneinfo import ZoneInfo
import numpy as np

from pvgisprototype.constants import double_numpi
from ...api.utilities.conversions import convert_to_radians
from ...api.utilities.timestamp import now_utc_datetimezone
from ...api.utilities.timestamp import ctx_convert_to_timezone
from ...api.utilities.image_offset_prototype import get_image_offset

from pvgisprototype import SolarTime
from pvgisprototype import Latitude
from pvgisprototype import Longitude
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarTimePVGISInputModel


@validate_with_pydantic(CalculateSolarTimePVGISInputModel)
def calculate_solar_time_pvgis(
        longitude: Latitude,
        latitude: Longitude,
        timestamp: datetime,
        timezone: ZoneInfo = None,
        days_in_a_year: float = 365.25,
        perigee_offset: float = 0.048869,
        eccentricity_correction_factor: float = 0.165,  # from the C code
        time_offset_global: float = 0,
    ):
    """Calculate the solar time.

    1. Map the day of the year onto the circumference of a circle, essentially
    converting the day of the year into radians.

    2. Approximate empirically the equation of time, which accounts for the
    elliptical shape of Earth's orbit and the tilt of its axis.

    3. Calculate the solar time by adding the current hour of the year, the
    time offset from the equation of time, and the hour offset (likely a
    longitude-based correction).

    Returns
    -------
    solar_time: float
        The solar time in decimal hours
    """
    # Handle Me during input validation? -------------------------------------
    if timezone != timestamp.tzinfo:
        try:
            timestamp = timestamp.astimezone(timezone)
        except Exception as e:
            logging.warning(f'Error setting tzinfo for timestamp = {timestamp}: {e}')
    # Handle Me during input validation? -------------------------------------
    year = timestamp.year
    start_of_year = datetime(year=year, month=1, day=1, tzinfo=timestamp.tzinfo)
    day_of_year = timestamp.timetuple().tm_yday
    day_of_year_in_radians = double_numpi * day_of_year / days_in_a_year  
    hour_of_year = int((timestamp - start_of_year).total_seconds() / 3600)
    hour_of_day = hour_of_year % 24  # integer

    # approximation like the Equation of Time?!
    time_offset = - 0.128 \
                  * np.sin(day_of_year_in_radians - perigee_offset) \
                  - eccentricity_correction_factor \
                  * np.sin(2 * day_of_year_in_radians + 0.34383)

    # Complicated implementation borrowed from SPECMAGIC!
    image_offset = get_image_offset(longitude, latitude)  # for `hour_offset`

    # adding longitude to UTC produces mean solar time!
    hour_offset = time_offset_global + longitude / 15 + image_offset  # for `solar_time`
    time_correction_factor_hours = hour_of_day + time_offset + hour_offset
    solar_time = timestamp + timedelta(hours=time_correction_factor_hours)
    
    # debug(locals())
    # return SolarTime(value=solar_time, unit='decimal hours')
    return solar_time
