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
from numpy import ndarray
from scipy.optimize import OptimizeResult

from pvgisprototype import SurfaceOrientation, SurfaceTilt
from pvgisprototype.api.position.models import (
    SOLAR_TIME_ALGORITHM_DEFAULT,
    SolarTimeModel,
)
from pvgisprototype.api.surface.parameter_models import (
    SurfacePositionOptimizerMethod,
    SurfacePositionOptimizerMode,
)
from pvgisprototype.api.surface.power import (
    calculate_mean_negative_photovoltaic_power_output,
)
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
)
from pvgisprototype.constants import (
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    MEAN_PHOTOVOLTAIC_POWER_NAME,
    RADIANS,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_ORIENTATION_NAME,
    SURFACE_TILT_DEFAULT,
    SURFACE_TILT_NAME,
    TIME_ALGORITHM_NAME,
    UNITS_COLUMN_NAME,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import logger


def build_optimiser_output(
    optimiser_output: OptimizeResult | ndarray,
    objective_function_arguments: dict,
    mode: SurfacePositionOptimizerMode,
    method: SurfacePositionOptimizerMethod,
    surface_orientation: SurfaceOrientation | None = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt | None = SURFACE_TILT_DEFAULT,
    solar_time_model: SolarTimeModel = SOLAR_TIME_ALGORITHM_DEFAULT,
    angle_output_units: str = RADIANS,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
):
    """
    Build the output dictionary for the surface position optimisation.

    Parameters
    ----------
    optimiser_output : OptimizeResult | ndarray
        The output of the optimiser.
    objective_function_arguments : dict
        The arguments passed to the optimiser.
    mode : SurfacePositionOptimizerMode
        The mode of the optimisation.
    method : SurfacePositionOptimizerMethod
        The method used for the optimisation.
    surface_orientation : SurfaceOrientation | None
        The surface orientation. If None, the default value is used.
    surface_tilt : SurfaceTilt | None
        The surface tilt. If None, the default value is used.
    solar_time_model : SolarTimeModel
        The solar time model used for the optimisation.
    angle_output_units : str
        The units of the angle output. Default is radians.
    verbose : int
        The verbosity level. Default is 0.

    Returns
    -------
    optimal_surface_position : dict
        A dictionary containing the optimal surface position, the mean photovoltaic
        power output and the units of the angle output.
    """
    if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
        logger.debug(
            f"i Build the output dictionary",
            alt=f"i [bold]Build[/bold] the [magenta]output dictionary[/magenta]",
        )

    optimal_surface_position = {
        SURFACE_ORIENTATION_NAME: None,
        SURFACE_TILT_NAME: None,
        MEAN_PHOTOVOLTAIC_POWER_NAME: None,
        UNITS_COLUMN_NAME: angle_output_units,
        TIME_ALGORITHM_NAME: solar_time_model.value,
    }

    if mode == SurfacePositionOptimizerMode.Tilt:

        if not isinstance(
            surface_orientation, SurfaceOrientation
        ):  # FIXME THIS SHOULD ONLY BE A TYPE SurfaceOrientation OBJECT
            surface_orientation = SurfaceOrientation(
                value=surface_orientation,
                unit=RADIANS,
            )

        surface_orientation = SurfaceOrientation(
            value=convert_float_to_degrees_if_requested(
                surface_orientation.value, angle_output_units
            ),
            unit=angle_output_units,
        )

        optimal_surface_position[SURFACE_ORIENTATION_NAME] = surface_orientation

        if method == SurfacePositionOptimizerMethod.brute:

            optimal_surface_position[SURFACE_TILT_NAME] = SurfaceTilt(
                value=convert_float_to_degrees_if_requested(
                    optimiser_output, angle_output_units  # type: ignore[arg-type]
                ),
                unit=angle_output_units,
                optimal=True,
                optimizer=method,
            )

            # NOTE Make last call to get full results as from API
            # NOTE No expected execution time cost since results are cached
            # NOTE Implement something like the snippet below
            # --------------------------------------------------->
            # arguments["surface_tilt"] = optimal_position[SURFACE_TILT_NAME].radians
            # arguments["surface_orientation"]=optimal_position[SURFACE_ORIENTATION_NAME].radians
            # photovoltaic_power_series = calculate_photovoltaic_power_output_series(
            #    **arguments,
            # )
            # ----------------------------------------------------
            optimal_surface_position[MEAN_PHOTOVOLTAIC_POWER_NAME] = (
                -calculate_mean_negative_photovoltaic_power_output(
                    surface_angle=optimiser_output,
                    objective_function_arguments=objective_function_arguments,
                    mode=mode,
                )
            )

            return optimal_surface_position

        if optimiser_output.success:  # type: ignore[union-attr]
            optimal_surface_position[SURFACE_TILT_NAME] = SurfaceTilt(
                value=convert_float_to_degrees_if_requested(
                    optimiser_output.x[0], angle_output_units  # type: ignore[union-attr]
                ),
                unit=angle_output_units,
                optimal=True,
                optimizer=method,
            )
            # NOTE Make last call to get full results as from API
            # NOTE No expected execution time cost since results are cached
            # NOTE Implement something like the snippet below
            # --------------------------------------------------->
            # arguments["surface_tilt"] = optimal_position[SURFACE_TILT_NAME].radians
            # arguments["surface_orientation"]=optimal_position[SURFACE_ORIENTATION_NAME].radians
            # photovoltaic_power_series = calculate_photovoltaic_power_output_series(
            #    **arguments,
            # )
            # ----------------------------------------------------
            optimal_surface_position[MEAN_PHOTOVOLTAIC_POWER_NAME] = (
                -optimiser_output.fun  # type: ignore[union-attr]
            )

            return optimal_surface_position

    if mode == SurfacePositionOptimizerMode.Orientation:
        if not isinstance(
            surface_tilt, SurfaceTilt
        ):  # FIXME THIS SHOULD ONLY BE A SurfaceOrientation OBJECT
            surface_tilt = SurfaceTilt(
                value=surface_tilt,
                unit=RADIANS,
            )

        surface_tilt = SurfaceTilt(
            value=convert_float_to_degrees_if_requested(
                surface_tilt.value, angle_output_units
            ),
            unit=angle_output_units,
        )

        optimal_surface_position[SURFACE_TILT_NAME] = surface_tilt

        if method == SurfacePositionOptimizerMethod.brute:
            optimal_surface_position[SURFACE_ORIENTATION_NAME] = SurfaceOrientation(
                value=convert_float_to_degrees_if_requested(
                    optimiser_output, angle_output_units  # type: ignore[arg-type]
                ),
                unit=angle_output_units,
                optimal=True,
                optimizer=method,
            )
            # NOTE Make last call to get full results as from API
            # NOTE No expected execution time cost since results are cached
            # NOTE Implement something like the snippet below
            # --------------------------------------------------->
            # arguments["surface_tilt"] = optimal_position[SURFACE_TILT_NAME].radians
            # arguments["surface_orientation"]=optimal_position[SURFACE_ORIENTATION_NAME].radians
            # photovoltaic_power_series = calculate_photovoltaic_power_output_series(
            #    **arguments,
            # )
            # ----------------------------------------------------
            optimal_surface_position[MEAN_PHOTOVOLTAIC_POWER_NAME] = (
                -calculate_mean_negative_photovoltaic_power_output(
                    surface_angle=optimiser_output,
                    objective_function_arguments=objective_function_arguments,
                    mode=mode,
                )
            )
        elif optimiser_output.success:  # type: ignore[union-attr]
            optimal_surface_position[SURFACE_ORIENTATION_NAME] = SurfaceOrientation(
                value=convert_float_to_degrees_if_requested(
                    optimiser_output.x[0], angle_output_units  # type: ignore[union-attr]
                ),
                unit=angle_output_units,
                optimal=True,
                optimizer=method,
            )
            # NOTE Make last call to get full results as from API
            # NOTE No expected execution time cost since results are cached
            # NOTE Implement something like the snippet below
            # --------------------------------------------------->
            # arguments["surface_tilt"] = optimal_position[SURFACE_TILT_NAME].radians
            # arguments["surface_orientation"]=optimal_position[SURFACE_ORIENTATION_NAME].radians
            # photovoltaic_power_series = calculate_photovoltaic_power_output_series(
            #    **arguments,
            # )
            # ----------------------------------------------------
            optimal_surface_position[MEAN_PHOTOVOLTAIC_POWER_NAME] = (
                -optimiser_output.fun  # type: ignore[union-attr]
            )

    if mode == SurfacePositionOptimizerMode.Orientation_and_Tilt:
        if method == SurfacePositionOptimizerMethod.brute:
            optimal_surface_position[SURFACE_ORIENTATION_NAME] = SurfaceOrientation(
                value=convert_float_to_degrees_if_requested(
                    optimiser_output[0], angle_output_units
                ),
                unit=angle_output_units,
                optimal=True,
                optimizer=method,
            )
            optimal_surface_position[SURFACE_TILT_NAME] = SurfaceTilt(
                value=convert_float_to_degrees_if_requested(
                    optimiser_output[1], angle_output_units
                ),
                unit=angle_output_units,
                optimal=True,
                optimizer=method,
            )
            # NOTE Make last call to get full results as from API
            # NOTE No expected execution time cost since results are cached
            # NOTE Implement something like the snippet below
            # --------------------------------------------------->
            # arguments["surface_tilt"] = optimal_position[SURFACE_TILT_NAME].radians
            # arguments["surface_orientation"]=optimal_position[SURFACE_ORIENTATION_NAME].radians
            # photovoltaic_power_series = calculate_photovoltaic_power_output_series(
            #    **arguments,
            # )
            # ----------------------------------------------------
            optimal_surface_position[MEAN_PHOTOVOLTAIC_POWER_NAME] = (
                -calculate_mean_negative_photovoltaic_power_output(
                    surface_angle=optimiser_output,
                    objective_function_arguments=objective_function_arguments,
                    mode=mode,
                )
            )
        elif optimiser_output.success:  # type: ignore[union-attr]
            optimal_surface_position[SURFACE_ORIENTATION_NAME] = SurfaceOrientation(
                value=convert_float_to_degrees_if_requested(
                    optimiser_output.x[0], angle_output_units  # type: ignore[union-attr]
                ),
                unit=angle_output_units,
                optimal=True,
                optimizer=method,
            )
            optimal_surface_position[SURFACE_TILT_NAME] = SurfaceTilt(
                value=convert_float_to_degrees_if_requested(
                    optimiser_output.x[1], angle_output_units  # type: ignore[union-attr]
                ),
                unit=angle_output_units,
                optimal=True,
                optimizer=method,
            )
            # NOTE Make last call to get full results as from API
            # NOTE No expected execution time cost since results are cached
            # NOTE Implement something like the snippet below
            # --------------------------------------------------->
            # arguments["surface_tilt"] = optimal_position[SURFACE_TILT_NAME].radians
            # arguments["surface_orientation"]=optimal_position[SURFACE_ORIENTATION_NAME].radians
            # photovoltaic_power_series = calculate_photovoltaic_power_output_series(
            #    **arguments,
            # )
            # ----------------------------------------------------
            optimal_surface_position[MEAN_PHOTOVOLTAIC_POWER_NAME] = -optimiser_output.fun  # type: ignore[union-attr]

    return optimal_surface_position
