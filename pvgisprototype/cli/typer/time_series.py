#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
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
