"""
PV electricity generation potential for different technologies & configurations
"""

from importlib.metadata import version
import warnings
from pathlib import Path
import sys
import typer
import typer.completion
from typer._completion_shared import Shells
from click import Context
from typer.core import TyperGroup
from typing import Annotated
from typing import Optional
from rich import print
from rich.panel import Panel

from pvgisprototype.cli.typer_parameters import OrderCommands
from pvgisprototype.cli.typer_parameters import typer_option_verbose
from pvgisprototype.cli.typer_parameters import typer_option_version
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_performance
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_series
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_geometry
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_toolbox
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_reference

from pvgisprototype.cli.power import power
from pvgisprototype.cli import series
from pvgisprototype.cli.irradiance import irradiance
from pvgisprototype.cli import position
from pvgisprototype.cli import time
from pvgisprototype.cli import surface
from pvgisprototype.cli import utilities
from pvgisprototype.cli import manual


state = {"verbose": False}


typer.rich_utils.Panel = Panel.fit
app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"PVGIS Command Line Interface [bold][magenta]prototype[/magenta][/bold]",
)


app_completion = typer.Typer(
    help="Generate and install completion scripts.",
    hidden=True,
)
app.add_typer(
    app_completion,
    name="completion",
)

@app_completion.command(
    no_args_is_help=True,
    help="Show completion for the specified shell, to copy or customize it.",
)
def show(
    ctx: typer.Context,
    shell: Shells,
) -> None:
    typer.completion.show_callback(ctx, None, shell)

@app_completion.command(
    no_args_is_help=True,
    help="Install completion for the specified shell.",
)
def install(
    ctx: typer.Context,
    shell: Shells,
) -> None:
    typer.completion.install_callback(ctx, None, shell)


app.add_typer(
    power.app,
    name="power",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_performance,
)
app.add_typer(
    series.app,
    name="series",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series,
)
# app.add_typer(
#     uniplot.app,
#     name="uniplot",
#     no_args_is_help=True,
#     rich_help_panel=rich_help_panel_series,
# )
app.add_typer(
    irradiance.app,
    name="irradiance",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series,
)
app.add_typer(
    time.app,
    name="time",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_geometry,
)
app.add_typer(
    position.app,
    name="position",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_geometry,
)
app.add_typer(
    surface.app,
    name="surface",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_geometry,
)
app.add_typer(
    utilities.app,
    name="utilities",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_toolbox,
)
app.add_typer(
    manual.app,
    name="manual",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_reference,
)


def setup_logging(logfile: Optional[Path] = None):
    """
    Configure logging to either stderr or a file based on the logfile argument.
    """
    from loguru import logger
    logger.remove()  # Remove default handler

    if logfile:
        logger.add(logfile, enqueue=True, backtrace=True, diagnose=True)
    
    # else:
    #     import sys
    #     logger.add(sys.stderr, enqueue=True, backtrace=True, diagnose=True)


@app.callback(no_args_is_help=True)
def main(
    version: Annotated[Optional[bool], typer_option_version] = None,
    verbose: Annotated[int, typer_option_verbose] = 0,
    log: Annotated[Optional[Path], typer.Option("--log", "-l", help="Specify a log file to write logs to, or omit for stderr.")] = None,
) -> None:
    """
    The main entry point for PVIS prototype
    """
    if verbose:
        print("Will write verbose output")
        state["verbose"] = True
    setup_logging(log)
    return


if __name__ == "__main__":
    app()
