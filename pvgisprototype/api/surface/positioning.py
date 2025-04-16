from math import radians
from typing import List
from zoneinfo import ZoneInfo

from numpy import ndarray
from pandas import DatetimeIndex, Timestamp
from scipy.optimize import OptimizeResult
from xarray import DataArray

from pvgisprototype import (
    Latitude,
    LinkeTurbidityFactor,
    Longitude,
    SpectralFactorSeries,
    SurfaceOrientation,
    SurfaceTilt,
    TemperatureSeries,
    WindSpeedSeries,
)
from pvgisprototype.api.irradiance.models import ModuleTemperatureAlgorithm
from pvgisprototype.api.performance.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.api.position.models import (
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SOLAR_TIME_ALGORITHM_DEFAULT,
    SUN_HORIZON_POSITION_DEFAULT,
    ShadingModel,
    ShadingState,
    SolarIncidenceModel,
    SolarPositionModel,
    SolarTimeModel,
    SunHorizonPositionModel,
)
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.surface.optimizer import optimizer
from pvgisprototype.api.surface.optimizer_bounds import define_optimiser_bounds
from pvgisprototype.api.surface.output import build_optimiser_output
from pvgisprototype.api.surface.parameter_models import (
    SurfacePositionOptimizerMethod,
    SurfacePositionOptimizerMethodSHGOSamplingMethod,
    SurfacePositionOptimizerMode,
)
from pvgisprototype.api.surface.parameters import (
    build_location_dictionary,
    build_other_input_arguments_dictionary,
)
from pvgisprototype.api.surface.power import (
    calculate_mean_negative_photovoltaic_power_output,
)
from pvgisprototype.constants import (
    ALBEDO_DEFAULT,
    ANGLE_OUTPUT_UNITS_DEFAULT,
    ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    EFFICIENCY_FACTOR_DEFAULT,
    FINGERPRINT_COLUMN_NAME,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    NUMBER_OF_ITERATIONS_DEFAULT,
    NUMBER_OF_SAMPLING_POINTS_SURFACE_POSITION_OPTIMIZATION,
    PEAK_POWER_DEFAULT,
    PERIGEE_OFFSET,
    REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    SOLAR_CONSTANT,
    SPECTRAL_FACTOR_DEFAULT,
    SYSTEM_EFFICIENCY_DEFAULT,
    TEMPERATURE_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    WIND_SPEED_DEFAULT,
    WORKERS_FOR_SURFACE_POSITION_OPTIMIZATION,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    cPROFILE_FLAG_DEFAULT,
)
from pvgisprototype.core.hashing import generate_hash
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger


