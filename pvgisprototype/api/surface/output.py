from numpy import ndarray
from scipy.optimize import OptimizeResult

from pvgisprototype.api.surface.power import calculate_mean_negative_photovoltaic_power_output
from pvgisprototype.log import logger
from pvgisprototype.api.surface.parameter_models import (
    SurfacePositionOptimizerMethod,
    SurfacePositionOptimizerMode,
)
from pvgisprototype import (
    SurfaceOrientation,
    SurfaceTilt,
)
from pvgisprototype.api.position.models import (
    SolarTimeModel,
    SOLAR_TIME_ALGORITHM_DEFAULT,
)
from pvgisprototype.constants import (
    FINGERPRINT_COLUMN_NAME,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    MEAN_PHOTOVOLTAIC_POWER_NAME,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_ORIENTATION_NAME,
    SURFACE_TILT_DEFAULT,
    RADIANS,
    SURFACE_TILT_NAME,
    VERBOSE_LEVEL_DEFAULT,
    UNITS_COLUMN_NAME,
    TIME_ALGORITHM_NAME,
)
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
)
from pvgisprototype.core.hashing import generate_hash


SUCCESSFUL_OPTIMISATION_TERMINATION_MESSAGE = "Optimization terminated successfully."


def build_optimiser_output(
    optimiser_output: OptimizeResult | ndarray,
    arguments: dict,
    mode: SurfacePositionOptimizerMode,
    method: SurfacePositionOptimizerMethod,
    surface_orientation: SurfaceOrientation | None = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt | None = SURFACE_TILT_DEFAULT,
    solar_time_model: SolarTimeModel = SOLAR_TIME_ALGORITHM_DEFAULT,
    angle_output_units: str = RADIANS,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
):
    """ """
    # def convert_and_set_angle(angle, angle_type):
    #     """Convert angle to the desired output units and set in the result dictionary."""
    #     if not isinstance(angle, angle_type):
    #         angle = angle_type(value=angle, unit=RADIANS)
    #     return angle_type(
    #         value=convert_float_to_degrees_if_requested(angle.value, angle_output_units),
    #         unit=angle_output_units,
    #     )

    if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
        logger.info(
            f"i Build the output dictionary",
            alt=f"i [bold]Build[/bold] the [magenta]output dictionary[/magenta]"
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
                    optimiser_output, angle_output_units
                ),
                unit=angle_output_units,
                optimal=True,
                optimizer=method,
            )
            
            # NOTE Make last call to get full results as from API
            # NOTE No expected execution time cost since results are cached
            # NOTE Implement something like the snippet below
            # --------------------------------------------------->
            #arguments["surface_tilt"] = optimal_position[SURFACE_TILT_NAME].radians
            #arguments["surface_orientation"]=optimal_position[SURFACE_ORIENTATION_NAME].radians
            #photovoltaic_power_series = calculate_photovoltaic_power_output_series(
            #    **arguments,
            #)
            # ----------------------------------------------------
            optimal_surface_position[MEAN_PHOTOVOLTAIC_POWER_NAME] = (
                -calculate_mean_negative_photovoltaic_power_output(
                    surface_angle=optimiser_output,
                    arguments=arguments,
                    mode=mode,
                )
            )

            return optimal_surface_position

        if optimiser_output.message == SUCCESSFUL_OPTIMISATION_TERMINATION_MESSAGE:
            optimal_surface_position[SURFACE_TILT_NAME] = SurfaceTilt(
                value=convert_float_to_degrees_if_requested(
                    optimiser_output.x[0], angle_output_units
                ),
                unit=angle_output_units,
                optimal=True,
                optimizer=method,
            )
            # NOTE Make last call to get full results as from API
            # NOTE No expected execution time cost since results are cached
            # NOTE Implement something like the snippet below
            # --------------------------------------------------->
            #arguments["surface_tilt"] = optimal_position[SURFACE_TILT_NAME].radians
            #arguments["surface_orientation"]=optimal_position[SURFACE_ORIENTATION_NAME].radians
            #photovoltaic_power_series = calculate_photovoltaic_power_output_series(
            #    **arguments,
            #)
            # ----------------------------------------------------
            optimal_surface_position[MEAN_PHOTOVOLTAIC_POWER_NAME] = -optimiser_output.fun

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
                    optimiser_output, angle_output_units
                ),
                unit=angle_output_units,
                optimal=True,
                optimizer=method,
            )
            # NOTE Make last call to get full results as from API
            # NOTE No expected execution time cost since results are cached
            # NOTE Implement something like the snippet below
            # --------------------------------------------------->
            #arguments["surface_tilt"] = optimal_position[SURFACE_TILT_NAME].radians
            #arguments["surface_orientation"]=optimal_position[SURFACE_ORIENTATION_NAME].radians
            #photovoltaic_power_series = calculate_photovoltaic_power_output_series(
            #    **arguments,
            #)
            # ----------------------------------------------------
            optimal_surface_position[MEAN_PHOTOVOLTAIC_POWER_NAME] = (
                -calculate_mean_negative_photovoltaic_power_output(
                    surface_angle=optimiser_output,
                    arguments=arguments,
                    mode=mode,
                )
            )
        elif optimiser_output.message == SUCCESSFUL_OPTIMISATION_TERMINATION_MESSAGE:
            optimal_surface_position[SURFACE_ORIENTATION_NAME] = SurfaceOrientation(
                value=convert_float_to_degrees_if_requested(
                    optimiser_output.x[0], angle_output_units
                ),
                unit=angle_output_units,
                optimal=True,
                optimizer=method,
            )
            # NOTE Make last call to get full results as from API
            # NOTE No expected execution time cost since results are cached
            # NOTE Implement something like the snippet below
            # --------------------------------------------------->
            #arguments["surface_tilt"] = optimal_position[SURFACE_TILT_NAME].radians
            #arguments["surface_orientation"]=optimal_position[SURFACE_ORIENTATION_NAME].radians
            #photovoltaic_power_series = calculate_photovoltaic_power_output_series(
            #    **arguments,
            #)
            # ----------------------------------------------------
            optimal_surface_position[MEAN_PHOTOVOLTAIC_POWER_NAME] = -optimiser_output.fun

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
            #arguments["surface_tilt"] = optimal_position[SURFACE_TILT_NAME].radians
            #arguments["surface_orientation"]=optimal_position[SURFACE_ORIENTATION_NAME].radians
            #photovoltaic_power_series = calculate_photovoltaic_power_output_series(
            #    **arguments,
            #)
            # ----------------------------------------------------
            optimal_surface_position[MEAN_PHOTOVOLTAIC_POWER_NAME] = (
                -calculate_mean_negative_photovoltaic_power_output(
                    surface_angle=optimiser_output,
                    arguments=arguments,
                    mode=mode,
                )
            )
        elif optimiser_output.message == SUCCESSFUL_OPTIMISATION_TERMINATION_MESSAGE:
            optimal_surface_position[SURFACE_ORIENTATION_NAME] = SurfaceOrientation(
                value=convert_float_to_degrees_if_requested(
                    optimiser_output.x[0], angle_output_units
                ),
                unit=angle_output_units,
                optimal=True,
                optimizer=method,
            )
            optimal_surface_position[SURFACE_TILT_NAME] = SurfaceTilt(
                value=convert_float_to_degrees_if_requested(
                    optimiser_output.x[1], angle_output_units
                ),
                unit=angle_output_units,
                optimal=True,
                optimizer=method,
            )
            # NOTE Make last call to get full results as from API
            # NOTE No expected execution time cost since results are cached
            # NOTE Implement something like the snippet below
            # --------------------------------------------------->
            #arguments["surface_tilt"] = optimal_position[SURFACE_TILT_NAME].radians
            #arguments["surface_orientation"]=optimal_position[SURFACE_ORIENTATION_NAME].radians
            #photovoltaic_power_series = calculate_photovoltaic_power_output_series(
            #    **arguments,
            #)
            # ----------------------------------------------------            
            optimal_surface_position[MEAN_PHOTOVOLTAIC_POWER_NAME] = -optimiser_output.fun

    return optimal_surface_position
