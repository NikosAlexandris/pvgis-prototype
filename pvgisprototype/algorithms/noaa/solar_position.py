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
from typing import Union, Sequence

from pvgisprototype.algorithms.noaa.fractional_year import calculate_fractional_year_time_series_noaa
from pvgisprototype.algorithms.noaa.equation_of_time import calculate_equation_of_time_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_declination import calculate_solar_declination_time_series_noaa
from pvgisprototype.algorithms.noaa.time_offset import calculate_time_offset_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_time import calculate_true_solar_time_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_hour_angle import calculate_solar_hour_angle_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_zenith import calculate_solar_zenith_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_altitude import calculate_solar_altitude_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_azimuth import calculate_solar_azimuth_time_series_noaa
from pvgisprototype.algorithms.noaa.event_time import calculate_event_time_time_series_noaa

from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.algorithms.noaa.function_models import CalculateTimeserieSolarPositionNOAAInput
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype import RefractedSolarZenith
from pvgisprototype import RefractedSolarZenith

from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint


radians_to_time_minutes = lambda value_in_radians: (1440 / (2 * pi)) * value_in_radians
degrees_to_time_minuts = lambda value_in_degrees: 4 * value_in_degrees
calculation_cache = {}


@log_function_call
@validate_with_pydantic(CalculateTimeserieSolarPositionNOAAInput)
def calculate_noaa_timeseries_solar_position(
    longitude: Longitude,       # radians 
    latitude: Latitude,         # radians
    timestamps: Sequence[datetime],
    timezone: ZoneInfo,
    refracted_solar_zenith: RefractedSolarZenith,  # radians
    apply_atmospheric_refraction: bool = False,
) -> dict:
    """
    """
    result = {}
    fractional_year = calculate_fractional_year_time_series_noaa(
        timestamps=timestamps,
    )
    equation_of_time = calculate_equation_of_time_time_series_noaa(
        timestamps=timestamps,
    )
    solar_declination = calculate_solar_declination_time_series_noaa(
        timestamps=timestamps,
    )
    time_offset = calculate_time_offset_time_series_noaa(
        longitude=longitude,
        timestamps=timestamps,
    )
    true_solar_time = calculate_true_solar_time_time_series_noaa(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
    )  # in minutes
    solar_hour_angle = calculate_solar_hour_angle_time_series_noaa(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
    )  # for solar_zenith
    solar_zenith = calculate_solar_zenith_time_series_noaa(
        latitude=latitude,
        timestamps=timestamps,
        solar_hour_angle_series=solar_hour_angle,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
    )
    solar_altitude = calculate_solar_altitude_time_series_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
    )
    solar_azimuth = calculate_solar_azimuth_time_series_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
    )
    sunrise_time = calculate_event_time_time_series_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        # timezone=timezone,
        event="sunrise",
        refracted_solar_zenith=refracted_solar_zenith,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
    )
    solar_noon_time = calculate_event_time_time_series_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        # timezone=timezone,
        event="noon",
        refracted_solar_zenith=refracted_solar_zenith,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
    )
    local_solar_time = calculate_true_solar_time_time_series_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        refracted_solar_zenith=refracted_solar_zenith,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
    )
    sunset_time = calculate_event_time_time_series_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        # timezone=timezone,
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
