from .noaa_models import Longitude_in_Radians
from .noaa_models import CalculateTrueSolarTimeNOAAInput
from .decorators import validate_with_pydantic
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo
from .time_offset import calculate_time_offset_noaa
from typing import NamedTuple
from pvgisprototype.api.named_tuples import generate


@validate_with_pydantic(CalculateTrueSolarTimeNOAAInput)
def calculate_true_solar_time_noaa(
        longitude: Longitude_in_Radians, 
        timestamp: datetime, 
        timezone: Optional[ZoneInfo],
        time_output_units: str = 'minutes',
        angle_units: str = 'radians',
    ) -> NamedTuple:
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
    time_offset = calculate_time_offset_noaa(
            longitude=longitude,
            timestamp=timestamp,
            time_output_units=time_output_units,
            angle_units=angle_units,
            )  # in minutes
    true_solar_time = (
        timestamp.hour * 60 + timestamp.minute + timestamp.second / 60 + time_offset.value
    )

    if time_output_units == 'minutes':
        if not 0 <= true_solar_time <= 1580:
            raise ValueError(f'The true solar time must range within [0, {1440+20}] minutes')

    # Convert to datetime object
    hours, remainder = divmod(true_solar_time, 60)
    minutes, seconds = divmod(remainder * 60, 60)
    true_solar_time = datetime(
            year=timestamp.year,
            month=timestamp.month,
            day=timestamp.day,
            hour=int(hours),
            minute=int(minutes),
            second=int(seconds),
            tzinfo=timestamp.tzinfo,
            )
    true_solar_time = generate(
        'true_solar_time',
        (true_solar_time, time_output_units),
    )
    return true_solar_time
