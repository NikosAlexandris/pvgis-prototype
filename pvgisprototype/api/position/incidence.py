"""
API modules to calculate the solar incidence angle between the direction of the
sun-to-surface vector and either the direction of the normal-to-surface vector
or the direction of the surface-plane vector.

Attention is required im handling the rotational solar azimuth and surface
orientation (also referred to as surface azimuth) anngles. The origin of
measuring azimuthal angles will obvisouly impact the direction of the
calculated angles. See also the API azimuth.py module.
"""

from typing import Dict, List
from zoneinfo import ZoneInfo

from devtools import debug
from pandas import DatetimeIndex
from xarray import DataArray

from pvgisprototype import (
    Latitude,
    Longitude,
    SolarIncidence,
    SurfaceOrientation,
    SurfaceTilt,
)
from pvgisprototype.algorithms.iqbal.solar_incidence import (
    calculate_solar_incidence_series_iqbal,
)
from pvgisprototype.algorithms.jenco.solar_incidence import (
    calculate_solar_incidence_series_jenco,
)
from pvgisprototype.algorithms.pvis.solar_incidence import (
    calculate_solar_incidence_series_hofierka,
)
from pvgisprototype.algorithms.pvlib.solar_incidence import (
    calculate_solar_incidence_series_pvlib,
)
from pvgisprototype.api.position.conversions import (
    convert_north_to_south_radians_convention,
)
from pvgisprototype.api.position.models import (
    ShadingModel,
    SolarIncidenceModel,
    SolarPositionModel,
    SolarTimeModel,
)
from pvgisprototype.api.position.shading import model_surface_in_shade_series
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ANGLE_OUTPUT_UNITS_DEFAULT,
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    AZIMUTH_ORIGIN_NAME,
    COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    INCIDENCE_ALGORITHM_NAME,
    INCIDENCE_DEFINITION,
    INCIDENCE_NAME,
    LOG_LEVEL_DEFAULT,
    NOT_AVAILABLE,
    PERIGEE_OFFSET,
    POSITION_ALGORITHM_NAME,
    RADIANS,
    REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    TIME_ALGORITHM_NAME,
    UNIT_NAME,
    VERBOSE_LEVEL_DEFAULT,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.log import log_function_call, logger
from pvgisprototype.validation.functions import (
    ModelSolarIncidenceTimeSeriesInputModel,
    validate_with_pydantic,
)


