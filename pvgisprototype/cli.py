"""
PV electricity generation potential for different technologies & configurations
"""

# from pvgisprototype import __app_name__, __version__
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

from . import manual
from . import geometry
from . import time
from . import irradiance
from . import tmy
from . import estimate_energy
from . import time_series
from . import utilities


state = {"verbose": False}


class OrderCommands(TyperGroup):
  def list_commands(self, ctx: Context):
    """Return list of commands in the order appear.
    See: https://github.com/tiangolo/typer/issues/428#issuecomment-1238866548
    """
    return list(self.commands)    # get commands using self.commands


app = typer.Typer(
    cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"PVGIS core CLI prototype",
)
# app_completion = typer.Typer(help="Generate and install completion scripts.", hidden=True)
# app.add_typer(app_completion, name="completion")
app.add_typer(manual.app, name='manual', no_args_is_help=True)
app.add_typer(geometry.app, name="geometry", no_args_is_help=True)
app.add_typer(time.app, name="time", no_args_is_help=True)
app.add_typer(irradiance.app, name="irradiance", no_args_is_help=True)
app.add_typer(tmy.app, name="tmy", no_args_is_help=True)
app.add_typer(estimate_energy.app, name="energy", no_args_is_help=True)
app.add_typer(time_series.app, name="series", no_args_is_help=True)
app.add_typer(utilities.app, name="helpers", no_args_is_help=True)


# @app_completion.command(no_args_is_help=True, help="Show completion for the specified shell, to copy or customize it.")
# def show(ctx: typer.Context, shell: Shells) -> None:
#     typer.completion.show_callback(ctx, None, shell)


# @app_completion.command(no_args_is_help=True, help="Install completion for the specified shell.")
# def install(ctx: typer.Context, shell: Shells) -> None:
#     typer.completion.install_callback(ctx, None, shell)


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
