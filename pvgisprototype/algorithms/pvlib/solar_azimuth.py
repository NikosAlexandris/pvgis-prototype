#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
import numpy
import pvlib
from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import Latitude, Longitude, SolarAzimuth
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
# @validate_with_pydantic(CalculateSolarAzimuthPVLIBInputModel)
def calculate_solar_azimuth_series_pvlib(
    longitude: Longitude,  # degrees
    latitude: Latitude,  # degrees
    timestamps: DatetimeIndex,
    # timezone: ZoneInfo,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> SolarAzimuth:
    """Calculate the solar azimuth (θ)"""
    solar_position = pvlib.solarposition.get_solarposition(
        timestamps, latitude.degrees, longitude.degrees
    )
    azimuth_origin = "North"
    solar_azimuth_series = solar_position["azimuth"].values

    if not numpy.all(numpy.isfinite(solar_azimuth_series)) or not numpy.all(
        (SolarAzimuth().min_degrees <= solar_azimuth_series)
        & (solar_azimuth_series <= SolarAzimuth().max_degrees)
    ):
        raise ValueError(
            f"Solar azimuth values should be finite numbers and range in [{SolarAzimuth().min_degrees}, {SolarAzimuth().max_degrees}] degrees"
        )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=solar_azimuth_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return SolarAzimuth(
        value=solar_azimuth_series,
        unit=DEGREES,
        solar_positioning_algorithm="pvlib",
        solar_timing_algorithm="pvlib",
        origin=azimuth_origin,
    )
