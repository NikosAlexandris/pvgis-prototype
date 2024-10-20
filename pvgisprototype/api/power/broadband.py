from pathlib import Path
from zoneinfo import ZoneInfo

import numpy
from devtools import debug
from pandas import DatetimeIndex, Timestamp
from rich import print

from pvgisprototype import (
    LinkeTurbidityFactor,
    PhotovoltaicPower,
    SpectralFactorSeries,
    SurfaceOrientation,
    SurfaceTilt,
)
from pvgisprototype.api.irradiance.diffuse.inclined import (
    calculate_diffuse_inclined_irradiance_series,
)
from pvgisprototype.api.irradiance.direct.inclined import (
    calculate_direct_inclined_irradiance_series_pvgis,
)
from pvgisprototype.api.irradiance.models import (
    MethodForInexactMatches,
    ModuleTemperatureAlgorithm,
)
from pvgisprototype.api.irradiance.reflected import (
    calculate_ground_reflected_inclined_irradiance_series,
)
from pvgisprototype.api.irradiance.shade import is_surface_in_shade_series
from pvgisprototype.api.performance.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.api.position.altitude import model_solar_altitude_series
from pvgisprototype.api.position.azimuth import model_solar_azimuth_series
from pvgisprototype.api.position.models import (
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SOLAR_TIME_ALGORITHM_DEFAULT,
    SolarIncidenceModel,
    SolarPositionModel,
    SolarTimeModel,
)
from pvgisprototype.api.power.efficiency import (
    calculate_pv_efficiency_series,
    calculate_spectrally_corrected_effective_irradiance,
)
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
)
from pvgisprototype.constants import (
    ABOVE_HORIZON_COLUMN_NAME,
    ALBEDO_DEFAULT,
    ALTITUDE_COLUMN_NAME,
    ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    AZIMUTH_COLUMN_NAME,
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
    EFFECTIVE_DIFFUSE_IRRADIANCE_COLUMN_NAME,
    EFFECTIVE_DIRECT_IRRADIANCE_COLUMN_NAME,
    EFFECTIVE_GLOBAL_IRRADIANCE_COLUMN_NAME,
    EFFECTIVE_REFLECTED_IRRADIANCE_COLUMN_NAME,
    EFFICIENCY_COLUMN_NAME,
    EFFICIENCY_FACTOR_DEFAULT,
    FINGERPRINT_COLUMN_NAME,
    FINGERPRINT_FLAG_DEFAULT,
    GLOBAL_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    IN_MEMORY_FLAG_DEFAULT,
    INCIDENCE_ALGORITHM_COLUMN_NAME,
    INCIDENCE_COLUMN_NAME,
    INCIDENCE_DEFINITION,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    LOW_ANGLE_COLUMN_NAME,
    MASK_AND_SCALE_FLAG_DEFAULT,
    MULTI_THREAD_FLAG_DEFAULT,
    NEIGHBOR_LOOKUP_DEFAULT,
    NOT_AVAILABLE,
    PEAK_POWER_COLUMN_NAME,
    PERIGEE_OFFSET,
    PERIGEE_OFFSET_COLUMN_NAME,
    PHOTOVOLTAIC_POWER,
    PHOTOVOLTAIC_POWER_COLUMN_NAME,
    PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME,
    POSITION_ALGORITHM_COLUMN_NAME,
    POWER_MODEL_COLUMN_NAME,
    POWER_UNIT,
    RADIANS,
    RADIATION_CUTOFF_THRESHHOLD,
    REFLECTED_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME,
    REFLECTED_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME,
    REFLECTIVITY_COLUMN_NAME,
    REFLECTIVITY_FACTOR_COLUMN_NAME,
    REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    SHADE_COLUMN_NAME,
    SOLAR_CONSTANT,
    SOLAR_CONSTANT_COLUMN_NAME,
    SPECTRAL_EFFECT_COLUMN_NAME,
    SPECTRAL_EFFECT_PERCENTAGE_COLUMN_NAME,
    SPECTRAL_FACTOR_COLUMN_NAME,
    SPECTRAL_FACTOR_DEFAULT,
    SURFACE_ORIENTATION_COLUMN_NAME,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_COLUMN_NAME,
    SURFACE_TILT_DEFAULT,
    SYMBOL_UNIT_TEMPERATURE,
    SYMBOL_UNIT_WIND_SPEED,
    SYSTEM_EFFICIENCY_COLUMN_NAME,
    SYSTEM_EFFICIENCY_DEFAULT,
    TECHNOLOGY_NAME,
    TEMPERATURE_COLUMN_NAME,
    TEMPERATURE_DEFAULT,
    TIME_ALGORITHM_COLUMN_NAME,
    TITLE_KEY_NAME,
    TOLERANCE_DEFAULT,
    UNIT_NAME,
    UNITLESS,
    VERBOSE_LEVEL_DEFAULT,
    WIND_SPEED_COLUMN_NAME,
    WIND_SPEED_DEFAULT,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    cPROFILE_FLAG_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger
from pvgisprototype.core.arrays import create_array
from pvgisprototype.core.hashing import generate_hash


@log_function_call
def calculate_photovoltaic_power_output_series(
    longitude: float,
    latitude: float,
    elevation: float,
    surface_orientation: SurfaceOrientation | None = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt | None = SURFACE_TILT_DEFAULT,
    timestamps: DatetimeIndex | None = DatetimeIndex([Timestamp.now(tz='UTC')]),
    timezone: ZoneInfo = ZoneInfo("UTC"),
    global_horizontal_irradiance: Path | None = None,
    direct_horizontal_irradiance: Path | None = None,
    spectral_factor_series: SpectralFactorSeries = SpectralFactorSeries(
        value=SPECTRAL_FACTOR_DEFAULT
    ),
    temperature_series: numpy.ndarray = numpy.array(TEMPERATURE_DEFAULT),
    wind_speed_series: numpy.ndarray = numpy.array(WIND_SPEED_DEFAULT),
    neighbor_lookup: MethodForInexactMatches = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: float | None = TOLERANCE_DEFAULT,
    mask_and_scale: bool = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: bool = IN_MEMORY_FLAG_DEFAULT,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LinkeTurbidityFactor(
        value=LINKE_TURBIDITY_TIME_SERIES_DEFAULT
    ),
    apply_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: float | None = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    albedo: float | None = ALBEDO_DEFAULT,
    apply_reflectivity_factor: bool = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_position_model: SolarPositionModel = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: SolarIncidenceModel = SolarIncidenceModel.iqbal,
    zero_negative_solar_incidence_angle: bool = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    solar_time_model: SolarTimeModel = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    # horizon_heights: List[float] = None,
    photovoltaic_module: PhotovoltaicModuleModel = PhotovoltaicModuleModel.CSI_FREE_STANDING,
    peak_power: float = 1,
    system_efficiency: float | None = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: PhotovoltaicModulePerformanceModel = PhotovoltaicModulePerformanceModel.king,
    radiation_cutoff_threshold: float = RADIATION_CUTOFF_THRESHHOLD,
    temperature_model: ModuleTemperatureAlgorithm = ModuleTemperatureAlgorithm.faiman,
    efficiency: float | None = EFFICIENCY_FACTOR_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    multi_thread: bool = MULTI_THREAD_FLAG_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
    profile: bool = cPROFILE_FLAG_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
):
    """
    Estimate the photovoltaic power over a time series or an arbitrarily
    aggregated energy production of a PV system based on the effective solar
    irradiance incident on a solar surface, the ambient temperature and
    optionally wind speed.

    Parameters
    ----------
    longitude : float
        The longitude of the location for which the energy production is calculated.
    latitude : float
        The latitude of the location.
    elevation : float
        Elevation of the location in meters.
    timestamps : DatetimeIndex, optional
        Specific timestamps for which to calculate the irradiance. Default is None.
    timezone : str | None, optional
        Timezone of the location. Default is None.
    global_horizontal_component : Path | None, optional
        Path to data file for global horizontal irradiance. Default is None.
    direct_horizontal_component : Path | None, optional
        Path to data file for direct horizontal irradiance. Default is None.
    temperature_series : TemperatureSeries
        Series of temperature values. Default is TEMPERATURE_DEFAULT.
    wind_speed_series : WindSpeedSeries
        Series of wind speed values. Default is WIND_SPEED_DEFAULT.
    mask_and_scale : bool, default False
        If True, applies masking and scaling to the input data.

    # ... other parameters ...

    Returns
    -------
    photovoltaic_power_output_series : ndarray
        Array of effective irradiance values.
    results : dict
        Dictionary containing detailed results of the calculation.
    title : str
        Title of the output data.

    Examples
    --------
    >>> calculate_photovoltaic_power_output_series(10.0, 20.0, 100.0)
    # This will return the effective irradiance series, results, and title for the specified parameters.

    Notes
    -----
    This function is part of the Typer-based CLI for the new PVGIS
    implementation in Python. It provides an interface for estimating the
    energy production of a photovoltaic system, taking into account various
    environmental and system parameters.

    """
    # import click
    # ctx = click.get_current_context()
    # print(f"args here : {ctx.args}")
    # print(f"Command here : {ctx.command}")
    # print(f"Command name here : {ctx.command.name}")
    # print(f"Command path here : {ctx.command_path}")
    # print(f"get_parameter_source() : {ctx.get_parameter_source('temperature_series')}")
    # print(f"get_usage() : {ctx.get_usage()}")
    # print(f"info_name : {ctx.info_name}")
    # print(f"invoked_subcommand : {ctx.invoked_subcommand}")
    # print(f"meta : {ctx.meta}")
    # print(f"obj : {ctx.obj}")
    # print(f"params : {ctx.params}")
    # print(f"parent : {ctx.parent}")
    # print()
    if profile:
        import cProfile

        pr = cProfile.Profile()
        pr.enable()

    if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
        logger.info(
            "i Modelling the solar altitude for the given timestamps ..",
            alt="i [bold]Modelling[/bold] the [magenta]solar altitude[/magenta] for the given timestamps .."
        )
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
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
        validate_output=validate_output,
    )
    if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
        logger.info(
            "i Modelling the solar azimuth for the given timestamps ..",
            alt="i [bold]Modelling[/bold] the [magenta]solar azimuth[/magenta] for the given timestamps .."
        )
    solar_azimuth_series = model_solar_azimuth_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        # solar_time_model=solar_time_model,
        # perigee_offset=perigee_offset,
        # eccentricity_correction_factor=eccentricity_correction_factor,
        dtype=dtype,
        array_backend=array_backend,
        verbose=0,
        log=log,
        validate_output=validate_output,
    )
    # Masks based on the solar altitude series
    if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
        logger.info(
            "i [bold]Masking out[/bold] moments in time when [magenta]the surface is not illuminated [/magenta] .."
        )
    mask_above_horizon = solar_altitude_series.value > 0
    mask_low_angle = (solar_altitude_series.value >= 0) & (
        solar_altitude_series.value < 0.04
    )  # FIXME: Is the value 0.04 in radians or degrees ?
    mask_below_horizon = solar_altitude_series.value < 0
    in_shade = is_surface_in_shade_series(
        solar_altitude_series,
        solar_azimuth_series,
        validate_output=validate_output,
    )
    mask_not_in_shade = ~in_shade
    # mask_above_horizon_not_in_shade = numpy.logical_and.reduce(mask_above_horizon, mask_not_in_shade)
    mask_above_horizon_not_in_shade = numpy.logical_and(
        mask_above_horizon, mask_not_in_shade
    )

    # In order to avoid unbound errors
    array_parameters = {
        "shape": timestamps.shape,
        "dtype": dtype,
        "init_method": "zeros",
        "backend": array_backend,
    }  # Borrow shape from timestamps

    # direct
    direct_horizontal_irradiance_series = create_array(**array_parameters)
    direct_inclined_irradiance_series = create_array(**array_parameters)
    calculated_diffuse_inclined_irradiance_series = (
        {}
    )  # no-values without direct sunlight

    # diffuse (== sky-reflected)
    diffuse_horizontal_irradiance_series = create_array(**array_parameters)
    diffuse_inclined_irradiance_series = create_array(**array_parameters)

    # ground-reflected
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

    # For very low sun angles
    direct_inclined_irradiance_series[mask_low_angle] = (
        0  # Direct radiation is negligible
    )

    # For sun below the horizon
    direct_inclined_irradiance_series[mask_below_horizon] = 0
    diffuse_inclined_irradiance_series[mask_below_horizon] = 0
    ground_reflected_inclined_irradiance_series[mask_below_horizon] = 0

    # For sun above horizon and not in shade
    if numpy.any(mask_above_horizon_not_in_shade):
        if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
            logger.info(
                "i [bold]Calculating[/bold] the [magenta]direct inclined irradiance[/magenta] for moments not in shade .."
            )
        calculated_direct_inclined_irradiance_series = (
            calculate_direct_inclined_irradiance_series_pvgis(
                longitude=longitude,
                latitude=latitude,
                elevation=elevation,
                timestamps=timestamps,
                timezone=timezone,
                direct_horizontal_component=direct_horizontal_irradiance,
                mask_and_scale=mask_and_scale,
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                in_memory=in_memory,
                surface_tilt=surface_tilt,
                surface_orientation=surface_orientation,
                linke_turbidity_factor_series=linke_turbidity_factor_series,
                apply_atmospheric_refraction=apply_atmospheric_refraction,
                refracted_solar_zenith=refracted_solar_zenith,
                apply_reflectivity_factor=apply_reflectivity_factor,
                solar_position_model=solar_position_model,
                solar_incidence_model=solar_incidence_model,
                zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
                solar_time_model=solar_time_model,
                solar_constant=solar_constant,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                angle_output_units=angle_output_units,
                dtype=dtype,
                array_backend=array_backend,
                verbose=verbose,
                log=log,
            )
        )
        direct_horizontal_irradiance_series = (
            calculated_direct_inclined_irradiance_series.components.get(
                DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
                numpy.array([]),
            )
        )

        direct_horizontal_irradiance_series = (
            calculated_direct_inclined_irradiance_series.components.get(
                DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
                numpy.array([]),
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
                numpy.array([]),
            )
        )
        direct_inclined_reflectivity_factor_series = (
            calculated_direct_inclined_irradiance_series.components.get(
                REFLECTIVITY_FACTOR_COLUMN_NAME, numpy.array([])
            )
        )
        direct_inclined_reflectivity_series = (
            calculated_direct_inclined_irradiance_series.components.get(
                REFLECTIVITY_COLUMN_NAME, numpy.array([])
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
            timestamps=timestamps,
            timezone=timezone,
            surface_tilt=surface_tilt,
            surface_orientation=surface_orientation,
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            refracted_solar_zenith=refracted_solar_zenith,
            global_horizontal_component=global_horizontal_irradiance,  # time series optional
            direct_horizontal_component=direct_horizontal_irradiance,  # time series, optional
            mask_and_scale=mask_and_scale,
            neighbor_lookup=neighbor_lookup,
            tolerance=tolerance,
            in_memory=in_memory,
            apply_reflectivity_factor=apply_reflectivity_factor,
            solar_position_model=solar_position_model,
            solar_incidence_model=solar_incidence_model,
            zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
            solar_time_model=solar_time_model,
            solar_constant=solar_constant,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            angle_output_units=angle_output_units,
            dtype=dtype,
            array_backend=array_backend,
            multi_thread=multi_thread,
            verbose=verbose,
            log=log,
        )
        diffuse_horizontal_irradiance_series = (
            calculated_diffuse_inclined_irradiance_series.components.get(
                DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
                numpy.array([]),
            )
        )
        diffuse_horizontal_irradiance_series = (
            calculated_diffuse_inclined_irradiance_series.components.get(
                DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
                numpy.array([]),
            )
        )
        diffuse_inclined_irradiance_series[mask_above_horizon] = (
            calculated_diffuse_inclined_irradiance_series.value[mask_above_horizon]
        )  # .value is the diffuse irradiance series
        diffuse_inclined_irradiance_before_reflectivity_series = (
            calculated_diffuse_inclined_irradiance_series.components.get(
                DIFFUSE_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
                numpy.array([]),
            )
        )
        diffuse_inclined_reflectivity_factor_series = (
            calculated_diffuse_inclined_irradiance_series.components.get(
                REFLECTIVITY_FACTOR_COLUMN_NAME, numpy.array([])
            )
        )
        diffuse_inclined_reflectivity_series = (
            calculated_diffuse_inclined_irradiance_series.components.get(
                REFLECTIVITY_COLUMN_NAME, numpy.array([])
            )
        )

        if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
            logger.info(
                "i [bold]Calculating[/bold] the [magenta]reflected inclined irradiance[/magenta] for daylight moments .."
            )
        calculated_ground_reflected_inclined_irradiance_series = (
            calculate_ground_reflected_inclined_irradiance_series(
                longitude=longitude,
                latitude=latitude,
                elevation=elevation,
                surface_orientation=surface_orientation,
                surface_tilt=surface_tilt,
                timestamps=timestamps,
                timezone=timezone,
                global_horizontal_component=global_horizontal_irradiance,  # optional
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
                verbose=verbose,
                log=log,
                fingerprint=fingerprint,
            )
        )
        ground_reflected_inclined_irradiance_series[mask_above_horizon] = (
            calculated_ground_reflected_inclined_irradiance_series.value[
                mask_above_horizon
            ]
        )  # .value is the ground reflected irradiance series
        ground_reflected_inclined_irradiance_before_reflectivity_series = (
            calculated_ground_reflected_inclined_irradiance_series.components.get(
                REFLECTED_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
                numpy.array([]),
            )
        )
        ground_reflected_inclined_reflectivity_factor_series = (
            calculated_ground_reflected_inclined_irradiance_series.components.get(
                REFLECTIVITY_FACTOR_COLUMN_NAME,
                numpy.array([]),
            )
        )
        ground_reflected_inclined_reflectivity_series = (
            calculated_ground_reflected_inclined_irradiance_series.components.get(
                REFLECTIVITY_COLUMN_NAME,
                numpy.array([]),
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

    # Does this make sense ?
    # global_inclined_reflectivity_factor_series = (
    #     direct_inclined_reflectivity_factor_series
    #     + diffuse_inclined_reflectivity_factor_series
    #     + ground_reflected_inclined_reflectivity_factor_series
    # )
    global_inclined_reflectivity_series = (
        direct_inclined_reflectivity_series
        + diffuse_inclined_reflectivity_series
        + ground_reflected_inclined_reflectivity_series
    )
    # -----------------------------------------------------------------------
    # Try the following, to deduplicate code,
    # global_inclined_irradiance_series = calculate_global_inclined_irradiance_series()
    # ?
    # -----------------------------------------------------------------------
    if not power_model:
        if not efficiency:  # user-set  -- RenameMe ?  FIXME
            efficiency_factor_series = system_efficiency
        else:
            efficiency_factor_series = efficiency

    else:
        if efficiency:
            efficiency_factor_series = efficiency
        else:
            effective_global_irradiance_series = calculate_spectrally_corrected_effective_irradiance(
                irradiance_series=global_inclined_irradiance_before_reflectivity_series,
                spectral_factor_series=spectral_factor_series,
                dtype=dtype,
                array_backend=array_backend,
                verbose=verbose,
                log=log,
                fingerprint=fingerprint,
            )
            efficiency_series = calculate_pv_efficiency_series(
                irradiance_series=global_inclined_irradiance_series,
                photovoltaic_module=photovoltaic_module,
                power_model=power_model,
                temperature_model=temperature_model,
                # model_constants=EFFICIENCY_MODEL_COEFFICIENTS_DEFAULT,
                spectral_factor_series=spectral_factor_series,  # required for the Power model !
                temperature_series=temperature_series,
                standard_test_temperature=TEMPERATURE_DEFAULT,
                wind_speed_series=wind_speed_series,
                radiation_cutoff_threshold=radiation_cutoff_threshold,
                dtype=dtype,
                array_backend=array_backend,
                verbose=verbose,
                log=log,
            )
            efficiency_factor_series = efficiency_series.value

    if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
        logger.info(
            "i [bold]Applying[/bold] [magenta]efficiency coefficients[/magenta] on the global inclined irradiance .."
        )
    # Power Model efficiency coefficients include temperature and low irradiance effect !
    photovoltaic_power_output_without_system_loss_series = (
        global_inclined_irradiance_series * efficiency_factor_series
    )  # Safer to deepcopy the efficiency_series which are modified _afer_ this point ?

    if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
        logger.info(
            "i [bold]Applying[/bold] [magenta]system loss[/magenta] on the effective photovoltaic power .."
        )
    photovoltaic_power_output_series = (
        photovoltaic_power_output_without_system_loss_series * system_efficiency
    )

    if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
        logger.info("i [bold]Building the output[/bold] ..")

    components_container = {
        "Metadata": lambda: {
            POSITION_ALGORITHM_COLUMN_NAME: solar_altitude_series.position_algorithm,
            TIME_ALGORITHM_COLUMN_NAME: solar_altitude_series.timing_algorithm,
            SOLAR_CONSTANT_COLUMN_NAME: solar_constant,
            PERIGEE_OFFSET_COLUMN_NAME: perigee_offset,
            ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME: eccentricity_correction_factor,
        },
        "Power": lambda: {
            TITLE_KEY_NAME: PHOTOVOLTAIC_POWER,
            PHOTOVOLTAIC_POWER_COLUMN_NAME: photovoltaic_power_output_series,
            TECHNOLOGY_NAME: photovoltaic_module.value,
            PEAK_POWER_COLUMN_NAME: peak_power,
            POWER_MODEL_COLUMN_NAME: power_model.value
            if power_model
            else NOT_AVAILABLE,
        },  # if verbose > 0 else {},
        "Power extended": lambda: {
            PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME: photovoltaic_power_output_without_system_loss_series,
        }
        if verbose > 1
        else {},
        "System loss": lambda: {
            EFFICIENCY_COLUMN_NAME: efficiency_factor_series,
            SYSTEM_EFFICIENCY_COLUMN_NAME: system_efficiency,
        }
        if verbose > 2
        else {},
        "Effective irradiance": lambda: {
            TITLE_KEY_NAME: PHOTOVOLTAIC_POWER + " & effective components",
            EFFECTIVE_GLOBAL_IRRADIANCE_COLUMN_NAME: global_inclined_irradiance_series
            * efficiency_factor_series,
            EFFECTIVE_DIRECT_IRRADIANCE_COLUMN_NAME: direct_inclined_irradiance_series
            * efficiency_factor_series,
            EFFECTIVE_DIFFUSE_IRRADIANCE_COLUMN_NAME: diffuse_inclined_irradiance_series
            * efficiency_factor_series,
            EFFECTIVE_REFLECTED_IRRADIANCE_COLUMN_NAME: ground_reflected_inclined_irradiance_series
            * efficiency_factor_series,
            SPECTRAL_EFFECT_COLUMN_NAME: effective_global_irradiance_series.components.get(
                SPECTRAL_EFFECT_COLUMN_NAME, numpy.array([])
            ),
            SPECTRAL_EFFECT_PERCENTAGE_COLUMN_NAME: effective_global_irradiance_series.components.get(
                SPECTRAL_EFFECT_PERCENTAGE_COLUMN_NAME, numpy.array([])
            ),
            SPECTRAL_FACTOR_COLUMN_NAME: effective_global_irradiance_series.components.get(
                SPECTRAL_FACTOR_COLUMN_NAME, numpy.array([])
            ),
        }
        if verbose > 3
        else {},
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
        "more_extended_2": lambda: {
            TITLE_KEY_NAME: PHOTOVOLTAIC_POWER + ", effective & in-plane components",
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
            # REFLECTED_HORIZONTAL_IRRADIANCE_COLUMN_NAME: calculated_ground_reflected_inclined_irradiance_series.components[REFLECTED_HORIZONTAL_IRRADIANCE_COLUMN_NAME], Is zero for horizontal surfaces !
        }
        if verbose > 6
        else {},
        "Meteorological variables": lambda: {
            TEMPERATURE_COLUMN_NAME: temperature_series.value,
            WIND_SPEED_COLUMN_NAME: wind_speed_series.value,
        }
        if verbose > 7
        else {},
        "Surface position": lambda: {
            SURFACE_ORIENTATION_COLUMN_NAME: convert_float_to_degrees_if_requested(
                surface_orientation, angle_output_units
            ),
            SURFACE_TILT_COLUMN_NAME: convert_float_to_degrees_if_requested(
                surface_tilt, angle_output_units
            ),
            ABOVE_HORIZON_COLUMN_NAME: mask_above_horizon,
            LOW_ANGLE_COLUMN_NAME: mask_low_angle,
            BELOW_HORIZON_COLUMN_NAME: mask_below_horizon,
            SHADE_COLUMN_NAME: in_shade,
        }
        if verbose > 8
        else {},
        "Solar position": lambda: {
            INCIDENCE_COLUMN_NAME: calculated_direct_inclined_irradiance_series.components[
                INCIDENCE_COLUMN_NAME
            ]
            if calculated_direct_inclined_irradiance_series.components
            else NOT_AVAILABLE,
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
            ALTITUDE_COLUMN_NAME: getattr(solar_altitude_series, angle_output_units),
            AZIMUTH_COLUMN_NAME: getattr(solar_azimuth_series, angle_output_units),
            UNIT_NAME: angle_output_units,
        }
        if verbose > 9
        else {},
        "fingerprint": lambda: {
            FINGERPRINT_COLUMN_NAME: generate_hash(photovoltaic_power_output_series),
        }
        if fingerprint
        else {},
    }

    components = {}
    for key, component in components_container.items():
        components.update(component())

    # Overwrite the direct irradiance 'components' with the global ones !
    # components = components | calculated_direct_inclined_irradiance_series.components

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    if profile:
        import io
        import pstats

        pr.disable()

        # write profiling statistics to file
        profile_filename = "profiling_stats.prof"
        pr.dump_stats(profile_filename)
        print(f"Profiling statistics saved to {profile_filename}")

        s = io.StringIO()
        sortby = pstats.SortKey.CUMULATIVE
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()

        if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
            print(s.getvalue())

    log_data_fingerprint(
        data=photovoltaic_power_output_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )
    return PhotovoltaicPower(
        value=photovoltaic_power_output_series,
        unit=POWER_UNIT,
        position_algorithm="",
        timing_algorithm="",
        elevation=elevation,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        irradiance=global_inclined_irradiance_series,
        components=components,
    )
