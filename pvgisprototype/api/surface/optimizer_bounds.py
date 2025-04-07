from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.log import logger
from math import radians
from scipy.optimize import Bounds
from pvgisprototype.api.surface.parameter_models import (
    SurfacePositionOptimizerMethod,
    SurfacePositionOptimizerMode,
)


def define_optimiser_bounds(
    min_surface_orientation,
    max_surface_orientation,
    min_surface_tilt,
    max_surface_tilt,
    mode,
    method,
    verbose,
) -> tuple | Bounds:
    """ """
    brute_force_precision = radians(1)
    surface_orientation_range = slice(
        min_surface_orientation, max_surface_orientation, brute_force_precision
    )
    surface_tilt_range = slice(
        min_surface_tilt, max_surface_tilt, brute_force_precision
    )

    if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
        logger.info(
            f"i Define bounds for the \'{method}\' optimiser ..",
            alt=f"i [bold]Define[/bold] bounds for the [magenta]{method}[/magenta] optimiser .."
        )

    if method == SurfacePositionOptimizerMethod.brute:
        return (
            (surface_orientation_range, surface_tilt_range)
            if mode == SurfacePositionOptimizerMode.Orientation_and_Tilt
            else (
                (
                    surface_tilt_range
                    if mode == SurfacePositionOptimizerMode.Tilt
                    else surface_orientation_range
                ),
            )
        )

    if mode == SurfacePositionOptimizerMode.Tilt:
        return Bounds(lb=surface_tilt_range.start, ub=surface_tilt_range.stop)

    if mode == SurfacePositionOptimizerMode.Orientation:
        return Bounds(
            lb=surface_orientation_range.start, ub=surface_orientation_range.stop
        )

    if mode == SurfacePositionOptimizerMode.Orientation_and_Tilt:
        return Bounds(
            lb=[surface_orientation_range.start, surface_tilt_range.start],
            ub=[surface_orientation_range.stop, surface_tilt_range.stop],
        )

    raise ValueError("Invalid mode provided.")
