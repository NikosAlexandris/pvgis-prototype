"""
API module to calculate the global (shortwave) irradiance over a
location for a period in time.
"""

from datetime import datetime
from pathlib import Path
from typing import List
from zoneinfo import ZoneInfo

import numpy
from devtools import debug
from numpy._core.multiarray import ndarray
from pandas import DatetimeIndex, Timestamp
from xarray import DataArray

from pvgisprototype import Irradiance, LinkeTurbidityFactor
from pvgisprototype.api.irradiance.diffuse.inclined import (
    calculate_diffuse_inclined_irradiance_series,
)
from pvgisprototype.api.irradiance.direct.inclined import (
    calculate_direct_inclined_irradiance_series,
)
from pvgisprototype.api.irradiance.limits import (
    LOWER_PHYSICALLY_POSSIBLE_LIMIT,
    UPPER_PHYSICALLY_POSSIBLE_LIMIT,
)
from pvgisprototype.api.irradiance.models import MethodForInexactMatches
from pvgisprototype.api.irradiance.reflected import (
    calculate_ground_reflected_inclined_irradiance_series,
)
# from pvgisprototype.api.irradiance.shade import is_surface_in_shade_series
from pvgisprototype.api.position.altitude import model_solar_altitude_series
from pvgisprototype.api.position.models import (
    SUN_HORIZON_POSITION_DEFAULT,
    ShadingState,
    SolarIncidenceModel,
    SolarPositionModel,
    SolarTimeModel,
    ShadingModel,
    SunHorizonPositionModel,
    select_models,
)
from pvgisprototype.api.position.shading import model_surface_in_shade_series
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
)
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.constants import (
    ABOVE_HORIZON_COLUMN_NAME,
    ALBEDO_DEFAULT,
    ALTITUDE_COLUMN_NAME,
    ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    ARRAY_BACKEND_DEFAULT,
    AZIMUTH_COLUMN_NAME,
    AZIMUTH_ORIGIN_COLUMN_NAME,
    BELOW_HORIZON_COLUMN_NAME,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    DIFFUSE_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME,
    DIFFUSE_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME,
    DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    DIRECT_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME,
    DIRECT_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME,
    ECCENTRICITY_CORRECTION_FACTOR,
    ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME,
    FINGERPRINT_COLUMN_NAME,
    FINGERPRINT_FLAG_DEFAULT,
    GLOBAL_INCLINED_IRRADIANCE,
    GLOBAL_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    HOFIERKA_2002,
    IRRADIANCE_UNIT,
    INCIDENCE_ALGORITHM_COLUMN_NAME,
    INCIDENCE_COLUMN_NAME,
    INCIDENCE_DEFINITION,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    LOW_ANGLE_COLUMN_NAME,
    NEIGHBOR_LOOKUP_DEFAULT,
    NOT_AVAILABLE,
    PERIGEE_OFFSET,
    PERIGEE_OFFSET_COLUMN_NAME,
    POSITION_ALGORITHM_COLUMN_NAME,
    RADIANS,
    RADIATION_MODEL_COLUMN_NAME,
    REFLECTED_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME,
    REFLECTED_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME,
    REFLECTIVITY_COLUMN_NAME,
    REFLECTIVITY_FACTOR_COLUMN_NAME,
    REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    SHADING_ALGORITHM_COLUMN_NAME,
    SHADING_STATES_COLUMN_NAME,
    SOLAR_CONSTANT_COLUMN_NAME,
    SUN_HORIZON_POSITION_COLUMN_NAME,
    SURFACE_IN_SHADE_COLUMN_NAME,
    SOLAR_CONSTANT,
    SUN_HORIZON_POSITIONS_NAME,
    SURFACE_ORIENTATION_COLUMN_NAME,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_COLUMN_NAME,
    SURFACE_TILT_DEFAULT,
    TIME_ALGORITHM_COLUMN_NAME,
    TITLE_KEY_NAME,
    TOLERANCE_DEFAULT,
    UNIT_NAME,
    VALIDATE_OUTPUT_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger
from pvgisprototype.core.arrays import create_array
from pvgisprototype.core.hashing import generate_hash
from pvgisprototype.validation.models import SurfaceOrientationModel, SurfaceTiltModel


@log_function_call
def calculate_global_inclined_irradiance_series(
    longitude: float,
    latitude: float,
    elevation: float,
    surface_orientation: SurfaceOrientationModel | None = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTiltModel | None = SURFACE_TILT_DEFAULT,
    timestamps: DatetimeIndex | None = DatetimeIndex([Timestamp.now(tz='UTC')]),
    timezone: ZoneInfo | None = None,
    global_horizontal_irradiance: ndarray | Path | None = None,
    direct_horizontal_irradiance: ndarray | Path | None = None,
    neighbor_lookup: MethodForInexactMatches = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: float | None = TOLERANCE_DEFAULT,
    mask_and_scale: bool = False,
    in_memory: bool = False,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    apply_atmospheric_refraction: bool = True,
    refracted_solar_zenith: float | None = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    albedo: float | None = ALBEDO_DEFAULT,
    apply_reflectivity_factor: bool = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    sun_horizon_position: List[SunHorizonPositionModel] = SUN_HORIZON_POSITION_DEFAULT,
    solar_incidence_model: SolarIncidenceModel = SolarIncidenceModel.jenco,
    zero_negative_solar_incidence_angle: bool = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    horizon_profile: DataArray | None = None,
    shading_model: ShadingModel = ShadingModel.pvis,
    shading_states: List[ShadingState] = [ShadingState.all],
    solar_time_model: SolarTimeModel = SolarTimeModel.noaa,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    validate_output:bool = VALIDATE_OUTPUT_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
):
    """Calculate the global irradiance on an inclined surface [W.m-2]

    Calculate the global irradiance on an inclined surface as the sum of the
    direct, the diffuse and the ground-reflected radiation components.
    The radiation, selectively attenuated by the atmosphere, which is not
    reflected or scattered and reaches the surface directly is the direct
    radiation. The scattered radiation that reaches the ground is the
    diffuse radiation. In addition, a smaller part of radiation is reflected
    from the ground onto the inclined surface. Only small percents of reflected
    radiation contribute to inclined surfaces, thus it is sometimes ignored.
    PVGIS, however, inherits the solutions adopted in the r.sun solar radiation
    model in which both the diffuse and reflected radiation components are
    considered.

    """
    solar_altitude_series = model_solar_altitude_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        # refracted_solar_zenith=refracted_solar_zenith,
        # solar_time_model=solar_time_model,
        # perigee_offset=perigee_offset,
        # eccentricity_correction_factor=eccentricity_correction_factor,
        # angle_output_units=angle_output_units,
        dtype=dtype,
        array_backend=array_backend,
        validate_output=validate_output,
        verbose=verbose,
        log=log,
    )
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
        validate_output=validate_output,
        verbose=verbose,
        log=log,
    )

    # In order to avoid unbound errors we pre-define `_series` objects
    array_parameters = {
        "shape": timestamps.shape,
        "dtype": dtype,
        "init_method": "zeros",
        "backend": array_backend,
    }  # Borrow shape from timestamps

    # direct
    direct_horizontal_irradiance_series = create_array(**array_parameters)
    direct_inclined_irradiance_series = create_array(**array_parameters)
    calculated_direct_inclined_irradiance_series = (
        {}
    )  # no-values without direct sunlight

    # diffuse (== sky-reflected)
    diffuse_horizontal_irradiance_series = create_array(**array_parameters)
    diffuse_inclined_irradiance_series = create_array(**array_parameters)

    # ground-reflected diffuse
    # there is no ground-reflected horizontal component as such !
    ground_reflected_inclined_irradiance_series = create_array(**array_parameters)

    # before reflectivity
    direct_inclined_irradiance_before_reflectivity_series = create_array(
        **array_parameters
    )
    diffuse_inclined_irradiance_before_reflectivity_series = create_array(
        **array_parameters
    )
    ground_reflected_inclined_irradiance_before_reflectivity_series = create_array(
        **array_parameters
    )

    # reflectivity effect factor/s
    direct_inclined_reflectivity_factor_series = create_array(**array_parameters)
    diffuse_inclined_reflectivity_factor_series = create_array(**array_parameters)
    ground_reflected_inclined_reflectivity_factor_series = create_array(
        **array_parameters
    )

    # after reflectivity effect
    direct_inclined_reflectivity_series = create_array(**array_parameters)
    diffuse_inclined_reflectivity_series = create_array(**array_parameters)
    ground_reflected_inclined_reflectivity_series = create_array(**array_parameters)

    # Select which solar positions related to the horizon to process
    sun_horizon_positions = select_models(
        SunHorizonPositionModel, sun_horizon_position
    )  # Using a callback fails!
    # and keep track of the position of the sun relative to the horizon
    sun_horizon_position_series = create_array(
        timestamps.shape, dtype="object", init_method="empty", backend=array_backend
    )

    # Following, create masks based on the solar altitude series --------

    # For sun below the horizon
    if SunHorizonPositionModel.below in sun_horizon_positions:
        mask_below_horizon = solar_altitude_series.value < 0
        sun_horizon_position_series[mask_below_horizon] = [SunHorizonPositionModel.below.value]
        if numpy.any(mask_below_horizon):
            logger.info(
                f"Positions of the sun below horizon :\n{sun_horizon_position_series}",
                alt=f"Positions of the sun [bold gray50]below horizon[/bold gray50] :\n{sun_horizon_position_series}"
            )
            direct_inclined_irradiance_series[mask_below_horizon] = 0
            diffuse_inclined_irradiance_series[mask_below_horizon] = 0
            ground_reflected_inclined_irradiance_series[mask_below_horizon] = 0

    # For very low sun angles
    if SunHorizonPositionModel.low_angle in sun_horizon_positions:
        mask_low_angle = numpy.logical_and(
            solar_altitude_series.value >= 0,
            solar_altitude_series.value < 0.04,  # FIXME: Is 0.04 in radians or degrees ?
            sun_horizon_position_series == None,  # operate only on unset elements
        )
        sun_horizon_position_series[mask_low_angle] = [
            SunHorizonPositionModel.low_angle.value
        ]
        direct_inclined_irradiance_series[mask_low_angle] = (
            0  # Direct radiation is negligible
        )

    # For sun above the horizon
    if SunHorizonPositionModel.above in sun_horizon_positions:
        mask_above_horizon = numpy.logical_and(
            solar_altitude_series.value > 0,
            sun_horizon_position_series == None,  # operate only on unset elements
        )
        sun_horizon_position_series[mask_above_horizon] = [
            SunHorizonPositionModel.above.value
        ]

        # For sun above horizon and not in shade
        mask_not_in_shade = ~surface_in_shade_series.value
        mask_above_horizon_not_in_shade = numpy.logical_and(
            mask_above_horizon,
            mask_not_in_shade,
            sun_horizon_position_series == None,
        )

        if numpy.any(mask_above_horizon_not_in_shade):
            # sun_horizon_position_series[mask_above_horizon_not_in_shade] = [SunHorizonPositionModel.above.name]
            logger.info(
                f"Including positions of the sun above horizon and not in shade :\n{sun_horizon_position_series}",
                alt=f"Including positions of the sun [bold yellow]above horizon[/bold yellow] and [bold red]not in shade[/bold red] :\n{sun_horizon_position_series}"
            )
            if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
                logger.info(
                    "i [bold]Calculating[/bold] the [magenta]direct inclined irradiance[/magenta] for moments not in shade .."
                )
            # if given, will read from external time series
            calculated_direct_inclined_irradiance_series = (
                calculate_direct_inclined_irradiance_series(
                    longitude=longitude,
                    latitude=latitude,
                    elevation=elevation,
                    surface_orientation=surface_orientation,
                    surface_tilt=surface_tilt,
                    timestamps=timestamps,
                    timezone=timezone,
                    direct_horizontal_irradiance=direct_horizontal_irradiance,
                    # neighbor_lookup=neighbor_lookup,
                    # tolerance=tolerance,
                    # mask_and_scale=mask_and_scale,
                    # in_memory=in_memory,
                    linke_turbidity_factor_series=linke_turbidity_factor_series,
                    apply_atmospheric_refraction=apply_atmospheric_refraction,
                    refracted_solar_zenith=refracted_solar_zenith,
                    apply_reflectivity_factor=apply_reflectivity_factor,
                    solar_position_model=solar_position_model,
                    solar_incidence_model=solar_incidence_model,
                    zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
                    horizon_profile=horizon_profile,
                    shading_model=shading_model,
                    solar_time_model=solar_time_model,
                    solar_constant=solar_constant,
                    perigee_offset=perigee_offset,
                    eccentricity_correction_factor=eccentricity_correction_factor,
                    angle_output_units=angle_output_units,
                    dtype=dtype,
                    array_backend=array_backend,
                    verbose=verbose,
                    log=log,
                    fingerprint=fingerprint,
                )
            )
            direct_horizontal_irradiance_series = (
                calculated_direct_inclined_irradiance_series.components.get(
                    DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
                    direct_horizontal_irradiance_series,
                )
            )
            direct_inclined_irradiance_series[mask_above_horizon_not_in_shade] = (
                calculated_direct_inclined_irradiance_series.value[
                    mask_above_horizon_not_in_shade
                ]
            )  # .value is the direct inclined irradiance series
            direct_inclined_irradiance_before_reflectivity_series = (
                calculated_direct_inclined_irradiance_series.components.get(
                    DIRECT_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
                    direct_inclined_irradiance_before_reflectivity_series,
                )
            )
            direct_inclined_reflectivity_factor_series = (
                calculated_direct_inclined_irradiance_series.components.get(
                    REFLECTIVITY_FACTOR_COLUMN_NAME,
                    direct_inclined_reflectivity_factor_series
                )
            )
            direct_inclined_reflectivity_series = (
                calculated_direct_inclined_irradiance_series.components.get(
                    REFLECTIVITY_COLUMN_NAME,
                    direct_inclined_reflectivity_series
                )
            )

        # Calculate diffuse and reflected irradiance for sun above horizon
        if not numpy.any(mask_above_horizon):
            logger.info(
                "i [yellow bold]Apparently there is no moment of the sun above the horizon in the requested time series![/yellow bold] "
            )
        else:
            if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
                logger.info(
                    "i [bold]Calculating[/bold] the [magenta]diffuse inclined irradiance[/magenta] for daylight moments .."
                )
            calculated_diffuse_inclined_irradiance_series = calculate_diffuse_inclined_irradiance_series(
                longitude=longitude,
                latitude=latitude,
                elevation=elevation,
                surface_orientation=surface_orientation,
                surface_tilt=surface_tilt,
                timestamps=timestamps,
                timezone=timezone,
                global_horizontal_irradiance=global_horizontal_irradiance,  # time series optional
                direct_horizontal_irradiance=direct_horizontal_irradiance,  # time series, optional
                # neighbor_lookup=neighbor_lookup,
                # tolerance=tolerance,
                # mask_and_scale=mask_and_scale,
                # in_memory=in_memory,
                linke_turbidity_factor_series=linke_turbidity_factor_series,
                apply_atmospheric_refraction=apply_atmospheric_refraction,
                refracted_solar_zenith=refracted_solar_zenith,
                apply_reflectivity_factor=apply_reflectivity_factor,
                solar_position_model=solar_position_model,
                solar_incidence_model=solar_incidence_model,
                zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
                horizon_profile=horizon_profile,
                shading_model=shading_model,
                shading_states=shading_states,
                solar_time_model=solar_time_model,
                solar_constant=solar_constant,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                angle_output_units=angle_output_units,
                dtype=dtype,
                array_backend=array_backend,
                validate_output=validate_output,
                verbose=0,  # no verbosity here by choice!
                log=log,
                fingerprint=fingerprint,
            )
            diffuse_horizontal_irradiance_series = (
                calculated_diffuse_inclined_irradiance_series.components.get(
                    DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
                    diffuse_horizontal_irradiance_series,
                )
            )
            diffuse_inclined_irradiance_series[mask_above_horizon] = (
                calculated_diffuse_inclined_irradiance_series.value[mask_above_horizon]
            )  # .value is the diffuse irradiance series
            diffuse_inclined_irradiance_before_reflectivity_series = (
                calculated_diffuse_inclined_irradiance_series.components.get(
                    DIFFUSE_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
                    diffuse_inclined_irradiance_before_reflectivity_series,
                )
            )
            diffuse_inclined_reflectivity_factor_series = (
                calculated_diffuse_inclined_irradiance_series.components.get(
                    REFLECTIVITY_FACTOR_COLUMN_NAME,
                    diffuse_inclined_reflectivity_factor_series
                )
            )
            diffuse_inclined_reflectivity_series = (
                calculated_diffuse_inclined_irradiance_series.components.get(
                    REFLECTIVITY_COLUMN_NAME,
                    diffuse_inclined_reflectivity_series
                )
            )
            if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
                logger.info(
                    "i [bold]Calculating[/bold] the [magenta]reflected inclined irradiance[/magenta] for daylight moments .."
                )
            calculated_ground_reflected_inclined_irradiance_series = calculate_ground_reflected_inclined_irradiance_series(
                longitude=longitude,
                latitude=latitude,
                elevation=elevation,
                surface_orientation=surface_orientation,
                surface_tilt=surface_tilt,
                timestamps=timestamps,
                timezone=timezone,
                global_horizontal_irradiance=global_horizontal_irradiance,  # time series, optional
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                mask_and_scale=mask_and_scale,
                in_memory=in_memory,
                linke_turbidity_factor_series=linke_turbidity_factor_series,
                apply_atmospheric_refraction=apply_atmospheric_refraction,
                refracted_solar_zenith=refracted_solar_zenith,
                albedo=albedo,
                apply_reflectivity_factor=apply_reflectivity_factor,
                solar_position_model=solar_position_model,
                solar_time_model=solar_time_model,
                solar_constant=solar_constant,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                angle_output_units=angle_output_units,
                dtype=dtype,
                array_backend=array_backend,
                verbose=0,  # no verbosity here by choice!
                log=log,
                fingerprint=fingerprint,
            )
            ground_reflected_inclined_irradiance_series[mask_above_horizon] = (
                calculated_ground_reflected_inclined_irradiance_series.value[
                    mask_above_horizon
                ]
            )  # .value is the ground reflected irradiance series
            ground_reflected_inclined_irradiance_before_reflectivity_series = (
                calculated_ground_reflected_inclined_irradiance_series.components.get(
                    REFLECTED_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
                    ground_reflected_inclined_irradiance_before_reflectivity_series,
                )
            )
            ground_reflected_inclined_reflectivity_factor_series = (
                calculated_ground_reflected_inclined_irradiance_series.components.get(
                    REFLECTIVITY_FACTOR_COLUMN_NAME,
                    ground_reflected_inclined_reflectivity_factor_series,
                )
            )
            ground_reflected_inclined_reflectivity_series = (
                calculated_ground_reflected_inclined_irradiance_series.components.get(
                    REFLECTIVITY_COLUMN_NAME,
                    ground_reflected_inclined_reflectivity_series,
                )
            )

    # sum components
    if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
        logger.info(
            "\ni [bold]Calculating[/bold] the [magenta]global inclined irradiance[/magenta] .."
        )
    global_inclined_irradiance_before_reflectivity_series = (
        direct_inclined_irradiance_before_reflectivity_series
        + diffuse_inclined_irradiance_before_reflectivity_series
        + ground_reflected_inclined_irradiance_before_reflectivity_series
    )
    global_inclined_irradiance_series = (
        direct_inclined_irradiance_series
        + diffuse_inclined_irradiance_series
        + ground_reflected_inclined_irradiance_series
    )
    global_inclined_reflectivity_series = (
        direct_inclined_reflectivity_series
        + diffuse_inclined_reflectivity_series
        + ground_reflected_inclined_reflectivity_series
    )
    # Warning
    out_of_range_indices = numpy.where(
        (global_inclined_irradiance_series < LOWER_PHYSICALLY_POSSIBLE_LIMIT)
        | (global_inclined_irradiance_series > UPPER_PHYSICALLY_POSSIBLE_LIMIT)
    )
    if out_of_range_indices[0].size > 0:
        logger.warning(
            f"{WARNING_OUT_OF_RANGE_VALUES} in `global_inclined_irradiance_series` : {out_of_range_indices[0]}!"
        )

    # Building the output dictionary ========================================

    components_container = {
        GLOBAL_INCLINED_IRRADIANCE: lambda: {
            TITLE_KEY_NAME: GLOBAL_INCLINED_IRRADIANCE,
            GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME: global_inclined_irradiance_series,
            RADIATION_MODEL_COLUMN_NAME: HOFIERKA_2002,
        },  # if verbose > 0 else {},
        GLOBAL_INCLINED_IRRADIANCE + " extended": lambda: {
                TITLE_KEY_NAME: GLOBAL_INCLINED_IRRADIANCE + " & relevant components",
            }
            if verbose > 1
            else {},
        "more_extended": lambda: (
            {
                DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME: direct_inclined_irradiance_series,
                DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME: diffuse_inclined_irradiance_series,
                REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME: ground_reflected_inclined_irradiance_series,
            }
            if verbose > 2
            else {}
        ),
        "Reflectivity": lambda: {
            REFLECTIVITY_COLUMN_NAME: global_inclined_reflectivity_series,
            # REFLECTIVITY_PERCENTAGE_COLUMN_NAME: global_inclined_reflectivity_loss_percentage_series if global_inclined_reflectivity_loss_percentage_series.size > 1 else NOT_AVAILABLE,
            # REFLECTIVITY_FACTOR_COLUMN_NAME: global_reflectivity_factor_series if global_reflectivity_factor_series.size > 1 else NOT_AVAILABLE,
            DIRECT_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME: direct_inclined_reflectivity_factor_series,
            DIFFUSE_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME: diffuse_inclined_reflectivity_factor_series,
            REFLECTED_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME: ground_reflected_inclined_reflectivity_factor_series,
        }
        if verbose > 6 and apply_reflectivity_factor
        else {},
        "Inclined irradiance components": lambda: {
            GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME: global_inclined_irradiance_series,
            DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME: direct_inclined_irradiance_series,
            DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME: diffuse_inclined_irradiance_series,
            REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME: ground_reflected_inclined_irradiance_series,
        }
        if verbose > 4
        else {},
        "Effective inclined irradiance": lambda: {
            TITLE_KEY_NAME: GLOBAL_INCLINED_IRRADIANCE + ", effective & in-plane irradiance components",
            GLOBAL_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME: global_inclined_irradiance_before_reflectivity_series,
            DIRECT_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME: direct_inclined_irradiance_before_reflectivity_series,
            DIFFUSE_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME: diffuse_inclined_irradiance_before_reflectivity_series,
            REFLECTED_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME: ground_reflected_inclined_irradiance_before_reflectivity_series,
        }
        if verbose > 5 and apply_reflectivity_factor
        else {},
        "Horizontal irradiance components": lambda: {
            DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME: direct_horizontal_irradiance_series,
            DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME: diffuse_horizontal_irradiance_series,
            # Ground-Reflected Horizontal Irradiance is zero for horizontal surfaces !
        }
        if verbose > 6
        else {},
        "Solar position": lambda: {
            INCIDENCE_COLUMN_NAME: calculated_direct_inclined_irradiance_series.components[
                INCIDENCE_COLUMN_NAME
            ]
            if calculated_direct_inclined_irradiance_series.components
            else NOT_AVAILABLE,
            ALTITUDE_COLUMN_NAME: getattr(solar_altitude_series, angle_output_units),
            # AZIMUTH_COLUMN_NAME: getattr(solar_azimuth_series, angle_output_units),
            SUN_HORIZON_POSITION_COLUMN_NAME: sun_horizon_position_series,
        }
        if verbose > 9
        else {},
        "Surface Position Metadata": lambda: {
            SURFACE_ORIENTATION_COLUMN_NAME: convert_float_to_degrees_if_requested(
                surface_orientation, angle_output_units
            ),
            SURFACE_TILT_COLUMN_NAME: convert_float_to_degrees_if_requested(
                surface_tilt, angle_output_units
            ),
            SHADING_ALGORITHM_COLUMN_NAME: surface_in_shade_series.shading_algorithm if horizon_profile is not None else 'Not performed',
            SHADING_STATES_COLUMN_NAME: shading_states if shading_states else NOT_AVAILABLE,
            }
            if verbose
            else {},
        "Surface position": lambda: {
                SURFACE_IN_SHADE_COLUMN_NAME: surface_in_shade_series.value,
            }
            if verbose > 1
            else {},
        "Solar Position Metadata": lambda: {
            UNIT_NAME: angle_output_units,
            INCIDENCE_ALGORITHM_COLUMN_NAME: calculated_direct_inclined_irradiance_series.components[
                INCIDENCE_ALGORITHM_COLUMN_NAME
            ]
            if calculated_direct_inclined_irradiance_series.components
            else NOT_AVAILABLE,
            INCIDENCE_DEFINITION: calculated_direct_inclined_irradiance_series.components[
                INCIDENCE_DEFINITION
            ]
            if calculated_direct_inclined_irradiance_series.components
            else NOT_AVAILABLE,
            SUN_HORIZON_POSITIONS_NAME: sun_horizon_positions,  # Requested positions
            POSITION_ALGORITHM_COLUMN_NAME: solar_altitude_series.position_algorithm,
            TIME_ALGORITHM_COLUMN_NAME: solar_altitude_series.timing_algorithm,
            SOLAR_CONSTANT_COLUMN_NAME: solar_constant,
            PERIGEE_OFFSET_COLUMN_NAME: perigee_offset,
            ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME: eccentricity_correction_factor,
            # ABOVE_HORIZON_COLUMN_NAME: mask_above_horizon,
            # LOW_ANGLE_COLUMN_NAME: mask_low_angle,
            # BELOW_HORIZON_COLUMN_NAME: mask_below_horizon,
            },
        "Fingerprint": lambda: (
            {
                FINGERPRINT_COLUMN_NAME: generate_hash(
                    global_inclined_irradiance_series
                ),
            }
            if fingerprint
            else {}
        ),
    }

    components = {}
    for _, component in components_container.items():
        components.update(component())

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=global_inclined_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return Irradiance(
        value=global_inclined_irradiance_series,
        unit=IRRADIANCE_UNIT,
        position_algorithm=solar_altitude_series.position_algorithm,
        timing_algorithm=solar_altitude_series.timing_algorithm,
        elevation=elevation,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        components=components,
    )
