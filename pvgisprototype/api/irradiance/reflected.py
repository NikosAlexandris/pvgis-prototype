from devtools import debug
import typer
from typing import Annotated
from typing import Optional
from .loss import calculate_angular_loss_factor_for_nondirect_irradiance
from pvgisprototype.api.geometry.time_models import SolarTimeModels
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
from pvgisprototype.api.geometry.solar_altitude import calculate_solar_altitude
from pvgisprototype.api.geometry.solar_azimuth import calculate_solar_azimuth
from pvgisprototype.models.standard.solar_incidence import calculate_solar_incidence
from math import sin
from math import cos
from .diffuse import diffuse_transmission_function
from .diffuse import diffuse_solar_altitude_function
from .constants import SOLAR_CONSTANT


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
    longitude: Annotated[float, typer.Argument(
        callback=convert_to_radians, min=-180, max=180)],
    latitude: Annotated[float, typer.Argument(
        callback=convert_to_radians, min=-90, max=90)],
    elevation: Annotated[float, typer.Argument(
        min=0, max=8848,
        help='Elevation',)],
        # rich_help_panel=rich_help_panel_geometry_surface)],
    timestamp: Annotated[Optional[datetime], typer.Argument(
        help='Timestamp',
        default_factory=now_utc_datetimezone)],
    timezone: Annotated[Optional[str], typer.Option(
        help='Timezone',
        callback=ctx_convert_to_timezone)] = None,
    surface_tilt: Annotated[Optional[float], typer.Option(
        min=0, max=90,
        help='Solar surface tilt angle',
        callback=convert_to_radians,
        rich_help_panel=rich_help_panel_geometry_surface)] = 45,
    surface_orientation: Annotated[Optional[float], typer.Option(
        min=0, max=360,
        help='Solar surface orientation angle. [yellow]Due north is 0 degrees.[/yellow]',
        callback=convert_to_radians,
        rich_help_panel=rich_help_panel_geometry_surface)] = 180,  # from North!
    linke_turbidity_factor: Annotated[Optional[float], typer.Option(
        min=0,
        help='Linke turbidity factor',
        rich_help_panel=rich_help_panel_advanced_options)] = 2,
    apply_atmospheric_refraction: Annotated[Optional[bool], typer.Option(
        '-a',
        '--atmospheric-refraction',
        help='Apply atmospheric refraction functions',
        rich_help_panel=rich_help_panel_advanced_options,
        )] = True,
    albedo: Annotated[Optional[float], typer.Option(
        min=0,
        help='Mean ground albedo',
        rich_help_panel=rich_help_panel_advanced_options)] = 2,
    direct_horizontal_component: Annotated[Optional[Path], typer.Option(
        help='Read horizontal irradiance time series data from a file',)] = None,
    apply_angular_loss_factor: Annotated[Optional[bool], typer.Option(
        help='Apply angular loss function',
        rich_help_panel=rich_help_panel_advanced_options)] = True,
    solar_time_model: Annotated[SolarTimeModels, typer.Option(
        '-m',
        '--solar-time-model',
        help="Model to calculate solar position",
        show_default=True,
        show_choices=True,
        case_sensitive=False,
        rich_help_panel=rich_help_panel_advanced_options)] = SolarTimeModels.skyfield,
    time_offset_global: Annotated[float, typer.Option(
        help='Global time offset',
        rich_help_panel=rich_help_panel_advanced_options)] = 0,
    hour_offset: Annotated[float, typer.Option(
        help='Hour offset',
        rich_help_panel=rich_help_panel_advanced_options)] = 0,
    solar_constant: Annotated[float, typer.Argument(
        min=1360,
        help="The mean solar electromagnetic radiation at the top of the atmosphere (~1360.8 W/m2) one astronomical unit (au) away from the Sun.")] = SOLAR_CONSTANT,
    days_in_a_year: Annotated[float, typer.Option(
        help='Days in a year',
        rich_help_panel=rich_help_panel_advanced_options)] = 365.25,
    perigee_offset: Annotated[float, typer.Option(
        help='Perigee offset',
        rich_help_panel=rich_help_panel_advanced_options)] = 0.048869,
    eccentricity: Annotated[float, typer.Option(
        help='Eccentricity',
        rich_help_panel=rich_help_panel_advanced_options)] = 0.01672,
    time_output_units: Annotated[str, typer.Option(
        '--time-output-units',
        show_default=True,
        case_sensitive=False,
        help="Time units for output and internal calculations (seconds, minutes or hours) - :warning: [bold red]Keep fingers away![/bold red]",
        rich_help_panel=rich_help_panel_advanced_options)] = 'minutes',
    angle_units: Annotated[str, typer.Option(
        show_default=True,
        case_sensitive=False,
        help="Angular units for internal solar geometry calculations. :warning: [bold red]Keep fingers away![/bold red]",
        rich_help_panel=rich_help_panel_advanced_options)] = 'radians',
    angle_output_units: Annotated[str, typer.Option(
        '-u',
        show_default=True,
        case_sensitive=False,
        help="Angular units for solar geometry calculations (degrees or radians). :warning: [bold red]Under development[/red bold]",
        rich_help_panel=rich_help_panel_advanced_options)] = 'radians',
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
        eccentricity=eccentricity,
        angle_output_units=angle_output_units,
    )

    # G0
    day_of_year = timestamp.timetuple().tm_yday
    extraterrestial_normal_irradiance = calculate_extraterrestrial_normal_irradiance(day_of_year)

    # extraterrestrial on a horizontal surface requires the solar altitude
    solar_altitude, solar_altitude_units = calculate_solar_altitude(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity=eccentricity,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        solar_time_model=solar_time_model,
        angle_output_units=angle_output_units,
    )

    # on a horizontal surface : G0h = G0 sin(h0)
    extraterrestial_horizontal_irradiance = extraterrestial_normal_irradiance * sin(solar_altitude)

    # Dhc [W.m-2]
    diffuse_horizontal_component = (
        extraterrestial_normal_irradiance
        * diffuse_transmission_function(solar_altitude)
        * diffuse_solar_altitude_function(solar_altitude, linke_turbidity_factor)
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
