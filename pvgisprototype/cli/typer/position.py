"""
Solar position and solar surface position parameters 
"""

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
from pvgisprototype.api.position.models import SolarIncidenceModel
from pvgisprototype.api.utilities.conversions import convert_to_radians
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_solar_position
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_earth_orbit
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_geometry_surface


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
typer_option_solar_declination_model = typer.Option(
    help='Model to calculate the solar declination angle',
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    # callback=_parse_model,  # This did not work!
    rich_help_panel=rich_help_panel_solar_position,
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

typer_option_solar_incidence_model = typer.Option(
    '--solar-incidence-model',
    help='Method to calculate the solar incidence angle',
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    rich_help_panel=rich_help_panel_solar_position,
)

# Solar position

typer_option_solar_position_model = typer.Option(
    '--solar-position-model',
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

# Solar surface parameters 

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
    callback=surface_tilt_callback,
    rich_help_panel=rich_help_panel_geometry_surface,
    # default_factory = SURFACE_TILT_DEFAULT,
    show_default=False,
)
typer_option_surface_tilt = typer.Option(
    help=surface_tilt_typer_help,
    min=SURFACE_TILT_MINIMUM,
    max=SURFACE_TILT_MAXIMUM,
    callback=surface_tilt_callback,
    rich_help_panel=rich_help_panel_geometry_surface,
    # default_factory = SURFACE_TILT_DEFAULT,
)
typer_option_random_surface_tilt = typer.Option(
    help='Random solar surface tilt angle',
    # min=SURFACE_TILT_MINIMUM,
    # max=SURFACE_TILT_MAXIMUM,
    # callback=random_surface_tilt,
    rich_help_panel=rich_help_panel_geometry_surface,
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
surface_orientation_typer_help='Solar surface orientation angle. [yellow]Due north is 0 degrees.[/yellow]'  # also known as : azimuth, in PVGIS : aspect
# Note, in PVGIS : '0=south, 90=west, -90=east' ? ----------------------------
typer_argument_surface_orientation = typer.Argument(
    help=surface_orientation_typer_help,
    min=SURFACE_ORIENTATION_MINIMUM,
    max=SURFACE_ORIENTATION_MAXIMUM,
    callback=convert_to_radians,
    rich_help_panel=rich_help_panel_geometry_surface,
    # default_factory = SURFACE_ORIENTATION_DEFAULT,
    show_default=False,
)
typer_option_surface_orientation = typer.Option(
    help=surface_orientation_typer_help,
    min=SURFACE_ORIENTATION_MINIMUM,
    max=SURFACE_ORIENTATION_MAXIMUM,
    callback=convert_to_radians,
    rich_help_panel=rich_help_panel_geometry_surface,
    # default_factory = SURFACE_ORIENTATION_DEFAULT,
)
typer_option_random_surface_orientation = typer.Option(
    help='Random solar surface orientation angle. [yellow]Due north is 0 degrees.[/yellow]',
    # min=SURFACE_ORIENTATION_MINIMUM,
    # max=SURFACE_ORIENTATION_MAXIMUM,
    # callback=random_surface_orientation,
    rich_help_panel=rich_help_panel_geometry_surface,
    # default_factory = SURFACE_ORIENTATION_DEFAULT,
)