@log_function_call
@custom_cached
@validate_with_pydantic(ModelSolarIncidenceTimeSeriesInputModel)
def model_solar_incidence_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo | None = None,
    surface_orientation: SurfaceOrientation = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt = SURFACE_TILT_DEFAULT,
    apply_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: (
        float | None
    ) = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    solar_time_model: SolarTimeModel = SolarTimeModel.milne,
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    solar_incidence_model: SolarIncidenceModel = SolarIncidenceModel.iqbal,
    horizon_profile: DataArray | None = None,
    shading_model: ShadingModel = ShadingModel.pvis,
    complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    zero_negative_solar_incidence_angle: bool = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    validate_output:bool = VALIDATE_OUTPUT_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> SolarIncidence:
    """ """
    logger.info(
            f"Executing solar positioning modelling function model_solar_incidence_series() for\n{timestamps}",
            alt=f"Executing [underline]solar positioning modelling[/underline] function model_solar_incidence_series() for\n{timestamps}"
            )
    solar_incidence_series = None
    surface_in_shade_series = model_surface_in_shade_series(
        horizon_profile=horizon_profile,
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_time_model=solar_time_model,
        solar_position_model=solar_position_model,
        shading_model=shading_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
        validate_output=validate_output,
    )

    if solar_incidence_model.value == SolarIncidenceModel.jenco:
        # Update-Me ----------------------------------------------------------
        # Hofierka (2002) measures azimuth angles from East !
        # Convert the user-defined North-based surface orientation angle to East-based
        # surface_orientation_east_convention = SurfaceOrientation(
        #     value=convert_north_to_east_radians_convention(
        #         north_based_angle=surface_orientation
        #     ),
        #     unit=RADIANS,
        # )
        surface_orientation_south_convention = SurfaceOrientation(
            value=convert_north_to_south_radians_convention(
                north_based_angle=surface_orientation
            ),
            unit=RADIANS,
        )
        # And apparently, defined the complementary surface tilt angle too!
        # from math import pi
        # surface_tilt = SurfaceTilt(
        #         value=(pi/2 - surface_tilt.radians),
        #         unit=RADIANS,
        #         )
        # ---------------------------------------------------------- Update-Me
        solar_incidence_series = calculate_solar_incidence_series_jenco(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            # surface_orientation=surface_orientation,
            # surface_orientation=surface_orientation_east_convention,
            surface_orientation=surface_orientation_south_convention,
            surface_tilt=surface_tilt,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            surface_in_shade_series=surface_in_shade_series,
            complementary_incidence_angle=complementary_incidence_angle,
            zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )

    if solar_incidence_model.value == SolarIncidenceModel.iqbal:
        # Iqbal (1983) measures azimuthal angles from South !
        surface_orientation_south_convention = SurfaceOrientation(
            value=convert_north_to_south_radians_convention(
                north_based_angle=surface_orientation
            ),
            unit=RADIANS,
        )
        solar_incidence_series = calculate_solar_incidence_series_iqbal(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            surface_orientation=surface_orientation_south_convention,
            surface_tilt=surface_tilt,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            surface_in_shade_series=surface_in_shade_series,
            complementary_incidence_angle=complementary_incidence_angle,
            zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
            dtype=dtype,
            array_backend=array_backend,
            validate_output=validate_output,
            verbose=verbose,
            log=log,
        )

    if solar_incidence_model.value == SolarIncidenceModel.hofierka:
        surface_orientation_south_convention = SurfaceOrientation(
            value=convert_north_to_south_radians_convention(
                north_based_angle=surface_orientation
            ),
            unit=RADIANS,
        )
        solar_incidence_series = calculate_solar_incidence_series_hofierka(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            # surface_orientation=surface_orientation,
            surface_orientation=surface_orientation_south_convention,
            surface_tilt=surface_tilt,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            complementary_incidence_angle=complementary_incidence_angle,
            zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )

    if solar_incidence_model.value == SolarIncidenceModel.pvlib:
        solar_incidence_series = calculate_solar_incidence_series_pvlib(
            longitude=longitude,
            latitude=latitude,
            surface_tilt=surface_tilt,
            surface_orientation=surface_orientation,
            timestamps=timestamps,
            complementary_incidence_angle=complementary_incidence_angle,
            zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    logger.info(
            f"Returning solar incidence time series :\n{solar_incidence_series}",
            alt=f"Returning [yellow]solar incidence[/yellow] time series :\n{solar_incidence_series}",
            )
    return solar_incidence_series


@log_function_call
def calculate_solar_incidence_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    surface_orientation: SurfaceOrientation = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt = SURFACE_TILT_DEFAULT,
    # solar_time_model: SolarTimeModel = SolarTimeModel.milne,
    solar_incidence_models: List[SolarIncidenceModel] = [SolarIncidenceModel.iqbal],
    horizon_profile: DataArray | None = None,
    shading_model: ShadingModel = ShadingModel.pvis,
    complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    zero_negative_solar_incidence_angle: bool = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = ANGLE_OUTPUT_UNITS_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> Dict:
    """Calculates the solar Incidence angle for the selected models and returns the results in a table"""
    results = {}
    for solar_incidence_model in solar_incidence_models:
        if (
            solar_incidence_model != SolarIncidenceModel.all
        ):  # ignore 'all' in the enumeration
            solar_incidence_series = model_solar_incidence_series(
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                timezone=timezone,
                surface_orientation=surface_orientation,
                surface_tilt=surface_tilt,
                # solar_time_model=solar_time_model,
                solar_incidence_model=solar_incidence_model,
                horizon_profile=horizon_profile,
                shading_model=shading_model,
                complementary_incidence_angle=complementary_incidence_angle,
                zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                dtype=dtype,
                array_backend=array_backend,
                validate_output=validate_output,
                verbose=verbose,
                log=log,
            )
            solar_incidence_model_series = {
                solar_incidence_model.name: {
                    TIME_ALGORITHM_NAME: (
                        solar_incidence_series.timing_algorithm
                        if solar_incidence_series
                        else NOT_AVAILABLE
                    ),
                    POSITION_ALGORITHM_NAME: (
                        solar_incidence_series.position_algorithm
                        if solar_incidence_series
                        else NOT_AVAILABLE
                    ),
                    # ALTITUDE_NAME: getattr(solar_altitude_series, angle_output_units, NOT_AVAILABLE) if solar_altitude_series else NOT_AVAILABLE,
                    # AZIMUTH_NAME: getattr(solar_azimuth_series, angle_output_units, NOT_AVAILABLE) if solar_azimuth_series else NOT_AVAILABLE,
                    AZIMUTH_ORIGIN_NAME: (
                        solar_incidence_series.azimuth_origin
                        if solar_incidence_series
                        else NOT_AVAILABLE
                    ),
                    # SURFACE_ORIENTATION_NAME: getattr(surface_orientation, angle_output_units, NOT_AVAILABLE) if surface_orientation else None,
                    # SURFACE_TILT_NAME: getattr(surface_tilt, angle_output_units, NOT_AVAILABLE) if surface_tilt else None,
                    INCIDENCE_ALGORITHM_NAME: (
                        solar_incidence_series.incidence_algorithm
                        if solar_incidence_series
                        else NOT_AVAILABLE
                    ),
                    INCIDENCE_NAME: (
                        getattr(
                            solar_incidence_series, angle_output_units, NOT_AVAILABLE
                        )
                        if solar_incidence_series
                        else NOT_AVAILABLE
                    ),
                    INCIDENCE_DEFINITION: (
                        solar_incidence_series.definition
                        if solar_incidence_series
                        else NOT_AVAILABLE
                    ),
                    UNIT_NAME: angle_output_units,
                }
            }
        results = results | solar_incidence_model_series

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return results
