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
from rich import print
from typing import Annotated
from pvgisprototype.cli.typer.verbosity import typer_option_verbose
from pvgisprototype.cli.typer.group import OrderCommands
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.cli.meteo.introduction import introduction
from pvgisprototype.cli.meteo.tmy import tmy
from pvgisprototype.cli.meteo.tmy import tmy_weighting
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_introduction
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_meteorology
from pvgisprototype.cli.messages import NOT_COMPLETE_CLI


app = typer.Typer(
    cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f":sun_behind_rain_cloud: Meteorology & Typical Meteorological Year",
)


@app.callback()
def main(
    ctx: typer.Context,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    debug: Annotated[bool, typer.Option(
        "--debug",
        help="Enable debug mode")] = False,
):
    """
    Typical Meteorological Year
    """
    # if verbose > 2:
    #     print(f"Executing command: {ctx.invoked_subcommand}")
    if verbose > 0:
        print("Will output verbosely")
        # state["verbose"] = True

    app.debug_mode = debug


app.command(
    name='introduction',
    help='A short primer on the Typical Meteorological Year',
    no_args_is_help=False,
    rich_help_panel=rich_help_panel_introduction,
)(introduction)
app.command(
    'tmy',
    help=f":sun_behind_rain_cloud: Typical Meteorological Year",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_meteorology,
)(tmy)
app.command(
    'weighting',
    help=f":sun_behind_rain_cloud: Weighting schemes for Typical Meteorological Year {NOT_COMPLETE_CLI}",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_meteorology,
)(tmy_weighting)
