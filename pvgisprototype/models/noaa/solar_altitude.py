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
        longitude: float,
        latitude: datetime,
        timestamp: float,
        timezone: str,
        apply_atmospheric_refraction: bool = True,
        time_output_units: str = 'minutes',
        angle_units: str = 'radians',
        angle_output_units: str = 'radians',
        ):
    """Calculate the solar zenith angle (φ) in radians
    """
    # debug(locals())
    solar_hour_angle, _units = calculate_solar_hour_angle_noaa(
        longitude,
        timestamp,
        timezone,
        time_output_units,
        angle_output_units,
    )
    solar_zenith, _units = calculate_solar_zenith_noaa(
        latitude,
        timestamp,
        solar_hour_angle,
        apply_atmospheric_refraction,
        # time_output_units,
        angle_units,
        angle_output_units,
            )  # radians
    solar_altitude = pi/2 - solar_zenith
    if not isfinite(solar_altitude) or not -pi/2 <= solar_altitude <= pi/2:
        raise ValueError(f'The `solar_altitude` should be a finite number ranging in [{-pi/2}, {pi/2}] radians')

    solar_altitude = convert_to_degrees_if_requested(solar_altitude,
                                                     angle_output_units)
    # debug(locals())
    return solar_altitude, angle_output_units
