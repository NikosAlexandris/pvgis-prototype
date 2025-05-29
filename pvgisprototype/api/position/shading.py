from typing import Dict, List
from zoneinfo import ZoneInfo

from devtools import debug
from pandas import DatetimeIndex, Timestamp
from xarray import DataArray

from pvgisprototype.api.position.output import (
    generate_dictionary_of_surface_in_shade_series,
)
from pvgisprototype import Latitude, Longitude, LocationShading
from pvgisprototype.algorithms.hofierka.position.shading import calculate_surface_in_shade_series_pvis
from pvgisprototype.api.position.models import SolarPositionModel, SolarTimeModel, ShadingModel
from pvgisprototype.api.position.altitude import model_solar_altitude_series
from pvgisprototype.api.position.azimuth import model_solar_azimuth_series
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    LOG_LEVEL_DEFAULT,
    NOT_AVAILABLE,
    PERIGEE_OFFSET,
    POSITIONING_ALGORITHM_NAME,
    RADIANS,
    UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    TIMING_ALGORITHM_NAME,
    UNIT_NAME,
    VALIDATE_OUTPUT_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_function_call, logger
from pvgisprototype.validation.functions import (
    ModelSurfaceInShadeSeriesInputModel,
    CalculateSurfaceInShadeSeriesInputModel,
    validate_with_pydantic,
)


@log_function_call
@custom_cached
@validate_with_pydantic(ModelSurfaceInShadeSeriesInputModel)
def model_surface_in_shade_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex | Timestamp | None,
    timezone: ZoneInfo | None,
    horizon_profile: DataArray | None,
    solar_time_model: SolarTimeModel = SolarTimeModel.noaa,
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    shading_model: ShadingModel = ShadingModel.pvis,
    adjust_for_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    # unrefracted_solar_zenith: UnrefractedSolarZenith | None = UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    eccentricity_phase_offset: float = PERIGEE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> LocationShading:
    """ """
    logger.debug(
        f"Executing shading modelling function model_shade_series() for\n{timestamps}",
        alt=f"Executing [underline]shading modelling[/underline] function model_shade_series() for\n{timestamps}",
    )
    surface_in_shade_series = None
    solar_altitude_series = model_solar_altitude_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
        # unrefracted_solar_zenith=unrefracted_solar_zenith,
        # solar_time_model=solar_time_model,
        eccentricity_phase_offset=eccentricity_phase_offset,
        eccentricity_amplitude=eccentricity_amplitude,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
        validate_output=validate_output,
    )
    solar_azimuth_series = model_solar_azimuth_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
        # unrefracted_solar_zenith=unrefracted_solar_zenith,
        solar_time_model=solar_time_model,
        eccentricity_phase_offset=eccentricity_phase_offset,
        eccentricity_amplitude=eccentricity_amplitude,
        dtype=dtype,
        array_backend=array_backend,
        verbose=0,
        log=log,
        validate_output=validate_output,
    )

    if shading_model.value == ShadingModel.pvlib:

        pass

    if shading_model.value == ShadingModel.pvis:

        surface_in_shade_series = calculate_surface_in_shade_series_pvis(
            solar_altitude_series=solar_altitude_series,
            solar_azimuth_series=solar_azimuth_series,
            horizon_profile=horizon_profile,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
            validate_output=validate_output,
        )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    logger.debug(
        f"Returning surface in shade time series :\n{surface_in_shade_series}",
        alt=f"Returning [gray]surface in shade[/gray] time series :\n{surface_in_shade_series}",
    )

    return surface_in_shade_series


@log_function_call
@validate_with_pydantic(CalculateSurfaceInShadeSeriesInputModel)
def calculate_surface_in_shade_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo | None,
    horizon_profile: DataArray | None,
    shading_models: List[ShadingModel] = [ShadingModel.pvis],
    solar_time_model: SolarTimeModel = SolarTimeModel.noaa,
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    adjust_for_atmospheric_refraction: bool = True,
    # unrefracted_solar_zenith: UnrefractedSolarZenith | None = UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    eccentricity_phase_offset: float = PERIGEE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
) -> Dict:
    """Calculates location shade using the requested models and returns the
    results in a dictionary.
    """
    results = {}
    for shading_model in shading_models:
        if shading_model != ShadingModel.all:  # ignore 'all' in the enumeration
            surface_in_shade_series = model_surface_in_shade_series(
                horizon_profile=horizon_profile,
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                timezone=timezone,
                solar_time_model=solar_time_model,
                solar_position_model=solar_position_model,
                shading_model=shading_model,
                adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
                # unrefracted_solar_zenith=unrefracted_solar_zenith,
                eccentricity_phase_offset=eccentricity_phase_offset,
                eccentricity_amplitude=eccentricity_amplitude,
                dtype=dtype,
                array_backend=array_backend,
                verbose=verbose,
                log=log,
                validate_output=validate_output,
            )
            surface_in_shade_model_series = {
                shading_model.name: {
                    TIMING_ALGORITHM_NAME: (
                        surface_in_shade_series.timing_algorithm
                        if surface_in_shade_series
                        else NOT_AVAILABLE
                    ),
                    POSITIONING_ALGORITHM_NAME: surface_in_shade_series.position_algorithm,
                    **generate_dictionary_of_surface_in_shade_series(
                        surface_in_shade_series,
                        angle_output_units,
                    ),
                    UNIT_NAME: angle_output_units,
                }
            }
            results = results | surface_in_shade_model_series

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return results
