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
from pvgisprototype.cli.typer.group import OrderCommands
from pvgisprototype.cli.irradiance.extraterrestrial.normal import (
    get_extraterrestrial_normal_irradiance_series,
)
from pvgisprototype.cli.irradiance.extraterrestrial.horizontal import (
    get_extraterrestrial_horizontal_irradiance_series,
)
from pvgisprototype.constants import (
    EXTRATERRESTRIAL_HORIZONTAL_IRRADIANCE_TYPER_HELP,
    EXTRATERRESTRIAL_HORIZONTAL_IRRADIANCE_TYPER_HELP_SHORT,
    EXTRATERRESTRIAL_NORMAL_IRRADIANCE_TYPER_HELP,
    EXTRATERRESTRIAL_NORMAL_IRRADIANCE_TYPER_HELP_SHORT,
)
from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_irradiance_series,
)


app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help="⍖ Estimate the clear-sky extraterrestrial irradiance",
)
app.command(
    name="normal",
    help=EXTRATERRESTRIAL_NORMAL_IRRADIANCE_TYPER_HELP,
    short_help=EXTRATERRESTRIAL_NORMAL_IRRADIANCE_TYPER_HELP_SHORT,
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)(get_extraterrestrial_normal_irradiance_series)
app.command(
    name="horizontal",
    help=EXTRATERRESTRIAL_HORIZONTAL_IRRADIANCE_TYPER_HELP,
    short_help=EXTRATERRESTRIAL_HORIZONTAL_IRRADIANCE_TYPER_HELP_SHORT,
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)(get_extraterrestrial_horizontal_irradiance_series)
