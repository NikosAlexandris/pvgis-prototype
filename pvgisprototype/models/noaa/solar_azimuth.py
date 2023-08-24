# from .noaa_models import LongitudeModel_in_Radians
# from .noaa_models import LatitudeModel_in_Radians
from .noaa_models import CalculateSolarAzimuthNOAAInput
from datetime import datetime
from .solar_declination import calculate_solar_declination_noaa
from .solar_hour_angle import calculate_solar_hour_angle_noaa
from .solar_zenith import calculate_solar_zenith_noaa
from math import sin
from math import cos
from math import acos
from math import pi
from math import isfinite
from ...api.utilities.conversions import convert_to_degrees_if_requested

from pvgisprototype.api.decorators import validate_with_pydantic
from pvgisprototype.api.data_classes import CompassSolarAzimuth
from pvgisprototype.api.data_classes import Longitude
from pvgisprototype.api.data_classes import Latitude


@validate_with_pydantic(CalculateSolarAzimuthNOAAInput)
def calculate_solar_azimuth_noaa(
        longitude: Longitude,   # radians
        latitude: Latitude,     # radians
        timestamp: datetime,
        timezone: str,
        apply_atmospheric_refraction: bool = True,
        time_output_units: str = 'minutes',
        angle_units: str = 'radians',
        angle_output_units: str = 'radians',
    )-> CompassSolarAzimuth:
    """Calculate the solar azimith (θ) in radians

    Parameters
    ----------
    latitude: float
        The latitude in radians
    """
    solar_declination = calculate_solar_declination_noaa(
            timestamp,
            angle_units,
            'radians',
            )  # radians
    solar_hour_angle = calculate_solar_hour_angle_noaa(
        longitude, timestamp, timezone, time_output_units, angle_output_units
    )  # radians
    solar_zenith = calculate_solar_zenith_noaa(
        latitude,
        timestamp,
        solar_hour_angle.value,
        apply_atmospheric_refraction,
        angle_units,
        angle_output_units,
            )  # radians
    # ------------------------------------------------------------------------
    # cosine_pi_minus_solar_azimuth = - (sin(latitude) * cos(solar_zenith) - sin(solar_declination)) / (
    #     cos(latitude) * sin(solar_zenith)
    # )
    # cosine_pi_minus_solar_azimuth = max(-1, min(1, cosine_pi_minus_solar_azimuth))
    # solar_azimuth = pi - pi_minus_solar_azimuth 
    # ------------------------------------------------------------------------

    # This formulas uses cosine,
    # so the _azimuth angle_ as shown by a calculator will always be positive
    # and should be interpreted as the angle between :
    #     - 0 and 180 degrees when the `solar_hour angle` is negative (morning)
    #     - 180 and 360 degrees when the `solar_hour_angle`, is positive (afternoon). 

    cosine_solar_azimuth = (
        sin(solar_declination.value) - sin(latitude) * cos(solar_zenith.value)
    ) / (cos(latitude) * sin(solar_zenith.value))
    solar_azimuth = acos(cosine_solar_azimuth)

    # # adjust azimuth range for the afternoon
    # if solar_hour_angle > 0:  
    #     solar_azimuth = 2*pi - solar_azimuth

    if not isfinite(solar_azimuth) or not 0 <= solar_azimuth <= 2*pi:
        raise ValueError('The `solar_azimuth` should be a finite number ranging in [0, 2π] radians')

    # solar_azimuth = convert_to_degrees_if_requested(solar_azimuth, angle_output_units)

    compass_solar_azimuth = 2*pi - solar_azimuth

    compass_solar_azimuth = CompassSolarAzimuth(
        value=compass_solar_azimuth,
        unit='radians',
    )    

    compass_solar_azimuth = convert_to_degrees_if_requested(
        compass_solar_azimuth,
        angle_output_units,
        )
    return compass_solar_azimuth
