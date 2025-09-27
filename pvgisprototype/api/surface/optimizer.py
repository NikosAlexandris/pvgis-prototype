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
from typing import Callable

from pvgisprototype import SurfaceTilt
from numpy import inf, ndarray
from scipy.optimize import Bounds, OptimizeResult, brute, minimize, shgo

from pvgisprototype.api.surface.parameter_models import (
    MINIMIZE_METHODS,
    SurfacePositionOptimizerMethod,
    SurfacePositionOptimizerMethodSHGOSamplingMethod,
    SurfacePositionOptimizerMode,
)
from pvgisprototype.api.surface.recommender import recommend_surface_position
from pvgisprototype.constants import (
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT, 
    NUMBER_OF_SAMPLING_POINTS_SURFACE_POSITION_OPTIMIZATION,
    OPTIMISER_GRADIENT_TOLERANCE,
    VERBOSE_LEVEL_DEFAULT, 
    WORKERS_FOR_SURFACE_POSITION_OPTIMIZATION,
)
from pvgisprototype.log import log_data_fingerprint, logger


def optimizer(
    objective_function_arguments: dict,
    func: Callable,
    method: SurfacePositionOptimizerMethod = SurfacePositionOptimizerMethod.l_bfgs_b,
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
) -> OptimizeResult | ndarray:

    optimal_position = OptimizeResult()
    if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
        logger.debug(
            f"i Estimate optimal positioning",
            alt=f"i [bold]Estimate[/bold] the [magenta]optimal positioning[/magenta]",
        )
    try:
        if method == SurfacePositionOptimizerMethod.shgo:
            optimal_position = shgo(
                func=func,
                bounds=bounds,
                args=(objective_function_arguments, mode),
                n=number_of_sampling_points,
                iters=iterations,
                options={"f_tol": precision_goal, "disp": False},
                sampling_method=sampling_method_shgo,
                workers=workers,
            )
        elif method == SurfacePositionOptimizerMethod.brute:
            optimal_position: ndarray = brute(
                func=func,
                ranges=bounds,
                args=(objective_function_arguments, mode),
                finish=None,
                workers=workers,
            )
        elif method in MINIMIZE_METHODS:
            recommended_surface_position = recommend_surface_position(
                mode=mode,
                latitude=objective_function_arguments["latitude"],
                recommended_surface_tilt=objective_function_arguments["latitude"],
            )
            optimiser_options = {
                "disp": convergence_verbosity,
                "maxiter": iterations,
                "gtol": gradient_tolerance,
                # "return_all": False,
            }
            if mode == SurfacePositionOptimizerMode.Orientation_and_Tilt:
                optimiser_options["norm"] = inf

            optimal_position = minimize(
                # fun=lambda x: func(x, *objective_function_arguments, mode),
                fun=lambda x: func(x, objective_function_arguments, mode),
                x0=recommended_surface_position,  # initial guess
                method=method,
                jac=jacobian,
                bounds=bounds,
                options=optimiser_options,
            )
        else:
            raise ValueError(
                f"At the moment only the methods {MINIMIZE_METHODS} are implemented !"
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
        raise Exception(f"{e}")
