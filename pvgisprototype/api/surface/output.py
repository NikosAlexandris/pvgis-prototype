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
from pvgisprototype.constants import (
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    RADIANS,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
)
from pvgisprototype.core.hashing import generate_hash


def build_optimiser_output(
    optimiser_output: dict,
    location_parameters: dict,
    mode: SurfacePositionOptimizerMode,
    method: SurfacePositionOptimizerMethod,
    surface_orientation: SurfaceOrientation | None = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt | None = SURFACE_TILT_DEFAULT,
    angle_output_units: str = RADIANS,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
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
        "surface_orientation": None,
        "surface_tilt": None,
        "mean_power_output": None,
        "Fingerprint": None,
    }

    if mode == SurfacePositionOptimizerMode.Tilt:
        if not isinstance(
            surface_orientation, SurfaceOrientation
        ):  # FIXME THIS SHOULD ONLY BE A SurfaceOrientation OBJECT
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
        optimal_surface_position["surface_orientation"] = surface_orientation

        if method == SurfacePositionOptimizerMethod.brute:
            optimal_surface_position["surface_tilt"] = SurfaceTilt(
                value=convert_float_to_degrees_if_requested(
                    optimiser_output, angle_output_units
                ),
                unit=angle_output_units,
                optimal=True,
                optimizer=method,
            )
            optimal_surface_position["mean_power_output"] = (
                -calculate_mean_negative_photovoltaic_power_output(
                    surface_angle=optimiser_output,
                    location_parameters=location_parameters,
                    mode=mode,
                )
            )

        elif optimiser_output.message == "Optimization terminated successfully.":
            optimal_surface_position["surface_tilt"] = SurfaceTilt(
                value=convert_float_to_degrees_if_requested(
                    optimiser_output.x[0], angle_output_units
                ),
                unit=angle_output_units,
                optimal=True,
                optimizer=method,
            )
            optimal_surface_position["mean_power_output"] = -optimiser_output.fun

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

        optimal_surface_position["surface_tilt"] = surface_tilt

        if method == SurfacePositionOptimizerMethod.brute:
            optimal_surface_position["surface_orientation"] = SurfaceOrientation(
                value=convert_float_to_degrees_if_requested(
                    optimiser_output, angle_output_units
                ),
                unit=angle_output_units,
                optimal=True,
                optimizer=method,
            )
            optimal_surface_position["mean_power_output"] = (
                -calculate_mean_negative_photovoltaic_power_output(
                    surface_angle=optimiser_output,
                    location_parameters=location_parameters,
                    mode=mode,
                )
            )
        elif optimiser_output.message == "Optimization terminated successfully.":
            optimal_surface_position["surface_orientation"] = SurfaceOrientation(
                value=convert_float_to_degrees_if_requested(
                    optimiser_output.x[0], angle_output_units
                ),
                unit=angle_output_units,
                optimal=True,
                optimizer=method,
            )
            optimal_surface_position["mean_power_output"] = -optimiser_output.fun

    if mode == SurfacePositionOptimizerMode.Orientation_and_Tilt:
        if method == SurfacePositionOptimizerMethod.brute:
            optimal_surface_position["surface_orientation"] = SurfaceOrientation(
                value=convert_float_to_degrees_if_requested(
                    optimiser_output[0], angle_output_units
                ),
                unit=angle_output_units,
                optimal=True,
                optimizer=method,
            )
            optimal_surface_position["surface_tilt"] = SurfaceTilt(
                value=convert_float_to_degrees_if_requested(
                    optimiser_output[1], angle_output_units
                ),
                unit=angle_output_units,
                optimal=True,
                optimizer=method,
            )
            optimal_surface_position["mean_power_output"] = (
                -calculate_mean_negative_photovoltaic_power_output(
                    surface_angle=optimiser_output,
                    location_parameters=location_parameters,
                    mode=mode,
                )
            )
        elif optimiser_output.message == "Optimization terminated successfully.":
            optimal_surface_position["surface_orientation"] = SurfaceOrientation(
                value=convert_float_to_degrees_if_requested(
                    optimiser_output.x[0], angle_output_units
                ),
                unit=angle_output_units,
                optimal=True,
                optimizer=method,
            )
            optimal_surface_position["surface_tilt"] = SurfaceTilt(
                value=convert_float_to_degrees_if_requested(
                    optimiser_output.x[1], angle_output_units
                ),
                unit=angle_output_units,
                optimal=True,
                optimizer=method,
            )
            optimal_surface_position["mean_power_output"] = -optimiser_output.fun

    # optimal_surface_position["Fingerprint"] = (
    #     generate_hash(optimal_surface_position) if fingerprint else {}
    # )

    return optimal_surface_position
