from math import acos, tan
from zoneinfo import ZoneInfo
import numpy
from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import HourAngleSunrise, Latitude, Longitude, SolarHourAngle
from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    RADIANS,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.validation.functions import (
    CalculateEventHourAnglePVISInputModel,
    validate_with_pydantic,
)


@log_function_call
@custom_cached
def calculate_solar_hour_angle_series_hofierka(
    longitude: Longitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> SolarHourAngle:
    """Calculate the hour angle ω'

    ω = (ST / 3600 - 12) * 15 * pi / 180

    Parameters
    ----------

    solar_time: float
        The solar time (ST) is a calculation of the passage of time based on the
        position of the Sun in the sky. It is expected to be decimal hours in a
        24 hour format and measured internally in seconds.

    Returns
    --------

    hour_angle: float
        The solar hour angle (ω) is the angle at any instant through which the
        earth has to turn to bring the meridian of the observer directly in
        line with the sun's rays measured in radian.

    Notes
    -----
    If not mistaken, in PVGIS' C source code, the conversion function is:

        hour_angle = (solar_time / 3600 - 12) * 15 * 0.0175

        where the solar time was given in seconds.

    """
    from pvgisprototype.algorithms.noaa.solar_time import (
        calculate_true_solar_time_series_noaa,
    )

    true_solar_time_series = calculate_true_solar_time_series_noaa(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    solar_hour_angle_series = (true_solar_time_series.minutes - 720.0) * (
        numpy.pi / 720.0
    )
    # if (
    #     not isfinite(hour_angle.degrees)
    #     or not hour_angle.min_degrees <= hour_angle.degrees <= hour_angle.max_degrees
    # ):
    #     raise ValueError(
    #         f"The calculated solar hour angle {hour_angle.degrees} is out of the expected range\
    #         [{hour_angle.min_degrees}, {hour_angle.max_degrees}] degrees"
    #     )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=solar_hour_angle_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return SolarHourAngle(
        value=solar_hour_angle_series,
        unit=RADIANS,
        position_algorithm=SolarPositionModel.hofierka,
        timing_algorithm="Hofierka",
    )
