"""
The true solar time based on NOAA's General Solar Position Calculations.
"""

from rich import print
from devtools import debug
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateTrueSolarTimeNOAAInput
from pvgisprototype.algorithms.noaa.function_models import CalculateTrueSolarTimeTimeSeriesNOAAInput
from pvgisprototype import Longitude
from pvgisprototype import TrueSolarTime
from typing import Optional
from typing import Union
from pandas import Timestamp
from pandas import Timedelta
from pandas import to_timedelta
from pandas import DatetimeIndex
from numpy import array
from numpy import mod
from pvgisprototype.algorithms.noaa.time_offset import calculate_time_offset_noaa
from pvgisprototype.algorithms.noaa.time_offset import calculate_time_offset_time_series_noaa
from datetime import datetime
from datetime import timedelta
from zoneinfo import ZoneInfo
from pvgisprototype.constants import MINUTES, RADIANS
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from cachetools import cached
from pvgisprototype.caching import custom_hashkey
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint


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

    Returns
    -------
    float: The true solar time

    Notes
    -----

    See also
    --------
    pysolar

    In pysolar the true solar time is calculated as follows :

        ```
        (math.tm_hour(when) * 60 + math.tm_min(when) + 4 * longitude_deg + equation_of_time(math.tm_yday(when)))
        ```

        in which equation the last part is the time offset

        ```
        4 * longitude_deg + equation_of_time(math.tm_yday(when)))
        ```

    Additional notes:

    From NOAA's General Solar Position Calculations
    
        "Next, the true solar time is calculated in the following two
        equations. First the time offset is found, in minutes, and then the
        true solar time, in minutes."

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

    References
    ----------
    .. [0] https://gml.noaa.gov/grad/solcalc/solareqns.PDF

    """
    time_offset = calculate_time_offset_noaa(
        longitude=longitude,
        timestamp=timestamp,
        timezone=timezone,
        )  # in minutes
    time_offset_timedelta = timedelta(minutes=time_offset.minutes)
    true_solar_time = timestamp + time_offset_timedelta
    true_solar_time_minutes = (
        true_solar_time.hour * 60
        + true_solar_time.minute
        + true_solar_time.second / 60
    )
    if not TrueSolarTime().min_minutes <= true_solar_time_minutes <= TrueSolarTime().max_minutes:
        raise ValueError(f'The calculated true solar time `{true_solar_time_minutes}` is out of the expected range [{TrueSolarTime().min_minutes}, {TrueSolarTime().max_minutes}] minutes!')

    return true_solar_time


@log_function_call
@cached(cache={}, key=custom_hashkey)
@validate_with_pydantic(CalculateTrueSolarTimeTimeSeriesNOAAInput)
def calculate_true_solar_time_time_series_noaa(
    longitude: Longitude,  # radians
    timestamps: DatetimeIndex,
    timezone: Optional[ZoneInfo],
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> DatetimeIndex:
    """Calculate the true solar time at a specific geographic locations for a

    Calculate the true solar time at a specific geographic locations for a
    series of timestamps based on NOAA's General Solar Position Calculations
    [0]_.

    Parameters
    ----------
    timestamp: datetime, optional
        The timestamp to calculate offset for
    
    timezone: str, optional
        The timezone for calculation

    dtype : str, optional
        The data type for the calculations (the default is 'float32').

    array_backend : str, optional
        The backend used for calculations (the default is 'NUMPY').

    verbose: int
        Verbosity level

    log: int
        Log level

    Returns
    -------
    TrueSolarTime

    Notes
    -----
    The true solar time is the sum of the time offset and the true solar time
    in minutes.

        time_offset = eqtime + 4*longitude – 60*timezone

    References
    ----------
    .. [0] https://gml.noaa.gov/grad/solcalc/solareqns.PDF

    """
    time_offset_series = calculate_time_offset_time_series_noaa(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
    )
    true_solar_time_series = (timestamps - timestamps.normalize()).total_seconds() + (
        time_offset_series.value * 60
    )
    true_solar_time_series_in_minutes = mod(
        (true_solar_time_series).astype(dtype) / 60, 1440
    )

    if not (
        (TrueSolarTime().min_minutes <= true_solar_time_series_in_minutes)
        & (true_solar_time_series_in_minutes <= TrueSolarTime().max_minutes)
    ).all(): 
        out_of_range_values = true_solar_time_series_in_minutes[
            ~(
                (TrueSolarTime().min_minutes <= true_solar_time_series_in_minutes)
                & (true_solar_time_series_in_minutes <= TrueSolarTime().max_minutes)
            )
        ]
        raise ValueError(
            f"The calculated true solar time series `{true_solar_time_series_in_minutes}` is out of the expected range [{TrueSolarTime().min_minutes}, {TrueSolarTime().max_minutes}] minutes!"
        )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
            data=true_solar_time_series_in_minutes.values,
            log_level=log,
            hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return TrueSolarTime(
        value=array(true_solar_time_series_in_minutes, dtype = "float32"),
        unit = MINUTES,
        timing_algorithm="NOAA",
    )
