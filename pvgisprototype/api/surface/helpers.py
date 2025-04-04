from numpy import ndarray
from xarray import DataArray

from pvgisprototype.api.position.models import ShadingModel
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
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.constants import (
    FINGERPRINT_FLAG_DEFAULT,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT, 
    SPECTRAL_FACTOR_DEFAULT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT, 
    TEMPERATURE_DEFAULT, 
    WIND_SPEED_DEFAULT,
    RADIANS,
)
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
)
from pvgisprototype.core.hashing import generate_hash

def build_location_dictionary(
    longitude,
    latitude,
    elevation,
    timestamps,
    timezone,
    surface_orientation,
    surface_tilt,
    mode,
):
    location_parameters = {
        "longitude": longitude,
        "latitude": latitude,
        "elevation": elevation,
        "timestamps": timestamps,
        "timezone": timezone,
    }
    if mode == SurfacePositionOptimizerMode.Tilt:
        location_parameters["surface_orientation"] = surface_orientation
        # location_parameters["initial_surface_tilt"] = latitude

    if mode == SurfacePositionOptimizerMode.Orientation:
        location_parameters["surface_tilt"] = surface_tilt
        # location_parameters["initial_surface_orientation"] = surface_orientation

    # if mode == SurfacePositionOptimizerMode.Tilt_and_Orientation:
        # location_parameters["initial_surface_tilt"] = surface_tilt
        # location_parameters["initial_surface_orientation"] = surface_orientation

    return location_parameters


# def calculate_mean_power_output(
def calculate_negative_mean_power_output(
    surface_angle,
    location_parameters,
    global_horizontal_irradiance: ndarray | None = None,
    direct_horizontal_irradiance: ndarray | None = None,
    spectral_factor_series: SpectralFactorSeries = SpectralFactorSeries(value=SPECTRAL_FACTOR_DEFAULT),
    temperature_series: TemperatureSeries = TemperatureSeries(value=TEMPERATURE_DEFAULT),
    wind_speed_series: WindSpeedSeries = WindSpeedSeries(value=WIND_SPEED_DEFAULT),
    horizon_profile: DataArray | None = None,
    shading_model: ShadingModel = ShadingModel.pvis,      
    linke_turbidity_factor_series: LinkeTurbidityFactor = LinkeTurbidityFactor(value=LINKE_TURBIDITY_TIME_SERIES_DEFAULT),
    photovoltaic_module: PhotovoltaicModuleModel = PhotovoltaicModuleModel.CSI_FREE_STANDING, 
    mode: SurfacePositionOptimizerMode = SurfacePositionOptimizerMode.Tilt,
):
    """
    Returns
    -------
    The mean of the negative power output

    """
    common_parameters = {
            'global_horizontal_irradiance': global_horizontal_irradiance,
            'direct_horizontal_irradiance': direct_horizontal_irradiance,
            'spectral_factor_series': spectral_factor_series,
            'temperature_series': temperature_series,
            'wind_speed_series': wind_speed_series,
            'horizon_profile': horizon_profile,
            'shading_model': shading_model,
            'linke_turbidity_factor_series': linke_turbidity_factor_series,
            'photovoltaic_module': photovoltaic_module,
            **location_parameters
            }

    if mode == SurfacePositionOptimizerMode.Tilt:
        power_output_series = calculate_photovoltaic_power_output_series(
            surface_tilt=surface_angle,
            **common_parameters,
        )

    if mode == SurfacePositionOptimizerMode.Orientation:
        power_output_series = calculate_photovoltaic_power_output_series(
            surface_orientation=surface_angle,
            **common_parameters,
        )

    if mode == SurfacePositionOptimizerMode.Tilt_and_Orientation:
        power_output_series = calculate_photovoltaic_power_output_series(
            surface_orientation=surface_angle[0],
            surface_tilt=surface_angle[1],
            **common_parameters,
        )

    return -(power_output_series).value.mean()
    # return -(
    #         power_output_series
    #     ).value.mean()  # returns the mean of the negative power output

# def calculate_negative_mean_power_output(
#     surface_angle,
#     location_parameters,
#     global_horizontal_irradiance: ndarray | None = None,
#     direct_horizontal_irradiance: ndarray | None = None,
#     spectral_factor_series: SpectralFactorSeries = SpectralFactorSeries(value=SPECTRAL_FACTOR_DEFAULT),
#     temperature_series: TemperatureSeries = TemperatureSeries(value=TEMPERATURE_DEFAULT),
#     wind_speed_series: WindSpeedSeries = WindSpeedSeries(value=WIND_SPEED_DEFAULT),
#     horizon_profile: DataArray | None = None,
#     shading_model: ShadingModel = ShadingModel.pvis,      
#     linke_turbidity_factor_series: LinkeTurbidityFactor = LinkeTurbidityFactor(value=LINKE_TURBIDITY_TIME_SERIES_DEFAULT),
#     photovoltaic_module: PhotovoltaicModuleModel = PhotovoltaicModuleModel.CSI_FREE_STANDING, 
#     mode: SurfacePositionOptimizerMode = SurfacePositionOptimizerMode.Tilt,
# ):
#     """
#     Returns
#     -------
#     The mean of the negative power output

