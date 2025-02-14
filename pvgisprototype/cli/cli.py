"""
Photovoltaic electricity generation potential for different technologies & configurations
"""

from pathlib import Path
from typing import Annotated

import typer
import typer.completion
from rich import print
from rich.panel import Panel
from typer._completion_shared import Shells

from pvgisprototype.cli.print.conventions import print_pvgis_conventions
from pvgisprototype.cli.print.citation import print_citation_text
from pvgisprototype.cli.typer.group import OrderCommands
from pvgisprototype.cli.typer.verbosity import typer_option_verbose
from pvgisprototype.cli.typer.version import typer_option_version
from pvgisprototype.cli.typer.log import typer_option_log
from pvgisprototype.cli.typer.log import typer_option_log_rich_handler
from pvgisprototype.cli.typer.log import typer_option_logfile
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_performance
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_series
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_position
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_toolbox
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_reference

from pvgisprototype.cli import manual
from pvgisprototype.cli.series import series
from pvgisprototype.cli import surface
from pvgisprototype.cli import time
from pvgisprototype.cli import utilities
from pvgisprototype.cli.power import power
from pvgisprototype.cli.irradiance import irradiance
from pvgisprototype.cli.meteo import meteo
from pvgisprototype.cli.position import position
from pvgisprototype.cli.power import power
from pvgisprototype.cli.performance import performance
from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_performance,
    rich_help_panel_position,
    rich_help_panel_reference,
    rich_help_panel_series,
    rich_help_panel_toolbox,
)
from pvgisprototype.cli.typer.group import OrderCommands
from pvgisprototype.cli.typer.log import (
    typer_option_log,
    typer_option_log_rich_handler,
    typer_option_logfile,
)
from pvgisprototype.cli.typer.verbosity import typer_option_verbose
from pvgisprototype.cli.typer.version import typer_option_version

state = {"verbose": False}


def show(
    ctx: typer.Context,
    shell: Shells,
) -> None:
    typer.completion.show_callback(ctx, None, shell)


def install(
    ctx: typer.Context,
    shell: Shells,
) -> None:
    typer.completion.install_callback(ctx, None, shell)


typer.rich_utils.Panel = Panel.fit
app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    # pretty_exceptions_enable=False,
    help="PVGIS Command Line Interface [bold][magenta]prototype[/magenta][/bold]",
)
app_completion = typer.Typer(
    help="Generate and install completion scripts.",
    hidden=True,
)
app.add_typer(
    app_completion,
    name="completion",
)
app_completion.command(
    no_args_is_help=True,
    help="Show completion for the specified shell, to copy or customize it.",
)(show)
app_completion.command(
    no_args_is_help=True,
    help="Install completion for the specified shell.",
)(install)

app.add_typer(
    performance.app,
    name="performance",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_performance,
)
app.add_typer(
    power.app,
    name="power",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_performance,
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
    meteo.app,
    name="meteo",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series,
)
app.add_typer(
    series.app,
    name="series",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series,
)
app.add_typer(
    time.app,
    name="time",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_position,
)
app.add_typer(
    position.app,
    name="position",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_position,
)
app.add_typer(
    surface.app,
    name="surface",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_position,
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
app.command(
    name="conventions",
    help="Conventions in PVGIS' solar positioning, irradiance & photovoltaic performance calculations",
    no_args_is_help=False,
    rich_help_panel=rich_help_panel_reference,
)(print_pvgis_conventions)
app.command(
    name="cite",
    help="Generate citation text for PVGIS",
    no_args_is_help=False,
    rich_help_panel=rich_help_panel_reference,
)(print_citation_text)


@app.callback(no_args_is_help=True)
def main(
    version: Annotated[bool, typer_option_version] = None,
    verbose: Annotated[int, typer_option_verbose] = 0,
    log: Annotated[int | None, typer_option_log] = None,
    log_rich_handler: Annotated[bool, typer_option_log_rich_handler] = False,
    log_file: Annotated[Path | None, typer_option_logfile] = None,
) -> None:
    """
    The main entry point for PVIS prototype
    """
    if verbose:
        print("Will write verbose output")
        state["verbose"] = True

    # if log:
    #     print(f"Log level = {log}")


if __name__ == "__main__":
    app()
