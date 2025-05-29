from os import read
from pvgisprototype.algorithms.huld.photovoltaic_module import PhotovoltaicModuleType
from pvgisprototype.api.position.azimuth import model_solar_azimuth_series
from pvgisprototype.api.position.incidence import model_solar_incidence_series
from pvgisprototype import (
        SolarAzimuth,
        SurfaceOrientation,
        SurfaceTilt,
        LinkeTurbidityFactor,
        GlobalInclinedIrradiance,
        )
from pvgisprototype.api.position.altitude import model_solar_altitude_series
from pvgisprototype.api.position.models import (
    SUN_HORIZON_POSITION_DEFAULT,
    ShadingState,
    SolarIncidenceModel,
    SolarPositionModel,
    SolarTimeModel,
    ShadingModel,
    SunHorizonPositionModel,
)
from pvgisprototype.api.position.shading import model_surface_in_shade_series
from pvgisprototype.constants import (
    ALBEDO_DEFAULT,
    ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    PERIGEE_OFFSET,
    # UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    SOLAR_CONSTANT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    SURFACE_TILT_HORIZONTALLY_FLAT_PANEL_THRESHOLD,
    VALIDATE_OUTPUT_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger
from pvgisprototype.core.arrays import create_array
from typing import List
from zoneinfo import ZoneInfo

import numpy
from devtools import debug
from numpy._core.multiarray import ndarray
from pandas import DatetimeIndex, Timestamp
from xarray import DataArray
from pandas import DatetimeIndex, Timestamp
from pvgisprototype.algorithms.hofierka.irradiance.shortwave.clear_sky.inclined import calculate_global_inclined_irradiance_hofierka
from pvgisprototype.algorithms.hofierka.irradiance.shortwave.inclined import calculate_global_inclined_irradiance_from_external_data_hofierka


@log_function_call
def calculate_global_inclined_irradiance(
    longitude: float,
    latitude: float,
    elevation: float,
    surface_orientation: SurfaceOrientation | None = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt | None = SURFACE_TILT_DEFAULT,
    timestamps: DatetimeIndex = DatetimeIndex([Timestamp.now(tz='UTC')]),
    timezone: ZoneInfo | None = None,
    global_horizontal_irradiance: ndarray | None = None,
    direct_horizontal_irradiance: ndarray | None = None,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    adjust_for_atmospheric_refraction: bool = True,
    # unrefracted_solar_zenith: UnrefractedSolarZenith | None = UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
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
    eccentricity_phase_offset: float = PERIGEE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    # angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
) -> GlobalInclinedIrradiance:
    """
    """
    # Some quantities are not always required, hence set them to avoid UnboundLocalError!
    array_parameters = {
        "shape": timestamps.shape,
        "dtype": dtype,
        "init_method": "empty",
        "backend": array_backend,
    }  # Borrow shape from timestamps
    solar_azimuth_series = SolarAzimuth(value=create_array(**array_parameters))
    solar_incidence_series = model_solar_incidence_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_incidence_model=solar_incidence_model,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        eccentricity_phase_offset=eccentricity_phase_offset,
        eccentricity_amplitude=eccentricity_amplitude,
        complementary_incidence_angle=True,  # = Sun-vector To Surface-plane (Jenčo, 1992) !
        zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
        dtype=dtype,
        array_backend=array_backend,
        verbose=0,
        log=log,
    )
    # Calculate quantities required : ---------------------------- >>> >>> >>>
    # 1. to model the diffuse horizontal irradiance [optional]
    # 2. to calculate the diffuse sky ... to consider shaded, sunlit and potentially sunlit surfaces
    
    # extraterrestrial on a horizontal surface requires the solar altitude
    solar_altitude_series = model_solar_altitude_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
        # unrefracted_solar_zenith=unrefracted_solar_zenith,
        # solar_time_model=solar_time_model,
        # eccentricity_phase_offset=eccentricity_phase_offset,
        # eccentricity_amplitude=eccentricity_amplitude,
        # angle_output_units=angle_output_units,
        dtype=dtype,
        array_backend=array_backend,
        validate_output=validate_output,
        verbose=verbose,
        log=log,
    )
    # Calculate quantities required : ---------------------------- <<< <<< <<<

    if surface_tilt > SURFACE_TILT_HORIZONTALLY_FLAT_PANEL_THRESHOLD:  # tilted (or inclined) surface
        # requires the solar incidence angle for shading and times of sunlit surface
        solar_incidence_series = model_solar_incidence_series(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            surface_orientation=surface_orientation,
            surface_tilt=surface_tilt,
            adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
            solar_incidence_model=solar_incidence_model,
            horizon_profile=horizon_profile,
            shading_model=shading_model,
            complementary_incidence_angle=True,  # True = between sun-vector and surface-plane !
            zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
            eccentricity_phase_offset=eccentricity_phase_offset,
            eccentricity_amplitude=eccentricity_amplitude,
            dtype=dtype,
            array_backend=array_backend,
            validate_output=validate_output,
            verbose=verbose,
            log=log,
        )

        # Potentially sunlit surface series : solar altitude < 0.1 radians (or < 5.7 degrees)
        if numpy.any(solar_altitude_series.radians < 0.1):  # requires the solar azimuth
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
                verbose=verbose,
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
        adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
        # unrefracted_solar_zenith=unrefracted_solar_zenith,
        eccentricity_phase_offset=eccentricity_phase_offset,
        eccentricity_amplitude=eccentricity_amplitude,
        dtype=dtype,
        array_backend=array_backend,
        validate_output=validate_output,
        verbose=verbose,
        log=log,
    )
    if isinstance(global_horizontal_irradiance, ndarray):
        global_inclined_irradiance_series = calculate_global_inclined_irradiance_from_external_data_hofierka(
            longitude=longitude,
            latitude=latitude,
            elevation=elevation,
            surface_orientation=surface_orientation,
            surface_tilt=surface_tilt,
            timestamps=timestamps,
            timezone=timezone,
            global_horizontal_irradiance=global_horizontal_irradiance,
            direct_horizontal_irradiance=direct_horizontal_irradiance,
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
            # unrefracted_solar_zenith=unrefracted_solar_zenith,
            albedo=albedo,
            apply_reflectivity_factor=apply_reflectivity_factor,
            solar_incidence_series=solar_incidence_series,
            solar_altitude_series=solar_altitude_series,
            solar_azimuth_series=solar_azimuth_series,
            solar_position_model=solar_position_model,
            sun_horizon_position=sun_horizon_position,
            surface_in_shade_series=surface_in_shade_series,
            solar_incidence_model=solar_incidence_model,
            zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
            horizon_profile=horizon_profile,
            shading_model=shading_model,
            solar_time_model=solar_time_model,
            solar_constant=solar_constant,
            eccentricity_phase_offset=eccentricity_phase_offset,
            eccentricity_amplitude=eccentricity_amplitude,
            # angle_output_units=angle_output_units,
            dtype=dtype,
            array_backend=array_backend,
            validate_output=validate_output,
            verbose=verbose,
            log=log,
            fingerprint=fingerprint,
        )
    else:
        global_inclined_irradiance_series = calculate_global_inclined_irradiance_hofierka(
            longitude=longitude,
            latitude=latitude,
            elevation=elevation,
            surface_orientation=surface_orientation,
            surface_tilt=surface_tilt,
            timestamps=timestamps,
            timezone=timezone,
            global_horizontal_irradiance=global_horizontal_irradiance,
            direct_horizontal_irradiance=direct_horizontal_irradiance,
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
            # unrefracted_solar_zenith=unrefracted_solar_zenith,
            albedo=albedo,
            apply_reflectivity_factor=apply_reflectivity_factor,
            solar_incidence_series=solar_incidence_series,
            solar_altitude_series=solar_altitude_series,
            solar_azimuth_series=solar_azimuth_series,
            solar_position_model=solar_position_model,
            sun_horizon_position=sun_horizon_position,
            surface_in_shade_series=surface_in_shade_series,
            solar_incidence_model=solar_incidence_model,
            zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
            horizon_profile=horizon_profile,
            shading_model=shading_model,
            solar_time_model=solar_time_model,
            solar_constant=solar_constant,
            eccentricity_phase_offset=eccentricity_phase_offset,
            eccentricity_amplitude=eccentricity_amplitude,
            # angle_output_units=angle_output_units,
            dtype=dtype,
            array_backend=array_backend,
            validate_output=validate_output,
            verbose=verbose,
            log=log,
            fingerprint=fingerprint,
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
            logger.debug(
                f"Including positions of the sun above horizon and not in shade :\n{sun_horizon_position_series}",
                alt=f"Including positions of the sun [bold yellow]above horizon[/bold yellow] and [bold red]not in shade[/bold red] :\n{sun_horizon_position_series}",
            )
            if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
                logger.debug(
                    "i [bold]Calculating[/bold] the [magenta]direct inclined irradiance[/magenta] for moments not in shade .."
                )
            # if given, will read from external time series
            calculated_direct_inclined_irradiance_series = calculate_direct_inclined_irradiance_series(
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
                    direct_inclined_reflectivity_factor_series,
                )
            )
            direct_inclined_reflectivity_series = (
                calculated_direct_inclined_irradiance_series.components.get(
                    REFLECTIVITY_COLUMN_NAME, direct_inclined_reflectivity_series
                )
            )

        # Calculate diffuse and reflected irradiance for sun above horizon
        if not numpy.any(mask_above_horizon):
            logger.debug(
                "i [yellow bold]Apparently there is no moment of the sun above the horizon in the requested time series![/yellow bold] "
            )
        else:
            if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
                logger.debug(
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
                    diffuse_inclined_reflectivity_factor_series,
                )
            )
            diffuse_inclined_reflectivity_series = (
                calculated_diffuse_inclined_irradiance_series.components.get(
                    REFLECTIVITY_COLUMN_NAME, diffuse_inclined_reflectivity_series
                )
            )
            if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
                logger.debug(
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
        logger.debug(
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
        GLOBAL_INCLINED_IRRADIANCE
        + " extended": lambda: (
            {
                TITLE_KEY_NAME: GLOBAL_INCLINED_IRRADIANCE + " & relevant components",
            }
            if verbose > 1
            else {}
        ),
        "more_extended": lambda: (
            {
                DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME: direct_inclined_irradiance_series,
                DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME: diffuse_inclined_irradiance_series,
                REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME: ground_reflected_inclined_irradiance_series,
            }
            if verbose > 2
            else {}
        ),
        "Reflectivity": lambda: (
            {
                REFLECTIVITY_COLUMN_NAME: global_inclined_reflectivity_series,
                # REFLECTIVITY_PERCENTAGE_COLUMN_NAME: global_inclined_reflectivity_loss_percentage_series if global_inclined_reflectivity_loss_percentage_series.size > 1 else NOT_AVAILABLE,
                # REFLECTIVITY_FACTOR_COLUMN_NAME: global_reflectivity_factor_series if global_reflectivity_factor_series.size > 1 else NOT_AVAILABLE,
                DIRECT_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME: direct_inclined_reflectivity_factor_series,
                DIFFUSE_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME: diffuse_inclined_reflectivity_factor_series,
                REFLECTED_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME: ground_reflected_inclined_reflectivity_factor_series,
            }
            if verbose > 6 and apply_reflectivity_factor
            else {}
        ),
        "Inclined irradiance components": lambda: (
            {
                GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME: global_inclined_irradiance_series,
                DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME: direct_inclined_irradiance_series,
                DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME: diffuse_inclined_irradiance_series,
                REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME: ground_reflected_inclined_irradiance_series,
            }
            if verbose > 4
            else {}
        ),
        "Effective inclined irradiance": lambda: (
            {
                TITLE_KEY_NAME: GLOBAL_INCLINED_IRRADIANCE
                + ", effective & in-plane irradiance components",
                GLOBAL_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME: global_inclined_irradiance_before_reflectivity_series,
                DIRECT_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME: direct_inclined_irradiance_before_reflectivity_series,
                DIFFUSE_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME: diffuse_inclined_irradiance_before_reflectivity_series,
                REFLECTED_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME: ground_reflected_inclined_irradiance_before_reflectivity_series,
            }
            if verbose > 5 and apply_reflectivity_factor
            else {}
        ),
        "Horizontal irradiance components": lambda: (
            {
                DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME: direct_horizontal_irradiance_series,
                DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME: diffuse_horizontal_irradiance_series,
                # Ground-Reflected Horizontal Irradiance is zero for horizontal surfaces !
            }
            if verbose > 6
            else {}
        ),
        "Solar position": lambda: (
            {
                INCIDENCE_COLUMN_NAME: (
                    calculated_direct_inclined_irradiance_series.components[
                        INCIDENCE_COLUMN_NAME
                    ]
                    if calculated_direct_inclined_irradiance_series.components
                    else NOT_AVAILABLE
                ),
                ALTITUDE_COLUMN_NAME: getattr(
                    solar_altitude_series, angle_output_units
                ),
                # AZIMUTH_COLUMN_NAME: getattr(solar_azimuth_series, angle_output_units),
                SUN_HORIZON_POSITION_COLUMN_NAME: sun_horizon_position_series,
            }
            if verbose > 9
            else {}
        ),
        "Surface Position Metadata": lambda: (
            {
                SURFACE_ORIENTATION_COLUMN_NAME: convert_float_to_degrees_if_requested(
                    surface_orientation, angle_output_units
                ),
                SURFACE_TILT_COLUMN_NAME: convert_float_to_degrees_if_requested(
                    surface_tilt, angle_output_units
                ),
                SHADING_ALGORITHM_COLUMN_NAME: (
                    surface_in_shade_series.shading_algorithm
                    if horizon_profile is not None
                    else "Not performed"
                ),
                SHADING_STATES_COLUMN_NAME: (
                    shading_states if shading_states else NOT_AVAILABLE
                ),
            }
            if verbose
            else {}
        ),
        "Surface position": lambda: (
            {
                SURFACE_IN_SHADE_COLUMN_NAME: surface_in_shade_series.value,
            }
            if verbose > 1
            else {}
        ),
        "Solar Position Metadata": lambda: {
            UNIT_NAME: angle_output_units,
            INCIDENCE_ALGORITHM_COLUMN_NAME: (
                calculated_direct_inclined_irradiance_series.components[
                    INCIDENCE_ALGORITHM_COLUMN_NAME
                ]
                if calculated_direct_inclined_irradiance_series.components
                else NOT_AVAILABLE
            ),
            INCIDENCE_DEFINITION: (
                calculated_direct_inclined_irradiance_series.components[
                    INCIDENCE_DEFINITION
                ]
                if calculated_direct_inclined_irradiance_series.components
                else NOT_AVAILABLE
            ),
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

>>>>>>> xyz-no-gitlab-test-server-version
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    global_inclined_irradiance_series.build_output(verbose, fingerprint)

    log_data_fingerprint(
        data=global_inclined_irradiance_series.value,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return global_inclined_irradiance_series
