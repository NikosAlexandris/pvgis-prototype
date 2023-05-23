from devtools import debug
import warnings
from importlib.metadata import version
import os.path
from pathlib import Path

import typer
import xarray as xr


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"pvgis prototype version: {version('pvgis-prototype')}")
        raise typer.Exit(code=0)


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"PVGIS core CLI prototype",
)


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
        # data_array = dataset[variable]
        # if "scale_factor" not in da.attrs:
        #     # This is CMSAF!
        #     logger.info("Dataset does not have encoding attrs (scale_factor, add_offset). Using defaults")
        #     scale_factor = 1
        #     add_offset = 0
        #     fill_value = da.attrs["_FillValue"]
        #     break

        # nc_scale_factor = da.attrs["scale_factor"]
        # nc_add_offset = da.attrs["add_offset"]
        # data_min = -32766 * nc_scale_factor + nc_add_offset
        # data_max = 32767 * nc_scale_factor + nc_add_offset
        # # logger.debug("%s, %s, %s, %s", nc_scale_factor, nc_add_offset, data_min, data_max)
    except Exception as exc:
        if "already exists as a scalar variable" in str(exc):
            to_be_dropped = str(exc).split("'")[-2]
            drop_variables.append(to_be_dropped)
            warnings.warn(f"Dropping scalar variable: {to_be_dropped}", RuntimeWarning)
        else:
            # typer.echo(f"Couldn't open {dataset_type.value} dataset: {str(exc)}")
            typer.echo(f"Couldn't open dataset: {str(exc)}")
            raise typer.Exit(code=33)

@app.command()
def query_location(
        netcdf: str,
        longitude: float,
        latitude: float,
        mask_and_scale=False,
        method='nearest',
        ) -> int:
    """
    """
    dataarray = read_raster_data(netcdf, mask_and_scale=mask_and_scale)
    data = dataarray.sel(
            lon=longitude,
            lat=latitude,
            method='nearest',
            )
    print(f"{float(data)}")
    return 0


if __name__ == "__main__":
    typer.run(read_raster_data)
