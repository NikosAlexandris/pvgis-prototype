"""
The true solar time based on NOAA's General Solar Position Calculations.
"""

from zoneinfo import ZoneInfo
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES

from devtools import debug
from numpy import array, mod
from pandas import DatetimeIndex

from pvgisprototype import Longitude, TrueSolarTime
from pvgisprototype.algorithms.noaa.function_models import (
    CalculateTrueSolarTimeTimeSeriesNOAAInput,
)
from pvgisprototype.algorithms.noaa.time_offset import calculate_time_offset_series_noaa
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    MINUTES,
    VERBOSE_LEVEL_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.validation.functions import validate_with_pydantic


@log_function_call
@custom_cached
@validate_with_pydantic(CalculateTrueSolarTimeTimeSeriesNOAAInput)
def calculate_true_solar_time_series_noaa(
    longitude: Longitude,  # radians
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
) -> TrueSolarTime:
    """Calculate the true solar time at a specific geographic locations for a
    time series.

    Calculate the true solar time at a specific geographic locations for a
    series of timestamps based on NOAA's General Solar Position Calculations
    [0]_.

    The true solar time is the sum of the mean solar time and the equation of
    time.  CONFIRM!?

    Parameters
    ----------
    timestamps: DatetimeIndex, optional
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
    time_offset_series = calculate_time_offset_series_noaa(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        validate_output=validate_output,
    )
    true_solar_time_series = (
        timestamps - timestamps.normalize()
    ).total_seconds() + time_offset_series.value * 60

    # array_parameters = {
    #     "shape": true_solar_time_series.shape,
    #     "dtype": dtype,
    #     "init_method": "zeros",
    #     "backend": array_backend,
    # }
    # true_solar_time_series_in_minutes = create_array(**array_parameters)
    true_solar_time_series_in_minutes = mod(
        (true_solar_time_series).astype(dtype) / 60, 1440
    )
    
    if validate_output:
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
                f"{WARNING_OUT_OF_RANGE_VALUES} "
                f"[{TrueSolarTime().min_minutes}, {TrueSolarTime().max_minutes}] minutes"
                f" in [code]true_solar_time_series_in_minutes[/code] : {out_of_range_values}"
            )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=true_solar_time_series_in_minutes,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return TrueSolarTime(
        value=array(true_solar_time_series_in_minutes, dtype=dtype),
        unit=MINUTES,
        timing_algorithm=SolarTimeModel.noaa,
    )
