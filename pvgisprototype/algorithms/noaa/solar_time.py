from devtools import debug
from pvgisprototype.api.decorators import validate_with_pydantic
from pvgisprototype.algorithms.noaa.function_models import CalculateTrueSolarTimeNOAAInput
from pvgisprototype.algorithms.noaa.function_models import CalculateTrueSolarTimeTimeSeriesNOAAInput
from pvgisprototype.api.models import Longitude
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo
from .time_offset import calculate_time_offset_noaa
from datetime import timedelta
from typing import Union
from typing import Sequence


@validate_with_pydantic(CalculateTrueSolarTimeNOAAInput)
def calculate_true_solar_time_noaa(
        longitude: Longitude,   # radians
        timestamp: datetime, 
        timezone: Optional[ZoneInfo],
        time_output_units: str = 'minutes',
        angle_units: str = 'radians',
    ) -> datetime:
    """Calculate the true solar time.

    The true solar time is the sum of the mean solar time and the equation of
    time.  CONFIRM!

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


    Notes
    -----

    Implementation in pysolar:

        ```
        (math.tm_hour(when) * 60 + math.tm_min(when) + 4 * longitude_deg + equation_of_time(math.tm_yday(when)))
        ```

        This means that the time offset is the 

        ```
        4 * longitude_deg + equation_of_time(math.tm_yday(when)))
        ```
        part.
    """
    time_offset = calculate_time_offset_noaa(
        longitude=longitude,
        timestamp=timestamp,
        timezone=timezone,
        time_output_units=time_output_units,
        angle_units=angle_units,
        )  # in minutes
    true_solar_time = (
        timestamp.hour * 60 + timestamp.minute + timestamp.second / 60 + time_offset.value
    )

    if time_output_units == 'minutes':
        # if not 0 <= true_solar_time <= 1440:
        # if not 0 <= true_solar_time <= 1580:
        # if not -790 <= true_solar_time <= 790:
        if not -1580 <= true_solar_time <= 1580:
            raise ValueError(f'The calculated true solar time `{true_solar_time}` is out of the expected range [-720, 720] minutes!')

    time_offset_timedelta = timedelta(minutes=true_solar_time)
    true_solar_datetime = timestamp + time_offset_timedelta
    true_solar_time = datetime(
            year=true_solar_datetime.year,
            month=true_solar_datetime.month,
            day=true_solar_datetime.day,
            hour=int(true_solar_datetime.hour),
            minute=int(true_solar_datetime.minute),
            second=int(true_solar_datetime.second),
            tzinfo=true_solar_datetime.tzinfo,
            )

    return true_solar_time


@validate_with_pydantic(CalculateTrueSolarTimeTimeSeriesNOAAInput)
def calculate_true_solar_time_time_series_noaa(
        longitude: Longitude,   # radians
        timestamps: Union[datetime, Sequence[datetime]], 
        timezone: Optional[ZoneInfo],
        time_output_units: str = 'minutes',
        angle_units: str = 'radians',
    ) -> Sequence[datetime]:
    true_solar_times = []
    for timestamp in timestamps:
        time_offset = calculate_time_offset_noaa(
            longitude=longitude,
            timestamp=timestamp,
            timezone=timezone,
            time_output_units=time_output_units,
            angle_units=angle_units,
        )  # in minutes
        true_solar_time = (
            timestamp.hour * 60 + timestamp.minute + timestamp.second / 60 + time_offset.value
        )

        if time_output_units == 'minutes':
            # if not 0 <= true_solar_time <= 1440:
            # if not 0 <= true_solar_time <= 1580:
            # if not -790 <= true_solar_time <= 790:
            if not -1580 <= true_solar_time <= 1580:
                raise ValueError(f'The calculated true solar time `{true_solar_time}` is out of the expected range [-1580, 1580] minutes!')

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
        true_solar_times.append(true_solar_time)

    return true_solar_times
