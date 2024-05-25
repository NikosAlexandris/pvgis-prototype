"""
Solar position and solar surface position parameters 
"""

from enum import Enum
from devtools import debug
from numpy import positive
import typer
from pvgisprototype.constants import SOLAR_DECLINATION_MINIMUM
from pvgisprototype.constants import SOLAR_DECLINATION_MAXIMUM
from pvgisprototype.constants import SOLAR_CONSTANT_MINIMUM
from pvgisprototype.constants import SURFACE_ORIENTATION_MINIMUM
from pvgisprototype.constants import SURFACE_ORIENTATION_MAXIMUM
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_MINIMUM
from pvgisprototype.constants import SURFACE_TILT_MAXIMUM
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.api.position.models import SolarIncidenceModel, SolarPositionParameter, select_models
from pvgisprototype.api.utilities.conversions import convert_to_radians
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_solar_position
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_earth_orbit
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_surface_geometry
from typing import List, Sequence


def solar_position_parameter_callback(
    ctx: typer.Context,
    position_parameter: List[Enum],
) -> Sequence[Enum]:
    """Set the default surface tilt equal to the latitude
    """
    uniplot = ctx.params.get('uniplot')
    if uniplot:
        from pvgisprototype.log import logger
        logger.warning(
            f'Attention ! You asked for a uniplot along with {ctx.command.name} and I think its less consfusing to only plot the incidence along with the altitude and azimuth angles!',
            # alt=f'Attention ! You are running [code]{ctx.command.name}[/code] which expected multiple surface tilt angles!',
        )
        position_parameter = [SolarPositionParameter.altitude,
                SolarPositionParameter.azimuth,
                SolarPositionParameter.incidence]

    debug(locals())
    return select_models(SolarPositionParameter, position_parameter)
    # return position_parameter


typer_option_solar_position_parameter = typer.Option(
    '--solar-position-parameter',
    '--position-parameter',
    help='Solar position parameter to calculate',
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    # callback=solar_position_parameter_callback,  # This did not work!
    rich_help_panel=rich_help_panel_solar_position,
)
typer_option_solar_declination_model = typer.Option(
    '--solar-declination-model',
    '--declination-model',
    help='Model to calculate the solar declination angle',
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    # callback=_parse_model,  # This did not work!
    rich_help_panel=rich_help_panel_solar_position,
)
typer_argument_solar_declination = typer.Argument(
    help='Solar declination angle',
    min=SOLAR_DECLINATION_MINIMUM,
    max=SOLAR_DECLINATION_MAXIMUM,
    callback=convert_to_radians,
    show_default=False,
)
typer_option_solar_declination = typer.Option(
    help='Solar declination angle',
    min=SOLAR_DECLINATION_MINIMUM,
    max=SOLAR_DECLINATION_MAXIMUM,
    callback=convert_to_radians,
)
solar_constant_typer_help='Top-of-Atmosphere mean solar electromagnetic radiation (W/m-2) 1 au (astronomical unit) away from the Sun.'  #  (~1360.8 W/m2)
typer_argument_solar_constant = typer.Argument(
    help=solar_constant_typer_help,
    min=SOLAR_CONSTANT_MINIMUM,
    rich_help_panel=rich_help_panel_earth_orbit,
    # default_factory = SOLAR_CONSTANT,
    show_default=False,
)
typer_option_solar_constant = typer.Option(
    help=solar_constant_typer_help,
    min=SOLAR_CONSTANT_MINIMUM,
    rich_help_panel=rich_help_panel_earth_orbit,
    # default_factory = SOLAR_CONSTANT,
)
typer_option_solar_position_model = typer.Option(
    '--solar-position-model',
    '--position-model',
    help='Model to calculate solar position',
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    # callback=_parse_model,  # This did not work!
    rich_help_panel=rich_help_panel_solar_position,
)
typer_argument_solar_altitude = typer.Argument(
    help='Solar altitude',
    rich_help_panel=rich_help_panel_solar_position,
    show_default=False,
)
typer_argument_solar_altitude_series = typer.Argument(
    help='Solar altitude series',
    rich_help_panel=rich_help_panel_solar_position,
    show_default=False,
)
typer_argument_refracted_solar_altitude = typer.Argument(
    help='Refracted solar altitude',
    rich_help_panel=rich_help_panel_solar_position,
)
typer_argument_refracted_solar_altitude_series = typer.Argument(
    help='Refracted solar altitude',
    rich_help_panel=rich_help_panel_solar_position,
)
typer_option_solar_incidence_model = typer.Option(
    '--solar-incidence-model',
    '--incidence-model',
    help='Method to calculate the solar incidence angle',
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    rich_help_panel=rich_help_panel_solar_position,
)
typer_option_sun_to_surface_plane_incidence_angle = typer.Option(
    '--sun-vector-to-surface-plane/--sun-vector-to-surface-normal',
    '--sun-to-plane/--sun-to-normal',
    help='Incidence angle between Sun-Vector and Surface- Normal or Plane',
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    rich_help_panel=rich_help_panel_solar_position,
)
typer_argument_solar_incidence = typer.Argument(
    help='Solar incidence',
    rich_help_panel=rich_help_panel_solar_position,
    show_default=False,
)
typer_argument_solar_incidence_series = typer.Argument(
    help='Solar incidence series',
    rich_help_panel=rich_help_panel_solar_position,
    show_default=False,
)

