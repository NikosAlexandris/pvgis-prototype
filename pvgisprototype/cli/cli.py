"""
PV electricity generation potential for different technologies & configurations
"""

from importlib.metadata import version
import warnings
from pathlib import Path
import typer
# import typer.completion
# from typer._completion_shared import Shells
from click import Context
from typer.core import TyperGroup
from typing import Annotated
from typing import Optional
from rich import print

from .typer_parameters import OrderCommands
from .rich_help_panel_names import rich_help_panel_performance
from . import energy
from .rich_help_panel_names import rich_help_panel_series
from . import series
from . import irradiance
from . import meteorology
from .rich_help_panel_names import rich_help_panel_geometry
from . import time
from . import position
from . import surface
from .rich_help_panel_names import rich_help_panel_toolbox
from . import utilities
from .rich_help_panel_names import rich_help_panel_reference
from . import manual


state = {"verbose": False}


app = typer.Typer(
    cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"PVGIS core CLI prototype",
)


# app_completion = typer.Typer(help="Generate and install completion scripts.", hidden=True)
# app.add_typer(app_completion, name="completion")

# @app_completion.command(no_args_is_help=True, help="Show completion for the specified shell, to copy or customize it.")
# def show(ctx: typer.Context, shell: Shells) -> None:
#     typer.completion.show_callback(ctx, None, shell)

# @app_completion.command(no_args_is_help=True, help="Install completion for the specified shell.")
# def install(ctx: typer.Context, shell: Shells) -> None:
#     typer.completion.install_callback(ctx, None, shell)


app.add_typer(
    energy.app,
    name="energy",
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
# app.add_typer(
#     meteorology.app,
#     name="meteorology",
#     no_args_is_help=True,
#     rich_help_panel=rich_help_panel_series,
# )
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


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"pvgis prototype version: {version('pvgis-prototype')}")
        raise typer.Exit(code=0)


@app.callback(no_args_is_help=True)
def main(
        verbose: Annotated[Optional[bool], typer.Option(
            help="Show details while executing commands")] = False,
        version: Annotated[Optional[bool], typer.Option(
                "--version",
                help="Show the application's version and exit",
                callback=_version_callback,
                is_eager=True)] = None,
        ) -> None:
    """
    callback() : PVIS prototype
    """
    if verbose:
        print("Will write verbose output")
        state["verbose"] = True
    return


if __name__ == "__main__":
    app()
