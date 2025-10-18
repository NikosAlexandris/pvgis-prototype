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

from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_output


def callback_update_verbosity_based_on_other_parameters(
    ctx: typer.Context,
    verbose: int,
):
    """
    Callback function :
        
        - set verbose to >=7 if analysis is requested !

        - set verbose to =3 if any solar event is requested !

          A solar event like Sunrise or Sunset, will only show-up after the
          specific condition set in the respective output section of a data
          model.  For example, lookup the YAML data model definition for the
          output of the command `position overview`.  If the condition is set
          to let a solar event appear in the output after a specific verbosity
          level, we need to force _this_ specific verbosity level in case we
          ask from the command for an `--event` and without any `-v`s.

    """
    event = ctx.params.get("event")
    analysis = ctx.params.get("analysis")
    quick_response_code = ctx.params.get("quick_response_code")

    if analysis or quick_response_code:
        if verbose < 7:
            verbose = 9

    if event:
        if verbose < 3:
            verbose = 3

    return verbose


def callback_quiet(
    ctx: typer.Context,
    quiet: bool,
) -> bool:
    """ """
    analysis = ctx.params.get("analysis")
    if analysis and not quiet:
        quiet = True
    return quiet


typer_option_verbose = typer.Option(
    "--verbose",
    "-v",
    help="Show details while executing commands",
    rich_help_panel=rich_help_panel_output,
    count=True,
    is_flag=False,
    show_default=True,
    callback=callback_update_verbosity_based_on_other_parameters,
)
typer_option_quiet = typer.Option(
    "--quiet",
    help="Do not print out the output",
    is_flag=True,
    show_default=True,
    rich_help_panel=rich_help_panel_output,
    callback=callback_quiet,
)
