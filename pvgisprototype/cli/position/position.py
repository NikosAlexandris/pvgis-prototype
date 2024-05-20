"""
Important sun and solar surface geometry parameters in calculating the amount of solar radiation that reaches a particular location on the Earth's surface
"""

import typer
from rich import print
from typing import Annotated
from typing import Optional
from pvgisprototype.cli.typer.group import OrderCommands
from pvgisprototype.cli.typer.verbosity import typer_option_verbose
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_introduction
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_overview
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_solar_position
from pvgisprototype.cli.position.introduction import introduction
from pvgisprototype.cli.position.overview_series import overview_series
from pvgisprototype.cli.position.declination import declination
from pvgisprototype.cli.position.hour_angle import hour_angle
from pvgisprototype.cli.position.sunrise import sunrise
from pvgisprototype.cli.position.zenith import zenith
from pvgisprototype.cli.position.altitude import altitude
from pvgisprototype.cli.position.azimuth import azimuth
from pvgisprototype.cli.position.incidence import incidence
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT


# state = {"verbose": False}


app = typer.Typer(
    cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f":triangular_ruler: Calculate solar geometry parameters for a location and moment in time",
)


@app.callback()
def main(
    ctx: typer.Context,
    verbose: Annotated[Optional[int], typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    debug: Annotated[Optional[bool], typer.Option(
        "--debug",
        help="Enable debug mode")] = False,
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
    name='introduction',
    help='A short primer on solar geometry',
    no_args_is_help=False,
    rich_help_panel=rich_help_panel_introduction,
)(introduction)
app.command(
    'overview-series',
    help='⦩⦬📈 Calculate series of solar position parameters',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_overview,
)(overview_series)
app.command(
    'declination',
    help='∢ Calculate the solar declination',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_solar_position,
)(declination)
app.command(
    'zenith',
    help=f' Calculate the solar zenith',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_solar_position,
)(zenith)
app.command(
    'hour-angle',
    help=':clock12: :globe_with_meridians: Calculate the hour angle (ω)',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_solar_position,
)(hour_angle)
app.command(
    'sun-rise-set',
     help=':sunrise: Calculate the hour angle (ω) at sun rise and set',
     no_args_is_help=True,
    rich_help_panel=rich_help_panel_solar_position,
)(sunrise)
app.command(
    'altitude',
    help=f'⦩ Calculate the solar altitude',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_solar_position,
)(altitude)
app.command(
    'azimuth',
    help='⦬ Calculate the solar azimuth',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_solar_position,
)(azimuth)
app.command(
    'incidence',
    help=f'⭸ Calculate the solar incidence angle',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_solar_position,
)(incidence)


if __name__ == "__main__":
    # import sys
    # commands = {'all', 'altitude', 'azimuth'}
    # sys.argv.insert(1, 'all') if sys.argv[1] not in commands else None
    app()
