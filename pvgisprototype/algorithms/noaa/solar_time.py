from rich import print
from devtools import debug
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateTrueSolarTimeNOAAInput
from pvgisprototype.algorithms.noaa.function_models import CalculateTrueSolarTimeTimeSeriesNOAAInput
from pvgisprototype import Longitude
from typing import Optional
from typing import Union
from pandas import Timestamp
from pandas import Timedelta
from pandas import DatetimeIndex
from pvgisprototype.algorithms.noaa.time_offset import calculate_time_offset_noaa
from pvgisprototype.algorithms.noaa.time_offset import calculate_time_offset_time_series_noaa
from datetime import datetime
from datetime import timedelta
from zoneinfo import ZoneInfo
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import RADIANS


@validate_with_pydantic(CalculateTrueSolarTimeNOAAInput)
def calculate_true_solar_time_noaa(
    longitude: Longitude,   # radians
    timestamp: Timestamp, 
    timezone: Optional[ZoneInfo],
    verbose: int = VERBOSE_LEVEL_DEFAULT,
) -> Timestamp:
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

    Additional notes:

    From https://gml.noaa.gov/grad/solcalc/solareqns.PDF :

    Next, the true solar time is calculated in the following two equations.
    First the time offset is found, in minutes, and then the true solar time,
    in minutes.

        time_offset = eqtime + 4*longitude – 60*timezone

        where :
            - eqtime is in minutes,
            - longitude is in degrees (positive to the east of the Prime
              Meridian),
            - timezone is in hours from UTC (U.S. Mountain Standard Time = –7
              hours).

        tst = hr*60 + mn + sc/60 + time_offset

        where : 
            - hr is the hour (0 - 23),
            - mn is the minute (0 - 59),
            - sc is the second (0 - 59).
    """
    time_offset = calculate_time_offset_noaa(
        longitude=longitude,
        timestamp=timestamp,
        timezone=timezone,
        )  # in minutes
    time_offset_timedelta = timedelta(minutes=time_offset.minutes)
    time_offset_timedelta = timedelta(minutes=time_offset.minutes)
    true_solar_time = timestamp + time_offset_timedelta
    true_solar_time_minutes = (
        true_solar_time.hour * 60
        + true_solar_time.minute
        + true_solar_time.second / 60
    )
    # if not -1580 <= true_solar_time.minutes <= 1580:
    if not -1580 <= true_solar_time_minutes <= 1580:
        raise ValueError(f'The calculated true solar time `{true_solar_time_minutes}` is out of the expected range [-1580, 1580] minutes!')

    return true_solar_time


@validate_with_pydantic(CalculateTrueSolarTimeTimeSeriesNOAAInput)
def calculate_true_solar_time_time_series_noaa(
    longitude: Longitude,  # radians
    timestamps: DatetimeIndex,
    timezone: Optional[ZoneInfo],
    time_output_units: str = "minutes",
    angle_units: str = RADIANS,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
) -> DatetimeIndex:
    """ """
    time_offset_series = calculate_time_offset_time_series_noaa(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
    )
    true_solar_time_series = timestamps + Timedelta(minutes=1) * time_offset_series.value

    # Faster way to check this ? -------------------------------------------
    hours = true_solar_time_series.hour
    minutes = true_solar_time_series.minute
    seconds = true_solar_time_series.second
    true_solar_time_series_in_minutes = hours * 60 + minutes + seconds / 60

    if not (
        (-1580 <= true_solar_time_series_in_minutes)
        & (true_solar_time_series_in_minutes <= 1580)
    ).all():
        out_of_range_values = true_solar_time_series_in_minutes[
            ~(
                (-1580 <= true_solar_time_series_in_minutes)
                & (true_solar_time_series_in_minutes <= 1580)
            )
        ]
        raise ValueError(
            f"The calculated true solar time series `{true_solar_time_series_in_minutes}` is out of the expected range [-1580, 1580] minutes!"
        )
    # ----------------------------------------------------------------------

    from pvgisprototype.validation.hashing import generate_hash
    # true_solar_time_series_hash = generate_hash(true_solar_time_series)
    print(
        'TST : calculate_true_solar_time_time_series_noaa()|',
        f"Data Type : [bold]{true_solar_time_series.dtype}[/bold] |",
        # f"Output Hash : [code]{true_solar_time_series_hash}[/code]",
    )

    return true_solar_time_series
