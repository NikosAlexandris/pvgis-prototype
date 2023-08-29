from devtools import debug
from datetime import datetime
from math import pi
from datetime import time
from datetime import timedelta
from pvgisprototype.api.decorators import validate_with_pydantic
from .noaa_models import CalculateEventTimeNOAAInput
from pvgisprototype.api.data_classes.models import Longitude
from pvgisprototype.api.data_classes.models import Latitude
from pvgisprototype.api.data_classes.models import EventTime
from .equation_of_time import calculate_equation_of_time_noaa
from .solar_declination import calculate_solar_declination_noaa
from .solar_hour_angle import calculate_solar_hour_angle_noaa
from .solar_zenith import calculate_solar_zenith_noaa
from .event_hour_angle import calculate_event_hour_angle_noaa
from ...api.utilities.timestamp import attach_requested_timezone


# TODO: Maybe create a function that accepts a named_tuple and checks existing units
radians_to_time_minutes = lambda value_in_radians: (1440 / (2 * pi)) * value_in_radians


@validate_with_pydantic(CalculateEventTimeNOAAInput)
def calculate_event_time_noaa(
    longitude: Longitude,   # radians
    latitude: Latitude, # radians
    timestamp: datetime,
    timezone: str,
    event: str,
    refracted_solar_zenith: float = 1.5853349194640094,  # radians
    apply_atmospheric_refraction: bool = False,
    time_output_units: str = 'minutes',
    angle_units: str = 'radians',
    angle_output_units: str = 'radians',
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
    solar_declination : float
        The solar declination, in radians.
    solar_zenith : float, optional
        The solar zenith, in radians. Default is the cosine of 90.833 degrees.
    equation_of_time : float
        The equation of time, in minutes.
    event : str
        The event to calculate the hour angle for, either of 'noon', 'sunrise'
        or 'sunset'.
    output_units : str, optional
        The units for the output, either "radians" or "degrees". Default is 'radians'.

    Returns
    -------
    datetime
        The time of the event as a datetime object.

    Notes
    -----
    - All angles in radians
    - cosine(90.833) = -0.9629159426075866
    """
    equation_of_time = calculate_equation_of_time_noaa(
            timestamp=timestamp,
            time_output_units=time_output_units,
            angle_units=angle_units,
            )  # minutes
    solar_declination = calculate_solar_declination_noaa(
            timestamp=timestamp,
            angle_units=angle_units,  # for calculate_fractional_year_noaa()
            angle_output_units=angle_output_units,
            )  # radians
    solar_hour_angle = calculate_solar_hour_angle_noaa(
            longitude=longitude,
            timestamp=timestamp,
            timezone=timezone,
            time_output_units=time_output_units,
            angle_output_units=angle_output_units,
            )  # radians
    solar_zenith = calculate_solar_zenith_noaa(
            latitude=latitude,
            timestamp=timestamp,
            solar_hour_angle=solar_hour_angle,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            # time_output_units,
            angle_output_units=angle_output_units,
            )  # radians
    event_hour_angle = calculate_event_hour_angle_noaa(
            latitude=latitude,
            timestamp=timestamp,
            refracted_solar_zenith=refracted_solar_zenith,
            angle_units=angle_units,
            angle_output_units=angle_output_units,
            )
    event_hour_angle_minutes = radians_to_time_minutes(event_hour_angle.value)
    longitude_minutes = radians_to_time_minutes(longitude.value)

    # 2 * pi radians equals a circle, 360 degrees or 24 hours
    # 60 minutes * 24 hours = 1440 minutes (in 24 hours or a day)
    # `(1440 / (2 * pi)) * value_in_radians`
    #   maps the value in radians
    #   from a range of 0 to 2 * pi (a full circle)
    #   to a range of 0 to 1440 (a full day in minutes)
    event_calculations = {
        'sunrise': 720 - (longitude_minutes + event_hour_angle_minutes) - equation_of_time.value,
        'noon': 720 - longitude_minutes - equation_of_time.value,
        'sunset': 720 - (longitude_minutes - event_hour_angle_minutes) - equation_of_time.value
    }
    
    event_time = event_calculations.get(event.lower())
    event_datetime = datetime.combine(timestamp.date(), time(0)) + timedelta(minutes=event_time)
    event_datetime_utc = attach_requested_timezone(event_datetime)  # assign UTC

    # debug(locals())
    return event_datetime_utc
