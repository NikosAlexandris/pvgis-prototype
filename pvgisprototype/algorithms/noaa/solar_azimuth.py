from devtools import debug
from typing import Union
from typing import Sequence
import numpy as np
from datetime import datetime
from zoneinfo import ZoneInfo
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
    verbose: int = 0,
)-> SolarAzimuth:
    """Calculate the solar azimuth angle (θ) in radians

    Parameters
    ----------
    latitude: float
        The latitude in radians
    """
    # Review & Cache Me ! ----------------------------------------------------
    solar_declination = calculate_solar_declination_noaa(
        timestamp=timestamp,
    )
    # ------------------------------------------------------------------------
    solar_hour_angle = calculate_solar_hour_angle_noaa(
        longitude=longitude,
        timestamp=timestamp,
        timezone=timezone,
    )
    solar_zenith = calculate_solar_zenith_noaa(
        latitude=latitude,
        timestamp=timestamp,
        solar_hour_angle=solar_hour_angle,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
    )

                   #   sin(latitude) * cos(solar_zenith) - sin(solar_declination)
    # cos(180 - θ) = - ----------------------------------------------------------
                   #            cos(latitude) * sin(solar_zenith)


    # or after converting cos(180 - θ) to - cos(θ)

                   #   sin(latitude) * cos(solar_zenith) - sin(solar_declination)
        # - cos(θ) = - ------------------------------------------------------------
                   #              cos(latitude) * sin(solar_zenith)


    # or :

                   # sin(latitude) * cos(solar_zenith) - sin(solar_declination)
          # cos(θ) = ----------------------------------------------------------
                   #             cos(latitude) * sin(solar_zenith)


    # or else, from the first equation, after multiplying by -1 :

                     # sin(latitude) * cos(solar_zenith) - sin(solar_declination)
    # - cos(180 - θ) = ----------------------------------------------------------
                     #          cos(latitude) * sin(solar_zenith)


    # or after multiplying by -1 again :

                   # sin(solar_declination) - sin(latitude) * cos(solar_zenith)
    # cos(180 - θ) = ----------------------------------------------------------
                   #            cos(latitude) * sin(solar_zenith)


    # or after converting cos(180 - θ) to - cos(θ)

               # sin(solar_declination) - sin(latitude) * cos(solar_zenith)
    # - cos(θ) = ----------------------------------------------------------
               #            cos(latitude) * sin(solar_zenith)

    # which is the same as reported in 

    numerator = sin(latitude.radians) * cos(solar_zenith.radians) - sin(solar_declination.radians)
    denominator = cos(latitude.radians) * sin(solar_zenith.radians)
    numerator = sin(latitude.radians) * cos(solar_zenith.radians) - sin(solar_declination.radians)
    denominator = cos(latitude.radians) * sin(solar_zenith.radians)
    # try else raise ... ?
    cosine_solar_azimuth = -1 * numerator / denominator
    solar_azimuth = acos(cosine_solar_azimuth)

    if solar_hour_angle.radians > 0:
        solar_azimuth = 2 * pi - solar_azimuth

    if not isfinite(solar_azimuth) or not 0 <= solar_azimuth <= 2*pi:
        raise ValueError('The `solar_azimuth` should be a finite number ranging in [0, 2π] radians')

    solar_azimuth = SolarAzimuth(
            value=solar_azimuth,
            unit='radians',
            )

    if verbose == 3:
        debug(locals())

    if not isfinite(solar_azimuth.radians) or not 0 <= solar_azimuth.radians <= 2*pi:
        raise ValueError('The `solar_azimuth` should be a finite number ranging in [0, 2π] radians')


    if not isfinite(solar_azimuth.radians) or not 0 <= solar_azimuth.radians <= 2*pi:
        raise ValueError('The `solar_azimuth` should be a finite number ranging in [0, 2π] radians')

    return solar_azimuth


@validate_with_pydantic(CalculateSolarAzimuthTimeSeriesNOAAInput)
def calculate_solar_azimuth_time_series_noaa(
    longitude: Longitude,   # radians
    latitude: Latitude,     # radians
    timestamps: Union[float, Sequence[float]],
    timezone: ZoneInfo,
    apply_atmospheric_refraction: bool = True,
    verbose: int = 0,
):# -> np.ndarray:
    """Calculate the solar azimuth (θ) in radians for a time series"""

    solar_declination_series = calculate_solar_declination_time_series_noaa(
        timestamps=timestamps,
    )
    solar_declination_series_array = np.array(
        [declination.radians for declination in solar_declination_series]
    )
    solar_hour_angle_series = calculate_solar_hour_angle_time_series_noaa(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
    )
    solar_hour_angle_series_array = np.array(
        [hour_angle.radians for hour_angle in solar_hour_angle_series]
    )
    solar_zenith_series = calculate_solar_zenith_time_series_noaa(
        latitude=latitude,
        timestamps=timestamps,
        solar_hour_angle_series=solar_hour_angle_series,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
    )
    solar_zenith_series_array = np.array(
        [zenith.radians for zenith in solar_zenith_series]
    )

    numerator_series = sin(latitude.radians) * np.cos(solar_zenith_series_array) - np.sin(solar_declination_series_array)
    denominator_series = cos(latitude.radians) * np.sin(solar_zenith_series_array)
    cosine_solar_azimuth_series = -1 * numerator_series / denominator_series
    solar_azimuth_series = np.arccos(cosine_solar_azimuth_series)

    if not np.all(np.isfinite(solar_azimuth_series)) or not np.all(
        (0 <= solar_azimuth_series) & (solar_azimuth_series <= 2 * np.pi)
    ):
        raise ValueError(f'The `solar_azimuth` is out of the expected range [0, {2* np.pi}] radians')

    solar_azimuth_series = [
        SolarAzimuth(value=azimuth, unit='radians') for azimuth in solar_azimuth_series
    ]
    if verbose == 3:
        debug(locals())

    return np.array(solar_azimuth_series, dtype=object)
