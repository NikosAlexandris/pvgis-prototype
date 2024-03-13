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
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pandas import DatetimeIndex
from rich import print
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES


@validate_with_pydantic(CalculateSolarAzimuthNOAAInput)
def calculate_solar_azimuth_noaa(
    longitude: Longitude,   # radians
    latitude: Latitude,     # radians
    timestamp: datetime,
    timezone: ZoneInfo,
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

                          # sin(latitude) * cos(solar_zenith) - sin(solar_declination)
          # θ = arccos(  -------------------------------------------------------------- )
                            #      cos(latitude) * sin(solar_zenith)


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
    # try else raise ... ?
    cosine_solar_azimuth = -1 * numerator / denominator
    solar_azimuth = acos(cosine_solar_azimuth)

    # ----------------------------------------------------- What is this for ?
    # if solar_hour_angle.radians > 0:
    #     solar_azimuth = 2 * pi - solar_azimuth
    # ------------------------------------------------------------------------

    if (
        not isfinite(solar_azimuth.degrees)
        or not solar_azimuth.min_degrees <= solar_azimuth.degrees <= solar_azimuth.max_degrees
    ):
        raise ValueError(
            f"The calculated solar azimuth angle {solar_azimuth.degrees} is out of the expected range\
            [{solar_azimuth.min_degrees}, {solar_azimuth.max_degrees}] degrees"
        )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return SolarAzimuth(
        value=solar_azimuth,
        unit=RADIANS,
        position_algorithm='NOAA',
        timing_algorithm='NOAA',
    )


@log_function_call
from cachetools import cached
from pvgisprototype.algorithms.caching import custom_hashkey
@cached(cache={}, key=custom_hashkey)
@validate_with_pydantic(CalculateSolarAzimuthTimeSeriesNOAAInput)
def calculate_solar_azimuth_time_series_noaa(
    longitude: Longitude,   # radians
    latitude: Latitude,     # radians
    timestamps: Union[datetime, DatetimeIndex],
    timezone: ZoneInfo,
    apply_atmospheric_refraction: bool = True,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = 0,
    log: int = 0,
) -> SolarAzimuth:
    """Calculate the solar azimuth (θ) for a time series"""
    solar_declination_series = calculate_solar_declination_time_series_noaa(
        timestamps=timestamps,
        dtype=dtype,
        backend=array_backend,
        verbose=verbose,
    )
    solar_hour_angle_series = calculate_solar_hour_angle_time_series_noaa(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
        dtype=dtype,
        backend=array_backend,
        verbose=verbose,
    )
    solar_zenith_series = calculate_solar_zenith_time_series_noaa(
        latitude=latitude,
        timestamps=timestamps,
        solar_hour_angle_series=solar_hour_angle_series,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        dtype=dtype,
        backend=array_backend,
        verbose=verbose,
    )
    numerator_series = sin(latitude.radians) * np.cos(solar_zenith_series.radians) - np.sin(solar_declination_series.radians)
    denominator_series = cos(latitude.radians) * np.sin(solar_zenith_series.radians)
    cosine_solar_azimuth_series = -1 * numerator_series / denominator_series
    solar_azimuth_series = np.arccos(cosine_solar_azimuth_series)

    if not np.all(np.isfinite(solar_azimuth_series)) or not np.all(
        (SolarAzimuth().min_radians <= solar_azimuth_series)
        & (solar_azimuth_series <= SolarAzimuth().max_radians)
    ):
        raise ValueError(
            f"At least one `solar_azimuth` value out of {solar_azimuth_series} is out of the expected range [{SolarAzimuth().min_radians}, {SolarAzimuth().max_radians}] radians"
        )
    log_data_fingerprint(
            data=solar_azimuth_series,
            log_level=log,
            hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return SolarAzimuth(
        value=solar_azimuth_series,
        unit=RADIANS,
        position_algorithm='NOAA',
        timing_algorithm='NOAA',
    )
