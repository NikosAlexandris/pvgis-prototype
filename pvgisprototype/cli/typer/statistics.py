"""
Statistics related options
"""

import typer
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_statistics


typer_option_statistics = typer.Option(
    help='Calculate and display summary statistics',
    rich_help_panel=rich_help_panel_statistics,
)
typer_option_groupby = typer.Option(
    help=f"Group statistics, ex. M or 3H. A number and date/time unit : (Y)ear, (M)onth, (D)ay, (W)eek, (S)eason. See Xarray\'s group-by operations.",
    rich_help_panel=rich_help_panel_statistics,
)
