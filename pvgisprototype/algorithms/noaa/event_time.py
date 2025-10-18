#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
import numpy
from pvgisprototype.core.arrays import create_array
from pvgisprototype.log import logger
from datetime import timedelta
from typing import List
from zoneinfo import ZoneInfo

from devtools import debug
from pandas import DatetimeIndex, NaT, Timestamp, Timedelta

from pvgisprototype import EventTime, Latitude, Longitude, UnrefractedSolarZenith
from pvgisprototype.algorithms.noaa.equation_of_time import (
    calculate_equation_of_time_series_noaa,
)
from pvgisprototype.algorithms.noaa.event_hour_angle import (
    calculate_event_hour_angle_series_noaa,
)
from pvgisprototype.algorithms.noaa.function_models import (
    CalculateEventTimeTimeSeriesNOAAInput,
)
from pvgisprototype.api.position.models import SolarEvent
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.validation.functions import validate_with_pydantic


def calculate_solar_event_time_in_minutes(
    longitude: Longitude,
    event_hour_angle: float,
    equation_of_time: float,
    timezone_offset_hours_utc: float,
    event_type: str,
) -> float:
    """
    Calculate the event time in minutes based on the event type.

    Parameters
    ----------
    longitude : Longitude
        The longitude in radians.
    event_hour_angle : float
        The event hour angle in minutes.
    equation_of_time : float
        The equation of time in minutes.
    timezone_offset_hours_utc : float
        The timezone offset in hours.
    event_type : str
        The type of solar event ('sunrise', 'noon', 'sunset').

    Returns
    -------
    float
        The calculated event time in minutes.
    """
    # Calculate the base time
    base = 720 - equation_of_time.minutes + timezone_offset_hours_utc * 60
    longitude_minutes = longitude.as_minutes
    event_hour_angle_minutes = event_hour_angle.as_minutes

    # Define event calculations
    event_calculations = {
        SolarEvent.astronomical_twilight.name: lambda: base - (longitude_minutes + event_hour_angle_minutes + 4 * 18),
        SolarEvent.nautical_twilight.name: lambda: base - (longitude_minutes + event_hour_angle_minutes + 4 * 12),
        SolarEvent.civil_twilight.name: lambda: base - (longitude_minutes + event_hour_angle_minutes + 4 * 6),
        SolarEvent.sunrise.name: lambda: base - (longitude_minutes + event_hour_angle_minutes),
        SolarEvent.noon.name: lambda: base - longitude_minutes,
        SolarEvent.sunset.name: lambda: base - (longitude_minutes - event_hour_angle_minutes),
        SolarEvent.daylength.name: lambda: (
            base - (longitude_minutes - event_hour_angle_minutes) - 
            (base - (longitude_minutes + event_hour_angle_minutes))
        ),
    }

    # Calculate and return the event time
    if event_type in event_calculations:
        return event_calculations[event_type]()
    else:
        # raise ValueError(f"Unknown event type: {event_type}")
        logger.warning(
                f"Calculation for the {event_type} yet not implemented!",
                alt= f"Calculation for the [code]{event_type}[/code] yet [bold]not implemented[/bold]!",
                )
        return NaT


def match_event_times_to_timestamps(
    solar_event_series: dict,
    timestamps: DatetimeIndex,
    array_backend: str,
):
    """
    """
    try:
        # Define matching threshold dynamically based on inferred frequency
        frequency_threshold = Timedelta(timestamps.freq)
    except:
        raise ValueError("Unable to infer frequency from timestamps.")

    event_timestamps = numpy.full(
            shape=timestamps.shape,
            fill_value=numpy.datetime64('NaT'),
            dtype='datetime64[ns]',
    )
    event_types = create_array(
        timestamps.shape, dtype="object", init_method="empty", backend=array_backend
    )
    naive_timestamps = timestamps.tz_localize(None)

    for event_type, event_times in solar_event_series.items():

        # Find indices of closest matching timestamps
        event_indexer = naive_timestamps.get_indexer(event_times, method='nearest')

        # However, assign event times to indices only if within the frequency threshold
        for idx, event_time in zip(event_indexer, event_times):
            if idx >= 0:  # Valid index
                closest_timestamp = naive_timestamps[idx]
                if abs(event_time - closest_timestamp) <= frequency_threshold:
                    event_timestamps[idx] = event_time.to_numpy()
                    event_types[idx] = event_type

    return event_types, event_timestamps


