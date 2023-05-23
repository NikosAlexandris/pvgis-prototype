import typer
import warnings

import os.path
from pathlib import Path
import xarray as xr

def read_raster_data(netcdf: str, longitude: float, latitude: float, mask_and_scale=False):
    """
    """
    try:
        # logger.debug("%s", netcdf.name)
        dataarray = xr.open_dataarray(
                filename_or_obj=netcdf,
                mask_and_scale=mask_and_scale,
                )
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

        data = dataarray.sel(
                lon=longitude,
                lat=latitude,
                method='nearest',
                )
        print(f"{float(data)}")
        # return data
    except Exception as exc:
        if "already exists as a scalar variable" in str(exc):
            to_be_dropped = str(exc).split("'")[-2]
            drop_variables.append(to_be_dropped)
            warnings.warn(f"Dropping scalar variable: {to_be_dropped}", RuntimeWarning)
        else:
            # typer.echo(f"Couldn't open {dataset_type.value} dataset: {str(exc)}")
            typer.echo(f"Couldn't open dataset: {str(exc)}")
            raise typer.Exit(code=33)

if __name__ == "__main__":
    typer.run(read_raster_data)