@log_function_call
def optimise_surface_position(
    longitude: Longitude,
    latitude: Latitude,
    elevation: float,  # change it to Elevation
    surface_orientation: SurfaceOrientation = SurfaceOrientation(
        value=radians(180), unit="radians"
    ),  # SurfaceOrientation().default_radians
    surface_tilt: SurfaceTilt = SurfaceTilt(
        value=radians(45), unit="radians"
    ),  # SurfaceTilt().default_radians
    min_surface_orientation: float = SurfaceOrientation().min_radians,
    max_surface_orientation: float = SurfaceOrientation().max_radians,
    min_surface_tilt: float = SurfaceTilt().min_radians,
    max_surface_tilt: float = SurfaceTilt().max_radians,
    timestamps: DatetimeIndex | None = DatetimeIndex([Timestamp.now(tz="UTC")]),
    timezone: ZoneInfo = ZoneInfo("UTC"),
    global_horizontal_irradiance: ndarray | None = None,
    direct_horizontal_irradiance: ndarray | None = None,
    spectral_factor_series: SpectralFactorSeries = SpectralFactorSeries(
        value=SPECTRAL_FACTOR_DEFAULT
    ),
    temperature_series: TemperatureSeries = TemperatureSeries(
        value=TEMPERATURE_DEFAULT
    ),
    wind_speed_series: WindSpeedSeries = WindSpeedSeries(value=WIND_SPEED_DEFAULT),
    linke_turbidity_factor_series: LinkeTurbidityFactor = LinkeTurbidityFactor(
        value=LINKE_TURBIDITY_TIME_SERIES_DEFAULT
    ),
    horizon_profile: DataArray | None = None,
    shading_model: ShadingModel = ShadingModel.pvis,
    shading_states: List[ShadingState] = [ShadingState.all],
    photovoltaic_module: PhotovoltaicModuleModel = PhotovoltaicModuleModel.CSI_FREE_STANDING,
    apply_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: float | None = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    albedo: float | None = ALBEDO_DEFAULT,
    apply_reflectivity_factor: bool = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_position_model: SolarPositionModel = SOLAR_POSITION_ALGORITHM_DEFAULT,
    sun_horizon_position: List[SunHorizonPositionModel] = SUN_HORIZON_POSITION_DEFAULT,
    solar_incidence_model: SolarIncidenceModel = SolarIncidenceModel.iqbal,
    zero_negative_solar_incidence_angle: bool = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    solar_time_model: SolarTimeModel = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    peak_power: float = PEAK_POWER_DEFAULT,
    system_efficiency: float | None = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: PhotovoltaicModulePerformanceModel = PhotovoltaicModulePerformanceModel.king,
    temperature_model: ModuleTemperatureAlgorithm = ModuleTemperatureAlgorithm.faiman,
    efficiency: float | None = EFFICIENCY_FACTOR_DEFAULT,
    mode: SurfacePositionOptimizerMode = SurfacePositionOptimizerMode.Tilt,
    method: SurfacePositionOptimizerMethod = SurfacePositionOptimizerMethod.l_bfgs_b,
    number_of_sampling_points: int = NUMBER_OF_SAMPLING_POINTS_SURFACE_POSITION_OPTIMIZATION,
    iterations: int = NUMBER_OF_ITERATIONS_DEFAULT,
    precision_goal: float = 1e-4,
    sampling_method_shgo=SurfacePositionOptimizerMethodSHGOSamplingMethod.sobol,
    workers: int = WORKERS_FOR_SURFACE_POSITION_OPTIMIZATION,
    angle_output_units: str = ANGLE_OUTPUT_UNITS_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
    profile: bool = cPROFILE_FLAG_DEFAULT,
):
    """
    This function optimizes the position of a surface.

    Parameters
    ----------
    longitude : float
        The longitude of the location.
    latitude : float
        The latitude of the location.
    elevation : float
        The elevation of the location.
    surface_orientation : SurfaceOrientation
        The orientation of the surface.
    surface_tilt : SurfaceTilt
        The tilt of the surface.
    min_surface_orientation : float
        The minimum orientation of the surface allowed.
    max_surface_orientation : float
        The maximum orientation of the surface allowed.
    min_surface_tilt : float
        The minimum tilt of the surface allowed.
    max_surface_tilt : float
        The maximum tilt of the surface allowed.
    timestamps : DatetimeIndex | None
        The timestamps to use for the optimisation.
    timezone : ZoneInfo
        The timezone to use for the optimisation.
    global_horizontal_irradiance : ndarray | None
        The global horizontal irradiance.
    direct_horizontal_irradiance : ndarray | None
        The direct horizontal irradiance.
    spectral_factor_series : SpectralFactorSeries
        The spectral factor series.
    temperature_series : TemperatureSeries
        The temperature series.
    wind_speed_series : WindSpeedSeries
        The wind speed series.
    linke_turbidity_factor_series : LinkeTurbidityFactor
        The Linke turbidity factor series.
    horizon_profile : DataArray | None
        The horizon profile.
    shading_model : ShadingModel
        The shading model.
    shading_states : List[ShadingState]
        The shading states.
    photovoltaic_module : PhotovoltaicModuleModel
        The photovoltaic module.
    apply_atmospheric_refraction : bool
        Whether to apply atmospheric refraction.
    refracted_solar_zenith : float | None
        The refracted solar zenith angle.
    albedo : float | None
        The albedo.
    apply_reflectivity_factor : bool
        Whether to apply the reflectivity factor.
    solar_position_model : SolarPositionModel
        The solar position model.
    sun_horizon_position : List[SunHorizonPositionModel]
        The sun horizon position.
    solar_incidence_model : SolarIncidenceModel
        The solar incidence model.
    zero_negative_solar_incidence_angle : bool
        Whether to zero negative solar incidence angles.
    solar_time_model : SolarTimeModel
        The solar time model.
    solar_constant : float
        The solar constant.
    perigee_offset : float
        The perigee offset.
    eccentricity_correction_factor : float
        The eccentricity correction factor.
    peak_power : float
        The peak power of the photovoltaic module.
    system_efficiency : float | None
        The system efficiency.
    power_model : PhotovoltaicModulePerformanceModel
        The power model.
    temperature_model : ModuleTemperatureAlgorithm
        The temperature model.
    efficiency : float | None
        The efficiency factor.
    mode : SurfacePositionOptimizerMode
        The optimization mode. Available options are `Tilt`, `Orientation` and `Orientation & Tilt`.
    method : SurfacePositionOptimizerMethod
        The optimization method. Multiple options are supported including L-BFGS-B, SHGO, CG.
    number_of_sampling_points : int
        The number of sampling points.
    iterations : int
        The number of iterations.
    precision_goal : float
        The precision goal.
    sampling_method_shgo : SurfacePositionOptimizerMethodSHGOSamplingMethod
        The sampling method for the SHGO optimizer.
    workers : int
        The number of workers.
    angle_output_units : str
        The unit of the angle output.
    verbose : int
        The verbosity level.
    log : int
        The log level.
    fingerprint : bool
        Whether to fingerprint the data.
    profile : bool
        Whether to profile the function.

    Returns
    -------
    optimiser_output : OptimizeResult | ndarray
        The optimal surface position.
    """
    if profile:
        import cProfile

        pr = cProfile.Profile()
        pr.enable()

    location_arguments = build_location_dictionary(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamps=timestamps,
        timezone=timezone,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        verbose=verbose,
        mode=mode,
    )

    # NOTE Fix me split me thematically!
    # ------------------------------------------
    # horizontal irradiance components, spectral,
    # meteorological variables, linke, apply atmospheric refraction
    # ------------------------------------------
    other_input_arguments = build_other_input_arguments_dictionary(
        global_horizontal_irradiance=global_horizontal_irradiance,
        direct_horizontal_irradiance=direct_horizontal_irradiance,
        spectral_factor_series=spectral_factor_series,
        photovoltaic_module=photovoltaic_module,
        temperature_series=temperature_series,
        wind_speed_series=wind_speed_series,
        horizon_profile=horizon_profile,
        shading_model=shading_model,
        shading_states=shading_states,
        albedo=albedo,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        apply_reflectivity_factor=apply_reflectivity_factor,
        solar_position_model=solar_position_model,
        sun_horizon_position=sun_horizon_position,
        solar_incidence_model=solar_incidence_model,
        zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
        solar_time_model=solar_time_model,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        peak_power=peak_power,
        system_efficiency=system_efficiency,
        power_model=power_model,
        temperature_model=temperature_model,
        efficiency=efficiency,
        verbose=verbose,
    )

    objective_function_arguments = location_arguments | other_input_arguments

    bounds = define_optimiser_bounds(
        min_surface_orientation=min_surface_orientation,
        max_surface_orientation=max_surface_orientation,
        min_surface_tilt=min_surface_tilt,
        max_surface_tilt=max_surface_tilt,
        mode=mode,
        method=method,
        verbose=verbose,
    )
    optimal_angles: OptimizeResult | ndarray = optimizer(
        objective_function_arguments=objective_function_arguments,
        func=calculate_mean_negative_photovoltaic_power_output,
        method=method,
        mode=mode,
        bounds=bounds,
        number_of_sampling_points=number_of_sampling_points,
        iterations=iterations,
        precision_goal=precision_goal,
        sampling_method_shgo=sampling_method_shgo,
        workers=workers,
        verbose=verbose,
        log=log,
    )
    optimal_position = build_optimiser_output(
        optimiser_output=optimal_angles,
        objective_function_arguments=objective_function_arguments,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        solar_time_model=solar_time_model,
        mode=mode,
        method=method,
        angle_output_units=angle_output_units,
        verbose=verbose,
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        from devtools import debug

        debug(locals())

    log_data_fingerprint(
        data=optimal_position,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    if fingerprint:
        optimal_position[FINGERPRINT_COLUMN_NAME] = generate_hash(optimal_position)

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

    return optimal_position
