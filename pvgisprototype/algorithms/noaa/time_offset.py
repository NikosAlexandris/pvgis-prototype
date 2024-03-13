from rich import print
from devtools import debug
from zoneinfo import ZoneInfo
from math import pi
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateTimeOffsetNOAAInput
from pvgisprototype.validation.functions import CalculateTimeOffsetNOAAInput
from pvgisprototype import Longitude
from pvgisprototype import TimeOffset
from pvgisprototype.algorithms.noaa.function_models import CalculateTimeOffsetTimeSeriesNOAAInput
from pvgisprototype.algorithms.noaa.equation_of_time import calculate_equation_of_time_noaa
from pvgisprototype.algorithms.noaa.equation_of_time import calculate_equation_of_time_time_series_noaa
from typing import Union
import numpy as np
from pvgisprototype import EquationOfTime
from pandas import Timestamp
from pandas import DatetimeIndex
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint


# equivalent to : 4 * longitude (in degrees) ?
radians_to_time_minutes = lambda value_in_radians: (1440 / (2 * pi)) * value_in_radians


@validate_with_pydantic(CalculateTimeOffsetNOAAInput)
def calculate_time_offset_noaa(
        longitude: Longitude, 
        timestamp: Timestamp, 
        timezone: ZoneInfo,
    ) -> TimeOffset:
    """Calculate the time offset in minutes based on NOAA's solar geometry equations.

    Calculate the time offset (minutes) for NOAA's solar position calculations.

    The time offset (in minutes) incorporates the Equation of Time and accounts
    for the variation of the Local Solar Time (LST) within a given time zone
    due to the longitude variations within the time zone.

    Parameters
    ----------
    longitude: float
        The longitude for calculation in radians (note: differs from the original
        equation which expects degrees).

    timestamp: Timestamp
        The timestamp to calculate the offset for

    equation_of_time: float
        The equation of time value for calculation

    Returns
    -------
    float: The time offset

    Notes
    -----

    The reference equation here is:

        `time_offset = eqtime + 4*longitude – 60*timezone`

        (source: https://gml.noaa.gov/grad/solcalc/solareqns.PDF)

        where (variable name and units):
            - time_offset, minutes
            - longitude, degrees
            - timezone, hours
            - eqtime, minutes

    A cleaner (?) reference:

        `TC = 4 * (Longitude - LSTM) + EoT`

        where:
            - TC        : Time Correction Factor, minutes
            - Longitude : Geographical Longitude, degrees
            - LSTM      : Local Standard Time Meridian, degrees * hours

                where:
                - `LSTM = 15 degrees * ΔTUTC`
            
                    where:
                    - ΔTUTC = LT - UTC, hours

                        where:
                        - ΔTUTC : difference of LT from UTC in hours
                        - LT    : Local Time
                        - UTC   : Universal Coordinated Time

            - The factor 4 (minutes) comes from the fact that the Earth
              rotates 1° every 4 minutes.

            Examples:
                Mount Olympus is UTC + 2, hence LSTM = 15 * 2 = 30 deg. East

    Notes
    -----

    The time offset in minutes ranges in

        [ -720 (Longitude) - 840 (TimeZone) - 20 (Equation of Time) = -1580,
          +720 (Longitude) + 840 (TimeZone) + 20 (Equation of Time) = 1580 ]

    The valid ranges of the components that contribute to the time offset are:

    - Geographical longitude ranges from west to east in [-180, 180] degrees.
      A day is approximately 1440 minutes, hence converting the degrees to minutes,
      the longitude ranges in [-720, 720] minutes.

    - The timezone offset from the Coordinated Universal Time (UTC),
      considering time zones that are offset by unusual amounts of time from
      UTC, ranges  from west of UTC to east of UTC in [-12, 14] hours or [-720,
      840] minutes.

    - The Equation of Time accounts for the variations in the Earth's orbital
      speed and axial tilt. It varies throughout the year, but is typically
      within the range of about -20 minutes to +20 minutes.
    """

    # This will be 0 for UTC, obviously! Review-Me! --------------------------

    if timestamp.tzinfo is None or timestamp.tzinfo.utcoffset(timestamp) is None:
        timestamp = timestamp.tz_localize(timezone)
    else:
        timestamp = timestamp.tz_convert(timezone)

    timezone_offset_minutes = timestamp.utcoffset().total_seconds() / 60  # minutes
    equation_of_time = calculate_equation_of_time_noaa(
        timestamp=timestamp,
        )  # minutes
    time_offset = longitude.as_minutes - timezone_offset_minutes + equation_of_time.minutes
    time_offset = TimeOffset(value=time_offset, unit='minutes')
    if not TimeOffset().min_minutes <= time_offset.minutes <= TimeOffset().max_minutes:
        raise ValueError(f'The calculated time offset {time_offset} is out of the expected range [{TimeOffset().min_minutes, TimeOffset().max_minutes}] minutes!')

    return time_offset


@log_function_call
from pandas import DatetimeIndex
from cachetools.keys import hashkey
def custom_hashkey(*args, **kwargs):
    args = tuple(str(arg) if isinstance(arg, DatetimeIndex) else arg for arg in args)
    kwargs = {k: str(v) if isinstance(v, DatetimeIndex) else v for k, v in kwargs.items()}
    return hashkey(*args, **kwargs)

from cachetools import cached
@cached(cache={}, key=custom_hashkey)
@validate_with_pydantic(CalculateTimeOffsetTimeSeriesNOAAInput)
def calculate_time_offset_time_series_noaa(
    longitude: Longitude, 
    timestamps: Union[Timestamp, DatetimeIndex],
    timezone: ZoneInfo,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = 0,
    log: int = 0,
) -> TimeOffset:
    """ """
    # We need a timezone!
    if timestamps.tzinfo is None:
        timestamps = timestamps.tz_localize(timezone)
    else:
        timestamps = timestamps.tz_convert(timezone)

    # Optimisation : calculate unique offsets
    unique_timezones = timestamps.map(lambda ts: ts.tzinfo)
    unique_offsets = {tz: tz.utcoffset(None).total_seconds() / 60 for tz in set(unique_timezones)}
    
    # Map offsets back to timestamps
    timezone_offset_minutes_series = np.array([unique_offsets[tz] for tz in unique_timezones], dtype=dtype)

    # 2
    equation_of_time_series = calculate_equation_of_time_time_series_noaa(
        timestamps,
        dtype=dtype,
        backend=array_backend,
        verbose=verbose,
    )
    time_offset_series = longitude.as_minutes - timezone_offset_minutes_series + equation_of_time_series.minutes

    if not np.all((TimeOffset().min_minutes <= time_offset_series) & (time_offset_series <= TimeOffset().max_minutes)):
        raise ValueError("At least one calculated time offset is out of the expected range [{TimeOffset().min_minutes, TimeOffset().max_minutes] minutes!")

    log_data_fingerprint(
            data=time_offset_series,
            log_level=log,
            hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return TimeOffset(
        value=time_offset_series,
        unit='minutes',
        position_algorithm='NOAA',
        timing_algorithm='NOAA',
    )
