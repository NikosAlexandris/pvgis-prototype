from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.log import logger
from pvgisprototype.api.surface.parameter_models import SurfacePositionOptimizerMode


def build_location_dictionary(
    longitude,
    latitude,
    elevation,
    timestamps,
    timezone,
    surface_orientation,
    surface_tilt,
    mode,
    verbose,
):
    """
    """
    if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
        logger.info(
            "i Collect location parameters",
            alt="i [bold]Collect[/bold] the [magenta]location parameters[/magenta]"
        )
    location_parameters = {
        "longitude": longitude,
        "latitude": latitude,
        "elevation": elevation,
        "timestamps": timestamps,
        "timezone": timezone,
    }
    if mode == SurfacePositionOptimizerMode.Tilt:
        location_parameters["surface_orientation"] = surface_orientation

    if mode == SurfacePositionOptimizerMode.Orientation:
        location_parameters["surface_tilt"] = surface_tilt

    return location_parameters

def build_other_input_arguments_dictionary(
    global_horizontal_irradiance,
    direct_horizontal_irradiance,
    spectral_factor_series,
    photovoltaic_module,
    temperature_series,
    wind_speed_series,
    horizon_profile,
    shading_model,
    linke_turbidity_factor_series,
    shading_states,
    apply_atmospheric_refraction,
    refracted_solar_zenith,
    albedo,
    apply_reflectivity_factor,
    solar_position_model,
    sun_horizon_position,
    solar_incidence_model,
    zero_negative_solar_incidence_angle,
    solar_time_model,
    solar_constant,
    perigee_offset,
    eccentricity_correction_factor,
    peak_power,
    system_efficiency,
    power_model,
    temperature_model,
    efficiency,
    verbose,
):
    if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
        logger.info(
            "i Collect the rest input parameters",
            alt="i [bold]Collect[/bold] the [magenta]rest input parameters[/magenta]"
        )
    input_parameters = {
        "global_horizontal_irradiance": global_horizontal_irradiance,
        "direct_horizontal_irradiance": direct_horizontal_irradiance,
        "spectral_factor_series": spectral_factor_series,
        "photovoltaic_module": photovoltaic_module,
        "temperature_series": temperature_series,
        "wind_speed_series": wind_speed_series,
        "horizon_profile": horizon_profile,
        "shading_model": shading_model,
        "linke_turbidity_factor_series": linke_turbidity_factor_series,
        "shading_states": shading_states,
        "apply_atmospheric_refraction": apply_atmospheric_refraction,
        "refracted_solar_zenith": refracted_solar_zenith,
        "albedo": albedo,
        "apply_reflectivity_factor": apply_reflectivity_factor,
        "solar_position_model": solar_position_model,
        "sun_horizon_position": sun_horizon_position,
        "solar_incidence_model": solar_incidence_model,
        "zero_negative_solar_incidence_angle": zero_negative_solar_incidence_angle,
        "solar_time_model": solar_time_model,
        "solar_constant": solar_constant,
        "perigee_offset": perigee_offset,
        "eccentricity_correction_factor": eccentricity_correction_factor,
        "peak_power": peak_power,
        "system_efficiency": system_efficiency,
        "power_model": power_model,
        "temperature_model": temperature_model,
        "efficiency": efficiency,
        "verbose": verbose,
    }

    return input_parameters