typer_option_zero_negative_solar_incidence_angle = typer.Option(
    '--zero-negative-solar-incidence-angle/--do-not-zero-negative-solar-incidence-angle',
    '--zero-negative-incidence-angle/--do-not-zero-negative-incidence-angle',
    '--zero-negative-incidence/--do-not-zero-negative-incidence',
    help='Zero negative solar incidence angles',
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    rich_help_panel=rich_help_panel_solar_position,
)

# Solar surface parameters 

surface_orientation_typer_help='Solar surface orientation angle. [yellow]Due north is 0 degrees.[/yellow]'  # also known as : azimuth, in PVGIS : aspect
# Note, in PVGIS : '0=south, 90=west, -90=east' ? ----------------------------
typer_argument_surface_orientation = typer.Argument(
    help=surface_orientation_typer_help,
    min=SURFACE_ORIENTATION_MINIMUM,
    max=SURFACE_ORIENTATION_MAXIMUM,
    is_eager=True,
    callback=convert_to_radians,
    rich_help_panel=rich_help_panel_surface_geometry,
    show_default=False,
)
typer_option_surface_orientation = typer.Option(
    help=surface_orientation_typer_help,
    min=SURFACE_ORIENTATION_MINIMUM,
    max=SURFACE_ORIENTATION_MAXIMUM,
    is_eager=True,
    callback=convert_to_radians,
    rich_help_panel=rich_help_panel_surface_geometry,
)
typer_option_random_surface_orientation = typer.Option(
    help='Random solar surface orientation angle. [yellow]Due north is 0 degrees.[/yellow]',
    # min=SURFACE_ORIENTATION_MINIMUM,
    # max=SURFACE_ORIENTATION_MAXIMUM,
    # callback=random_surface_orientation,
    rich_help_panel=rich_help_panel_surface_geometry,
    # default_factory = SURFACE_ORIENTATION_DEFAULT,
)


def surface_tilt_callback(
    ctx: typer.Context,
    # param: typer.CallbackParam,
    surface_tilt: float,
) -> float:
    """Set the default surface tilt equal to the latitude

    Notes
    -----
    Redesign Me ?

    """
    if ctx.resilient_parsing:
        return
    
    if not surface_tilt:
        surface_tilt = ctx.params.get('latitude')
        from rich import print
        print(f'[yellow]* Surface tilt set to match the input latitude[/yellow]!')
    else:
        from math import radians
        surface_tilt = radians(surface_tilt)

    return surface_tilt


