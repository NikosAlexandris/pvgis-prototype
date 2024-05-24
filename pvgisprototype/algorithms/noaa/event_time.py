from datetime import time
from datetime import timedelta
from typing import Optional, List
<<<<<<< HEAD
from pandas import DatetimeIndex
from pandas import NaT
from zoneinfo import ZoneInfo
import numpy as np

||||||| 4cd84259
=======
from devtools import debug
from pandas import DatetimeIndex
>>>>>>> main
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.algorithms.noaa.function_models import CalculateEventTimeNOAAInput
from pvgisprototype.algorithms.noaa.function_models import CalculateEventTimeTimeSeriesNOAAInput
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from datetime import datetime
from pvgisprototype import RefractedSolarZenith
<<<<<<< HEAD
from pvgisprototype import EventTime
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype import EventTime
from pvgisprototype.algorithms.noaa.event_hour_angle import calculate_event_hour_angle_noaa
||||||| 4cd84259
from pvgisprototype.algorithms.noaa.event_hour_angle import calculate_event_hour_angle_noaa
=======
>>>>>>> main
from pvgisprototype.algorithms.noaa.event_hour_angle import calculate_event_hour_angle_time_series_noaa
from pvgisprototype.algorithms.noaa.equation_of_time import calculate_equation_of_time_time_series_noaa
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
def calculate_event_time_time_series_noaa(
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
):
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
<<<<<<< HEAD
    event_hour_angle = calculate_event_hour_angle_noaa(
        latitude=latitude,
        timestamp=timestamp,
        refracted_solar_zenith=refracted_solar_zenith,
    )
    equation_of_time = calculate_equation_of_time_noaa(
        timestamp=timestamp,
    )
    # 2 * pi radians equals a circle, 360 degrees or 24 hours
    # 60 minutes * 24 hours = 1440 minutes (in 24 hours or a day)
    # The calculation `(1440 / (2 * pi)) * value_in_radians`
    #   maps a  'value in radians'
    #   from a range of [0, 2 * pi] which is a full circle
    #   to a range of [0, 1440] which is a full day in minutes
    event_calculations = {
        'sunrise': 720 - (longitude.as_minutes + event_hour_angle.as_minutes) - equation_of_time.minutes,
        'noon': 720 - longitude.as_minutes - equation_of_time.minutes,
        'sunset': 720 - (longitude.as_minutes - event_hour_angle.as_minutes) - equation_of_time.minutes,
    }
    event_time = event_calculations.get(event.lower())
    event_datetime = datetime.combine(timestamp.date(), time(0)) + timedelta(minutes=event_time)
    event_datetime_utc = attach_requested_timezone(event_datetime)  # assign UTC

    return event_datetime_utc


