from devtools import debug

"""
The General Solar Position Calculations
provided by the NOAA Global Monitoring Division

See also: https://unpkg.com/solar-calculator@0.1.0/index.js
"""

import logging
from datetime import datetime
from datetime import timedelta
from datetime import time
from math import sin
from math import cos
from math import tan
from math import acos
from math import radians
from math import degrees
from math import pi
from math import isfinite
from typing import Annotated
from typing import Callable
from typing import Optional
from typing import Tuple
from typing import Union
from .decorators import validate_with_pydantic
from .noaa_models import Longitude
from .noaa_models import Latitude
from .noaa_models import CalculateSolarPositionNOAA
from zoneinfo import ZoneInfo

from .fractional_year import calculate_fractional_year_noaa 
from .equation_of_time import calculate_equation_of_time_noaa
from .solar_declination import calculate_solar_declination_noaa
from .time_offset import calculate_time_offset_noaa
from .solar_time import calculate_true_solar_time_noaa
from .solar_hour_angle import calculate_solar_hour_angle_noaa
from .solar_zenith import adjust_solar_zenith_for_atmospheric_refraction
from .solar_zenith import calculate_solar_zenith_noaa
from .solar_altitude import calculate_solar_altitude_noaa
from .solar_azimuth import calculate_solar_azimuth_noaa
from .event_hour_angle import calculate_event_hour_angle_noaa
from .event_time import calculate_event_time_noaa
from .local_time import calculate_local_solar_time_noaa

# REVIEW - ME
# 
# 1. Return the result without `output_units` : they are asked in the input!

radians_to_time_minutes = lambda value_in_radians: (1440 / (2 * pi)) * value_in_radians
degrees_to_time_minuts = lambda value_in_degrees: 4 * value_in_degrees


calculation_cache = {}


@validate_with_pydantic(CalculateSolarPositionNOAA)
def calculate_noaa_solar_position(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: str,
    refracted_solar_zenith: float = 1.5853349194640094,  # radians
    apply_atmospheric_refraction: bool = False,
    time_output_units: str = 'minutes',
    angle_units: str = 'radians',
    angle_output_units: str = 'radians',
) -> dict:
    """
    """
    result = {}
    fractional_year, _units = calculate_fractional_year_noaa(
            timestamp,
            angle_output_units
            )
    equation_of_time, _units = calculate_equation_of_time_noaa(
            timestamp,
            time_output_units,
            angle_units,  # for calculate_fractional_year_noaa()
            )
    solar_declination, _units = calculate_solar_declination_noaa(
            timestamp,
            angle_units,  # for calculate_fractional_year_noaa()
            angle_output_units
            )
    time_offset, _units = calculate_time_offset_noaa(
            longitude,
            timestamp,
            time_output_units,  # for calculate_equation_of_time_noaa()
            angle_units,  # for calculate_equation_of_time_noaa()
            )
    true_solar_time, _units = calculate_true_solar_time_noaa(
            longitude,
            timestamp,
            timezone,
            time_output_units,
            )
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
            angle_units,
            angle_output_units,
            )
    solar_altitude, _units = calculate_solar_altitude_noaa(
            longitude,
            latitude,
            timestamp,
            timezone,
            apply_atmospheric_refraction,
            time_output_units,
            angle_units,
            angle_output_units,
    )
    solar_azimuth, _units = calculate_solar_azimuth_noaa(
            longitude,
            latitude,
            timestamp,
            timezone,
            apply_atmospheric_refraction,
            time_output_units,
            angle_units,
            angle_output_units,
            )
    sunrise_time, _units = calculate_event_time_noaa(
            longitude,
            latitude,
            timestamp,
            timezone,
            'sunrise',
            refracted_solar_zenith,
            apply_atmospheric_refraction,
            time_output_units,
            angle_units,
            angle_output_units,
            )
    solar_noon_time, _units = calculate_event_time_noaa(
            longitude,
            latitude,
            timestamp,
            timezone,
            'noon',
            refracted_solar_zenith,
            apply_atmospheric_refraction,
            time_output_units,
            angle_units,
            angle_output_units,
            )
    local_solar_time, _units = calculate_local_solar_time_noaa(
            longitude,
            latitude,
            timestamp,
            timezone,
            refracted_solar_zenith,
            apply_atmospheric_refraction,
            time_output_units,
            angle_units,
            angle_output_units,
            )
    sunset_time, _units = calculate_event_time_noaa(
            longitude,
            latitude,
            timestamp,
            timezone,
            'sunset',
            refracted_solar_zenith,
            apply_atmospheric_refraction,
            time_output_units,
            angle_units,
            angle_output_units,
            )
    result['fractional_year'] = fractional_year
    result['equation_of_time'] = equation_of_time
    result['solar_declination'] = solar_declination
    result['time_offset'] = time_offset
    result['true_solar_time'] = true_solar_time
    result['solar_hour_angle'] = solar_hour_angle
    result['solar_zenith'] = solar_zenith
    result['solar_altitude'] = solar_altitude
    result['solar_azimuth'] = solar_azimuth
    result['sunrise_time'] = sunrise_time
    result['noon_time'] = solar_noon_time
    result['local_solar_time'] = local_solar_time
    result['sunset_time'] = sunset_time

    return result
