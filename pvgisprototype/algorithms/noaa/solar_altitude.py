from devtools import debug
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from cachetools import cached
from pvgisprototype.caching import custom_hashkey
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.algorithms.noaa.function_models import CalculateSolarAltitudeTimeSeriesNOAAInput
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from zoneinfo import ZoneInfo
from pvgisprototype import SolarAltitude
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.algorithms.noaa.solar_zenith import calculate_solar_zenith_time_series_noaa
import numpy as np
from pvgisprototype.algorithms.noaa.solar_zenith import calculate_solar_zenith_time_series_noaa
import numpy as np
from pandas import DatetimeIndex
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.log import logger


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
    solar_zenith_series = calculate_solar_zenith_time_series_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
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
        timing_algorithm=solar_zenith_series.timing_algorithm,
    )