@validate_with_pydantic(CalculateEventTimeTimeSeriesNOAAInput)
def calculate_event_time_time_series_noaa(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    event: str,
    timezone: ZoneInfo,
    refracted_solar_zenith: RefractedSolarZenith = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = 0,
    log: int = 0,
)-> EventTime:
    event_hour_angle = calculate_event_hour_angle_time_series_noaa(
||||||| 4cd84259
    event_hour_angle = calculate_event_hour_angle_noaa(
        latitude=latitude,
        timestamp=timestamp,
        refracted_solar_zenith=refracted_solar_zenith,
    )
    equation_of_time = calculate_equation_of_time_noaa(
        timestamp=timestamp,
    )
    # 2 * pi radians equals a circle, 360 degrees or 24 hours
    # 60 minutes * 24 hours = 1440 minutes (in 24 hours or a day)
    # The calculation `(1440 / (2 * pi)) * value_in_radians`
    #   maps a  'value in radians'
    #   from a range of [0, 2 * pi] which is a full circle
    #   to a range of [0, 1440] which is a full day in minutes
    event_calculations = {
        'sunrise': 720 - (longitude.as_minutes + event_hour_angle.as_minutes) - equation_of_time.minutes,
        'noon': 720 - longitude.as_minutes - equation_of_time.minutes,
        'sunset': 720 - (longitude.as_minutes - event_hour_angle.as_minutes) - equation_of_time.minutes,
    }
    event_time = event_calculations.get(event.lower())
    event_datetime = datetime.combine(timestamp.date(), time(0)) + timedelta(minutes=event_time)
    event_datetime_utc = attach_requested_timezone(event_datetime)  # assign UTC

    return event_datetime_utc


@validate_with_pydantic(CalculateEventTimeTimeSeriesNOAAInput)
def calculate_event_time_time_series_noaa(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: datetime,
    # timezone: str,
    event: str,
    refracted_solar_zenith: RefractedSolarZenith,
    apply_atmospheric_refraction: bool = False,
)-> List[datetime]:
    event_hour_angle = calculate_event_hour_angle_time_series_noaa(
=======
    event_hour_angle_series = calculate_event_hour_angle_time_series_noaa(
>>>>>>> main
        latitude=latitude,
        timestamps=timestamps,
        refracted_solar_zenith=refracted_solar_zenith,
    )
    equation_of_time_series = calculate_equation_of_time_time_series_noaa(
        timestamps=timestamps,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
    )
<<<<<<< HEAD

    timezone_offset_timedelta = timezone.utcoffset(None)
    timezone_offset_hours_utc = timezone_offset_timedelta.total_seconds() / 3600

||||||| 4cd84259
    # 2 * pi radians equals a circle, 360 degrees or 24 hours
    # 60 minutes * 24 hours = 1440 minutes (in 24 hours or a day)
    # The calculation `(1440 / (2 * pi)) * value_in_radians`
    #   maps a  'value in radians'
    #   from a range of [0, 2 * pi] which is a full circle
    #   to a range of [0, 1440] which is a full day in minutes
=======
>>>>>>> main
    event_calculations = {
<<<<<<< HEAD
        'sunrise': 720 - (longitude.as_minutes + event_hour_angle.as_minutes) - equation_of_time.minutes + timezone_offset_hours_utc * 60,
        'noon': (720 - longitude.as_minutes - equation_of_time.minutes + timezone_offset_hours_utc * 60),
        'sunset': 720 - (longitude.as_minutes - event_hour_angle.as_minutes) - equation_of_time.minutes + timezone_offset_hours_utc * 60,
||||||| 4cd84259
        'sunrise': 720 - (longitude.as_minutes + event_hour_angle.as_minutes) - equation_of_time.minutes,
        'noon': 720 - longitude.as_minutes - equation_of_time.minutes,
        'sunset': 720 - (longitude.as_minutes - event_hour_angle.as_minutes) - equation_of_time.minutes,
=======
        'sunrise': 720 - (longitude.as_minutes + event_hour_angle_series.as_minutes) - equation_of_time_series.minutes,
        'noon': 720 - longitude.as_minutes - equation_of_time_series.minutes,
        'sunset': 720 - (longitude.as_minutes - event_hour_angle_series.as_minutes) - equation_of_time_series.minutes,
>>>>>>> main
    }
<<<<<<< HEAD
    event_time = event_calculations.get(event.lower())
    event_datetimes = [datetime.combine(ts.date(), time(0)) + timedelta(minutes=et) for ts, et in zip(timestamps, event_time.tolist())]
||||||| 4cd84259
    event_time = event_calculations.get(event.lower())
    # event_datetime = datetime.combine(timestamps.date(), time(0)) + timedelta(minutes=event_time)
    event_datetimes = [datetime.combine(ts.date(), time(0)) + timedelta(minutes=et) for ts, et in zip(timestamps, event_time)]
=======
    event_time_series = event_calculations.get(event.lower())
    date_series = timestamps.date
    event_time_series_timedelta = np.array([timedelta(minutes=et) for et in event_time_series], dtype='timedelta64[m]')
    event_datetime_series = np.array([datetime.combine(date, time(0)) for date in date_series]) + event_time_series_timedelta
    event_datetime_series_utc = [attach_requested_timezone(ed) for ed in event_datetime_series]  # assign UTC
>>>>>>> main

<<<<<<< HEAD
    return EventTime(value = DatetimeIndex(event_datetimes), event = event)
||||||| 4cd84259
    event_datetime_utc = [attach_requested_timezone(ed) for ed in event_datetimes]  # assign UTC

    return event_datetime_utc
=======
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=event_datetime_series_utc,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return event_datetime_series_utc
>>>>>>> main
