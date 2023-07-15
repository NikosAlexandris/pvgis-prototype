from devtools import debug

from .noaa_models import CalculateTrueSolarTimeNOAAInput
from .decorators import validate_with_pydantic
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo
from .time_offset import calculate_time_offset_noaa


@validate_with_pydantic(CalculateTrueSolarTimeNOAAInput)
def calculate_true_solar_time_noaa(
        longitude: float,
        timestamp: datetime, 
        timezone: Optional[ZoneInfo],
        time_output_units: str = 'minutes',
        angle_units: str = 'radians',
    ) -> float:
    """Calculate the true solar time.

    Parameters
    ----------
    timestamp: datetime, optional
        The timestamp to calculate offset for
    timezone: str, optional
        The timezone for calculation
    time_offset: float
        The time offset for calculation

    Returns
    -------
    float: The true solar time
    """
    # debug(locals())
    # if timezone != timestamp.tzinfo:
    #     try:
    #         timestamp = timestamp.astimezone(timezone)
    #     except pytz.UnknownTimeZoneError as e:
    #         logging.warning(f'Unknown timezone: {e}')
    #         raise
    
    time_offset, _units = calculate_time_offset_noaa(
            longitude,
            timestamp,
            time_output_units,
            angle_units,
            )  # in minutes
    true_solar_time = (
        timestamp.hour * 60 + timestamp.minute + timestamp.second / 60 + time_offset
    )

    # debug(locals())
    if time_output_units == 'minutes':
        if not 0 <= true_solar_time <= 1440:
            raise ValueError("The true solar time must range within [0, 1440] minutes")

    # debug(locals())
    return true_solar_time, time_output_units