@log_function_call
@custom_cached
@validate_with_pydantic(CalculateEventTimeTimeSeriesNOAAInput)
def calculate_solar_event_time_series_noaa(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    event: List[SolarEvent | None] = [None],
    unrefracted_solar_zenith: UnrefractedSolarZenith = UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    # adjust_for_atmospheric_refraction: bool = False,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> EventTime:
    """Calculate the time of solar events like sunrise, noon, or sunset.

    For sunrise and sunset, the zenith is set to 90.833 degrees (the
    approximate correction for atmospheric refraction and the size of the solar
    disk).

    Parameters
    ----------
    latitude : Latitude
        The latitude in radians.
    longitude : Longitude
        The longitude in radians.
    timestamps : DatetimeIndex
        The date to calculate the event for.
    timezone : ZoneInfo
        The timezone information.
    unrefracted_solar_zenith : UnrefractedSolarZenith, optional
        The zenith of the sun, adjusted for atmospheric refraction. Defaults to
        1.5853349194640094 radians, which corresponds to 90.833 degrees. This
        is the zenith at sunrise or sunset, adjusted for the approximate
        correction for atmospheric refraction at those times, and the size of
        the solar disk.
    event : List[Optional[SolarEvent]], optional
        A list of solar events to calculate the hour angle for, i.e. 'noon', 'sunrise', or 'sunset'.
    dtype : str, optional
        Data type for calculations. Default is DATA_TYPE_DEFAULT.
    array_backend : str, optional
        Backend for array operations. Default is ARRAY_BACKEND_DEFAULT.
    verbose : int, optional
        Verbosity level for logging. Default is VERBOSE_LEVEL_DEFAULT.
    log : int, optional
        Log level for logging. Default is LOG_LEVEL_DEFAULT.

    Returns
    -------
    EventTime
        The calculated times of the requested solar events as a DatetimeIndex.

    Notes
    -----
    - All angles are in radians.
    - The calculation `(1440 / (2 * pi)) * value_in_radians` maps a 'value in
      radians' from a range of [0, 2 * pi] which is a full circle to a range of
      [0, 1440] which is a full day in minutes.

    """
    if event == [SolarEvent.none]:
        return EventTime(
            value=None,
            event=None,
        )

    # Create an array of NaTs based on unique days from timestamps
    unique_days = timestamps.normalize().unique()
    event_hour_angle_series = calculate_event_hour_angle_series_noaa(
        latitude=latitude,
        timestamps=unique_days,
        unrefracted_solar_zenith=unrefracted_solar_zenith,
    )
    equation_of_time_series = calculate_equation_of_time_series_noaa(
        timestamps=unique_days,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
    )
    timezone_offset_timedelta = timezone.utcoffset(None)
    timezone_offset_hours_utc = timezone_offset_timedelta.total_seconds() / 3600

    from pvgisprototype.api.position.models import select_models
    requested_solar_events = select_models(
        SolarEvent, event
    )  # Using a callback fails!

    # Vectorized calculation of event times
    solar_events_time_series_in_minutes = {
        solar_event: calculate_solar_event_time_in_minutes(
            longitude,
            event_hour_angle_series,
            equation_of_time_series,
            timezone_offset_hours_utc,
            solar_event.name,
        )
        for solar_event in requested_solar_events if solar_event in SolarEvent
    }

    solar_event_series = dict()
    for solar_event in requested_solar_events:

        # Check if the event has calculated times
        if solar_event in solar_events_time_series_in_minutes:

            # Get the event times in minutes
            solar_event_series[solar_event] = DatetimeIndex(
                [
                    Timestamp(ts.date()) + timedelta(minutes=float(et))
                    for ts, et in zip(
                        unique_days, solar_events_time_series_in_minutes[solar_event]
                    )
                ]
            )
        else:
            logger.error(f"Event {event} not found in event_time_series_in_minutes.")

    event_types, event_timestamps = match_event_times_to_timestamps(
            solar_event_series=solar_event_series,
            timestamps=timestamps,
            array_backend=array_backend,
            )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=solar_event_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return EventTime(
        value=event_timestamps,
        event=event_types,
        hour_angle=event_hour_angle_series,
        equation_of_time=equation_of_time_series,
    )
