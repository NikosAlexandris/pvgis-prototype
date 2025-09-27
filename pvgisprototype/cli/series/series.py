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
import typer
from pvgisprototype.cli.messages import NOT_IMPLEMENTED_CLI
from pvgisprototype.cli.typer.group import OrderCommands
from pvgisprototype.cli.series.introduction import series_introduction
from pvgisprototype.cli.series.inspect import inspect_xarray_supported_data
from pvgisprototype.cli.series.select import select, select_fast, select_sarah
from pvgisprototype.cli.series.resample import resample
from pvgisprototype.cli.series.plot import plot
from pvgisprototype.cli.series.uniplot import uniplot
from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_introduction,
    rich_help_panel_plotting,
    rich_help_panel_series,
)
from pvgisprototype.constants import SYMBOL_CHART_CURVE, SYMBOL_GROUP, SYMBOL_PLOT, SYMBOL_SELECT


app = typer.Typer(
    cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"{SYMBOL_CHART_CURVE} Work with time series",
)
app.command(
    name="introduction",
    # no_args_is_help=False,
    help="  Introduction on the [cyan]series[/cyan] command",
    rich_help_panel=rich_help_panel_introduction,
)(series_introduction)
app.command(
    name="inspect",
    help="Inspect an Xarray-supported data file format",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series,
)(inspect_xarray_supported_data)
app.command(
    "select",
    no_args_is_help=True,
    help="  Select time series over a location",
    rich_help_panel=rich_help_panel_series,
)(select)
app.command(
    "select-sarah",
    no_args_is_help=True,
    help="  Select SARAH time series over a location",
)(select_sarah)
app.command(
    "select-fast",
    no_args_is_help=True,
    help=f"{SYMBOL_SELECT} Retrieve series over a location.-",
    rich_help_panel=rich_help_panel_series,
)(select_fast)
app.command(
    name="resample",
    no_args_is_help=True,
    help=f"{SYMBOL_GROUP} Group-by of time series over a location {NOT_IMPLEMENTED_CLI}",
    rich_help_panel=rich_help_panel_series,
)(resample)
app.command(
    name="plot",
    no_args_is_help=True,
    help=f"{SYMBOL_PLOT} Plot time series",
    rich_help_panel=rich_help_panel_plotting,
)(plot)
app.command(
    name="uniplot",
    no_args_is_help=True,
    help="  Plot time series in the terminal",
    rich_help_panel=rich_help_panel_plotting,
)(uniplot)


if __name__ == "__main__":
    app()
