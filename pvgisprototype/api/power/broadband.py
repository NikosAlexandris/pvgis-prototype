from typing import List
from zoneinfo import ZoneInfo
import numpy
from numpy import ndarray
from devtools import debug
from pandas import DatetimeIndex, Timestamp
from xarray import DataArray
from pvgisprototype import (
    LinkeTurbidityFactor,
    DirectHorizontalIrradianceFromExternalData,
    PhotovoltaicPower,
    PhotovoltaicPowerFromExternalData,
    SpectralFactorSeries,
    SurfaceOrientation,
    SurfaceTilt,
)
from pvgisprototype.api.irradiance.models import (
    ModuleTemperatureAlgorithm,
)
# from pvgisprototype.api.performance.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.algorithms.huld.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.api.position.models import (
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SOLAR_TIME_ALGORITHM_DEFAULT,
    SUN_HORIZON_POSITION_DEFAULT,
    ShadingModel,
    ShadingState,
    SolarIncidenceModel,
    SolarPositionModel,
    SunHorizonPositionModel,
    SolarTimeModel,
    select_models,
)
from pvgisprototype.api.position.output import generate_dictionary_of_surface_in_shade_series_x
from pvgisprototype.api.irradiance.shortwave.inclined import calculate_global_inclined_irradiance
from pvgisprototype.api.irradiance.effective import calculate_spectrally_corrected_effective_irradiance
from pvgisprototype.api.power.efficiency import (
    calculate_photovoltaic_efficiency_series,
)
# from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel, PhotovoltaicModuleType
from pvgisprototype.algorithms.huld.photovoltaic_module import PhotovoltaicModuleModel, PhotovoltaicModuleType
from pvgisprototype.constants import (
    ALBEDO_DEFAULT,
    ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    EFFICIENCY_FACTOR_DEFAULT,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    PEAK_POWER_DEFAULT,
    PERIGEE_OFFSET,
    RADIANS,
    RADIATION_CUTOFF_THRESHHOLD,
    SOLAR_CONSTANT,
    SPECTRAL_FACTOR_DEFAULT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    SYSTEM_EFFICIENCY_DEFAULT,
    TEMPERATURE_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    WIND_SPEED_DEFAULT,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    cPROFILE_FLAG_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger


@log_function_call
def calculate_photovoltaic_power_output_series(
    longitude: float,
    latitude: float,
    elevation: float,
    surface_orientation: SurfaceOrientation | None = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt | None = SURFACE_TILT_DEFAULT,
    timestamps: DatetimeIndex = DatetimeIndex([Timestamp.now(tz='UTC')]),
    timezone: ZoneInfo | None = ZoneInfo("UTC"),
    global_horizontal_irradiance: ndarray | None = None,
    direct_horizontal_irradiance: ndarray | None = None,
    spectral_factor_series: SpectralFactorSeries = SpectralFactorSeries(
        value=SPECTRAL_FACTOR_DEFAULT
    ),
    temperature_series: numpy.ndarray = numpy.array(TEMPERATURE_DEFAULT),
    wind_speed_series: numpy.ndarray = numpy.array(WIND_SPEED_DEFAULT),
    linke_turbidity_factor_series: LinkeTurbidityFactor = LinkeTurbidityFactor(
        value=LINKE_TURBIDITY_TIME_SERIES_DEFAULT
    ),
    adjust_for_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    # unrefracted_solar_zenith: UnrefractedSolarZenith | None = UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    albedo: float | None = ALBEDO_DEFAULT,
    apply_reflectivity_factor: bool = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_position_model: SolarPositionModel = SOLAR_POSITION_ALGORITHM_DEFAULT,
    sun_horizon_position: List[SunHorizonPositionModel] = SUN_HORIZON_POSITION_DEFAULT,
    solar_incidence_model: SolarIncidenceModel = SolarIncidenceModel.iqbal,
    zero_negative_solar_incidence_angle: bool = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    horizon_profile: DataArray | None = None,
    shading_model: ShadingModel = ShadingModel.pvis,
    shading_states: List[ShadingState] = [ShadingState.all],
    solar_time_model: SolarTimeModel = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_constant: float = SOLAR_CONSTANT,
    eccentricity_phase_offset: float = PERIGEE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    # photovoltaic_module_type: PhotovoltaicModuleType = PhotovoltaicModuleType.Monofacial,  # Leave Me Like This !
    photovoltaic_module: PhotovoltaicModuleModel = PhotovoltaicModuleModel.CSI_FREE_STANDING,
    peak_power: float = PEAK_POWER_DEFAULT,
    system_efficiency: float | None = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: PhotovoltaicModulePerformanceModel = PhotovoltaicModulePerformanceModel.king,
    radiation_cutoff_threshold: float = RADIATION_CUTOFF_THRESHHOLD,
    temperature_model: ModuleTemperatureAlgorithm = ModuleTemperatureAlgorithm.faiman,
    efficiency: float | None = EFFICIENCY_FACTOR_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
    profile: bool = cPROFILE_FLAG_DEFAULT,
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

    global_inclined_irradiance_series = calculate_global_inclined_irradiance(
                longitude=longitude,
                latitude=latitude,
                elevation=elevation,
                surface_orientation=surface_orientation,
                surface_tilt=surface_tilt,
                timestamps=timestamps,
                timezone=timezone,
                global_horizontal_irradiance=global_horizontal_irradiance,  # time series optional
                direct_horizontal_irradiance=direct_horizontal_irradiance,  # time series, optional
                linke_turbidity_factor_series=linke_turbidity_factor_series,
                adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
                # unrefracted_solar_zenith=unrefracted_solar_zenith,
                apply_reflectivity_factor=apply_reflectivity_factor,
                solar_position_model=solar_position_model,
                sun_horizon_position=sun_horizon_position,
                solar_incidence_model=solar_incidence_model,
                zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
                horizon_profile=horizon_profile,
                shading_model=shading_model,
                shading_states=shading_states,
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

    if not power_model:
        if not efficiency:  # user-set  -- RenameMe ?  FIXME
            efficiency_factor_series = system_efficiency
        else:
            efficiency_factor_series = efficiency

    else:
        effective_global_irradiance_series = calculate_spectrally_corrected_effective_irradiance(
            irradiance_series=global_inclined_irradiance_series.value_before_reflectivity,
            spectral_factor_series=spectral_factor_series,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
            fingerprint=fingerprint,
        )
        if efficiency:
            efficiency_factor_series = efficiency
        else:
            efficiency_series = calculate_photovoltaic_efficiency_series(
                irradiance_series=global_inclined_irradiance_series.value,
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
        global_inclined_irradiance_series.value * efficiency_factor_series
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

    # Overwrite the direct irradiance 'components' with the global ones !
    # components = components | calculated_direct_inclined_irradiance_series.components

    if isinstance(
        global_inclined_irradiance_series.direct_horizontal_irradiance,
        DirectHorizontalIrradianceFromExternalData,
    ):
        photovoltaic_power = PhotovoltaicPowerFromExternalData(
            value=photovoltaic_power_output_series,
            photovoltaic_power_without_system_loss=photovoltaic_power_output_without_system_loss_series,
            #
            photovoltaic_module_type=PhotovoltaicModuleType.Monofacial,
            technology=photovoltaic_module.value,
            power_model=power_model.value,
            system_efficiency=system_efficiency,
            efficiency_factor=efficiency_factor_series,
            #
            temperature=temperature_series,
            wind_speed=wind_speed_series,
            #
            effective_global_irradiance=global_inclined_irradiance_series.value
            * efficiency_factor_series,
            effective_direct_irradiance=global_inclined_irradiance_series.direct_inclined_irradiance
            * efficiency_factor_series,
            effective_diffuse_irradiance=global_inclined_irradiance_series.diffuse_inclined_irradiance
            * efficiency_factor_series,
            effective_ground_reflected_irradiance=global_inclined_irradiance_series.ground_reflected_inclined_irradiance
            * efficiency_factor_series,
            spectral_effect=effective_global_irradiance_series.spectral_effect,
            spectral_effect_percentage=effective_global_irradiance_series.spectral_effect_percentage,
            spectral_factor=spectral_factor_series,
            #
            peak_power=peak_power,
            ## Inclined Irradiance Components
            global_inclined_irradiance=global_inclined_irradiance_series.value,
            direct_inclined_irradiance=global_inclined_irradiance_series.direct_inclined_irradiance,
            diffuse_inclined_irradiance=global_inclined_irradiance_series.diffuse_inclined_irradiance,
            ground_reflected_inclined_irradiance=global_inclined_irradiance_series.ground_reflected_inclined_irradiance,
            #
            ## Loss due to Reflectivity
            global_inclined_reflectivity=global_inclined_irradiance_series.reflectivity,
            direct_inclined_reflectivity=global_inclined_irradiance_series.direct_inclined_reflectivity,
            diffuse_inclined_reflectivity=global_inclined_irradiance_series.diffuse_inclined_reflectivity,
            ground_reflected_inclined_reflectivity=global_inclined_irradiance_series.ground_reflected_inclined_reflectivity,
            #
            ## Reflectivity Factor for Irradiance Components
            direct_inclined_reflectivity_factor=global_inclined_irradiance_series.direct_inclined_reflectivity_factor,
            diffuse_inclined_reflectivity_factor=global_inclined_irradiance_series.diffuse_inclined_reflectivity_factor,
            ground_reflected_inclined_reflectivity_factor=global_inclined_irradiance_series.ground_reflected_inclined_reflectivity_factor,
            #
            ## Reflectivity Coefficient which defines the Reflectivity Factor for Irradiance Components
            # direct_inclined_reflectivity_coefficient=direct_inclined_reflectivity_coefficient_series,
            diffuse_inclined_reflectivity_coefficient=global_inclined_irradiance_series.diffuse_inclined_reflectivity_coefficient,
            # ground_reflected_inclined_reflectivity_coefficient=ground_reflected_inclined_reflectivity_coefficient_series,
            #
            ## Inclined Irradiance before loss due to Reflectivity
            global_inclined_before_reflectivity=global_inclined_irradiance_series.value_before_reflectivity,
            direct_inclined_before_reflectivity=global_inclined_irradiance_series.direct_inclined_before_reflectivity,
            diffuse_inclined_before_reflectivity=global_inclined_irradiance_series.diffuse_inclined_before_reflectivity,
            ground_reflected_inclined_before_reflectivity=global_inclined_irradiance_series.ground_reflected_inclined_before_reflectivity,
            #
            ## Horizontal Irradiance Components
            global_horizontal_irradiance=global_horizontal_irradiance,
            direct_horizontal_irradiance=global_inclined_irradiance_series.direct_horizontal_irradiance,
            diffuse_horizontal_irradiance=global_inclined_irradiance_series.diffuse_horizontal_irradiance,
            #
            ## Components of the Extraterrestrial irradiance
            extraterrestrial_horizontal_irradiance=global_inclined_irradiance_series.extraterrestrial_horizontal_irradiance,
            extraterrestrial_normal_irradiance=global_inclined_irradiance_series.extraterrestrial_normal_irradiance,
            linke_turbidity_factor=linke_turbidity_factor_series,
            #
            ## Location and Position
            elevation=elevation,
            surface_orientation=surface_orientation,
            surface_tilt=surface_tilt,
            sun_horizon_positions=global_inclined_irradiance_series.sun_horizon_positions,  # states != sun_horizon_position
            #
            ## Solar Position parameters
            surface_in_shade=global_inclined_irradiance_series.surface_in_shade,
            **generate_dictionary_of_surface_in_shade_series_x(
                global_inclined_irradiance_series.surface_in_shade,
            ),
            solar_incidence=global_inclined_irradiance_series.solar_incidence,
            shading_state=global_inclined_irradiance_series.shading_state,
            sun_horizon_position=global_inclined_irradiance_series.sun_horizon_position,  # positions != sun_horizon_positions
            solar_altitude=global_inclined_irradiance_series.solar_altitude,
            # refracted_solar_altitude=global_inclined_irradiance_series.refracted_solar_altitude,
            solar_azimuth=global_inclined_irradiance_series.solar_azimuth,
            azimuth_origin=global_inclined_irradiance_series.solar_azimuth.origin,
            # azimuth_difference=azimuth_difference_series,
            #
            ## Positioning, Timing and Atmospheric algorithms
            solar_positioning_algorithm=global_inclined_irradiance_series.solar_positioning_algorithm,
            solar_timing_algorithm=global_inclined_irradiance_series.solar_timing_algorithm,
            adjusted_for_atmospheric_refraction=global_inclined_irradiance_series.adjusted_for_atmospheric_refraction,
            solar_incidence_model=global_inclined_irradiance_series.solar_incidence_model,
            solar_incidence_definition=global_inclined_irradiance_series.solar_incidence.definition,
            # azimuth_origin_column_name=getattr(global_inclined_irradiance_series.solar_azimuth_series, 'origin'),
            #     SOLAR_CONSTANT_COLUMN_NAME: solar_constant,
            #     PERIGEE_OFFSET_COLUMN_NAME: eccentricity_phase_offset,
            #     ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME: eccentricity_amplitude,
            shading_algorithm=global_inclined_irradiance_series.shading_algorithm,
            shading_states=shading_states,
            #
            ## Sources
        )
    else:
        photovoltaic_power = PhotovoltaicPower(
            value=photovoltaic_power_output_series,
            photovoltaic_power_without_system_loss=photovoltaic_power_output_without_system_loss_series,
            photovoltaic_module_type=PhotovoltaicModuleType.Monofacial,
            technology=photovoltaic_module.value,
            power_model=power_model.value,
            system_efficiency=system_efficiency,
            efficiency_factor=efficiency_factor_series,
            temperature=temperature_series,
            wind_speed=wind_speed_series,
            effective_global_irradiance=global_inclined_irradiance_series.value * efficiency_factor_series,
            effective_direct_irradiance=global_inclined_irradiance_series.direct_inclined_irradiance * efficiency_factor_series,
            effective_diffuse_irradiance=global_inclined_irradiance_series.diffuse_inclined_irradiance * efficiency_factor_series,
            effective_ground_reflected_irradiance=global_inclined_irradiance_series.ground_reflected_inclined_irradiance * efficiency_factor_series,
            spectral_effect=effective_global_irradiance_series.spectral_effect,
            spectral_effect_percentage=effective_global_irradiance_series.spectral_effect_percentage,
            spectral_factor=spectral_factor_series,
            peak_power=peak_power,
            ## Inclined Irradiance Components
            global_inclined_irradiance=global_inclined_irradiance_series.value,
            direct_inclined_irradiance=global_inclined_irradiance_series.direct_inclined_irradiance,
            diffuse_inclined_irradiance=global_inclined_irradiance_series.diffuse_inclined_irradiance,
            ground_reflected_inclined_irradiance=global_inclined_irradiance_series.ground_reflected_inclined_irradiance,
            #
            ## Loss due to Reflectivity
            global_inclined_reflectivity=global_inclined_irradiance_series.reflectivity,
            direct_inclined_reflectivity=global_inclined_irradiance_series.direct_inclined_reflectivity,
            diffuse_inclined_reflectivity=global_inclined_irradiance_series.diffuse_inclined_reflectivity,
            ground_reflected_inclined_reflectivity=global_inclined_irradiance_series.ground_reflected_inclined_reflectivity,
            #
            ## Reflectivity Factor for Irradiance Components
            direct_inclined_reflectivity_factor=global_inclined_irradiance_series.direct_inclined_reflectivity_factor,
            diffuse_inclined_reflectivity_factor=global_inclined_irradiance_series.diffuse_inclined_reflectivity_factor,
            ground_reflected_inclined_reflectivity_factor=global_inclined_irradiance_series.ground_reflected_inclined_reflectivity_factor,
            #
            ## Reflectivity Coefficient which defines the Reflectivity Factor for Irradiance Components
            # direct_inclined_reflectivity_coefficient=direct_inclined_reflectivity_coefficient_series,
            diffuse_inclined_reflectivity_coefficient=global_inclined_irradiance_series.diffuse_inclined_reflectivity_coefficient,
            # ground_reflected_inclined_reflectivity_coefficient=ground_reflected_inclined_reflectivity_coefficient_series,
            #
            ## Inclined Irradiance before loss due to Reflectivity
            global_inclined_before_reflectivity=global_inclined_irradiance_series.value_before_reflectivity,
            direct_inclined_before_reflectivity=global_inclined_irradiance_series.direct_inclined_before_reflectivity,
            diffuse_inclined_before_reflectivity=global_inclined_irradiance_series.diffuse_inclined_before_reflectivity,
            ground_reflected_inclined_before_reflectivity=global_inclined_irradiance_series.ground_reflected_inclined_before_reflectivity,
            #
            ## Horizontal Irradiance Components
            global_horizontal_irradiance=global_horizontal_irradiance,
            direct_horizontal_irradiance=global_inclined_irradiance_series.direct_horizontal_irradiance,
            diffuse_horizontal_irradiance=global_inclined_irradiance_series.diffuse_horizontal_irradiance,
            #
            ## Components of the Extraterrestrial irradiance
            extraterrestrial_horizontal_irradiance=global_inclined_irradiance_series.extraterrestrial_horizontal_irradiance,
            extraterrestrial_normal_irradiance=global_inclined_irradiance_series.extraterrestrial_normal_irradiance,
            linke_turbidity_factor=linke_turbidity_factor_series,
            #
            ## Location and Position
            elevation=elevation,
            surface_orientation=surface_orientation,
            surface_tilt=surface_tilt,
            sun_horizon_positions=global_inclined_irradiance_series.sun_horizon_positions,  # states != sun_horizon_position
            #
            ## Solar Position parameters
            surface_in_shade=global_inclined_irradiance_series.surface_in_shade,
            **generate_dictionary_of_surface_in_shade_series_x(
                    global_inclined_irradiance_series.surface_in_shade,
            ),
            solar_incidence=global_inclined_irradiance_series.solar_incidence,
            shading_state=global_inclined_irradiance_series.shading_state,
            sun_horizon_position=global_inclined_irradiance_series.sun_horizon_position,  # positions != sun_horizon_positions
            solar_altitude=global_inclined_irradiance_series.solar_altitude,
            # refracted_solar_altitude=global_inclined_irradiance_series.refracted_solar_altitude,
            solar_azimuth=global_inclined_irradiance_series.solar_azimuth,
            azimuth_origin=global_inclined_irradiance_series.solar_azimuth.origin,
            # azimuth_difference=azimuth_difference_series,
            #
            ## Positioning, Timing and Atmospheric algorithms
            solar_positioning_algorithm=global_inclined_irradiance_series.solar_positioning_algorithm,
            solar_timing_algorithm=global_inclined_irradiance_series.solar_timing_algorithm,
            adjusted_for_atmospheric_refraction=global_inclined_irradiance_series.adjusted_for_atmospheric_refraction,
            solar_incidence_model=global_inclined_irradiance_series.solar_incidence_model,
            solar_incidence_definition=global_inclined_irradiance_series.solar_incidence.definition,
            # azimuth_origin_column_name=getattr(global_inclined_irradiance_series.solar_azimuth_series, 'origin'),
            #     SOLAR_CONSTANT_COLUMN_NAME: solar_constant,
            #     PERIGEE_OFFSET_COLUMN_NAME: eccentricity_phase_offset,
            #     ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME: eccentricity_amplitude,
            shading_algorithm=global_inclined_irradiance_series.shading_algorithm,
            shading_states=shading_states,
            #
            ## Sources
        )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    photovoltaic_power.build_output(
        verbose=verbose, fingerprint=fingerprint
    )

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

    return photovoltaic_power
    # return PhotovoltaicPower(
    #     value=photovoltaic_power_output_series,
    #     elevation=elevation,
    #     surface_orientation=surface_orientation,
    #     surface_tilt=surface_tilt,
    #     irradiance=global_inclined_irradiance_series.value,
    #     components=components,
    # )
