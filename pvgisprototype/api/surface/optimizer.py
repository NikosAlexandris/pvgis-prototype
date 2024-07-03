from typing import Callable

from scipy import optimize

from pvgisprototype import SurfaceTilt
from pvgisprototype.api.surface.parameter_models import (
    SurfacePositionOptimizerMethod,
    SurfacePositionOptimizerMode,
)


def optimizer(
    location_parameters: dict,
    func: Callable,
    method: SurfacePositionOptimizerMethod = SurfacePositionOptimizerMethod.shgo,
    iterations: int = 100,
    mode: SurfacePositionOptimizerMode = SurfacePositionOptimizerMode.Tilt,
    bounds: optimize.Bounds = optimize.Bounds(
        lb=SurfaceTilt().min_radians, ub=SurfaceTilt().max_radians
    ),
    workers: int = 1,
    sampling_method_shgo: str = "sobol",
):
    if method == SurfacePositionOptimizerMethod.shgo:
        result = optimize.shgo(
            func=func,
            bounds=bounds,
            n=iterations,
            args=(location_parameters, mode),
            sampling_method=sampling_method_shgo,
            workers=workers,
            options={"disp": True},
        )

    if method == SurfacePositionOptimizerMethod.brute:
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
