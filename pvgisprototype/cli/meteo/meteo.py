import typer
from rich import print
from typing import Annotated
from typing import Optional
from pvgisprototype.cli.typer.verbosity import typer_option_verbose
from pvgisprototype.cli.typer.group import OrderCommands
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
# from pvgisprototype.cli.meteo.introduction import introduction
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
    help=f":sun_behind_rain_cloud: Meteorological time series",
)


@app.callback()
def main(
    ctx: typer.Context,
    verbose: Annotated[Optional[int], typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    debug: Annotated[Optional[bool], typer.Option(
        "--debug",
        help="Enable debug mode")] = False,
):
    """
    Meteorological time series
    """
    # if verbose > 2:
    #     print(f"Executing command: {ctx.invoked_subcommand}")
    if verbose > 0:
        print("Will output verbosely")
        # state["verbose"] = True

    app.debug_mode = debug


# app.command(
#     name='introduction',
#     help='A short primer on solar geometry',
#     no_args_is_help=False,
#     rich_help_panel=rich_help_panel_introduction,
# )(introduction)
app.command(
    'tmy',
    help=f":sun_behind_rain_cloud: Typical Meteorological Year",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_meteorology,
)(tmy)
app.command(
    'tmy-weighting',
    help=f":sun_behind_rain_cloud: Weighting schemes for Typical Meteorological Year {NOT_COMPLETE_CLI}",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_meteorology,
)(tmy_weighting)