#     """
#     return - calculate_mean_power_output(
#         surface_angle=surface_angle,
#         location_parameters=location_parameters,
#         global_horizontal_irradiance=global_horizontal_irradiance,
#         direct_horizontal_irradiance=direct_horizontal_irradiance,
#         spectral_factor_series=spectral_factor_series,
#         temperature_series=temperature_series,
#         wind_speed_series=wind_speed_series,
#         horizon_profile=horizon_profile,
#         shading_model=shading_model,
#         linke_turbidity_factor_series=linke_turbidity_factor_series,
#         photovoltaic_module=photovoltaic_module,
#         mode=mode,
#     )


def build_optimiser_output(
    result_optimizer,
    location_parameters: dict,
    mode: SurfacePositionOptimizerMode,
    method: SurfacePositionOptimizerMethod,
    surface_orientation: SurfaceOrientation | None = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt | None = SURFACE_TILT_DEFAULT,
    angle_output_units: str = RADIANS,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
):
    """
    """
    # def convert_and_set_angle(angle, angle_type):
    #     """Convert angle to the desired output units and set in the result dictionary."""
    #     if not isinstance(angle, angle_type):
    #         angle = angle_type(value=angle, unit=RADIANS)
    #     return angle_type(
    #         value=convert_float_to_degrees_if_requested(angle.value, angle_output_units),
    #         unit=angle_output_units,
    #     )

    result_dictionary = {
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
            value=convert_float_to_degrees_if_requested(surface_orientation.value, angle_output_units),
            unit=angle_output_units,
        )
        result_dictionary["surface_orientation"] = surface_orientation

        if method == SurfacePositionOptimizerMethod.brute:
            result_dictionary["surface_tilt"] = SurfaceTilt(
                value=convert_float_to_degrees_if_requested(result_optimizer, angle_output_units),
                unit=angle_output_units,
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
                value=convert_float_to_degrees_if_requested(result_optimizer.x[0], angle_output_units),
                unit=angle_output_units,
                optimal=True,
                optimizer=method,
            )
            result_dictionary["mean_power_output"] = -result_optimizer.fun

    if mode == SurfacePositionOptimizerMode.Orientation:
        if not isinstance(
                surface_tilt, SurfaceTilt
            ):  # FIXME THIS SHOULD ONLY BE A SurfaceOrientation OBJECT
                surface_tilt = SurfaceTilt(
                    value=surface_tilt, 
                    unit=RADIANS,
                )

        surface_tilt = SurfaceTilt(
                value=convert_float_to_degrees_if_requested(surface_tilt.value, angle_output_units),
                unit=angle_output_units,
            )
            
        result_dictionary["surface_tilt"] = surface_tilt

        if method == SurfacePositionOptimizerMethod.brute:
            result_dictionary["surface_orientation"] = SurfaceOrientation(
                value=convert_float_to_degrees_if_requested(result_optimizer, angle_output_units),
                unit=angle_output_units,
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
                value=convert_float_to_degrees_if_requested(result_optimizer.x[0], angle_output_units),
                unit=angle_output_units,
                optimal=True,
                optimizer=method,
            )
            result_dictionary["mean_power_output"] = -result_optimizer.fun

    if mode == SurfacePositionOptimizerMode.Tilt_and_Orientation:
        if method == SurfacePositionOptimizerMethod.brute:
            result_dictionary["surface_orientation"] = SurfaceOrientation(
                value=convert_float_to_degrees_if_requested(result_optimizer[0], angle_output_units),
                unit=angle_output_units,
                optimal=True,
                optimizer=method,
            )
            result_dictionary["surface_tilt"] = SurfaceTilt(
                value=convert_float_to_degrees_if_requested(result_optimizer[1], angle_output_units),
                unit=angle_output_units,
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
                value=convert_float_to_degrees_if_requested(result_optimizer.x[0], angle_output_units),
                unit=angle_output_units,
                optimal=True,
                optimizer=method,
            )
            result_dictionary["surface_tilt"] = SurfaceTilt(
                value=convert_float_to_degrees_if_requested(result_optimizer.x[1], angle_output_units),
                unit=angle_output_units,
                optimal=True,
                optimizer=method,
            )
            result_dictionary["mean_power_output"] = -result_optimizer.fun

    # result_dictionary["Fingerprint"] = (
    #     generate_hash(result_dictionary) if fingerprint else {}
    # )

    return result_dictionary
