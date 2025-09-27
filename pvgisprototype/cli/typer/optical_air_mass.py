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

## Optical air mass

from typing import List

import numpy as np
import typer
from typer import Context

from pvgisprototype import OpticalAirMass
from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_atmospheric_properties,
)
from pvgisprototype.constants import OPTICAL_AIR_MASS_DEFAULT, OPTICAL_AIR_MASS_UNIT


def parse_optical_air_mass(optical_air_mass_input: str):
    if isinstance(optical_air_mass_input, str):
        optical_air_mass_strings = optical_air_mass_input.split(",")
        return optical_air_mass_strings
    else:
        return optical_air_mass_input


def optical_air_mass_callback(value: str, ctx: Context):
    """Callback to handle the optical air mass series input or provide a default series."""
    if value:
        return OpticalAirMass(value=value, unit=OPTICAL_AIR_MASS_UNIT)


typer_option_optical_air_mass = typer.Option(
    help=f"Relative optical air mass [{OPTICAL_AIR_MASS_UNIT}]",
    rich_help_panel=rich_help_panel_atmospheric_properties,
    # default_factory=OPTICAL_AIR_MASS_DEFAULT,
    callback=optical_air_mass_callback,
)

## Optical air mass series


def parse_optical_air_mass_series(optical_air_mass_factor_input: str) -> List[float]:
    """Parse a string of optical air mass values separated by commas into a list of floats."""
    if isinstance(optical_air_mass_factor_input, str):
        optical_air_mass_factor_strings = optical_air_mass_factor_input.split(",")
        optical_air_mass_factor_series = [
            optical_air_mass_factor
            for optical_air_mass_factor in optical_air_mass_factor_strings
        ]
        return optical_air_mass_factor_series
    else:
        return optical_air_mass_factor_input


def optical_air_mass_series_callback(value: str, ctx: Context):
    """Callback to handle the optical air mass series input or provide a default series."""
    timestamps = ctx.params.get("timestamps")
    optical_air_mass = np.array([OPTICAL_AIR_MASS_DEFAULT for _ in timestamps])
    return OpticalAirMass(value=optical_air_mass, unit=OPTICAL_AIR_MASS_UNIT)


typer_option_optical_air_mass_series = typer.Option(
    help=f"Relative optical air mass series [{OPTICAL_AIR_MASS_UNIT}]",
    parser=parse_optical_air_mass_series,
    callback=optical_air_mass_series_callback,
    rich_help_panel=rich_help_panel_atmospheric_properties,
    # default_factory=OPTICAL_AIR_MASS_DEFAULT,
)
