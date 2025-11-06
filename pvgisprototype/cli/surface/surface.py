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
from rich.console import Console
from pvgisprototype.cli.messages import NOT_IMPLEMENTED_CLI
from pvgisprototype.cli.surface.elevation import get_elevation
from pvgisprototype.cli.surface.horizon import get_horizon
from pvgisprototype.cli.surface.optimiser import optimal_surface_position
from pvgisprototype.cli.typer.group import OrderCommands
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_surface
from pvgisprototype.constants import SYMBOL_ELEVATION, SYMBOL_HORIZON, SYMBOL_ORIENTATION, SYMBOL_TILT


app = typer.Typer(
    cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help="󰶛  Calculate solar surface geometry parameters for a location and moment in time",
)
console = Console()


app.command(
    "optimise",
    help=f"{SYMBOL_ORIENTATION}{SYMBOL_TILT} Optimise the position of a solar surface for maximum photovoltaic performance",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_surface,
)(optimal_surface_position)
app.command(
    "horizon",
    no_args_is_help=True,
    help=f"{SYMBOL_HORIZON} Calculate the horizon profile around a location from a digital elevation model {NOT_IMPLEMENTED_CLI}",
    rich_help_panel=rich_help_panel_surface,
)(get_horizon)
app.command(
    "elevation",
    no_args_is_help=True,
    help=f"{SYMBOL_ELEVATION} Retrieve the elevation for a location from digital elevation data {NOT_IMPLEMENTED_CLI}",
    rich_help_panel=rich_help_panel_surface,
)(get_elevation)
