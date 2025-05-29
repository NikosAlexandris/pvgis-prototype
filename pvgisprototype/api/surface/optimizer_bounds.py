from math import radians

from scipy.optimize import Bounds

from pvgisprototype.api.surface.parameter_models import (
    SurfacePositionOptimizerMethod,
    SurfacePositionOptimizerMode,
)
from pvgisprototype.constants import (
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import logger


def define_optimiser_bounds(
    min_surface_orientation: float,
    max_surface_orientation: float,
    min_surface_tilt: float,
    max_surface_tilt: float,
    mode: SurfacePositionOptimizerMode,
    method: SurfacePositionOptimizerMethod,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
) -> tuple | Bounds:
    """
    Define bounds for the optimisation process.

    Parameters
    ----------
    min_surface_orientation: float
        The minimum surface orientation allowed.
    max_surface_orientation: float
        The maximum surface orientation allowed.
    min_surface_tilt: float
        The minimum surface tilt allowed.
    max_surface_tilt: float
        The maximum surface tilt allowed.
    mode: SurfacePositionOptimizerMode
        The optimisation mode.
    method: SurfacePositionOptimizerMethod
        The optimisation method.
    verbose: int, optional
        The verbosity level. Defaults to VERBOSE_LEVEL_DEFAULT.

    Returns
    -------
    tuple | Bounds
        The bounds for the optimisation process.

    Notes
    -----
    The bounds are defined as follows:

    - For the SurfacePositionOptimizerMode.Orientation_and_Tilt mode, the bounds are defined as a tuple of two slices.
    - For the SurfacePositionOptimizerMode.Tilt mode, the bounds are defined as a Bounds object with the lower and upper
      bounds set to the minimum and maximum surface tilt respectively.
    - For the SurfacePositionOptimizerMode.Orientation mode, the bounds are defined as a Bounds object with the lower and
      upper bounds set to the minimum and maximum surface orientation respectively.

    If the method is SurfacePositionOptimizerMethod.brute, the bounds are returned as a tuple of two slices. Otherwise,
    the bounds are returned as a Bounds object.
    """
    brute_force_precision = radians(1)
    surface_orientation_range = slice(
        min_surface_orientation, max_surface_orientation, brute_force_precision
    )
    surface_tilt_range = slice(
        min_surface_tilt, max_surface_tilt, brute_force_precision
    )

    if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
        logger.debug(
            f"i Define bounds for the '{method}' optimiser ..",
            alt=f"i [bold]Define[/bold] bounds for the [magenta]{method}[/magenta] optimiser ..",
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
