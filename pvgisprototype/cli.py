"""
PV electricity generation potential for different technologies and configurations
"""

# from pvgisprototype import __app_name__, __version__
from importlib.metadata import version

import warnings
from pathlib import Path

import typer
from typing import Optional

# from .manual import app as manual
from .estimate_energy import app as estimate
from .tmy import app as tmy
from .time_series import app as timeseries
from .utilities import app as utility
from .solar_constant import app as solar_constant


state = {"verbose": False}


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
)
# app.add_typer(manual, name'manual', help='Manual for PVGIS commands, arguments and options')
app.add_typer(estimate, name="estimate", help='Estimate the energy production of a PV system')
app.add_typer(tmy, name="tmy", help='Generate the Typical Meteorological Year')
app.add_typer(timeseries, name="time-series", help='Retrieve time series of solar radiation and/or PV output power')
app.add_typer(utility, name="utility", help='Diagnose data issues and more')
app.add_typer(solar_constant, name="solar-constant", help='Compute the solar constant corrected for the given day in the year')


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"pvgis prototype version: {version('pvgis-prototype')}")
        raise typer.Exit(code=0)


@app.callback()
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
