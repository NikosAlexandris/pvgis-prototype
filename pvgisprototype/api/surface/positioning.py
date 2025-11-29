#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
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
from pvgisprototype.api.irradiance.diffuse.clear_sky.horizontal import calculate_clear_sky_diffuse_horizontal_irradiance
from pvgisprototype.api.irradiance.direct.horizontal import calculate_clear_sky_direct_horizontal_irradiance_series
from pvgisprototype.api.irradiance.models import ModuleTemperatureAlgorithm
from pvgisprototype.algorithms.huld.models import PhotovoltaicModulePerformanceModel
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
from pvgisprototype.algorithms.huld.photovoltaic_module import PhotovoltaicModuleModel
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
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    EFFICIENCY_FACTOR_DEFAULT,
    FINGERPRINT_COLUMN_NAME,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    NUMBER_OF_ITERATIONS_DEFAULT,
    NUMBER_OF_SAMPLING_POINTS_SURFACE_POSITION_OPTIMIZATION,
    PEAK_POWER_DEFAULT,
    ECCENTRICITY_PHASE_OFFSET,
    UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
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
from pvgisprototype.log import log_data_fingerprint, log_function_call


def build_surface_position_optimisation_mode(
    surface_orientation,
    surface_tilt,
    mode: SurfacePositionOptimizerMode
):
    """
    """
    surface_position_arguments = {}
    if mode == SurfacePositionOptimizerMode.Tilt:
        surface_position_arguments = {
        'surface_orientation': surface_orientation
        }
    if mode == SurfacePositionOptimizerMode.Orientation:
        surface_position_arguments["surface_tilt"] = surface_tilt

    return surface_position_arguments


