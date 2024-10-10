"""
The time offset based on NOAA's General Solar Position Calculations.
"""

from zoneinfo import ZoneInfo
import numpy
from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import Longitude, TimeOffset
from pvgisprototype.algorithms.noaa.equation_of_time import (
    calculate_equation_of_time_series_noaa,
)
from pvgisprototype.algorithms.noaa.function_models import (
    CalculateTimeOffsetTimeSeriesNOAAInput,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    MINUTES,
    TIMEZONE_UTC,
    VERBOSE_LEVEL_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.validation.functions import validate_with_pydantic


ZONEINFO_UTC = ZoneInfo(TIMEZONE_UTC)


@log_function_call
@custom_cached
@validate_with_pydantic(CalculateTimeOffsetTimeSeriesNOAAInput)
def calculate_time_offset_series_noaa(
    longitude: Longitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo = ZONEINFO_UTC,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
) -> TimeOffset:
    """Calculate the variation of the local solar time within a
    given timezone for a time series.

    Calculate the variation of the local solar time, also referred to as _time
    offset_, within a timezone for NOAA's General Solar Position Calculations
    [0]_.

    The time offset (in minutes) incorporates the Equation of Time and
    accounts for the variation of the Local Solar Time (LST) within a given
    timezone due to the longitude variations within the time zone.

    Parameters
    ----------
    longitude: float
        The longitude for calculation in radians (note: differs from the original
        equation which expects degrees).

    timestamps: DatetimeIndex
        The timestamp to calculate the offset for

    timezone: ZoneInfo, optional
        The timezone

    dtype : str, optional
        The data type for the calculations (the default is 'float32').

    array_backend : str, optional
        The backend used for calculations (the default is 'NUMPY').

    verbose: int, optional
        Verbosity level

    log: int, optional
        Log level

    Returns
    -------
    TimeOffset:
        The time offset for a single or a series of timestamps.

    Notes
    -----
    The equation given in NOAA's General Solar Position Calculations [0]_ is

        time_offset = eqtime + 4*longitude – 60*timezone

        where (variable name and units):
        - time_offset, minutes
        - longitude, degrees
        - timezone, hours
        - eqtime, minutes

    See also
    --------
    pysolar

        In pysolar the true solar time is calculated as follows :

        ```
        (math.tm_hour(when) * 60 + math.tm_min(when) + 4 * longitude_deg + equation_of_time(math.tm_yday(when)))
        ```

        in which equation the time offset is the last part.

        ```
        4 * longitude_deg + equation_of_time(math.tm_yday(when)))
        ```

    Another reference

        TC = 4 * (Longitude - LSTM) + EoT

        where:

        - TC        : Time Correction Factor, minutes
        - Longitude : Geographical Longitude, degrees
        - LSTM      : Local Standard Time Meridian, degrees * hours
        - EoT       : Equation of Time

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

    The time offset in minutes ranges in

        [ -720 (Longitude) - 720 (Up to -12 TimeZones) - 20 (Equation of Time) = -1460,
          +720 (Longitude) + 840 (Up to +14 TimeZones) + 20 (Equation of Time) = 1580 ]

    The valid ranges of the components that contribute to the time offset are:

    - Geographical longitude ranges from west to east in [-180, 180] degrees.
      A day is approximately 1440 minutes, hence converting the degrees to
      minutes, the longitude ranges in [-720, 720] minutes.

    - The timezone offset from the Coordinated Universal Time (UTC),
      considering time zones that are offset by unusual amounts of time from
      UTC, ranges  from west of UTC to east of UTC in [-12, 14] hours or [-720,
      840] minutes.

    - The Equation of Time accounts for the variations in the Earth's orbital
      speed and axial tilt. It varies throughout the year, but is typically
      within the range of about -20 minutes to +20 minutes.

    References
    ----------
    .. [0] https://gml.noaa.gov/grad/solcalc/solareqns.PDF

    """
    local_standard_time_meridian_minutes_series = 0  # in UTC the offest is 0
    if timezone and timezone != ZONEINFO_UTC:
        # We need the .tz attribute to compare with the user-requested timezone !
        if not timestamps.tz:
            timestamps = timestamps.tz_localize(timezone)

        # Explain why this is necessary !-------------- Further Optimisation ?
        unique_timezone_offsets_in_minutes = {
            stamp.tzinfo: stamp.tzinfo.utcoffset(stamp).total_seconds() / 60
            for stamp in timestamps if stamp.tzinfo is not None
        }
        local_standard_time_meridian_minutes_series = numpy.array(
            [
                unique_timezone_offsets_in_minutes[stamp.tzinfo]
                for stamp in timestamps
                if stamp.tzinfo is not None
            ],
            dtype=dtype,
        )
        # # ------------------------------------------- Further Optimisation ?

    equation_of_time_series = calculate_equation_of_time_series_noaa(
        timestamps=timestamps,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        validate_output=validate_output,
    )
    time_offset_series_in_minutes = (
        longitude.as_minutes
        - local_standard_time_meridian_minutes_series
        + equation_of_time_series.minutes
    )

    if validate_output:
        if not numpy.all(
            (TimeOffset().min_minutes <= time_offset_series_in_minutes)
            & (time_offset_series_in_minutes <= TimeOffset().max_minutes)
        ):
            index_of_out_of_range_values = np.where(
                (time_offset_series_in_minutes < TimeOffset().min_minutes)
                | (time_offset_series_in_minutes > TimeOffset().max_minutes)
            )
            out_of_range_values = time_offset_series_in_minutes[
                index_of_out_of_range_values
            ]
            raise ValueError(
                f"{WARNING_OUT_OF_RANGE_VALUES} "
                f"[{TimeOffset().min_minutes}, {TimeOffset().max_minutes}] minutes"
                f" in [code]time_offset_series_in_minutes[/code] : {out_of_range_values}"
            )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=time_offset_series_in_minutes,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return TimeOffset(
        value=time_offset_series_in_minutes,
        unit=MINUTES,
        position_algorithm="NOAA",
        timing_algorithm="NOAA",
    )
