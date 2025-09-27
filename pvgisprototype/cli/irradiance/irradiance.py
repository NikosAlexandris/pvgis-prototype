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
from pvgisprototype.cli.irradiance.introduction import solar_irradiance_introduction
from pvgisprototype.cli.irradiance.shortwave.shortwave import app as global_irradiance
from pvgisprototype.cli.irradiance.direct.direct import app as direct_irradiance
from pvgisprototype.cli.irradiance.diffuse.diffuse import app as diffuse_irradiance
from pvgisprototype.cli.irradiance.diffuse.ground_reflected import (
    get_ground_reflected_inclined_irradiance_series,
)
from pvgisprototype.cli.irradiance.extraterrestrial.extraterrestrial import app as extraterrestrial_irradiance
from pvgisprototype.cli.irradiance.reflectivity import app as reflectivity_factor
from pvgisprototype.cli.irradiance.limits import app as limits
from pvgisprototype.cli.irradiance.kato_bands import print_kato_spectral_bands
from pvgisprototype.cli.messages import NOT_COMPLETE_CLI
from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_introduction,
    rich_help_panel_irradiance_series,
    rich_help_panel_toolbox,
)
from pvgisprototype.cli.typer.group import OrderCommands
from pvgisprototype.constants import (
    REFLECTIVITY_TYPER_HELP,
    REFLECTIVITY_TYPER_HELP_SHORT,
    EXTRATERRESTRIAL_IRRADIANCE_TYPER_HELP,
    EXTRATERRESTRIAL_IRRADIANCE_TYPER_HELP_SHORT,
    DIFFUSE_IRRADIANCE_TYPER_HELP,
    DIFFUSE_IRRADIANCE_TYPER_HELP_SHORT,
    DIRECT_IRRADIANCE_TYPER_HELP,
    DIRECT_IRRADIANCE_TYPER_HELP_SHORT,
    GLOBAL_IRRADIANCE_TYPER_HELP,
    GLOBAL_IRRADIANCE_TYPER_HELP_SHORT,
    REFLECTIVITY_TYPER_HELP_SHORT,
    SOLAR_IRRADIANCE_TYPER_HELP,
    GROUND_REFLECTED_IRRADIANCE_TYPER_HELP,
    GROUND_REFLECTED_IRRADIANCE_TYPER_HELP_SHORT,
    SYMBOL_IRRADIANCE_LIMITS,
)

app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=SOLAR_IRRADIANCE_TYPER_HELP,
)
app.command(
    name="introduction",
    help="A short primer on solar irradiance",
    no_args_is_help=False,
    rich_help_panel=rich_help_panel_introduction,
)(solar_irradiance_introduction)
app.add_typer(
    global_irradiance,
    name="global",
    help=GLOBAL_IRRADIANCE_TYPER_HELP,
    short_help=GLOBAL_IRRADIANCE_TYPER_HELP_SHORT,
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)
app.add_typer(
    direct_irradiance,
    name="direct",
    help=DIRECT_IRRADIANCE_TYPER_HELP,
    short_help=DIRECT_IRRADIANCE_TYPER_HELP_SHORT,
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)
app.add_typer(
    diffuse_irradiance,
    name="diffuse",
    help=DIFFUSE_IRRADIANCE_TYPER_HELP,
    short_help=DIFFUSE_IRRADIANCE_TYPER_HELP_SHORT,
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)
app.command(
    name="reflected",
    help=GROUND_REFLECTED_IRRADIANCE_TYPER_HELP,
    short_help=GROUND_REFLECTED_IRRADIANCE_TYPER_HELP_SHORT,
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)(get_ground_reflected_inclined_irradiance_series)
app.add_typer(
    extraterrestrial_irradiance,
    name="extraterrestrial",
    help=EXTRATERRESTRIAL_IRRADIANCE_TYPER_HELP,
    short_help=EXTRATERRESTRIAL_IRRADIANCE_TYPER_HELP_SHORT,
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)
app.add_typer(
    reflectivity_factor,
    name="reflectivity",
    help=f"{REFLECTIVITY_TYPER_HELP} {NOT_COMPLETE_CLI}",
    short_help=f"{REFLECTIVITY_TYPER_HELP_SHORT} {NOT_COMPLETE_CLI}",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_toolbox,
)
app.add_typer(
    limits,
    name="limits",
    help=f"{SYMBOL_IRRADIANCE_LIMITS} Calculate physically possible irradiance limits",
    short_help=f"{SYMBOL_IRRADIANCE_LIMITS} Calculate physically possible irradiance limits",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_toolbox,
)
app.command(
    name="kato-bands",
    help=f"{SYMBOL_IRRADIANCE_LIMITS} Print limits and center wavelengths of KATO spectral bands",
    short_help=f"{SYMBOL_IRRADIANCE_LIMITS} Kato spectral bands limits and center wavelengths",
    no_args_is_help=False,
    rich_help_panel=rich_help_panel_toolbox,
)(print_kato_spectral_bands)
