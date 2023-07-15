import typer
from typing import Annotated
from typing import Optional
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np

from ...api.constants import double_numpi
from ...api.utilities.conversions import convert_to_radians
from ...api.utilities.timestamp import now_utc_datetimezone
from ...api.utilities.timestamp import ctx_convert_to_timezone
from ...api.utilities.image_offset_prototype import get_image_offset


def calculate_solar_time_pvgis(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        latitude: Annotated[Optional[float], typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone)],
        timezone: Annotated[Optional[ZoneInfo], typer.Option(
            help='Timezone',
            callback=ctx_convert_to_timezone)] = None,
        days_in_a_year: float = 365.25,
        perigee_offset: float = 0.048869,
        eccentricity: float = 0.165,  # from the C code
        time_slot_offset_global: float = 0,
) -> float:
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
                  - eccentricity \
                  * np.sin(2 * day_of_year_in_radians + 0.34383)

    # Complicated implementation borrowed from SPECMAGIC!
    image_offset = get_image_offset(longitude, latitude)  # for `hour_offset`

    # adding longitude to UTC produces mean solar time!
    hour_offset = time_slot_offset_global + longitude / 15 + image_offset  # for `solar_time`
    solar_time = hour_of_day + time_offset + hour_offset
    
    # debug(locals())
    return solar_time, 'decimal hours'
