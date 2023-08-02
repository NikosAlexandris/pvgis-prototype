from .noaa_models import CalculateSolarAltitudeNOAAInput
from .decorators import validate_with_pydantic
from datetime import datetime
from .solar_hour_angle import calculate_solar_hour_angle_noaa
from .solar_zenith import calculate_solar_zenith_noaa
from math import pi
from math import isfinite
from ...api.utilities.conversions import convert_to_degrees_if_requested

from pvgisprototype.api.data_classes import SolarAltitude
from pvgisprototype.api.data_classes import Longitude
from pvgisprototype.api.data_classes import Latitude


@validate_with_pydantic(CalculateSolarAltitudeNOAAInput, expand_args=True)
def calculate_solar_altitude_noaa(
        longitude: Longitude,   # radians
        latitude: Latitude,     # radians
        timestamp: float,
        timezone: str,
        apply_atmospheric_refraction: bool = True,
        time_output_units: str = 'minutes',
        angle_output_units: str = 'radians',
    )-> SolarAltitude:
    """Calculate the solar zenith angle (φ) in radians
    """
    solar_hour_angle = calculate_solar_hour_angle_noaa(
        longitude,
        timestamp,
        timezone,
        time_output_units,
        angle_output_units,
    )
    solar_zenith = calculate_solar_zenith_noaa(
        latitude,
        timestamp,
        solar_hour_angle.value,
        apply_atmospheric_refraction,
        angle_output_units='radians',
    )  # radians
    solar_altitude = pi/2 - solar_zenith.value
    if not isfinite(solar_altitude) or not -pi/2 <= solar_altitude <= pi/2:
        raise ValueError(f'The `solar_altitude` should be a finite number ranging in [{-pi/2}, {pi/2}] radians')

    solar_altitude = SolarAltitude(value=solar_altitude, unit=angle_output_units)
    return solar_altitude
