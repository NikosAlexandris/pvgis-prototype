from devtools import debug
from typing import Tuple
from datetime import datetime
from math import cos
from math import tan
from math import acos
from pvgisprototype.validation.functions import validate_with_pydantic
from .function_models import CalculateEventHourAngleNOAAInput
from pvgisprototype import Latitude
from pvgisprototype import RefractedSolarZenith
from pvgisprototype import EventTime
from .solar_declination import calculate_solar_declination_noaa
from pvgisprototype.api.utilities.conversions import convert_to_degrees_if_requested


@validate_with_pydantic(CalculateEventHourAngleNOAAInput)
def calculate_event_hour_angle_noaa(
        latitude: Latitude, # radians
        timestamp: datetime,
        refracted_solar_zenith: RefractedSolarZenith,
        angle_units: str = 'radians',
        # angle_output_units: str = 'radians',
    ) -> EventTime:
    """
    Calculates the event hour angle using the NOAA method.

    Parameters
    ----------
    latitude : Latitude
        The geographic latitude for which to calculate the event hour angle.

    timestamp : datetime
        The date and time for which to calculate the event hour angle.
    
    refracted_solar_zenith : float, optional
        The zenith of the sun, adjusted for atmospheric refraction. Defaults to
        1.5853349194640094 radians, which corresponds to 90.833 degrees. This
        is the zenith at sunrise or sunset, adjusted for the approximate
        correction for atmospheric refraction at those times, and the size of
        the solar disk.
    
    angle_units : str, optional
        The unit in which the angles are input. Defaults to 'radians'.
    
    angle_output_units : str, optional
        The unit in which the output angle should be returned. Defaults to
        'radians'.

    Returns
    -------
    event_hour_angle : float
        The calculated event hour angle.
    
    angle_output_units : str
        The unit of the output angle.

    Notes
    -----
    The function implements NOAA calculations for the solar declination and
    the event hour angle. The solar declination is calculated first in radians,
    followed by the event hour angle in radians.

    Commented out: If the output units are 'degrees', the function
    will convert the calculated event hour angle from radians to degrees.
    """
    solar_declination = calculate_solar_declination_noaa(
            timestamp=timestamp,
            angle_units=angle_units,
            # angle_output_units='radians',
            )  # radians
    cosine_event_hour_angle = cos(refracted_solar_zenith.radians) / (
        cos(latitude.radians) * cos(solar_declination.radians)
    ) - tan(latitude.radians) * tan(solar_declination.radians)
    event_hour_angle = acos(cosine_event_hour_angle)  # radians

    event_hour_angle = EventTime(value=event_hour_angle, unit='radians')

    # event_hour_angle = convert_to_degrees_if_requested(
    #         event_hour_angle,
    #         angle_output_units,
    #         )

    return event_hour_angle
