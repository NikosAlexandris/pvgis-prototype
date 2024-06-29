from devtools import debug
from zoneinfo import ZoneInfo
from pandas import DatetimeIndex
import pvlib
from datetime import datetime
import numpy

from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarAzimuthPVLIBInputModel
from pvgisprototype import SolarAzimuth
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype.constants import DEGREES
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from pvgisprototype.caching import custom_cached
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT


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
    azimuth_origin = 'North'
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
        position_algorithm="pvlib",
        timing_algorithm="pvlib",
        origin=azimuth_origin,
    )
