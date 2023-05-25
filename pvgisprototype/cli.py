"""
PV electricity generation potential for different technologies and configurations
"""

import warnings
from importlib.metadata import version
import os.path
from pathlib import Path

import typer
import xarray as xr




app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"PVGIS core CLI prototype",
)
app.add_typer(estimate_energy, name="estimate", help='Estimate the energy production of a PV system')
app.add_typer(tmy, name="tmy", help='Generate the Typical Meteorological Year')
app.add_typer(timeseries, name="timeseries", help='Retrieve time series of solar radiation and/or PV output power')


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"pvgis prototype version: {version('pvgis-prototype')}")
        raise typer.Exit(code=0)


def read_raster_data(netcdf: str, mask_and_scale=False):
    """
    """
    try:
        # logger.debug("%s", netcdf.name)
        dataarray = xr.open_dataarray(
                filename_or_obj=netcdf,
                mask_and_scale=mask_and_scale,
                )
        return dataarray

    except Exception as exc:
        if "already exists as a scalar variable" in str(exc):
            to_be_dropped = str(exc).split("'")[-2]
            drop_variables.append(to_be_dropped)
            warnings.warn(f"Dropping scalar variable: {to_be_dropped}", RuntimeWarning)
        else:
            # typer.echo(f"Couldn't open {dataset_type.value} dataset: {str(exc)}")
            typer.echo(f"Couldn't open dataset: {str(exc)}")
            raise typer.Exit(code=33)


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
    if verbose:
        print("Will write verbose output")
        state["verbose"] = True
    return


# @app.callback()
# def callback():
#     """
#     callback() : PVGIS core CLI prototype
#     """


if __name__ == "__main__":
    app()
