from devtools import debug
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from cachetools import cached
from pvgisprototype.caching import custom_hashkey
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarAltitudeNOAAInput
from pvgisprototype.validation.functions import CalculateSolarAltitudeNOAAInput
from pvgisprototype.algorithms.noaa.function_models import CalculateSolarAltitudeTimeSeriesNOAAInput
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from datetime import datetime
from zoneinfo import ZoneInfo
from pvgisprototype import SolarAltitude
from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.algorithms.noaa.solar_hour_angle import calculate_solar_hour_angle_noaa
from pvgisprototype.algorithms.noaa.solar_zenith import calculate_solar_zenith_noaa
from pvgisprototype.algorithms.noaa.solar_hour_angle import calculate_solar_hour_angle_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_zenith import calculate_solar_zenith_time_series_noaa
from math import pi
from math import isfinite
import numpy as np
from pvgisprototype.algorithms.noaa.solar_hour_angle import calculate_solar_hour_angle_noaa
from pvgisprototype.algorithms.noaa.solar_zenith import calculate_solar_zenith_noaa
from pvgisprototype.algorithms.noaa.solar_hour_angle import calculate_solar_hour_angle_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_zenith import calculate_solar_zenith_time_series_noaa
from math import pi
from math import isfinite
import numpy as np
from pandas import DatetimeIndex
from rich import print
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.log import logger


@validate_with_pydantic(CalculateSolarAltitudeNOAAInput)
def calculate_solar_altitude_noaa(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo,
    apply_atmospheric_refraction: bool = True,
    verbose: int = 0,
)-> SolarAltitude:
    """Calculate the solar altitude angle for a location and moment in time"""
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
    solar_altitude = pi / 2 - solar_zenith.radians
    if (
        # not isfinite(solar_altitude.degrees)
        # or not solar_altitude.min_degrees <= solar_altitude.degrees <= solar_altitude.max_degrees
        not isfinite(solar_altitude)
        or not SolarAltitude().min_radians <= solar_altitude <= SolarAltitude().max_radians
    ):
        raise ValueError(
            f"The calculated solar altitude angle {solar_altitude.degrees} is out of the expected range\
            [{solar_altitude.min_degrees}, {solar_altitude.max_degrees}] radians"
        )
    if verbose > 5:
        debug(locals())

    return SolarAltitude(
        value=solar_altitude,
        unit=RADIANS,
        position_algorithm='NOAA',
        timing_algorithm='NOAA',
    )


@log_function_call
@cached(cache={}, key=custom_hashkey)
@validate_with_pydantic(CalculateSolarAltitudeTimeSeriesNOAAInput)
def calculate_solar_altitude_time_series_noaa(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    apply_atmospheric_refraction: bool = True,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = 0,
    log: int = 0,
) -> SolarAltitude:
    """Calculate the solar altitude angle for a location over a time series"""
    solar_hour_angle_series = calculate_solar_hour_angle_time_series_noaa(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    solar_zenith_series = calculate_solar_zenith_time_series_noaa(
        latitude=latitude,
        timestamps=timestamps,
        solar_hour_angle_series=solar_hour_angle_series,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    solar_altitude_series = np.pi / 2 - solar_zenith_series.radians
    if not np.all(np.isfinite(solar_altitude_series)) or not np.all(
        (-np.pi / 2 <= solar_altitude_series) & (solar_altitude_series <= np.pi / 2)
    ):
        raise ValueError(
            f"The `solar_altitude` should be a finite number ranging in [{-np.pi/2}, {np.pi/2}] radians"
        )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
            data=solar_altitude_series,
            log_level=log,
            hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return SolarAltitude(
        value=solar_altitude_series,
        unit=RADIANS,
        position_algorithm=solar_zenith_series.position_algorithm,
        timing_algorithm=solar_hour_angle_series.timing_algorithm,
    )
