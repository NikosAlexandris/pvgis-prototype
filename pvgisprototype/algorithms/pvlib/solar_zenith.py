from datetime import datetime

import numpy
import pvlib
from devtools import debug

from pvgisprototype import Latitude, Longitude, SolarZenith
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
# @validate_with_pydantic(CalculateSolarZenithPVLIBInputModel)
def calculate_solar_zenith_series_pvlib(
    longitude: Longitude,  # degrees
    latitude: Latitude,  # degrees
    timestamps: datetime,
    # timezone: ZoneInfo,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> SolarZenith:
    """Calculate the solar azimith (θ) in radians"""
    solar_position = pvlib.solarposition.get_solarposition(
        timestamps, latitude.degrees, longitude.degrees
    )
    solar_zenith_series = solar_position["zenith"].values

    if not numpy.all(numpy.isfinite(solar_zenith_series)) or not numpy.all(
        (SolarZenith().min_degrees <= solar_zenith_series)
        & (solar_zenith_series <= SolarZenith().max_degrees)
    ):
        raise ValueError(
            f"Solar zenith values should be finite numbers and range in [{SolarZenith().min_degrees}, {SolarZenith().max_degrees}] degrees"
        )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=solar_zenith_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )
    return SolarZenith(
        value=solar_zenith_series,
        unit=DEGREES,
        position_algorithm="pvlib",
        timing_algorithm="pvlib",
    )
