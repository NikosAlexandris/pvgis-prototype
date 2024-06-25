from enum import Enum
from scipy import optimize
import math
from pvgisprototype.api.power.broadband import (
    calculate_photovoltaic_power_output_series,
)
from pvgisprototype import SurfaceOrientation, SurfaceTilt


class OptimizerMethod(str, Enum):
    brute = "Brute"
    shgo = "SHGO"
    powell = "Powell"
    nelder_mead = "Nelder-Mead"  # Not working properly right now
    bfgs = "BFGS"  # Not working properly right now
    l_bfgs_b = "L-BFGS-B"  # Not working properly right now
    direct = "DIRECT"


class OptimizerMode(str, Enum):
    tilt = "Tilt"
    orientation = "Orientation"
    tilt_orientation = "Tilt-Orientation"


def create_dictionary_for_location_parameters(
    longitude,
    latitude,
    elevation,
    timestamps,
    timezone,
    spectral_factor_series,
    photovoltaic_module,
    temperature_series,
    wind_speed_series,
    linke_turbidity_factor_series,
    surface_orientation,
    surface_tilt,
    mode,
):

    dictionary_for_location_parameters = {
        "longitude": longitude,
        "latitude": latitude,
        "elevation": elevation,
        "timestamps": timestamps,
        "timezone": timezone,
        "spectral_factor_series": spectral_factor_series,
        "photovoltaic_module": photovoltaic_module,
        "temperature_series": temperature_series,
        "wind_speed_series": wind_speed_series,
        "linke_turbidity_factor_series": linke_turbidity_factor_series,
    }
    if mode == OptimizerMode.tilt:
        dictionary_for_location_parameters["surface_orientation"] = surface_orientation

    if mode == OptimizerMode.orientation:
        dictionary_for_location_parameters["surface_tilt"] = surface_tilt

    return dictionary_for_location_parameters


def create_bounds_for_optimizer(
    min_surface_orientation,
    max_surface_orientation,
    min_surface_tilt,
    max_surface_tilt,
    mode,
    method,
):

    brute_force_precision = math.radians(1)
    range_surface_orientation = slice(
        min_surface_orientation, max_surface_orientation, brute_force_precision
    )
    range_surface_tilt = slice(
        min_surface_tilt, max_surface_tilt, brute_force_precision
    )

    if mode == OptimizerMode.tilt:
        bounds = optimize.Bounds(
            lb=range_surface_tilt.start, ub=range_surface_tilt.stop
        )
        range = (range_surface_tilt,)

    if mode == OptimizerMode.orientation:
        bounds = optimize.Bounds(
            lb=range_surface_orientation.start, ub=range_surface_orientation.stop
        )
        range = (range_surface_orientation,)

    if mode == OptimizerMode.tilt_orientation:
        bounds = optimize.Bounds(
            lb=[range_surface_orientation.start, range_surface_tilt.start],
            ub=[range_surface_orientation.stop, range_surface_tilt.stop],
        )
        range = (range_surface_orientation, range_surface_tilt)

    if method == OptimizerMethod.brute:
        return range

    else:
        return bounds


def calculate_mean_negative_power_output(surface_angle, location_parameters, mode):
    """
    """
    # from devtools import debug
    # debug(locals())
    if mode == OptimizerMode.tilt:
        power_output_series = calculate_photovoltaic_power_output_series(
            surface_tilt=surface_angle,
            **location_parameters,
        )

    if mode == OptimizerMode.orientation:
        from devtools import debug
        debug(locals())
        power_output_series = calculate_photovoltaic_power_output_series(
            surface_orientation=surface_angle,
            **location_parameters,
        )

    if mode == OptimizerMode.tilt_orientation:
        power_output_series = calculate_photovoltaic_power_output_series(
            surface_orientation=surface_angle[0],
            surface_tilt=surface_angle[1],
            **location_parameters,
        )

    return -(
        power_output_series
    ).value.mean()  # returns the mean of the negative power output


def create_dictionary_for_result_optimizer(
    result_optimizer,
    mode,
    method,
    surface_orientation,
    surface_tilt,
    location_parameters,
):

    result_dictionary = {
        "surface_orientation": None,
        "surface_tilt": None,
        "mean_power_output": None,
    }

    if mode == OptimizerMode.tilt:
        result_dictionary["surface_orientation"] = surface_orientation

        if method == OptimizerMethod.brute:
            result_dictionary["surface_tilt"] = SurfaceTilt(
                value=result_optimizer,
                unit="radians",
                optimal=True,
                optimizer=method,
            )
            result_dictionary["mean_power_output"] = (
                - calculate_mean_negative_power_output(
                    surface_angle=result_optimizer,
                    location_parameters=location_parameters,
                    mode=mode,
                )
            )
        elif result_optimizer.message == "Optimization terminated successfully.":
            result_dictionary["surface_tilt"] = SurfaceTilt(
                value=result_optimizer.x[0],
                unit="radians",
                optimal=True,
                optimizer=method,
            )
            result_dictionary["mean_power_output"] = -result_optimizer.fun

    if mode == OptimizerMode.orientation:
        result_dictionary["surface_tilt"] = surface_tilt

        if method == OptimizerMethod.brute:
            result_dictionary["surface_orientation"] = SurfaceOrientation(
                value=result_optimizer,
                unit="radians",
                optimal=True,
                optimizer=method,
            )
            result_dictionary["mean_power_output"] = (
                - calculate_mean_negative_power_output(
                    surface_angle=result_optimizer,
                    location_parameters=location_parameters,
                    mode=mode,
                )
            )
        elif result_optimizer.message == "Optimization terminated successfully.":
            result_dictionary["surface_orientation"] = SurfaceOrientation(
                value=result_optimizer.x[0],
                unit="radians",
                optimal=True,
                optimizer=method,
            )
            result_dictionary["mean_power_output"] = -result_optimizer.fun

    if mode == OptimizerMode.tilt_orientation:

        if method == OptimizerMethod.brute:
            result_dictionary["surface_orientation"] = SurfaceOrientation(
                value=result_optimizer[0],
                unit="radians",
                optimal=True,
                optimizer=method,
            )
            result_dictionary["surface_tilt"] = SurfaceTilt(
                value=result_optimizer[1],
                unit="radians",
                optimal=True,
                optimizer=method,
            )
            result_dictionary["mean_power_output"] = (
                -calculate_mean_negative_power_output(
                    surface_angle=result_optimizer,
                    location_parameters=location_parameters,
                    mode=mode,
                )
            )
        elif result_optimizer.message == "Optimization terminated successfully.":
            result_dictionary["surface_orientation"] = SurfaceOrientation(
                value=result_optimizer.x[0],
                unit="radians",
                optimal=True,
                optimizer=method,
            )
            result_dictionary["surface_tilt"] = SurfaceTilt(
                value=result_optimizer.x[1],
                unit="radians",
                optimal=True,
                optimizer=method,
            )
            result_dictionary["mean_power_output"] = -result_optimizer.fun

    return result_dictionary
