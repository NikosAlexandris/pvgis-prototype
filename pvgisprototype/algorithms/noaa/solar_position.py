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
from zoneinfo import ZoneInfo
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

from pvgisprototype.api.decorators import validate_with_pydantic
from pvgisprototype.algorithms.noaa.function_models import CalculateSolarPositionNOAAInput
from pvgisprototype.api.models import Longitude
from pvgisprototype.api.models import Latitude


radians_to_time_minutes = lambda value_in_radians: (1440 / (2 * pi)) * value_in_radians
degrees_to_time_minuts = lambda value_in_degrees: 4 * value_in_degrees
calculation_cache = {}


@validate_with_pydantic(CalculateSolarPositionNOAAInput)
def calculate_noaa_solar_position(
    longitude: Longitude,       # radians 
    latitude: Latitude,         # radians
    timestamp: datetime,
    timezone: str = None,
    refracted_solar_zenith: float = 1.5853349194640094,  # radians
    apply_atmospheric_refraction: bool = False,
    time_output_units: str = 'minutes',
    angle_units: str = 'radians',
    angle_output_units: str = 'radians',
) -> dict:
    """
    """
    result = {}
    fractional_year = calculate_fractional_year_noaa(
        timestamp=timestamp,
        angle_output_units=angle_output_units,
    )
    equation_of_time = calculate_equation_of_time_noaa(
        timestamp=timestamp,
        time_output_units=time_output_units,
        angle_units=angle_units,
    )
    solar_declination = calculate_solar_declination_noaa(
        timestamp=timestamp,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
    )
    time_offset = calculate_time_offset_noaa(
        longitude=longitude,
        timestamp=timestamp,
        time_output_units=time_output_units,  # for calculate_equation_of_time_noaa()
        angle_units=angle_units,  # for calculate_equation_of_time_noaa()
    )
    true_solar_time = calculate_true_solar_time_noaa(
        longitude=longitude,
        timestamp=timestamp,
        timezone=timezone,
        time_output_units=time_output_units,
    )  # in minutes
    solar_hour_angle = calculate_solar_hour_angle_noaa(
        longitude=longitude,
        timestamp=timestamp,
        timezone=timezone,
        time_output_units=time_output_units,
        angle_output_units=angle_output_units,
    )  # for solar_zenith
    solar_zenith = calculate_solar_zenith_noaa(
        latitude=latitude,
        timestamp=timestamp,
        solar_hour_angle=solar_hour_angle,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        angle_output_units=angle_output_units,
    )
    solar_altitude = calculate_solar_altitude_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
    )
    solar_azimuth = calculate_solar_azimuth_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
    )
    sunrise_time = calculate_event_time_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        event="sunrise",
        refracted_solar_zenith=refracted_solar_zenith,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
    )
    solar_noon_time = calculate_event_time_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        event="noon",
        refracted_solar_zenith=refracted_solar_zenith,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
    )
    local_solar_time = calculate_local_solar_time_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        refracted_solar_zenith=refracted_solar_zenith,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
    )
    sunset_time = calculate_event_time_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        event="sunset",
        refracted_solar_zenith=refracted_solar_zenith,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
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