surface_tilt_typer_help='Solar surface tilt angle from the horizontal plane'  # in PVGIS : slope
typer_argument_surface_tilt = typer.Argument(
    help=surface_tilt_typer_help,
    min=SURFACE_TILT_MINIMUM,
    max=SURFACE_TILT_MAXIMUM,
    is_eager=True,
    callback=surface_tilt_callback,
    rich_help_panel=rich_help_panel_surface_geometry,
    # default_factory = SURFACE_TILT_DEFAULT,
    show_default=False,
)
typer_option_surface_tilt = typer.Option(
    help=surface_tilt_typer_help,
    min=SURFACE_TILT_MINIMUM,
    max=SURFACE_TILT_MAXIMUM,
    is_eager=True,
    callback=surface_tilt_callback,
    rich_help_panel=rich_help_panel_surface_geometry,
    # default_factory = SURFACE_TILT_DEFAULT,
)
typer_option_random_surface_tilt = typer.Option(
    help='Random solar surface tilt angle',
    # min=SURFACE_TILT_MINIMUM,
    # max=SURFACE_TILT_MAXIMUM,
    # callback=random_surface_tilt,
    is_eager=True,
    rich_help_panel=rich_help_panel_surface_geometry,
    # default_factory = SURFACE_TILT_DEFAULT,
)
typer_option_optimise_surface_tilt = typer.Option(
    help='Optimise inclination for a fixed PV system',  # in PVGIS : optimalinclination
    # default_factory = OPTIMISE_SURFACE_TILT_FLAG_DEFAULT,
)
typer_option_optimise_surface_geometry = typer.Option(
    help='Optimise inclination and orientation for a fixed PV system',  # in PVGIS : optimalangles
    # default_factory = OPTIMISE_SURFACE_GEOMETRY_FLAG_DEFAULT,
)


def parse_surface_orientation_multi(
   surface_orientation_multi_input: str,
):
    if isinstance(surface_orientation_multi_input, str):
        return list(map(float, surface_orientation_multi_input.split(","))) 
    
    return surface_orientation_multi_input


def surface_orientation_multi_callback(
    ctx: typer.Context,
    surface_orientation_multi: list[float],
):
    if len(surface_orientation_multi) == 1:
        from pvgisprototype.log import logger
        logger.warning(
            f'Attention ! You are running {ctx.command.name} which expected multiple surface orientation angles!',
            alt=f'Attention ! You are running [code]{ctx.command.name}[/code] which expected multiple surface orientation angles!',
        )
    # Change to convert to radians if requested
    surface_orientation_multi_output = [convert_to_radians(ctx, None, surface_orientation) for surface_orientation in surface_orientation_multi]
    return surface_orientation_multi_output     


surface_orientation_multi_help='Multiple solar surface orientation angles.'
typer_option_surface_orientation_multi = typer.Option(
    help=surface_orientation_multi_help,
    rich_help_panel=rich_help_panel_surface_geometry,
    is_eager=True,
    parser=parse_surface_orientation_multi,
    callback=surface_orientation_multi_callback,
    show_default=False,
)


def parse_surface_tilt_multi(
   surface_tilt_multi_input: str,
):
    if isinstance(surface_tilt_multi_input, str):
        return list(map(float, surface_tilt_multi_input.split(","))) 
    
    return surface_tilt_multi_input


def surface_tilt_multi_callback(
    ctx: typer.Context,
    surface_tilt_multi: list[float],
):
    if len(surface_tilt_multi) == 1:
        from pvgisprototype.log import logger
        logger.warning(
            f'Attention ! You are running {ctx.command.name} which expected multiple surface tilt angles!',
            alt=f'Attention ! You are running [code]{ctx.command.name}[/code] which expected multiple surface tilt angles!',
        )
    surface_tilt_multi_output = [convert_to_radians(ctx, None, surface_tilt) for surface_tilt in surface_tilt_multi]
    return surface_tilt_multi_output       


surface_tilt_multi_help='Multiple solar surface tilt angles from the horizontal plane.'
typer_option_surface_tilt_multi = typer.Option(
    help=surface_tilt_multi_help,
    rich_help_panel=rich_help_panel_surface_geometry,
    parser=parse_surface_tilt_multi,
    callback=surface_tilt_multi_callback,
    show_default=False,
)