@log_function_call
def optimise_surface_position(
    longitude: Longitude,
    latitude: Latitude,
    elevation: float,  # change it to Elevation
    #
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
    #
    timestamps: DatetimeIndex = DatetimeIndex([Timestamp.now(tz="UTC")]),
    timezone: ZoneInfo = ZoneInfo("UTC"),
    #
    global_horizontal_irradiance: ndarray | None = None,
    direct_horizontal_irradiance: ndarray | None = None,
    spectral_factor_series: SpectralFactorSeries = SpectralFactorSeries(
        value=SPECTRAL_FACTOR_DEFAULT
    ),
    temperature_series: TemperatureSeries = TemperatureSeries(
        value=TEMPERATURE_DEFAULT
    ),
    wind_speed_series: WindSpeedSeries = WindSpeedSeries(value=WIND_SPEED_DEFAULT),
    linke_turbidity_factor_series: LinkeTurbidityFactor = LinkeTurbidityFactor(),
    #
    horizon_profile: DataArray | None = None,
    shading_model: ShadingModel = ShadingModel.pvgis,
    shading_states: List[ShadingState] = [ShadingState.all],
    #
    adjust_for_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: float | None = UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    albedo: float | None = ALBEDO_DEFAULT,
    apply_reflectivity_factor: bool = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_position_model: SolarPositionModel = SOLAR_POSITION_ALGORITHM_DEFAULT,
    sun_horizon_position: List[SunHorizonPositionModel] = SUN_HORIZON_POSITION_DEFAULT,
    solar_incidence_model: SolarIncidenceModel = SolarIncidenceModel.iqbal,
    zero_negative_solar_incidence_angle: bool = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    solar_time_model: SolarTimeModel = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_constant: float = SOLAR_CONSTANT,
    #
    eccentricity_phase_offset: float = ECCENTRICITY_PHASE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    #
    photovoltaic_module: PhotovoltaicModuleModel = PhotovoltaicModuleModel.CSI_FREE_STANDING,
    peak_power: float = PEAK_POWER_DEFAULT,
    system_efficiency: float | None = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: PhotovoltaicModulePerformanceModel = PhotovoltaicModulePerformanceModel.king,
    temperature_model: ModuleTemperatureAlgorithm = ModuleTemperatureAlgorithm.faiman,
    efficiency: float | None = EFFICIENCY_FACTOR_DEFAULT,
    #
    mode: SurfacePositionOptimizerMode = SurfacePositionOptimizerMode.Tilt,
    method: SurfacePositionOptimizerMethod = SurfacePositionOptimizerMethod.l_bfgs_b,
    number_of_sampling_points: int = NUMBER_OF_SAMPLING_POINTS_SURFACE_POSITION_OPTIMIZATION,
    iterations: int = NUMBER_OF_ITERATIONS_DEFAULT,
    precision_goal: float = 1e-4,
    shgo_sampling_method=SurfacePositionOptimizerMethodSHGOSamplingMethod.sobol,
    workers: int = WORKERS_FOR_SURFACE_POSITION_OPTIMIZATION,
    #
    angle_output_units: str = ANGLE_OUTPUT_UNITS_DEFAULT,
    #
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    #
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
    #
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
    adjust_for_atmospheric_refraction : bool
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

    # build reusable parameter dictionaries
    coordinates = {
        'longitude': longitude,
        'latitude': latitude,
    }
    location_arguments = build_location_dictionary(
        **coordinates,
        elevation=elevation,
    )
    time = {
        'timestamps': timestamps,
        'timezone': timezone,
    }
    horizontal_irradiance = {
        'global_horizontal_irradiance': global_horizontal_irradiance,
        'direct_horizontal_irradiance': direct_horizontal_irradiance,
    }
    irradiance_parameters = {
        **horizontal_irradiance,
        'spectral_factor_series': spectral_factor_series,
        'solar_constant': solar_constant,
            }
    meteorological_variables = {
        'temperature_series':temperature_series,
        'wind_speed_series': wind_speed_series,
    }
    solar_positioning = {
        'solar_position_model': solar_position_model,
        'adjust_for_atmospheric_refraction': adjust_for_atmospheric_refraction,
        'solar_time_model': solar_time_model,
    }
    shading_parameters = {
        'horizon_profile': horizon_profile,
        'shading_model': shading_model,
        'shading_states': shading_states,
    }
    solar_incidence_parameters = {
        'solar_incidence_model': solar_incidence_model,
        'zero_negative_solar_incidence_angle': zero_negative_solar_incidence_angle,
    }
    photovoltaic_performance_parameters = {
        'photovoltaic_module': photovoltaic_module,
        'peak_power': peak_power,
        'system_efficiency': system_efficiency,
        'power_model': power_model,
        'temperature_model': temperature_model,
        'efficiency': efficiency,
    }
    earth_orbit = {
        'eccentricity_phase_offset': eccentricity_phase_offset,
        'eccentricity_amplitude': eccentricity_amplitude,
    }
    array_parameters = {
        "dtype": dtype,
        "array_backend": array_backend,
    }
    output_parameters = {
        'verbose': verbose,
        'log': log,
    }
    surface_positioning_arguments = build_surface_position_optimisation_mode(
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        mode=mode,
    )
    surface_properties = {
        'albedo': albedo,
    }
    # ------------------------------------------
    # spectral,
    # 
    #, linke, apply atmospheric refraction
    # ------------------------------------------

    if not isinstance(global_horizontal_irradiance, ndarray) and not isinstance(
        direct_horizontal_irradiance, ndarray
    ):
        direct_horizontal_irradiance = calculate_clear_sky_direct_horizontal_irradiance_series(
            # longitude=longitude,  # required by some of the solar time algorithms
            **location_arguments,
            **time,
            **solar_positioning,
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            # unrefracted_solar_zenith=unrefracted_solar_zenith,
            solar_constant=solar_constant,
            **earth_orbit,
            horizon_profile=horizon_profile,
            shading_model=shading_model,
            **array_parameters,
            # validate_output=validate_output,
            **output_parameters,
            fingerprint=fingerprint,
        )
        diffuse_horizontal_irradiance = calculate_clear_sky_diffuse_horizontal_irradiance(
                **coordinates,
                **time,
                linke_turbidity_factor_series=linke_turbidity_factor_series,
                **solar_positioning,
                # unrefracted_solar_zenith=unrefracted_solar_zenith,
                solar_constant=solar_constant,
                **earth_orbit,
                **array_parameters,
                **output_parameters,
                fingerprint=fingerprint,
        )
        global_horizontal_irradiance = (
            direct_horizontal_irradiance.value
            + diffuse_horizontal_irradiance.value
        )

    other_input_arguments = build_other_input_arguments_dictionary(
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        # refracted_solar_zenith=refracted_solar_zenith,
        apply_reflectivity_factor=apply_reflectivity_factor,
        sun_horizon_position=sun_horizon_position,
        #
    )
    objective_function_arguments = (
        location_arguments
        | time
        | irradiance_parameters
        | meteorological_variables
        | solar_positioning
        | surface_positioning_arguments
        | surface_properties
        | shading_parameters
        | solar_incidence_parameters
        | photovoltaic_performance_parameters
        | earth_orbit
        | other_input_arguments
        | output_parameters
    )
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
        shgo_sampling_method=shgo_sampling_method,
        workers=workers,
        **output_parameters,
    )
    # optimal_position = build_optimiser_output(
    optimal_position, _optimal_surface_position = build_optimiser_output(
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

    return optimal_position, _optimal_surface_position
