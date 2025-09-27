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

from pvgisprototype.cli.irradiance.direct.horizontal import (
    get_direct_horizontal_irradiance_series,
)
from pvgisprototype.cli.irradiance.direct.inclined import (
    get_direct_inclined_irradiance_series,
)
from pvgisprototype.cli.irradiance.direct.normal import (
    get_direct_normal_irradiance_series,
)
from pvgisprototype.cli.irradiance.direct.normal_from_horizontal import (
    get_direct_normal_from_horizontal_irradiance_series,
)
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_irradiance_series
from pvgisprototype.cli.typer.group import OrderCommands


app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=":sun_with_face: Calculate the overcast or estimate the clear-sky direct solar irradiance incident on a solar surface",
)
app.command(
    name="normal",
    help="Estimate the the clear-sky direct normal irradiance over a period of time",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)(get_direct_normal_irradiance_series)
app.command(
    name="normal-from-horizontal",
    help="Calculate the overcast or estimate the clear-sky direct normal from the horizontal irradiance over a period of time",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)(get_direct_normal_from_horizontal_irradiance_series)
app.command(
    name="horizontal",
    help="Estimate the the clear-sky direct horizontal irradiance over a period of time",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)(get_direct_horizontal_irradiance_series)
app.command(
    "inclined",
    help="Calculate the overcast or estimate the clear-sky direct inclined irradiance over a period of time",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)(get_direct_inclined_irradiance_series)
