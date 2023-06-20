"""
PV electricity generation potential for different technologies and configurations
"""

# from pvgisprototype import __app_name__, __version__
from importlib.metadata import version

import warnings
from pathlib import Path

from rich import print
import typer
from typing import Optional

# from .manual import app as manual
from .irradiance import app as irradiance
from .estimate_energy import app as estimate
from .tmy import app as tmy
from .time_series import app as timeseries
from .utilities import app as utility
from .solar_geometry_constants import app as solar_geometry_constants
from .solar_geometry_variables import app as solar_geometry_variables
from .solar_position import app as solar_position


state = {"verbose": False}


app = typer.Typer(
    add_completion=True,
    add_help_option=True,
    help=f"PVGIS core CLI prototype",
)

# app.add_typer(manual, name'manual', help='Manual for PVGIS commands, arguments and options')
app.add_typer(irradiance, name="irradiance", help='Estimate the direct normal radiation', no_args_is_help=True)
app.add_typer(estimate, name="energy", help='Estimate the energy production of a PV system', no_args_is_help=True)
app.add_typer(tmy, name="tmy", help='Generate the Typical Meteorological Year', no_args_is_help=True)
app.add_typer(timeseries, name="time-series", help='Retrieve time series of solar radiation and/or PV output power', no_args_is_help=True)
app.add_typer(utility, name="utility", help='Diagnose data issues and more', no_args_is_help=True)
# app.add_typer(solar_geometry_constants, name="geometry-constants", help='Compute solar geometry constants for a day in a year', no_args_is_help=True)
# app.add_typer(solar_geometry_variables, name="geometry-variables", help='Compute solar geometry variables for a day in a year', no_args_is_help=True)

app.add_typer(solar_position, name="solar-position", help='Compute solar altitude and azimuth for a position and time in year and day', no_args_is_help=True)


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
    callback() : PVGIS core CLI prototype
    """
    if verbose:
        print("Will write verbose output")
        state["verbose"] = True
    return


if __name__ == "__main__":
    app()
