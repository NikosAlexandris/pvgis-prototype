from devtools import debug
from datetime import datetime
from zoneinfo import ZoneInfo
from math import isfinite
import numpy
import pvlib
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarAltitudePVLIBInputModel
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype import SolarAltitude
from pvgisprototype.constants import DEGREES
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from cachetools import cached
from pvgisprototype.caching import custom_hashkey
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT


@validate_with_pydantic(CalculateSolarAltitudePVLIBInputModel)
def calculate_solar_altitude_pvlib(
        longitude: Longitude,   # degrees
        latitude: Latitude,     # degrees
        timestamp: datetime,
        timezone: ZoneInfo,
    )-> SolarAltitude:
    """Calculate the solar altitude angle in degrees using pvlib"""
    solar_position = pvlib.solarposition.get_solarposition(timestamp, latitude.degrees, longitude.degrees)
    solar_altitude = solar_position['apparent_elevation'].values[0]

    solar_altitude = SolarAltitude(
        value=solar_altitude,
        unit=DEGREES,
        position_algorithm='pvlib',
        timing_algorithm='pvlib',
    )
    if (
        not isfinite(solar_altitude.degrees)
        or not solar_altitude.min_degrees <= solar_altitude.degrees <= solar_altitude.max_degrees
    ):
        raise ValueError(
            f"The calculated solar altitude angle {solar_altitude.degrees} is out of the expected range\
            [{solar_altitude.min_degrees}, {solar_altitude.max_degrees}] degrees"
        )
    return solar_altitude


@log_function_call
@cached(cache={}, key=custom_hashkey)
# @validate_with_pydantic(CalculateSolarAltitudePVLIBInputModel)
def calculate_solar_altitude_series_pvlib(
    longitude: Longitude,  # degrees
    latitude: Latitude,  # degrees
    timestamps: datetime,
    # timezone: ZoneInfo,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> SolarAltitude:
    """Calculate the solar altitude (θ)"""
    solar_position = pvlib.solarposition.get_solarposition(
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
