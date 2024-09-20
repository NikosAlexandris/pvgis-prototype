"""
Time series

Paramters for external time series datasets.
"""

import typer

from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_time_series_data,
    rich_help_panel_time_series_data_selection,
)

time_series_typer_help = "A time series dataset (any format supported by Xarray)"
typer_argument_time_series = typer.Argument(
    help=time_series_typer_help,
    rich_help_panel=rich_help_panel_time_series_data,
    is_eager=True,
    show_default=False,
)
typer_option_time_series = typer.Option(
    help=time_series_typer_help,
    show_default=False,
    is_eager=True,
    rich_help_panel=rich_help_panel_time_series_data,
)
typer_option_data_variable = typer.Option(
    help="Variable name",
    show_default=False,
    rich_help_panel=rich_help_panel_time_series_data_selection,
)
typer_option_mask_and_scale = typer.Option(
    help="Mask and scale the series",
    rich_help_panel=rich_help_panel_time_series_data_selection,
)
typer_option_nearest_neighbor_lookup = typer.Option(
    help="Enable nearest neighbor (inexact) lookups. Read Xarray manual on [underline]nearest-neighbor-lookups[/underline]",
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    rich_help_panel=rich_help_panel_time_series_data_selection,
)
typer_option_tolerance = typer.Option(
    help="Maximum distance between original & new labels for inexact matches. Read Xarray manual on [underline]nearest-neighbor-lookups[/underline]",
    #  https://docs.xarray.dev/en/stable/user-guide/indexing.html#nearest-neighbor-lookups',
    rich_help_panel=rich_help_panel_time_series_data_selection,
)
typer_option_in_memory = typer.Option(
    help="Use in-memory processing",  # You may need to customize the help text
    rich_help_panel=rich_help_panel_time_series_data_selection,
)
