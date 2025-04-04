from math import radians
from pvgisprototype import SurfaceOrientation
from numpy import ndarray, rec
from xarray import DataArray

from pvgisprototype import (
    TemperatureSeries,
    WindSpeedSeries,
    SpectralFactorSeries,
    LinkeTurbidityFactor,
    SurfaceTilt,
)
from scipy.optimize import brute, minimize, shgo, Bounds
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.series.models import MethodForInexactMatches
from pvgisprototype.api.surface.parameter_models import (
    SurfacePositionOptimizerMethod,
    SurfacePositionOptimizerMethodSHGOSamplingMethod,
    SurfacePositionOptimizerMode,
)
from pvgisprototype.api.position.models import ShadingModel
from typing import Callable

from pvgisprototype.constants import (
    IN_MEMORY_FLAG_DEFAULT, 
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT, 
    MASK_AND_SCALE_FLAG_DEFAULT,
    SPECTRAL_FACTOR_DEFAULT, 
    TEMPERATURE_DEFAULT, 
    TOLERANCE_DEFAULT, 
    WIND_SPEED_DEFAULT, 
    WORKERS_FOR_SURFACE_POSITION_OPTIMIZATION,
    NUMBER_OF_SAMPLING_POINTS_SURFACE_POSITION_OPTIMIZATION
)


def build_initial_guess(
    mode: SurfacePositionOptimizerMode,
    recommended_surface_tilt: float,
    recommended_surface_orientation: SurfaceOrientation = SurfaceOrientation(
        value=radians(180), unit="radians"
    ),  # SurfaceOrientation().default_radians
):
    """
    """
    if mode == SurfacePositionOptimizerMode.Tilt:
        # initial guess for surface tilt !
        return recommended_surface_tilt

    if mode == SurfacePositionOptimizerMode.Orientation:
        # initial guess for surface orientation
        return recommended_surface_orientation.radians
    
    if mode == SurfacePositionOptimizerMode.Tilt_and_Orientation:
        return [
                recommended_surface_orientation.radians,
                recommended_surface_tilt,
                ]


def optimizer(
    location_parameters: dict,
    func: Callable,
    global_horizontal_irradiance: ndarray | None = None,
    direct_horizontal_irradiance: ndarray | None = None,
    spectral_factor_series: SpectralFactorSeries = SpectralFactorSeries(value=SPECTRAL_FACTOR_DEFAULT),
    temperature_series: TemperatureSeries = TemperatureSeries(value=TEMPERATURE_DEFAULT),
    wind_speed_series: WindSpeedSeries = WindSpeedSeries(value=WIND_SPEED_DEFAULT),
    neighbor_lookup: MethodForInexactMatches = MethodForInexactMatches.nearest,
    tolerance: float | None = TOLERANCE_DEFAULT,
    mask_and_scale: bool = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: bool = IN_MEMORY_FLAG_DEFAULT,
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
    workers: int = WORKERS_FOR_SURFACE_POSITION_OPTIMIZATION,
    sampling_method_shgo: SurfacePositionOptimizerMethodSHGOSamplingMethod = SurfacePositionOptimizerMethodSHGOSamplingMethod.sobol,
):
    """
    """
    if method == SurfacePositionOptimizerMethod.shgo:
        result = shgo(
            func=func,
            bounds=bounds,
            args=(
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
                ),
            n=number_of_sampling_points,
            iters=iterations,
            options={"f_tol": precision_goal, "disp": False},
            sampling_method=sampling_method_shgo,
            workers = workers,
        )
        if not result['success']:
            raise ValueError(f"Failed to optimize... : {str(result['message'])}")

    if method == SurfacePositionOptimizerMethod.brute:
        result = brute(
            func=func,
            ranges=bounds,
            args=(
                location_parameters,
                global_horizontal_irradiance,
                direct_horizontal_irradiance,
                spectral_factor_series,
                temperature_series,
                wind_speed_series,
                neighbor_lookup,
                tolerance,
                mask_and_scale,
                in_memory,
                horizon_profile,
                shading_model,
                linke_turbidity_factor_series,
                photovoltaic_module,
                mode,
                ),
            finish=None,
            workers=workers,
        )
    if method == SurfacePositionOptimizerMethod.cg:
        initial_guess = build_initial_guess(
            mode=mode,
            recommended_surface_tilt=location_parameters["latitude"],
        )
        args = (
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
        result = minimize(
            fun=lambda x: func(x, *args),
            x0=initial_guess,
            method="CG",
            jac="2-point",
            bounds=bounds,
            options={"maxiter": iterations, "disp": False, "return_all": False},
        )

    else:
        print(f"At the moment only the methods {SurfacePositionOptimizerMethod.shgo}, {SurfacePositionOptimizerMethod.brute}, {SurfacePositionOptimizerMethod.cg} are implemented !")# watch out for when the method passed is not shgo or brute. FIX THIS
    
    return result
