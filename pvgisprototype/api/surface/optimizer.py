from numpy import inf
from pvgisprototype.log import logger
from numpy import ndarray
from xarray import DataArray

from pvgisprototype import (
    TemperatureSeries,
    WindSpeedSeries,
    SpectralFactorSeries,
    LinkeTurbidityFactor,
    SurfaceTilt,
)
from scipy.optimize import OptimizeResult, brute, minimize, shgo, Bounds
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.series.models import MethodForInexactMatches
from pvgisprototype.api.surface.parameter_models import (
    MINIMIZE_METHODS,
    SurfacePositionOptimizerMethod,
    SurfacePositionOptimizerMethodSHGOSamplingMethod,
    SurfacePositionOptimizerMode,
)
from pvgisprototype.api.position.models import ShadingModel
from typing import Callable

from pvgisprototype.constants import (
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    IN_MEMORY_FLAG_DEFAULT, 
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT, 
    MASK_AND_SCALE_FLAG_DEFAULT,
    OPTIMISER_GRADIENT_TOLERANCE,
    SPECTRAL_FACTOR_DEFAULT, 
    TEMPERATURE_DEFAULT, 
    TOLERANCE_DEFAULT,
    VERBOSE_LEVEL_DEFAULT, 
    WIND_SPEED_DEFAULT, 
    WORKERS_FOR_SURFACE_POSITION_OPTIMIZATION,
    NUMBER_OF_SAMPLING_POINTS_SURFACE_POSITION_OPTIMIZATION
)
from pvgisprototype.log import log_data_fingerprint
from pvgisprototype.api.surface.recommender import recommend_surface_position


def optimizer(
    location_parameters: dict,
    func: Callable,
    global_horizontal_irradiance: ndarray | None = None,
    direct_horizontal_irradiance: ndarray | None = None,
    spectral_factor_series: SpectralFactorSeries = SpectralFactorSeries(value=SPECTRAL_FACTOR_DEFAULT),
    temperature_series: TemperatureSeries = TemperatureSeries(value=TEMPERATURE_DEFAULT),
    wind_speed_series: WindSpeedSeries = WindSpeedSeries(value=WIND_SPEED_DEFAULT),
    horizon_profile: DataArray | None = None,
    shading_model: ShadingModel = ShadingModel.pvis,    
    photovoltaic_module: PhotovoltaicModuleModel = PhotovoltaicModuleModel.CSI_FREE_STANDING, 
    linke_turbidity_factor_series: LinkeTurbidityFactor = LinkeTurbidityFactor(value = LINKE_TURBIDITY_TIME_SERIES_DEFAULT),
    method: SurfacePositionOptimizerMethod = SurfacePositionOptimizerMethod.shgo,
    number_of_sampling_points: int = NUMBER_OF_SAMPLING_POINTS_SURFACE_POSITION_OPTIMIZATION,
    iterations: int = 100,
    precision_goal: float = 1e-4,
    mode: SurfacePositionOptimizerMode = SurfacePositionOptimizerMode.Tilt,
    bounds: tuple | Bounds = Bounds(
        lb=SurfaceTilt().min_radians, ub=SurfaceTilt().max_radians
    ),
    jacobian: str | bool = "2-point",
    convergence_verbosity: bool = False,
    gradient_tolerance: float = OPTIMISER_GRADIENT_TOLERANCE,
    workers: int = WORKERS_FOR_SURFACE_POSITION_OPTIMIZATION,
    sampling_method_shgo: SurfacePositionOptimizerMethodSHGOSamplingMethod = SurfacePositionOptimizerMethodSHGOSamplingMethod.sobol,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> OptimizeResult:
    """
    """
    optimal_position = OptimizeResult()
    objective_function_arguments = (
        location_parameters,
        global_horizontal_irradiance,
        direct_horizontal_irradiance,
        spectral_factor_series,
        temperature_series,
        wind_speed_series,
        horizon_profile,
        shading_model,
        linke_turbidity_factor_series,
        photovoltaic_module,
        mode,
    )
    if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
        logger.info(
            f"i Estimate optimal positioning",
            alt=f"i [bold]Estimate[/bold] the [magenta]optimal positioning[/magenta]"
        )
    try:
        print(f"Method : {method}")
        if method == SurfacePositionOptimizerMethod.shgo:
            optimal_position = shgo(
                func=func,
                bounds=bounds,
                args=objective_function_arguments,
                n=number_of_sampling_points,
                iters=iterations,
                options={"f_tol": precision_goal, "disp": False},
                sampling_method=sampling_method_shgo,
                workers = workers,
            )
        elif method == SurfacePositionOptimizerMethod.brute:
            optimal_position = brute(
                func=func,
                ranges=bounds,
                args=objective_function_arguments,
                finish=None,
                workers=workers,
            )
        elif method in MINIMIZE_METHODS:
            recommended_surface_position = recommend_surface_position(
                mode=mode,
                latitude=location_parameters['latitude'],
                recommended_surface_tilt=location_parameters["latitude"],
            )
            optimiser_options = {
                "disp": convergence_verbosity,
                "maxiter": iterations,
                "gtol": gradient_tolerance,
                "return_all": False,
            }
            if mode == SurfacePositionOptimizerMode.Orientation_and_Tilt:
                optimiser_options["norm"] = inf
            optimal_position = minimize(
                fun=lambda x: func(x, *objective_function_arguments, mode),
                x0=recommended_surface_position,  # initial guess
                method=method,
                jac=jacobian,
                # bounds=bounds,
                options=optimiser_options,
            )
        else:
            print(
                f"At the moment only the methods {SurfacePositionOptimizerMethod.shgo}, {SurfacePositionOptimizerMethod.brute}, {SurfacePositionOptimizerMethod.cg} are implemented !"
            )  # watch out for when the method passed is not shgo or brute. FIX THIS

        if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
            from devtools import debug
            debug(locals())

        log_data_fingerprint(
            data=optimal_position,
            log_level=log,
            hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
        )

        return optimal_position

    except Exception as e:
        # if not optimal_position['success']:
        #     raise ValueError(f"Failed to optimize... : {str(optimal_position['message'])}")
        print(f"Exception : {e}")
