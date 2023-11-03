from datetime import time
from datetime import timedelta
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.algorithms.noaa.function_models import CalculateEventTimeNOAAInput
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from datetime import datetime
from pvgisprototype import RefractedSolarZenith
from pvgisprototype.algorithms.noaa.event_hour_angle import calculate_event_hour_angle_noaa
from pvgisprototype.algorithms.noaa.equation_of_time import calculate_equation_of_time_noaa
from pvgisprototype.api.utilities.timestamp import attach_requested_timezone


@validate_with_pydantic(CalculateEventTimeNOAAInput)
def calculate_event_time_noaa(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: str,
    event: str,
    refracted_solar_zenith: RefractedSolarZenith,
    apply_atmospheric_refraction: bool = False,
)-> datetime:
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
    """
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
        'sunrise': 720 - (longitude.minutes + event_hour_angle.minutes) - equation_of_time.minutes,
        'noon': 720 - longitude.minutes - equation_of_time.minutes,
        'sunset': 720 - (longitude.minutes - event_hour_angle.minutes) - equation_of_time.minutes,
    }
    event_time = event_calculations.get(event.lower())
    event_datetime = datetime.combine(timestamp.date(), time(0)) + timedelta(minutes=event_time)
    event_datetime_utc = attach_requested_timezone(event_datetime)  # assign UTC

    return event_datetime_utc
