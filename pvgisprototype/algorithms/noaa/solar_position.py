from devtools import debug

"""
The General Solar Position Calculations
provided by the NOAA Global Monitoring Division

See also: https://unpkg.com/solar-calculator@0.1.0/index.js
"""

import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from math import pi

from .fractional_year import calculate_fractional_year_noaa 
from .equation_of_time import calculate_equation_of_time_noaa
from .solar_declination import calculate_solar_declination_noaa
from .time_offset import calculate_time_offset_noaa
from .solar_time import calculate_apparent_solar_time_noaa
from .solar_hour_angle import calculate_solar_hour_angle_noaa
from .solar_zenith import calculate_solar_zenith_noaa
from .solar_altitude import calculate_solar_altitude_noaa
from .solar_azimuth import calculate_solar_azimuth_noaa
from .event_time import calculate_event_time_noaa
from .local_time import calculate_local_solar_time_noaa

from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.algorithms.noaa.function_models import CalculateSolarPositionNOAAInput
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype import RefractedSolarZenith
from pvgisprototype import RefractedSolarZenith


radians_to_time_minutes = lambda value_in_radians: (1440 / (2 * pi)) * value_in_radians
degrees_to_time_minuts = lambda value_in_degrees: 4 * value_in_degrees
calculation_cache = {}


@validate_with_pydantic(CalculateSolarPositionNOAAInput)
def calculate_noaa_solar_position(
    longitude: Longitude,       # radians 
    latitude: Latitude,         # radians
    timestamp: datetime,
    timezone: ZoneInfo,
    refracted_solar_zenith: RefractedSolarZenith,  # radians
    timezone: ZoneInfo,
    refracted_solar_zenith: RefractedSolarZenith,  # radians
    apply_atmospheric_refraction: bool = False,
) -> dict:
    """
    """
    result = {}
    fractional_year = calculate_fractional_year_noaa(
        timestamp=timestamp,
    )
    equation_of_time = calculate_equation_of_time_noaa(
        timestamp=timestamp,
    )
    solar_declination = calculate_solar_declination_noaa(
        timestamp=timestamp,
    )
    time_offset = calculate_time_offset_noaa(
        longitude=longitude,
        timestamp=timestamp,
    )
    true_solar_time = calculate_apparent_solar_time_noaa(
        longitude=longitude,
        timestamp=timestamp,
        timezone=timezone,
    )  # in minutes
    solar_hour_angle = calculate_solar_hour_angle_noaa(
        longitude=longitude,
        timestamp=timestamp,
        timezone=timezone,
    )  # for solar_zenith
    solar_zenith = calculate_solar_zenith_noaa(
        latitude=latitude,
        timestamp=timestamp,
        solar_hour_angle=solar_hour_angle,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
    )
    solar_altitude = calculate_solar_altitude_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
    )
    solar_azimuth = calculate_solar_azimuth_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
    )
    sunrise_time = calculate_event_time_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        event="sunrise",
        refracted_solar_zenith=refracted_solar_zenith,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
    )
    solar_noon_time = calculate_event_time_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        event="noon",
        refracted_solar_zenith=refracted_solar_zenith,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
    )
    local_solar_time = calculate_local_solar_time_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        refracted_solar_zenith=refracted_solar_zenith,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
    )
    sunset_time = calculate_event_time_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        event="sunset",
        refracted_solar_zenith=refracted_solar_zenith,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
    )
    result["fractional_year"] = fractional_year
    result["equation_of_time"] = equation_of_time
    result["solar_declination"] = solar_declination
    result["time_offset"] = time_offset
    result["true_solar_time"] = true_solar_time
    result["solar_hour_angle"] = solar_hour_angle
    result["solar_zenith"] = solar_zenith
    result["solar_altitude"] = solar_altitude
    result["solar_azimuth"] = solar_azimuth
    result["sunrise_time"] = sunrise_time
    result["noon_time"] = solar_noon_time
    result["local_solar_time"] = local_solar_time
    result["sunset_time"] = sunset_time

    return result
