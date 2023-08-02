from .noaa_models import Longitude_in_Radians
from .noaa_models import Latitude_in_Radians
from .noaa_models import CalculateSolarAltitudeNOAAInput
from .decorators import validate_with_pydantic
from datetime import datetime
from .solar_hour_angle import calculate_solar_hour_angle_noaa
from .solar_zenith import calculate_solar_zenith_noaa
from math import pi
from math import isfinite
from ...api.utilities.conversions import convert_to_degrees_if_requested


@validate_with_pydantic(CalculateSolarAltitudeNOAAInput)
def calculate_solar_altitude_noaa(
        longitude: Longitude_in_Radians,
        latitude: Latitude_in_Radians,
        timestamp: float,
        timezone: str,
        apply_atmospheric_refraction: bool = True,
        time_output_units: str = 'minutes',
        angle_units: str = 'radians',
        angle_output_units: str = 'radians',
        ):
    """Calculate the solar zenith angle (φ) in radians
    """
    solar_hour_angle, solar_hour_angle_units = calculate_solar_hour_angle_noaa(
        longitude,
        timestamp,
        timezone,
        time_output_units,
        angle_output_units,
    )
    solar_zenith, solar_zenith_units = calculate_solar_zenith_noaa(
        latitude,
        timestamp,
        solar_hour_angle,
        apply_atmospheric_refraction,
        angle_units='radians',
        angle_output_units='radians',
    )  # radians
    solar_altitude = pi/2 - solar_zenith
    if not isfinite(solar_altitude) or not -pi/2 <= solar_altitude <= pi/2:
        raise ValueError(f'The `solar_altitude` should be a finite number ranging in [{-pi/2}, {pi/2}] radians')

    return solar_altitude, solar_zenith_units
