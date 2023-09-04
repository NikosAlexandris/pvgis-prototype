from devtools import debug
from typing import Union
from typing import Sequence
import numpy as np
from datetime import datetime
from math import sin
from math import cos
from math import acos
from math import pi
from math import isfinite
from pvgisprototype.api.utilities.conversions import convert_to_degrees_if_requested
from pvgisprototype.algorithms.noaa.solar_declination import calculate_solar_declination_noaa
from pvgisprototype.algorithms.noaa.solar_declination import calculate_solar_declination_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_hour_angle import calculate_solar_hour_angle_noaa
from pvgisprototype.algorithms.noaa.solar_hour_angle import calculate_solar_hour_angle_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_zenith import calculate_solar_zenith_noaa
from pvgisprototype.algorithms.noaa.solar_zenith import calculate_solar_zenith_time_series_noaa

from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.algorithms.noaa.function_models import CalculateSolarAzimuthNOAAInput
from pvgisprototype.algorithms.noaa.function_models import CalculateSolarAzimuthTimeSeriesNOAAInput
from pvgisprototype import SolarAzimuth
from pvgisprototype import Longitude
from pvgisprototype import Latitude


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
    )-> SolarAzimuth:
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
    )
    solar_hour_angle = calculate_solar_hour_angle_noaa(
        longitude, timestamp, timezone, time_output_units, angle_output_units
    )
    solar_zenith = calculate_solar_zenith_noaa(
        latitude=latitude,
        timestamp=timestamp,
        solar_hour_angle=solar_hour_angle,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        angle_output_units='radians',
    )
                     # sin(latitude) * cos(solar_zenith) - sin(solar_declination)
    # cos(180 - θ) = - ----------------------------------------------------------
                     #            cos(latitude) * sin(solar_zenith)


                     # sin(latitude) * cos(solar_zenith) - sin(solar_declination)
        # - cos(θ) = - ------------------------------------------------------------
                     #            cos(latitude) * sin(solar_zenith)


                   # sin(latitude) * cos(solar_zenith) - sin(solar_declination)
          # cos(θ) = ----------------------------------------------------------
                   #             cos(latitude) * sin(solar_zenith)


    # numerator = sin(solar_declination.value) - sin(latitude.value) * cos(solar_zenith.value)
    numerator = sin(latitude.value) * cos(solar_zenith.value) - sin(solar_declination.value)
    denominator = cos(latitude.value) * sin(solar_zenith.value)
    # try else raise ... ?
    cosine_solar_azimuth = numerator / denominator
    solar_azimuth = acos(cosine_solar_azimuth)

    if not isfinite(solar_azimuth) or not 0 <= solar_azimuth <= 2*pi:
        raise ValueError('The `solar_azimuth` should be a finite number ranging in [0, 2π] radians')

    solar_azimuth = SolarAzimuth(
            value=solar_azimuth,
            unit='radians',
            )
    solar_azimuth = convert_to_degrees_if_requested(solar_azimuth, angle_output_units)

    return solar_azimuth


@validate_with_pydantic(CalculateSolarAzimuthTimeSeriesNOAAInput)
def calculate_solar_azimuth_time_series_noaa(
    longitude: Longitude,   # radians
    latitude: Latitude,     # radians
    timestamps: Union[float, Sequence[float]],
    timezone: str,
    apply_atmospheric_refraction: bool = True,
    time_output_units: str = 'minutes',
    angle_units: str = 'radians',
    angle_output_units: str = 'radians',
):# -> np.ndarray:
    """Calculate the solar azimuth (θ) in radians for a time series"""

    solar_declination_series = calculate_solar_declination_time_series_noaa(
        timestamps,
        angle_units,
        'radians',
    )
    solar_hour_angle_series = calculate_solar_hour_angle_time_series_noaa(
        longitude, timestamps, timezone, time_output_units, angle_output_units
    )
    solar_zenith_series = calculate_solar_zenith_time_series_noaa(
        latitude=latitude,
        timestamps=timestamps,
        solar_hour_angle_series=solar_hour_angle_series,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        angle_output_units='radians',
    )

    solar_azimuth_series = []
    for solar_declination, solar_zenith in zip(solar_declination_series, solar_zenith_series):
        numerator = sin(latitude.value) * cos(solar_zenith.value) - sin(solar_declination.value)
        denominator = cos(latitude.value) * sin(solar_zenith.value)
        cosine_solar_azimuth = numerator / denominator
        solar_azimuth = acos(cosine_solar_azimuth)

        if not isfinite(solar_azimuth) or not 0 <= solar_azimuth <= 2*pi:
            raise ValueError('The `solar_azimuth` should be a finite number ranging in [0, 2π] radians')

        solar_azimuth = SolarAzimuth(
                value=solar_azimuth,
                unit='radians',
                )
        solar_azimuth = convert_to_degrees_if_requested(solar_azimuth, angle_output_units)
        solar_azimuth_series.append(solar_azimuth)

    return np.array(solar_azimuth_series, dtype=object)
