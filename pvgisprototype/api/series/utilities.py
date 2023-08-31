from devtools import debug
import warnings
import typer
import netCDF4
from colorama import Fore
from colorama import Style
from .log import logger
import xarray as xr

from pvgisprototype import Latitude
from pvgisprototype import Longitude


# Hardcodings
# exclamation_mark = u'\N{heavy exclamation mark symbol}'
exclamation_mark = u'\N{exclamation mark}'
check_mark = u'\N{check mark}'
x_mark = u'\N{Ballot Script X}'

def load_or_open_dataarray(function, filename_or_obj, mask_and_scale):
    try:
        dataarray = function(
            filename_or_obj=filename_or_obj,
            mask_and_scale=mask_and_scale,
        )
        return dataarray

    except Exception as exc:
        typer.echo(f"Could not load or open the data: {str(exc)}")
        raise typer.Exit(code=33)


def open_data_array(
        netcdf: str,
        mask_and_scale=False,
        in_memory: bool = False,
        ):
    """
    """
    # try:
    #     if in_memory:
    #         dataarray = xr.load_dataarray(
    #                 filename_or_obj=netcdf,
    #                 mask_and_scale=mask_and_scale,
    #                 )
    #         return dataarray
    # except Exception as exc:
    #     typer.echo(f"Could not load the data in memory: {str(exc)}")
    #     try:
    #         dataarray = xr.open_dataarray(
    #                 filename_or_obj=netcdf,
    #                 mask_and_scale=mask_and_scale,
    #                 )
    #         return dataarray
    #     except Exception as exc:
    #         typer.echo(f"Could not open the data: {str(exc)}")
    #         raise typer.Exit(code=33)
    if in_memory:
        print('In memory')
        return load_or_open_dataarray(xr.load_dataarray, netcdf, mask_and_scale)
    else:
        print('Open file')
        return load_or_open_dataarray(xr.open_dataarray, netcdf, mask_and_scale)



def get_scale_and_offset(netcdf):
    """Get scale and offset values from a netCDF file"""
    dataset = netCDF4.Dataset(netcdf)
    netcdf_dimensions = set(dataset.dimensions)
    netcdf_dimensions.update({'lon', 'longitude', 'lat', 'latitude'})  # all space dimensions?
    netcdf_variables = set(dataset.variables)
    variable = str(list(netcdf_variables.difference(netcdf_dimensions))[0])  # single variable name!

    if 'scale_factor' in dataset[variable].ncattrs():
        scale_factor = dataset[variable].scale_factor
    else:
        scale_factor = None

    if 'add_offset' in dataset[variable].ncattrs():
        add_offset = dataset[variable].add_offset
    else:
        add_offset = None

    return (scale_factor, add_offset)


def select_coordinates(
        data_array,
        longitude: Longitude = None,
        latitude: Latitude = None,
        time: str = None,
        method: str ='nearest',
        tolerance: float = 0.1,
        verbose: bool = False,
        ):
    """Select single pair of coordinates from a data array
    
    Will select center coordinates if none of (longitude, latitude) are
    provided.
    """
    # ----------------------------------------------------------- Deduplicate me
    # Ugly hack for when dimensions 'longitude', 'latitude' are not spelled out!
    # Use `coords` : a time series of a single pair of coordinates has only a `time` dimension!
    indexers = {}
    dimensions = [dimension for dimension in data_array.coords if isinstance(dimension, str)]
    if set(['lon', 'lat']) & set(dimensions):
        x = 'lon'
        y = 'lat'
    elif set(['longitude', 'latitude']) & set(dimensions):
        x = 'longitude'
        y = 'latitude'

    if (x and y):
        logger.info(f'Dimensions  : {x}, {y}')

    if not (longitude and latitude):
        warning = Fore.YELLOW + f'{exclamation_mark} Coordinates (longitude, latitude) not provided. Selecting center coordinates.' + Style.RESET_ALL
        logger.warning(warning)
        typer.echo(Fore.YELLOW + warning)

        center_longitude = float(data_array[x][len(data_array[x])//2])
        center_latitude = float(data_array[y][len(data_array[y])//2])
        indexers[x] = center_longitude
        indexers[y] = center_latitude

        text_coordinates = Fore.GREEN + f'{check_mark} Center coordinates (longitude, latitude) : {center_longitude}, {center_latitude}.' + Style.RESET_ALL

    else:
        indexers[x] = longitude
        indexers[y] = latitude
        text_coordinates = Fore.GREEN + f'{check_mark} Coordinates : {longitude}, {latitude}.' + Style.RESET_ALL

    try:
        if not time:
            data_array = data_array.sel(
                    **indexers,
                    method=method,
                    )
        else:
            # Review-Me ------------------------------------------------------
            data_array = data_array.sel(
                    time=time, method=method).sel(
                        **indexers,
                        method=method,
                        tolerance=tolerance,
                    )
            # Review-Me ------------------------------------------------------

    except Exception as exc:
        typer.echo(f"Something went wrong in selecting the data: {str(exc)}")
        raise SystemExit(33)

    logger.info(text_coordinates)
    typer.echo(text_coordinates)
    return data_array
