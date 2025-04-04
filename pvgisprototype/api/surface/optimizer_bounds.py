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
) -> tuple | Bounds:
    """ """
    brute_force_precision = radians(1)
    surface_orientation_range = slice(
        min_surface_orientation, max_surface_orientation, brute_force_precision
    )
    surface_tilt_range = slice(
        min_surface_tilt, max_surface_tilt, brute_force_precision
    )

    if method == SurfacePositionOptimizerMethod.brute:
        return (
            (surface_orientation_range, surface_tilt_range)
            if mode == SurfacePositionOptimizerMode.Tilt_and_Orientation
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

    if mode == SurfacePositionOptimizerMode.Tilt_and_Orientation:
        return Bounds(
            lb=[surface_orientation_range.start, surface_tilt_range.start],
            ub=[surface_orientation_range.stop, surface_tilt_range.stop],
        )

    raise ValueError("Invalid mode provided.")
