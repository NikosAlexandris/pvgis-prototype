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
import numpy as np
import typer
from rich import box
from rich.console import Console
from rich.table import Table

from pvgisprototype.api.irradiance.limits import (
    EXTREMELY_RARE_LIMITS,
    PHYSICALLY_POSSIBLE_LIMITS,
    calculate_limits,
)
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_irradiance_series
from pvgisprototype.cli.typer.group import OrderCommands
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT

app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    help="Calculate physically possible irradiance limits",
)


def round_float_values(obj, rounding_places=3):
    if isinstance(obj, float):
        return round(obj, rounding_places)
    elif isinstance(obj, list):
        return [round_float_values(x, rounding_places) for x in obj]
    elif isinstance(obj, dict):
        return {
            key: round_float_values(value, rounding_places)
            for key, value in obj.items()
        }
    elif isinstance(obj, np.ndarray):
        return np.around(obj, roundings=rounding_places)
    else:
        return obj


def print_limits_table(
    limits_dictionary,
    rounding_places=ROUNDING_PLACES_DEFAULT,
):
    """Print table of physically possible irradiance limits"""
    limits_dictionary = round_float_values(limits_dictionary, rounding_places)
    table = Table(box=box.SIMPLE_HEAD)
    table.add_column("Component")
    table.add_column("Min", justify="right")
    table.add_column("Max", justify="right")

    for component, limits in limits_dictionary.items():
        table.add_row(component, str(limits["Min"]), str(limits["Max"]))

    Console().print(table)


@app.command(
    "physical",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)
def calculate_physical_limits(
    solar_zenith: float,
    air_temperature: float = 300,
    rounding_places: int = 5,
):
    """Calculate physically possible limits."""
    limits = calculate_limits(solar_zenith, air_temperature, PHYSICALLY_POSSIBLE_LIMITS)
    print_limits_table(limits_dictionary=limits, rounding_places=rounding_places)
    return limits


@app.command(
    "rare",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)
def calculate_rare_limits(
    solar_zenith: float,
    air_temperature: float = 300,
    rounding_places: int = 5,
):
    """Calculate extremely rare limits."""
    limits = calculate_limits(solar_zenith, air_temperature, EXTREMELY_RARE_LIMITS)
    print_limits_table(limits_dictionary=limits, rounding_places=rounding_places)
    return limits
