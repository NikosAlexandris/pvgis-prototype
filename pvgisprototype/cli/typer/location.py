"""
Solar time

Parameters that relate to the question "Where ?".
"""

import typer

from pvgisprototype.api.utilities.conversions import convert_to_radians
from pvgisprototype.constants import (
    ELEVATION_MAXIMUM,
    ELEVATION_MINIMUM,
    LATITUDE_MAXIMUM,
    LATITUDE_MINIMUM,
    LONGITUDE_MAXIMUM,
    LONGITUDE_MINIMUM,
)

longitude_typer_help = "Longitude in decimal degrees ranging in [-180, 360]. [yellow]If ranging in [0, 360], consider the `--convert-longitude-360` option.[/yellow]"
typer_argument_longitude = typer.Argument(
    help=longitude_typer_help,
    min=LONGITUDE_MINIMUM,
    max=LONGITUDE_MAXIMUM,
    callback=convert_to_radians,
    # callback=convert_to_Longitude,
    show_default=False,
)
typer_argument_longitude_in_degrees = typer.Argument(
    help=longitude_typer_help,
    min=LONGITUDE_MINIMUM,
    max=LONGITUDE_MAXIMUM,
    show_default=False,
)
latitude_typer_help = "Latitude in decimal degrees ranging in [-90, 90]"
typer_argument_latitude = typer.Argument(
    help=latitude_typer_help,
    min=LATITUDE_MINIMUM,
    max=LATITUDE_MAXIMUM,
    callback=convert_to_radians,
    show_default=False,
)
typer_argument_latitude_in_degrees = typer.Argument(
    help=latitude_typer_help,
    min=LATITUDE_MINIMUM,
    max=LATITUDE_MAXIMUM,
    show_default=False,
)
typer_argument_elevation = typer.Argument(
    help="Topographical elevation",
    min=ELEVATION_MINIMUM,
    max=ELEVATION_MAXIMUM,
    # rich_help_panel=rich_help_panel_geometry_surface,
    # default_factory=0,
    show_default=False,
)
typer_argument_horizon_heights = typer.Option(
    help="List of horizon heights (comma-separated values or .csv file) at equal angular distance around the horizon given in clockwise direction starting at North, going to East, South, West, and back to North (first point is due north, last is west of north). Example: 10, 20, 30, 20, 5, 0, 10, 20, 5, 0, 10, 20, 30, 20, 5, 0, 10, 20, 5, 0",
    # default_factory = None,
    show_default=False,
)
