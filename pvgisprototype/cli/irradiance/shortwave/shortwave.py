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

from pvgisprototype.cli.irradiance.shortwave.horizontal import (
    get_global_horizontal_irradiance_series,
)
from pvgisprototype.cli.irradiance.shortwave.inclined import (
    get_global_inclined_irradiance_series,
)
from pvgisprototype.cli.irradiance.shortwave.spectral import (
    get_spectrally_resolved_global_inclined_irradiance_series,
)
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_irradiance_series
from pvgisprototype.cli.typer.group import OrderCommands

app = typer.Typer(
    cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=":sun_with_face:⤋ Estimate the global irradiance incident on a surface over a time series ",
)
app.command(
    name="horizontal",
    no_args_is_help=True,
    help="Calculate the broadband global horizontal irradiance over a time series",
    rich_help_panel=rich_help_panel_irradiance_series,
)(get_global_horizontal_irradiance_series)
app.command(
    name="inclined",
    no_args_is_help=True,
    help="Calculate the broadband global inclined irradiance over a time series",
    rich_help_panel=rich_help_panel_irradiance_series,
)(get_global_inclined_irradiance_series)
app.command(
    name="spectral",
    no_args_is_help=True,
    help="Calculate the spectrally resolved global inclined irradiance over a time series",
    rich_help_panel=rich_help_panel_irradiance_series,
)(get_spectrally_resolved_global_inclined_irradiance_series)
