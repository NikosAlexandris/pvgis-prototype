import pvlib
from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import (
    Latitude,
    Longitude,
    SolarIncidence,
    SurfaceOrientation,
    SurfaceTilt,
)
from pvgisprototype.algorithms.pvlib.solar_azimuth import (
    calculate_solar_azimuth_series_pvlib,
)
from pvgisprototype.algorithms.pvlib.solar_zenith import (
    calculate_solar_zenith_series_pvlib,
)
from pvgisprototype.api.datetime.now import now_utc_datetimezone
from pvgisprototype.api.position.models import SolarIncidenceModel
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    COMPLEMENTARY_INCIDENCE_ANGLE_DEFINITION,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    NO_SOLAR_INCIDENCE,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger


@log_function_call
@custom_cached
# @validate_with_pydantic(CalculateSolarIncidencePVLIBInputModel)
def calculate_solar_incidence_series_pvlib(
    longitude: Longitude,
    latitude: Latitude,
    surface_orientation: SurfaceOrientation = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt = SURFACE_TILT_DEFAULT,
    timestamps: DatetimeIndex = now_utc_datetimezone(),
    # adjust_for_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
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
        logger.debug(
            f":information: Converting solar incidence angle to {COMPLEMENTARY_INCIDENCE_ANGLE_DEFINITION}...",
            alt=f":information: [bold][magenta]Converting[/magenta] solar incidence angle to {COMPLEMENTARY_INCIDENCE_ANGLE_DEFINITION}[/bold]...",
        )
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
