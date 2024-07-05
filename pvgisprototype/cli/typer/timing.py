"""
Typer definitions for input parameters related to Solar time
"""

import typer

from pvgisprototype.api.datetime.conversion import convert_hours_to_datetime_time
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_solar_time

typer_option_solar_time_model = typer.Option(
    "--solar-time-model",
    help="Model to calculate solar time",
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    rich_help_panel=rich_help_panel_solar_time,
)
typer_argument_true_solar_time = typer.Argument(
    help="The apparent (or true) solar time in decimal hours on a 24 hour base",
    callback=convert_hours_to_datetime_time,
    rich_help_panel=rich_help_panel_solar_time,
    show_default=False,
)
typer_argument_hour_angle = typer.Argument(
    help="Solar hour angle in radians",
    min=0,
    max=1,
    show_default=False,
)
