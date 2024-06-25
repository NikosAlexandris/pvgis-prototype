from pvgisprototype import SurfaceOrientation, SurfaceTilt
from scipy import optimize
from pvgisprototype.api.surface.helper_functions import (
    OptimizerMethod,
    OptimizerMode,
    calculate_mean_negative_power_output,
)
from typing import Callable


def optimizer(
    location_parameters: dict,
    func: Callable,
    method: OptimizerMethod = OptimizerMethod.shgo,
    iterations: int = 100,
    mode: OptimizerMode = OptimizerMode.tilt,
    bounds: optimize.Bounds = optimize.Bounds(
        lb=SurfaceTilt().min_radians, ub=SurfaceTilt().max_radians
    ),
    workers: int = 1,
    sampling_method_shgo: str = "sobol",
):
    if method == OptimizerMethod.shgo:
        result = optimize.shgo(
            func=func,
            bounds=bounds,
            n=iterations,
            args=(location_parameters, mode),
            sampling_method=sampling_method_shgo,
            workers=workers,
            options={"disp": True},
        )

    if method == OptimizerMethod.brute:
        result = optimize.brute(
            func=func,
            ranges=bounds,
            args=(location_parameters, mode),
            finish=None,
            workers=workers,
        )
    else:
        # watch out for when the method passed is not shgo or brute. FIX THIS
        pass
    return result
