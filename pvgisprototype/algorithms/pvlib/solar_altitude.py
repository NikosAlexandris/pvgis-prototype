import numpy
from pvlib.solarposition import get_solarposition
from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import Latitude, Longitude, SolarAltitude
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    DEGREES,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call


@log_function_call
@custom_cached
# @validate_with_pydantic(CalculateSolarAltitudePVLIBInputModel)
def calculate_solar_altitude_series_pvlib(
    longitude: Longitude,  # degrees
    latitude: Latitude,  # degrees
    timestamps: DatetimeIndex,
    # timezone: ZoneInfo,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> SolarAltitude:
    """Calculate the solar altitude (θ)"""
    solar_position = get_solarposition(
        timestamps, latitude.degrees, longitude.degrees
    )
    solar_altitude_series = solar_position["apparent_elevation"].values

    if not numpy.all(numpy.isfinite(solar_altitude_series)) or not numpy.all(
        (SolarAltitude().min_degrees <= solar_altitude_series)
        & (solar_altitude_series <= SolarAltitude().max_degrees)
    ):
        raise ValueError(
            f"Solar altitude values should be finite numbers and range in [{SolarAltitude().min_degrees}, {SolarAltitude().max_degrees}] degrees"
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
        unit=DEGREES,
        position_algorithm="pvlib",
        timing_algorithm="pvlib",
    )
