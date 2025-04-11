from math import radians
from typing import List

from zoneinfo import ZoneInfo
from numpy import ndarray
from pandas import DatetimeIndex, Timestamp
from xarray import DataArray
from scipy.optimize import OptimizeResult

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
from pvgisprototype.constants import (
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    SPECTRAL_FACTOR_DEFAULT,
    TEMPERATURE_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    WIND_SPEED_DEFAULT,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    WORKERS_FOR_SURFACE_POSITION_OPTIMIZATION,
    FINGERPRINT_COLUMN_NAME,
    ANGLE_OUTPUT_UNITS_DEFAULT,
    NUMBER_OF_SAMPLING_POINTS_SURFACE_POSITION_OPTIMIZATION,
    NUMBER_OF_ITERATIONS_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    ALBEDO_DEFAULT,
    ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    SOLAR_CONSTANT,
    PERIGEE_OFFSET,
    ECCENTRICITY_CORRECTION_FACTOR,
    PEAK_POWER_DEFAULT,
    SYSTEM_EFFICIENCY_DEFAULT,
    EFFICIENCY_FACTOR_DEFAULT,
)

from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.surface.power import calculate_mean_negative_photovoltaic_power_output
from pvgisprototype.api.surface.parameters import build_location_dictionary, build_other_input_arguments_dictionary
from pvgisprototype.api.surface.output import build_optimiser_output
from pvgisprototype.api.surface.parameter_models import (
    SurfacePositionOptimizerMethod,
    SurfacePositionOptimizerMethodSHGOSamplingMethod,
    SurfacePositionOptimizerMode,
)
from pvgisprototype.api.surface.optimizer import optimizer
from pvgisprototype.api.surface.optimizer_bounds import define_optimiser_bounds
from pvgisprototype.api.position.models import (
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SOLAR_TIME_ALGORITHM_DEFAULT,
    SUN_HORIZON_POSITION_DEFAULT,    
    ShadingModel,
    ShadingState,
    SolarPositionModel,
    SunHorizonPositionModel,
    SolarIncidenceModel,
    SolarTimeModel,

)
from pvgisprototype.api.irradiance.models import (
    ModuleTemperatureAlgorithm,
)
from pvgisprototype.api.performance.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.core.hashing import generate_hash
from pvgisprototype.log import logger, log_function_call, log_data_fingerprint


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
    timestamps: DatetimeIndex | None = DatetimeIndex([Timestamp.now(tz='UTC')]),
    timezone: ZoneInfo = ZoneInfo('UTC'),
    global_horizontal_irradiance: ndarray | None = None,
    direct_horizontal_irradiance: ndarray | None = None,
    spectral_factor_series: SpectralFactorSeries = SpectralFactorSeries(value=SPECTRAL_FACTOR_DEFAULT),
    temperature_series: TemperatureSeries = TemperatureSeries(value=TEMPERATURE_DEFAULT),
    wind_speed_series: WindSpeedSeries = WindSpeedSeries(value=WIND_SPEED_DEFAULT),
    linke_turbidity_factor_series: LinkeTurbidityFactor = LinkeTurbidityFactor(value=LINKE_TURBIDITY_TIME_SERIES_DEFAULT),
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
    method: SurfacePositionOptimizerMethod = SurfacePositionOptimizerMethod.shgo,
    number_of_sampling_points: int = NUMBER_OF_SAMPLING_POINTS_SURFACE_POSITION_OPTIMIZATION,
    iterations: int = NUMBER_OF_ITERATIONS_DEFAULT,
    precision_goal: float = 1e-4,
    sampling_method_shgo = SurfacePositionOptimizerMethodSHGOSamplingMethod.sobol,
    workers: int = WORKERS_FOR_SURFACE_POSITION_OPTIMIZATION,
    angle_output_units: str = ANGLE_OUTPUT_UNITS_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
):
    """
    """
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

    arguments = location_arguments | other_input_arguments

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
        arguments=arguments,
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
        arguments=arguments,
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
    return optimal_position
