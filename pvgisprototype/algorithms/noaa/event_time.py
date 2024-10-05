from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import EventTime, Latitude, Longitude, RefractedSolarZenith
from pvgisprototype.algorithms.noaa.equation_of_time import (
    calculate_equation_of_time_series_noaa,
)
from pvgisprototype.algorithms.noaa.event_hour_angle import (
    calculate_event_hour_angle_series_noaa,
)
from pvgisprototype.algorithms.noaa.function_models import (
    CalculateEventTimeTimeSeriesNOAAInput,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    NOT_AVAILABLE,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.core.validation.functions import validate_with_pydantic


@log_function_call
@custom_cached
@validate_with_pydantic(CalculateEventTimeTimeSeriesNOAAInput)
def calculate_event_time_series_noaa(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    event: str,
    refracted_solar_zenith: RefractedSolarZenith,
    apply_atmospheric_refraction: bool = False,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> EventTime:
    """Calculate the sunrise or sunset

    For the special case of sunrise or sunset, the zenith is set to 90.833 deg.
    (the approximate correction for atmospheric refraction at sunrise and
    sunset, and the size of the solar disk).

    Parameters
    ----------
    latitude : float
        The latitude, in radians.
    longitude : float
        The longitude, in radians.
    timestamp : datetime
        The date to calculate the event for.
    refracted_solar_zenith : float, optional
        The refracted solar zenith angle in radians. Default is the cosine of 90.833 degrees.
    event : str
        The event to calculate the hour angle for, either of 'noon', 'sunrise' or 'sunset'.

    Returns
    -------
    datetime
        The time of the event as a datetime object.

    Notes
    -----
    - All angles in radians
    - cosine(90.833) = -0.9629159426075866

    2 * pi radians equals a circle, 360 degrees or 24 hours
    60 minutes * 24 hours = 1440 minutes (in 24 hours or a day)
    The calculation `(1440 / (2 * pi)) * value_in_radians`
      maps a  'value in radians'
      from a range of [0, 2 * pi] which is a full circle
      to a range of [0, 1440] which is a full day in minutes
    """
    event_hour_angle_series = calculate_event_hour_angle_series_noaa(
        latitude=latitude,
        timestamps=timestamps,
        refracted_solar_zenith=refracted_solar_zenith,
    )
    equation_of_time_series = calculate_equation_of_time_series_noaa(
        timestamps=timestamps,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
    )

    timezone_offset_timedelta = timezone.utcoffset(None)
    timezone_offset_hours_utc = timezone_offset_timedelta.total_seconds() / 3600

    event_calculations = {
        "sunrise": 720
        - (longitude.as_minutes + event_hour_angle_series.as_minutes)
        - equation_of_time_series.minutes
        + timezone_offset_hours_utc * 60,
        "noon": (
            720
            - longitude.as_minutes
            - equation_of_time_series.minutes
            + timezone_offset_hours_utc * 60
        ),
        "sunset": 720
        - (longitude.as_minutes - event_hour_angle_series.as_minutes)
        - equation_of_time_series.minutes
        + timezone_offset_hours_utc * 60,
    }
    event_time_series = event_calculations.get(event.lower(), NOT_AVAILABLE)
    event_datetimes = [
        datetime.combine(ts.date(), time(0)) + timedelta(minutes=et)
        for ts, et in zip(timestamps, event_time_series.tolist())
    ]

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=DatetimeIndex(event_datetimes),
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return EventTime(
        value=DatetimeIndex(event_datetimes),
        event=event,
    )
