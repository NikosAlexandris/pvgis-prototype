from devtools import debug
from zoneinfo import ZoneInfo
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
from cachetools import cached
from pvgisprototype.caching import custom_hashkey
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT


@log_function_call
@validate_with_pydantic(CalculateSolarAzimuthPVLIBInputModel)
def calculate_solar_azimuth_pvlib(
    longitude: Longitude,  # degrees
    latitude: Latitude,  # degrees
    timestamp: datetime,
    timezone: ZoneInfo,
) -> SolarAzimuth:
    """Calculate the solar azimuth (θ) in degrees"""
    solar_position = pvlib.solarposition.get_solarposition(
        timestamp, latitude.degrees, longitude.degrees
    )
    solar_azimuth = solar_position["azimuth"].values[0]

    # if (
    #     not isfinite(solar_azimuth)
    #     or not solar_azimuth.min_degrees <= solar_azimuth <= solar_azimuth.max_degrees
    # ):
    #     raise ValueError(
    #         f"The calculated solar azimuth angle {solar_azimuth.degrees} is out of the expected range\
    #         [{solar_azimuth.min_degrees}, {solar_azimuth.max_degrees}] degrees"
    #     )
    if (
        (solar_azimuth < SolarAzimuth().min_degrees)
        | (solar_azimuth > SolarAzimuth().max_degrees)
    ).any():
        out_of_range_values = solar_azimuth[
            (solar_azimuth < SolarAzimuth().min_degrees)
            | (solar_azimuth > SolarAzimuth().max_degrees)
        ]
        # raise ValueError(# ?
        raise ValueError(
            f"{WARNING_OUT_OF_RANGE_VALUES} "
            f"[{SolarAzimuth().min_radians}, {SolarAzimuth().max_radians}] radians"
            f" in [code]solar_azimuth_series[/code] : {out_of_range_values}"
        )
    return SolarAzimuth(
        value=solar_azimuth,
        unit=DEGREES,
        position_algorithm="pvlib",
        timing_algorithm="pvlib",
        origin="North",
    )


@log_function_call
@cached(cache={}, key=custom_hashkey)
# @validate_with_pydantic(CalculateSolarAzimuthPVLIBInputModel)
def calculate_solar_azimuth_series_pvlib(
    longitude: Longitude,  # degrees
    latitude: Latitude,  # degrees
    timestamps: datetime,
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
    )
