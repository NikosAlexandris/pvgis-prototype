import math
from pathlib import Path
from typing import Optional

from scipy import optimize

from pvgisprototype import SurfaceOrientation, SurfaceTilt
from pvgisprototype.api.power.broadband import (
    calculate_photovoltaic_power_output_series,
)
from pvgisprototype.api.surface.parameter_models import (
    SurfacePositionOptimizerMethod,
    SurfacePositionOptimizerMode,
)
from pvgisprototype import (
    LinkeTurbidityFactor,
    SpectralFactorSeries,
    TemperatureSeries,
    WindSpeedSeries,
    SurfaceOrientation,
    SurfaceTilt,
)
from pvgisprototype.api.irradiance.models import (
    MethodForInexactMatches,
    ModuleTemperatureAlgorithm,
)
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.constants import IN_MEMORY_FLAG_DEFAULT, LINKE_TURBIDITY_TIME_SERIES_DEFAULT, MASK_AND_SCALE_FLAG_DEFAULT, SPECTRAL_FACTOR_DEFAULT, TEMPERATURE_DEFAULT, TOLERANCE_DEFAULT, WIND_SPEED_DEFAULT


def create_dictionary_for_location_parameters(
    longitude,
    latitude,
    elevation,
    timestamps,
    timezone,
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
    }
    if mode == SurfacePositionOptimizerMode.Tilt:
        dictionary_for_location_parameters["surface_orientation"] = surface_orientation

    if mode == SurfacePositionOptimizerMode.Orientation:
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
    """ """
    brute_force_precision = math.radians(1)
    range_surface_orientation = slice(
        min_surface_orientation, max_surface_orientation, brute_force_precision
    )
    range_surface_tilt = slice(
        min_surface_tilt, max_surface_tilt, brute_force_precision
    )

    if mode == SurfacePositionOptimizerMode.Tilt:
        bounds = optimize.Bounds(
            lb=range_surface_tilt.start, ub=range_surface_tilt.stop
        )
        range = (range_surface_tilt,)

    if mode == SurfacePositionOptimizerMode.Orientation:
        bounds = optimize.Bounds(
            lb=range_surface_orientation.start, ub=range_surface_orientation.stop
        )
        range = (range_surface_orientation,)

    if mode == SurfacePositionOptimizerMode.Tilt_and_Orientation:
        bounds = optimize.Bounds(
            lb=[range_surface_orientation.start, range_surface_tilt.start],
            ub=[range_surface_orientation.stop, range_surface_tilt.stop],
        )
        range = (range_surface_orientation, range_surface_tilt)

    if method == SurfacePositionOptimizerMethod.brute:
        return range

    else:
        return bounds


def calculate_mean_negative_power_output(
    surface_angle,
    location_parameters,
    global_horizontal_irradiance: Optional[Path] = None,
    direct_horizontal_irradiance: Optional[Path] = None,
    spectral_factor_series: SpectralFactorSeries = SpectralFactorSeries(value=SPECTRAL_FACTOR_DEFAULT),
    temperature_series: TemperatureSeries = TemperatureSeries(value=TEMPERATURE_DEFAULT),
    wind_speed_series: WindSpeedSeries = WindSpeedSeries(value=WIND_SPEED_DEFAULT),
    neighbor_lookup: MethodForInexactMatches = MethodForInexactMatches.nearest,
    tolerance: Optional[float] = TOLERANCE_DEFAULT,
    mask_and_scale: bool = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: bool = IN_MEMORY_FLAG_DEFAULT,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LinkeTurbidityFactor(value=LINKE_TURBIDITY_TIME_SERIES_DEFAULT),
    photovoltaic_module: PhotovoltaicModuleModel = PhotovoltaicModuleModel.CSI_FREE_STANDING, 
    mode: SurfacePositionOptimizerMode = SurfacePositionOptimizerMode.Tilt,
):
    """
    """
    # from devtools import debug
    # debug(locals())
    if mode == SurfacePositionOptimizerMode.Tilt:
        power_output_series = calculate_photovoltaic_power_output_series(
            surface_tilt=surface_angle,
            global_horizontal_irradiance=global_horizontal_irradiance,
            direct_horizontal_irradiance=direct_horizontal_irradiance,
            spectral_factor_series=spectral_factor_series,
            temperature_series=temperature_series,
            wind_speed_series=wind_speed_series,
            neighbor_lookup=neighbor_lookup,
            tolerance=tolerance,
            mask_and_scale=mask_and_scale,
            in_memory=in_memory,
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            photovoltaic_module=photovoltaic_module,
            **location_parameters,
        )

    if mode == SurfacePositionOptimizerMode.Orientation:
        # from devtools import debug
        # debug(locals())
        power_output_series = calculate_photovoltaic_power_output_series(
            surface_orientation=surface_angle,
            global_horizontal_irradiance=global_horizontal_irradiance,
            direct_horizontal_irradiance=direct_horizontal_irradiance,
            spectral_factor_series=spectral_factor_series,
            temperature_series=temperature_series,
            wind_speed_series=wind_speed_series,
            neighbor_lookup=neighbor_lookup,
            tolerance=tolerance,
            mask_and_scale=mask_and_scale,
            in_memory=in_memory,
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            photovoltaic_module=photovoltaic_module,
            **location_parameters,
        )

    if mode == SurfacePositionOptimizerMode.Tilt_and_Orientation:
        power_output_series = calculate_photovoltaic_power_output_series(
            surface_orientation=surface_angle[0],
            surface_tilt=surface_angle[1],
            global_horizontal_irradiance=global_horizontal_irradiance,
            direct_horizontal_irradiance=direct_horizontal_irradiance,
            spectral_factor_series=spectral_factor_series,
            temperature_series=temperature_series,
            wind_speed_series=wind_speed_series,
            neighbor_lookup=neighbor_lookup,
            tolerance=tolerance,
            mask_and_scale=mask_and_scale,
            in_memory=in_memory,
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            photovoltaic_module=photovoltaic_module,
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

    if mode == SurfacePositionOptimizerMode.Tilt:
        if isinstance(
            surface_orientation, SurfaceOrientation
        ):  # FIXME THIS SHOULD ONLY BE A SurfaceOrientation OBJECT
            result_dictionary["surface_orientation"] = surface_orientation
        else:
            result_dictionary["surface_orientation"] = SurfaceOrientation(
                value=surface_orientation, unit="radians"
            )

        if method == SurfacePositionOptimizerMethod.brute:
            result_dictionary["surface_tilt"] = SurfaceTilt(
                value=result_optimizer,
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
            result_dictionary["surface_tilt"] = SurfaceTilt(
                value=result_optimizer.x[0],
                unit="radians",
                optimal=True,
                optimizer=method,
            )
            result_dictionary["mean_power_output"] = -result_optimizer.fun

    if mode == SurfacePositionOptimizerMode.Orientation:
        if isinstance(
            surface_orientation, SurfaceTilt
        ):  # FIXME THIS SHOULD ONLY BE A SurfaceTilt OBJECT
            result_dictionary["surface_tilt"] = surface_tilt
        else:
            result_dictionary["surface_tilt"] = SurfaceOrientation(
                value=surface_tilt, unit="radians"
            )

        if method == SurfacePositionOptimizerMethod.brute:
            result_dictionary["surface_orientation"] = SurfaceOrientation(
                value=result_optimizer,
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
            result_dictionary["mean_power_output"] = -result_optimizer.fun

    if mode == SurfacePositionOptimizerMode.Tilt_and_Orientation:
        if method == SurfacePositionOptimizerMethod.brute:
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
