from pvgisprototype.api.power.broadband import (
    calculate_photovoltaic_power_output_series,
)
from pvgisprototype.api.surface.parameter_models import SurfacePositionOptimizerMode

"""
Create the functions that the optimizer will minimize, in order to find the point where the 
power output/irradiance are maximized.

A function for each case. Is it necessary??? 
    - Maybe I can have just one function (although i think scipy function works differently
     when calling the function if it's one or two variables )
    - Anyway, maybe I could have two functions (for the 1D problem and the 2D problem) 

"""


def calculate_mean_negative_photovoltaic_power_output(
    surface_angle: tuple,
    objective_function_arguments: dict,
    mode: SurfacePositionOptimizerMode = SurfacePositionOptimizerMode.Tilt,
):
    """
    Calculate the mean negative photovoltaic power output.

    Parameters
    ----------
    surface_angle : tuple
        The angle(s) of the surface to be optimized.
    objective_function_arguments : dict
        The arguments to be passed to the function that calculates the photovoltaic
        power output.
    mode : SurfacePositionOptimizerMode
        The mode of the optimization. If `SurfacePositionOptimizerMode.Tilt`, the
        function will calculate the photovoltaic power output for the given surface
        tilt. If `SurfacePositionOptimizerMode.Orientation`, the function will
        calculate the photovoltaic power output for the given surface orientation. If
        `SurfacePositionOptimizerMode.Orientation_and_Tilt`, the function will
        calculate the photovoltaic power output for the given surface orientation and
        tilt.

    Returns
    -------
    float
        The mean negative photovoltaic power output.
    """
    if mode == SurfacePositionOptimizerMode.Tilt:
        photovoltaic_power_output_series = calculate_photovoltaic_power_output_series(
            surface_tilt=surface_angle,
            **objective_function_arguments,
        )

    if mode == SurfacePositionOptimizerMode.Orientation:
        photovoltaic_power_output_series = calculate_photovoltaic_power_output_series(
            surface_orientation=surface_angle,
            **objective_function_arguments,
        )

    if mode == SurfacePositionOptimizerMode.Orientation_and_Tilt:
        photovoltaic_power_output_series = calculate_photovoltaic_power_output_series(
            surface_orientation=surface_angle[0],
            surface_tilt=surface_angle[1],
            **objective_function_arguments,
        )

    return -(photovoltaic_power_output_series).value.mean()
