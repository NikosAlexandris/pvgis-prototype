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
from pvgisprototype.core.validation.functions import (
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


@validate_with_pydantic(CalculateEventHourAnglePVISInputModel)
def calculate_event_hour_angle_pvis(  # rename to: calculate_event_hour_angle
    latitude: Latitude,
    surface_tilt: float = 0,
    solar_declination: float = 0,
) -> HourAngleSunrise:
    """Calculate the hour angle (ω) at sunrise and sunset

    Hour angle = acos(-tan(Latitude Angle-Tilt Angle)*tan(Declination Angle))

    The hour angle (ω) at sunrise and sunset measures the angular distance
    between the sun at the local solar time and the sun at solar noon.

    ω = acos(-tan(Φ-β)*tan(δ))

    Parameters
    ----------

    latitude: float
        Latitude (Φ) is the angle between the sun's rays and its projection on the
        horizontal surface measured in radians

    surface_tilt: float
        Surface tilt (or slope) (β) is the angle between the inclined surface
        (slope) and the horizontal plane.

    solar_declination: float
        Solar declination (δ) is the angle between the equator and a line drawn
        from the centre of the Earth to the centre of the sun measured in
        radians.

    Returns
    -------
    hour_angle_sunrise: float
        Hour angle (ω) is the angle at any instant through which the earth has
        to turn to bring the meridian of the observer directly in line with the
        sun's rays measured in radian.
    """
    hour_angle_sunrise_value = acos(
        -tan(latitude - surface_tilt) * tan(solar_declination)
    )
    hour_angle_sunrise = HourAngleSunrise(
        value=hour_angle_sunrise_value,
        unit=RADIANS,
    )

    return hour_angle_sunrise
