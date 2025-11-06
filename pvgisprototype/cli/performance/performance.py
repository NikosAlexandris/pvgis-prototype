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

from pvgisprototype.cli.performance.broadband import (
    photovoltaic_power_output_series,
)
from pvgisprototype.cli.performance.broadband_multiple_surfaces import (
    photovoltaic_power_output_series_from_multiple_surfaces,
)
from pvgisprototype.cli.performance.introduction import photovoltaic_performance_introduction
from pvgisprototype.cli.performance.spectral import spectral_photovoltaic_performance_analysis
from pvgisprototype.cli.performance.spectral_effect import spectral_factor
from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_introduction,
    rich_help_panel_performance,
    rich_help_panel_spectral_factor,
)
from pvgisprototype.cli.typer.group import OrderCommands
from pvgisprototype.constants import (
    SYMBOL_EFFICIENCY,
    SYMBOL_BROADBAND_IRRADIANCE,
    SYMBOL_FACTOR,
    SYMBOL_INTRODUCTION,
    SYMBOL_POWER,
    SYMBOL_SPECTRALLY_RESOLVED_IRRADIANCE,
)
from pvgisprototype.cli.messages import NOT_IMPLEMENTED_CLI


app = typer.Typer(
    cls=OrderCommands,
    # pretty_exceptions_short=True,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"{SYMBOL_EFFICIENCY} Estimate the performance of a photovoltaic system over a time series",
)
app.command(
    name="introduction",
    help=f"{SYMBOL_INTRODUCTION} Primer on performance of a photovoltaic system",
    no_args_is_help=False,
    rich_help_panel=rich_help_panel_introduction,
)(photovoltaic_performance_introduction)
app.command(
    name="broadband",
    help=f"{SYMBOL_POWER} {SYMBOL_BROADBAND_IRRADIANCE} {SYMBOL_EFFICIENCY} Estimate the performance of a photovoltaic system based on [bold]broadband irradiance[/bold], ambient temperature and wind speed",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_performance,
)(photovoltaic_power_output_series)
app.command(
    name="broadband-multi",
    help=f"{SYMBOL_POWER} [{SYMBOL_BROADBAND_IRRADIANCE}] {SYMBOL_EFFICIENCY} Estimate the performance of a multiple-surfaces photovoltaic system based on [bold]broadband irradiance[/bold], ambient temperature and wind speed",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_performance,
)(photovoltaic_power_output_series_from_multiple_surfaces)
app.command(
    name="spectral",
    help=f"{SYMBOL_POWER} {SYMBOL_SPECTRALLY_RESOLVED_IRRADIANCE} {SYMBOL_EFFICIENCY} Estimate the performance of a photovoltaic system based on [bold]spectrally resolved irradiance[/bold], ambient temperature or wind speed {NOT_IMPLEMENTED_CLI}",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_performance,)(spectral_photovoltaic_performance_analysis)
# app.command(
#     name="spectral-factor",
#     help="Estimate the spectral factor",
#     no_args_is_help=True,
#     rich_help_panel=rich_help_panel_spectral_factor,
# )(spectral_factor)
# app.command(
#     name="spectral-mismatch",
#     help="Estimate the spectral mismatch",
#     no_args_is_help=True,
#     rich_help_panel=rich_help_panel_performance_toolbox,
# )(spectral_mismatch)
app.command(
    name="spectral-factor",
    help=f"{SYMBOL_SPECTRALLY_RESOLVED_IRRADIANCE} {SYMBOL_FACTOR} Estimate the spectral factor",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_spectral_factor,
)(spectral_factor)
