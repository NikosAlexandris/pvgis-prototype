from devtools import debug
import typer
from typing import Annotated, Optional, Union, List
from rich.console import Console
from pvgisprototype.cli.typer.group import OrderCommands


app = typer.Typer(
    cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"󰶛  Calculate solar surface geometry parameters for a location and moment in time",
)
console = Console()


@app.command('surface-orientation', no_args_is_help=True, help=':compass: Calculate the solar surface orientation (azimuth) [red]Not implemented![/red]')
def surface_orientation():
    """Calculate the surface azimuth angle

    The surface azimuth or orientation (also known as Psi) is the angle between
    the projection on a horizontal plane of the normal to a surface and the
    local meridian, with north through east directions being positive.
    """

    #
    # Update Me
    #

    print('Not implemented')


@app.command('surface-tilt', no_args_is_help=True, help='Calculate the solar surface tile (slope) [red]Not implemented![/red]')
def surface_tilt():
    """Calculate the surface tilt angle

    The surface tilt (or slope, also known as beta) is the angle between the
    plane of the surface and the horizontal plane. A horizontal surface has a
    slope of 0°, and a vertical surface has a slope of 90°.
    """

    #
    # Update Me
    #

    print('Not implemented')
