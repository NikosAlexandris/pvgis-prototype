from devtools import debug
import typer
from typing import Annotated
from typing import Optional
from .loss import calculate_angular_loss_factor_for_nondirect_irradiance
from pvgisprototype.api.geometry.models import SolarTimeModels
from ..utilities.conversions import convert_to_radians
from datetime import datetime
from ..utilities.timestamp import now_utc_datetimezone
from ..utilities.timestamp import ctx_convert_to_timezone
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_series_irradiance
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_toolbox
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_advanced_options
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_geometry_surface
from pathlib import Path
from .direct import calculate_direct_horizontal_irradiance
from .extraterrestrial import calculate_extraterrestrial_normal_irradiance
from pvgisprototype.api.geometry.solar_altitude import model_solar_altitude
from pvgisprototype.models.pvis.solar_incidence import calculate_solar_incidence
from math import sin
from math import cos
from .diffuse import diffuse_transmission_function
from .diffuse import diffuse_solar_altitude_function
from .constants import SOLAR_CONSTANT

from pvgisprototype.cli.typer_parameters import typer_argument_longitude
from pvgisprototype.cli.typer_parameters import typer_argument_latitude
from pvgisprototype.cli.typer_parameters import typer_argument_elevation
from pvgisprototype.cli.typer_parameters import typer_option_refracted_solar_zenith
from pvgisprototype.cli.typer_parameters import typer_argument_timestamp
from pvgisprototype.cli.typer_parameters import typer_option_timezone
from pvgisprototype.cli.typer_parameters import typer_argument_surface_tilt
from pvgisprototype.cli.typer_parameters import typer_argument_surface_orientation
from pvgisprototype.cli.typer_parameters import typer_option_linke_turbidity_factor
from pvgisprototype.cli.typer_parameters import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer_parameters import typer_option_refracted_solar_zenith
from pvgisprototype.cli.typer_parameters import typer_option_albedo
from pvgisprototype.cli.typer_parameters import typer_option_direct_horizontal_component
from pvgisprototype.cli.typer_parameters import typer_option_apply_angular_loss_factor
from pvgisprototype.cli.typer_parameters import typer_option_solar_time_model
from pvgisprototype.cli.typer_parameters import typer_option_global_time_offset
from pvgisprototype.cli.typer_parameters import typer_option_hour_offset
from pvgisprototype.cli.typer_parameters import typer_argument_solar_constant
from pvgisprototype.cli.typer_parameters import typer_option_days_in_a_year
from pvgisprototype.cli.typer_parameters import typer_option_perigee_offset
from pvgisprototype.cli.typer_parameters import typer_option_eccentricity
from pvgisprototype.cli.typer_parameters import typer_option_time_output_units
from pvgisprototype.cli.typer_parameters import typer_option_angle_units
from pvgisprototype.cli.typer_parameters import typer_option_angle_output_units
from pvgisprototype.cli.typer_parameters import typer_option_rounding_places
from pvgisprototype.cli.typer_parameters import typer_option_verbose


AOIConstants = []
AOIConstants.append(-0.074)
AOIConstants.append(0.155)


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"Calculate reflected solar irradiance",
)


# @app.command('reflected', no_args_is_help=True)
@app.callback(
       invoke_without_command=True,
       no_args_is_help=True,
       # context_settings={"ignore_unknown_options": True},
       help=f'Calculate the clear-sky ground reflected irradiance',
       )
def calculate_ground_reflected_inclined_irradiance(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    surface_tilt: Annotated[Optional[float], typer_argument_surface_tilt] = 45,
    surface_orientation: Annotated[Optional[float], typer_argument_surface_orientation] = 180,
    linke_turbidity_factor: Annotated[Optional[float], typer_option_linke_turbidity_factor] = 2,
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = True,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = 1.5853349194640094,  # radians
    albedo: Annotated[Optional[float], typer_option_albedo] = 2,
    direct_horizontal_component: Annotated[Optional[Path], typer_option_direct_horizontal_component] = None,
    apply_angular_loss_factor: Annotated[Optional[bool], typer_option_apply_angular_loss_factor] = True,
    solar_time_model: Annotated[SolarTimeModels, typer_option_solar_time_model] = SolarTimeModels.skyfield,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = 0,
    hour_offset: Annotated[float, typer_option_hour_offset] = 0,
    solar_constant: Annotated[float, typer_argument_solar_constant] = SOLAR_CONSTANT,
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = 365.25,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = 0.048869,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity] = 0.01672,
    time_output_units: Annotated[str, typer_option_time_output_units] = 'minutes',
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = 'radians',
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = 5,
    verbose: Annotated[Optional[bool], typer_option_verbose]= False,
):
    """Calculate the clear-sky diffuse ground reflected irradiance on an inclined surface (Ri).

    The calculation relies on an isotropic assumption. The ground reflected
    clear-sky irradiance received on an inclined surface [W.m-2] is
    proportional to the global horizontal irradiance Ghc, to the mean ground
    albedo ρg and a fraction of the ground viewed by an inclined surface
    rg(γN).
    """
    # from the model
    direct_horizontal_component = calculate_direct_horizontal_irradiance(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamp=timestamp,
        timezone=timezone,
        linke_turbidity_factor=linke_turbidity_factor,
        solar_time_model=solar_time_model,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        solar_constant=solar_constant,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        angle_output_units=angle_output_units,
    )

    # G0
    # day_of_year = timestamp.timetuple().tm_yday
    extraterrestial_normal_irradiance = calculate_extraterrestrial_normal_irradiance(timestamp)

    # extraterrestrial on a horizontal surface requires the solar altitude
    # solar_altitude, solar_altitude_units = calculate_solar_altitude(
    solar_altitude = model_solar_altitude(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        solar_time_model=solar_time_model,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
        )

    # on a horizontal surface : G0h = G0 sin(h0)
    extraterrestial_horizontal_irradiance = extraterrestial_normal_irradiance * sin(solar_altitude.value)

    # Dhc [W.m-2]
    diffuse_horizontal_component = (
        extraterrestial_normal_irradiance
        * diffuse_transmission_function(solar_altitude.value)
        * diffuse_solar_altitude_function(solar_altitude.value, linke_turbidity_factor)
    )
    global_horizontal_irradiance = direct_horizontal_component + diffuse_horizontal_component

    ground_view_fraction = (1 - cos(surface_tilt)) / 2

    # clear-sky ground reflected irradiance
    ground_reflected_irradiance = albedo * global_horizontal_irradiance * ground_view_fraction

    if apply_angular_loss_factor:
        ground_reflected_irradiance_angular_loss_coefficient = sin(surface_tilt) + (surface_tilt - sin(surface_tilt)) / (1 - cos(surface_tilt))
        ground_reflected_irradiance_loss_factor = calculate_angular_loss_factor_for_nondirect_irradiance(
            angular_loss_coefficient=ground_reflected_irradiance_angular_loss_coefficient,
            solar_incidence_angle_1=AOIConstants[0],
            solar_incidence_angle_2=AOIConstants[1],
        )
        ground_reflected_irradiance *= ground_reflected_irradiance_loss_factor

    typer.echo(ground_reflected_irradiance)

    return ground_reflected_irradiance
