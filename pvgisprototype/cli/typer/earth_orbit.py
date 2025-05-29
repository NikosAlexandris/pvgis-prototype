"""
Earh orbit input parameters
"""

import typer

from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_earth_orbit
from pvgisprototype.constants import SOLAR_CONSTANT_MINIMUM

solar_constant_typer_help = "Top-of-Atmosphere mean solar electromagnetic radiation (W/m-2) 1 au (astronomical unit) away from the Sun."  #  (~1360.8 W/m2)


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
typer_option_eccentricity_phase_offset = typer.Option(
    help="Eccentricity phase offset (in radians) aligning the eccentricity correction with Earth's perihelion position in its orbit, part of calculation of the solar declination angle.",
    rich_help_panel=rich_help_panel_earth_orbit,
    # default_factory=PERIGEE_OFFSET,
)
typer_option_eccentricity_amplitude = typer.Option(
    help="Amplitude of the Earth's orbital eccentricity effect on solar irradiance variation throughout the year, part of the calculation of the solar declination angle.",
    rich_help_panel=rich_help_panel_earth_orbit,
    # default_factory=0.ECCENTRICITY_CORRECTION_FACTOR,
)
