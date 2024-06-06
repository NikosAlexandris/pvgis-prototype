from devtools import debug
from math import pi
from datetime import datetime
from zoneinfo import ZoneInfo
from math import isfinite
import numpy
import pvlib
from pvgisprototype.api.position.models import SolarIncidenceModel
from pvgisprototype import SurfaceOrientation
from pvgisprototype import SurfaceTilt
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarAltitudePVLIBInputModel
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype import SolarAltitude
from pvgisprototype import SolarIncidence
from pvgisprototype.constants import NO_SOLAR_INCIDENCE
from pvgisprototype.constants import RADIANS
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pandas import DatetimeIndex
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
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT
from pvgisprototype.constants import ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT
from pvgisprototype.algorithms.pvlib.solar_zenith import calculate_solar_zenith_series_pvlib
from pvgisprototype.algorithms.pvlib.solar_azimuth import calculate_solar_azimuth_series_pvlib
from pvgisprototype.log import logger


@log_function_call
@cached(cache={}, key=custom_hashkey)
# @validate_with_pydantic(CalculateSolarIncidencePVLIBInputModel)
def calculate_solar_incidence_series_pvlib(
    longitude: Longitude,
    latitude: Latitude,
    surface_orientation: SurfaceOrientation = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt = SURFACE_TILT_DEFAULT,
    timestamps: DatetimeIndex = now_utc_datetimezone(),
    # timezone: ZoneInfo | None = None,
    # apply_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    zero_negative_solar_incidence_angle: bool = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> SolarIncidence:
    """Calculate the solar incidence (θ)"""
    solar_position = pvlib.solarposition.get_solarposition(
        timestamps, latitude.degrees, longitude.degrees
    )
    solar_zenith_series = calculate_solar_zenith_series_pvlib(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    solar_azimuth_series = calculate_solar_azimuth_series_pvlib(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    solar_incidence_series_in_degrees = pvlib.irradiance.aoi(
         surface_tilt=surface_tilt.degrees,
         surface_azimuth=surface_orientation.degrees,
         solar_zenith=solar_zenith_series.degrees,
         solar_azimuth=solar_azimuth_series.degrees,
    )
    # solar_incidence_series = solar_position["apparent_elevation"].values

    incidence_angle_definition = SolarIncidence().definition
    incidence_angle_description = SolarIncidence().description
    if complementary_incidence_angle:
        logger.info(':information: [bold][magenta]Converting[/magenta] solar incidence angle to {COMPLEMENTARY_INCIDENCE_ANGLE_DEFINITION}[/bold]...')
        solar_incidence_series_in_degrees = 90 - solar_incidence_series_in_degrees
        incidence_angle_definition = SolarIncidence().definition_complementary
        incidence_angle_description = SolarIncidence().description_complementary

    if zero_negative_solar_incidence_angle:
        # set negative or below horizon angles ( == solar zenith > 90 ) to 0 !
        solar_incidence_series_in_degrees[
            (solar_incidence_series_in_degrees < 0) | (solar_zenith_series.degrees > 90)
        ] = NO_SOLAR_INCIDENCE

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=solar_incidence_series_in_degrees,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )
    from pvgisprototype.constants import DEGREES
    return SolarIncidence(
        value=solar_incidence_series_in_degrees,
        unit=DEGREES,
        position_algorithm=solar_zenith_series.position_algorithm,
        timing_algorithm=solar_zenith_series.timing_algorithm,
        incidence_algorithm=SolarIncidenceModel.pvlib,
        definition=incidence_angle_definition,
        description=incidence_angle_description,
        azimuth_origin=solar_azimuth_series.origin,
    )
