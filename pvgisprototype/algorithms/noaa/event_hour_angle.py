from devtools import debug
from datetime import datetime
# from math import cos
# from math import tan
# from math import acos
import numpy as np
from typing import Union, Sequence
from pandas import DatetimeIndex
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.algorithms.noaa.function_models import CalculateEventHourAngleNOAAInput
from pvgisprototype.algorithms.noaa.function_models import CalculateEventHourAngleTimeSeriesNOAAInput
from pvgisprototype import Latitude
from pvgisprototype import RefractedSolarZenith
from pvgisprototype import EventHourAngle
from pvgisprototype.algorithms.noaa.solar_declination import calculate_solar_declination_noaa
from pvgisprototype.algorithms.noaa.solar_declination import calculate_solar_declination_time_series_noaa
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT

@validate_with_pydantic(CalculateEventHourAngleNOAAInput)
def calculate_event_hour_angle_noaa(
        latitude: Latitude, # radians
        timestamp: datetime,
        refracted_solar_zenith: RefractedSolarZenith,
    ) -> EventHourAngle:
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
            )  # radians
    cosine_event_hour_angle = np.cos(refracted_solar_zenith.radians) / (
        np.cos(latitude.radians) * np.cos(solar_declination.radians)
    ) - np.tan(latitude.radians) * np.tan(solar_declination.radians)
    event_hour_angle = np.arccos(cosine_event_hour_angle)  # radians
    event_hour_angle = EventHourAngle(value=event_hour_angle, unit=RADIANS)

    return event_hour_angle


@validate_with_pydantic(CalculateEventHourAngleTimeSeriesNOAAInput)
def calculate_event_hour_angle_time_series_noaa(
    latitude: Latitude, # radians
    timestamps: DatetimeIndex,
    refracted_solar_zenith: RefractedSolarZenith = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = 0,
    log: int = 0,
) -> EventHourAngle:
    """
    """
    solar_declination = calculate_solar_declination_time_series_noaa(
        timestamps=timestamps,
    )  # radians
    cosine_event_hour_angle = np.cos(refracted_solar_zenith.radians) / (
        np.cos(latitude.radians) * np.cos(solar_declination.radians)
    ) - np.tan(latitude.radians) * np.tan(solar_declination.radians)
    event_hour_angle = np.arccos(np.clip(cosine_event_hour_angle, -1, 1))  # radians
    event_hour_angle = event_hour_angle.astype(dtype)

    return EventHourAngle(value=event_hour_angle, 
                        unit=RADIANS)
