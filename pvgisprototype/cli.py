"""
PV electricity generation potential for different technologies & configurations
"""

# from pvgisprototype import __app_name__, __version__
from importlib.metadata import version

import warnings
from pathlib import Path

import typer
from click import Context
from typer.core import TyperGroup
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
app.add_typer(manual.app, name='manual', no_args_is_help=True)
app.add_typer(geometry.app, name="geometry", no_args_is_help=True)
app.add_typer(time.app, name="time", no_args_is_help=True)
app.add_typer(irradiance.app, name="irradiance", no_args_is_help=True)
app.add_typer(tmy.app, name="tmy", no_args_is_help=True)
app.add_typer(estimate_energy.app, name="energy", no_args_is_help=True)
app.add_typer(time_series.app, name="series", no_args_is_help=True)
app.add_typer(utilities.app, name="helpers", no_args_is_help=True)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"pvgis prototype version: {version('pvgis-prototype')}")
        raise typer.Exit(code=0)


@app.callback(no_args_is_help=True)
def main(
        verbose: bool = False,
        version: Optional[bool] = typer.Option(
            None,
            "--version",
            "-v",
            help="Show the application's version and exit.",
            callback=_version_callback,
            is_eager=True,
            )
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
