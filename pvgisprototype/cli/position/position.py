"""
Important sun and solar surface position parameters in calculating the amount of solar radiation that reaches a particular location on the Earth's surface
"""

from typing import Annotated

import typer
from rich import print

from pvgisprototype.cli.position.altitude import altitude
from pvgisprototype.cli.position.azimuth import azimuth
from pvgisprototype.cli.position.declination import declination
from pvgisprototype.cli.position.hour_angle import hour_angle
from pvgisprototype.cli.position.shading import in_shade
from pvgisprototype.cli.position.incidence import incidence
from pvgisprototype.cli.position.introduction import introduction
from pvgisprototype.cli.position.overview import overview
from pvgisprototype.cli.position.sunrise import sunrise
from pvgisprototype.cli.position.zenith import zenith
from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_introduction,
    rich_help_panel_overview,
    rich_help_panel_solar_position,
)
from pvgisprototype.cli.typer.group import OrderCommands
from pvgisprototype.cli.typer.verbosity import typer_option_verbose
from pvgisprototype.constants import (
    SYMBOL_ALTITUDE,
    SYMBOL_AZIMUTH,
    SYMBOL_HOUR_ANGLE,
    SYMBOL_INCIDENCE,
    SYMBOL_INTRODUCTION,
    VERBOSE_LEVEL_DEFAULT,
    SYMBOL_SHADING,
    SYMBOL_ZENITH,
)

# state = {"verbose": False}


app = typer.Typer(
    cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=":triangular_ruler: Calculate solar position parameters for a location and moment in time",
)


@app.callback()
def main(
    # ctx: typer.Context,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    debug: Annotated[
        bool, typer.Option("--debug", help="Enable debug mode")
    ] = False,
):
    """
    Solar position algorithms
    """
    # if verbose > 2:
    #     print(f"Executing command: {ctx.invoked_subcommand}")
    if verbose > 0:
        print("Will output verbosely")
        # state["verbose"] = True

    app.debug_mode = debug


app.command(
    name="introduction",
    help=f"{SYMBOL_INTRODUCTION} A short primer on solar position",
    no_args_is_help=False,
    rich_help_panel=rich_help_panel_introduction,
)(introduction)
app.command(
    "overview",
    help="⦩⦬📈 Calculate series of solar position parameters",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_overview,
)(overview)
app.command(
    "declination",
    help="∢ Calculate the solar declination",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_solar_position,
)(declination)
app.command(
    "zenith",
    help=f"{SYMBOL_ZENITH} Calculate the solar zenith",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_solar_position,
)(zenith)
app.command(
    "hour-angle",
    help=f"{SYMBOL_HOUR_ANGLE} Calculate the hour angle (ω)",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_solar_position,
)(hour_angle)
app.command(
    "sun-rise-set",
    help=":sunrise: Calculate the hour angle (ω) at sun rise and set",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_solar_position,
)(sunrise)
app.command(
    "altitude",
    help=f"{SYMBOL_ALTITUDE} Calculate the solar altitude",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_solar_position,
)(altitude)
app.command(
    "azimuth",
    help=f"{SYMBOL_AZIMUTH} Calculate the solar azimuth",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_solar_position,
)(azimuth)
app.command(
    "in-shade",
    help=f"{SYMBOL_SHADING} Determine the surface-in-shade",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_solar_position,
)(in_shade)
app.command(
    "incidence",
    help=f"{SYMBOL_INCIDENCE} Calculate the solar incidence angle",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_solar_position,
)(incidence)


if __name__ == "__main__":
    # import sys
    # commands = {'all', 'altitude', 'azimuth'}
    # sys.argv.insert(1, 'all') if sys.argv[1] not in commands else None
    app()
