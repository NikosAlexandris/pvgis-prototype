from datetime import time
from datetime import timedelta
from pandas import DatetimeIndex
import numpy as np

from devtools import debug
from pandas import DatetimeIndex
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.algorithms.noaa.function_models import CalculateEventTimeTimeSeriesNOAAInput
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from datetime import datetime
from pvgisprototype import RefractedSolarZenith
from pvgisprototype import EventTime
from pvgisprototype.constants import NOT_AVAILABLE
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.algorithms.noaa.event_hour_angle import calculate_event_hour_angle_time_series_noaa
from pvgisprototype.algorithms.noaa.equation_of_time import calculate_equation_of_time_series_noaa
from pvgisprototype.api.utilities.timestamp import attach_requested_timezone
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from cachetools import cached
from pvgisprototype.caching import custom_hashkey


@log_function_call
@cached(cache={}, key=custom_hashkey)
@validate_with_pydantic(CalculateEventTimeTimeSeriesNOAAInput)
def calculate_event_time_series_noaa(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    # timezone: str,
    event: str,
    refracted_solar_zenith: RefractedSolarZenith,
    apply_atmospheric_refraction: bool = False,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
)-> EventTime:
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
    event_hour_angle_series = calculate_event_hour_angle_time_series_noaa(
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
    event_calculations = {
        "sunrise": 720 - (longitude.as_minutes + event_hour_angle_series.as_minutes) - equation_of_time_series.minutes,
        "noon": 720 - longitude.as_minutes - equation_of_time_series.minutes,
        "sunset": 720 - (longitude.as_minutes - event_hour_angle_series.as_minutes) - equation_of_time_series.minutes,
    }
    event_time_series = event_calculations.get(event.lower(), NOT_AVAILABLE)
    date_series = timestamps.date
    event_time_series_timedelta = np.array([timedelta(minutes=et) for et in event_time_series], dtype='timedelta64[m]')
    event_datetime_series = np.array([datetime.combine(date, time(0)) for date in date_series]) + event_time_series_timedelta
    event_datetime_series_utc = DatetimeIndex(attach_requested_timezone(ed) for ed in event_datetime_series) # assign UTC

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=event_datetime_series_utc,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return EventTime(
        value=event_datetime_series_utc,
        event=event,
    )
