from pathlib import Path
from typing import Dict, List
from zoneinfo import ZoneInfo

from devtools import debug
from pandas import DatetimeIndex, Timestamp

from pvgisprototype import Latitude, Longitude, LocationShade, HorizonHeight
from pvgisprototype.algorithms.pvlib.shade import (
    calculate_shade_series_pvlib,
)
from pvgisprototype.api.position.models import SolarPositionModel, SolarTimeModel, ShadingModel
from pvgisprototype.api.position.altitude import model_solar_altitude_series    #  gounaol
from pvgisprototype.api.position.azimuth import model_solar_azimuth_series      #  gounaol
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ALTITUDE_NAME,
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    LOG_LEVEL_DEFAULT,
    NOT_AVAILABLE,
    PERIGEE_OFFSET,
    POSITION_ALGORITHM_NAME,
    RADIANS,
    REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    TIME_ALGORITHM_NAME,
    UNIT_NAME,
    VERBOSE_LEVEL_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.log import log_function_call, logger
# from pvgisprototype.validation.functions import (
#     ModelShadeSeriesInputModel,
#     validate_with_pydantic,
# )


@log_function_call
@custom_cached
# @validate_with_pydantic(ModelShadeSeriesInputModel)
def model_shade_series(
    horizon_height: HorizonHeight,
    horizon_interval: float,
    shadow_indicator: Path,
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex | Timestamp | None,
    timezone: ZoneInfo,
    solar_time_model: SolarTimeModel = SolarTimeModel.noaa,
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    shading_model: ShadingModel = ShadingModel.pvlib,
    apply_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: float | None = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
) -> LocationShade:
    """
    """
    logger.info(
            f"Executing shading modelling function model_shade_series() for\n{timestamps}",
            alt=f"Executing [underline]shading modelling[/underline] function model_shade_series() for\n{timestamps}"
            )
    shade_series = None

    solar_altitude_series = model_solar_altitude_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        solar_time_model=solar_time_model,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
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
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        solar_time_model=solar_time_model,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        dtype=dtype,
        array_backend=array_backend,
        verbose=0,
        log=log,
        validate_output=validate_output,
    )
    if shading_model.value == ShadingModel.pvlib:
        shade_series = calculate_shade_series_pvlib(
            solar_altitude_series=solar_altitude_series,
            solar_azimuth_series=solar_azimuth_series,
            shadow_indicator=shadow_indicator,
            horizon_height=horizon_height,
            horizon_interval=horizon_interval,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
            validate_output=validate_output,
        )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    logger.info(
            f"Returning shade time series :\n{shade_series}",
            alt=f"Returning [gray]shade[/gray] time series :\n{shade_series}",
            )
    return shade_series


@log_function_call
def calculate_shade_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    horizon_height: HorizonHeight,
    horizon_interval: float | None = 7.5,
    shadow_indicator: Path | None = None,
    shading_models: List[ShadingModel] = [ShadingModel.pvlib],
    solar_time_model: SolarTimeModel = SolarTimeModel.noaa,
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    apply_atmospheric_refraction: bool = True,
    refracted_solar_zenith: float | None = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
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
        if (
            shading_model != ShadingModel.all
        ):  # ignore 'all' in the enumeration
            shade_series = model_shade_series(
                horizon_height = horizon_height,
                horizon_interval = horizon_interval,
                shadow_indicator = shadow_indicator,
                longitude = longitude,
                latitude = latitude,
                timestamps = timestamps,
                timezone = timezone,
                solar_time_model = solar_time_model,
                solar_position_model = solar_position_model,
                shading_model = shading_model,
                apply_atmospheric_refraction = apply_atmospheric_refraction,
                refracted_solar_zenith = refracted_solar_zenith,
                perigee_offset = perigee_offset,
                eccentricity_correction_factor = eccentricity_correction_factor,
                dtype = dtype,
                array_backend = array_backend,
                verbose = verbose,
                log = log,
                validate_output = validate_output,
            )
            # shading_model_overview = {
            #     shading_model.name: {
            #         # TIME_ALGORITHM_NAME: (
            #         #     shade_series.timing_algorithm
            #         #     if shade_series
            #         #     else NOT_AVAILABLE
            #         # ),
            #         POSITION_ALGORITHM_NAME: shading_model.value,
            #         ALTITUDE_NAME: (
            #             getattr(
            #                 shade_series, angle_output_units, NOT_AVAILABLE
            #             )
            #             if shade_series
            #             else NOT_AVAILABLE
            #         ),
            #         UNIT_NAME: None,
            #     }
            # }
            # results = results | shading_model_overview

    return shade_series
