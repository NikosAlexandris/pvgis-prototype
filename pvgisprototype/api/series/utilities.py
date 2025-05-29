from pathlib import Path

import numpy
import typer
import xarray as xr
from devtools import debug
from rich import print
from xarray.core.dataarray import DataArray
from xarray.core.dataset import Dataset

from pvgisprototype import Latitude, Longitude
from pvgisprototype.api.series.hardcodings import check_mark, exclamation_mark, x_mark
from pvgisprototype.api.series.models import MethodForInexactMatches
from pvgisprototype.cli.messages import ERROR_IN_SELECTING_DATA
from pvgisprototype.constants import (
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_function_call, logger


def load_or_open_dataarray(function, filename_or_object, mask_and_scale):
    try:
        dataarray = function(
            filename_or_obj=filename_or_object,
            mask_and_scale=mask_and_scale,
        )
        return dataarray

    except Exception as exc:
        typer.echo(f"Could not load or open the data: {str(exc)}")
        raise typer.Exit(code=33)


def load_or_open_dataset(function, filename_or_object, mask_and_scale):
    try:
        dataset = function(
            filename_or_obj=filename_or_object,
            mask_and_scale=mask_and_scale,
        )
        return dataset
    except Exception as exc:
        typer.echo(f"Could not load or open the dataset: {str(exc)}")
        raise typer.Exit(code=33)


def open_data_array(
    input_data: str,
    mask_and_scale: bool = False,
    in_memory: bool = False,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
):
    """ """
    # try:
    #     if in_memory:
    #         dataarray = xr.load_dataarray(
    #                 filename_or_object=netcdf,
    #                 mask_and_scale=mask_and_scale,
    #                 )
    #         return dataarray
    # except Exception as exc:
    #     typer.echo(f"Could not load the data in memory: {str(exc)}")
    #     try:
    #         dataarray = xr.open_dataarray(
    #                 filename_or_object=input_data_file,
    #                 mask_and_scale=mask_and_scale,
    #                 )
    #         return dataarray
    #     except Exception as exc:
    #         typer.echo(f"Could not open the data: {str(exc)}")
    #         raise typer.Exit(code=33)
    if in_memory:
        if verbose > 0:
            logger.debug(f"Loading data array '{input_data}' in memory...")
        return load_or_open_dataarray(
            function=xr.load_dataarray,
            filename_or_object=input_data,
            mask_and_scale=mask_and_scale,
        )
    else:
        if verbose > 0:
            logger.debug(f"Opening data array '{input_data}'...")
        return load_or_open_dataarray(
            function=xr.open_dataarray,
            filename_or_object=input_data,
            mask_and_scale=mask_and_scale,
        )


def open_data_set(
    input_data: Path,
    mask_and_scale: bool = False,
    in_memory: bool = False,
    verbose: int = 0,
):
    """Open or load a dataset based on the input flags."""
    if in_memory:
        if verbose > 0:
            logger.debug(f"Loading dataset '{input_data}' in memory...")
        return load_or_open_dataset(
            function=xr.load_dataset,
            filename_or_object=input_data,
            mask_and_scale=mask_and_scale,
        )
    else:
        if verbose > 0:
            logger.debug(f"Opening dataset '{input_data}'...")
        return load_or_open_dataset(
            function=xr.open_dataset,
            filename_or_object=input_data,
            mask_and_scale=mask_and_scale,
        )


def load_or_open_dataarray_from_dataset(
    dataset: Path,
    variable: str | None = None,
    longitude: float | None = None,
    latitude: float | None = None,
    time: str | None = None,
    column_numbers: str | None = None,
    mask_and_scale: bool = False,
    in_memory: bool = False,
    method: str = "nearest",
    tolerance: float = 0.1,
    verbose: int = 0,
):
    """
    Load or open a variable from a dataset and select coordinates.

    Parameters
    ----------
    dataset: Path to the NetCDF dataset file.
    variable: The variable name to extract from the dataset.
    longitude: Longitude value to select.
    latitude: Latitude value to select.
    time: Time value to select.
    mask_and_scale: Boolean to mask and scale data.
    in_memory: Boolean to load dataset into memory.
    method: Method for selecting nearest coordinates ('nearest').
    tolerance: Tolerance level for selecting the nearest coordinate.
    verbose: Verbosity level for logging.
    """

    # Open the dataset
    ds = open_data_set(
        input_data=dataset,
        mask_and_scale=mask_and_scale,
        in_memory=in_memory,
        verbose=verbose,
    )

    # If a variable is specified, check and extract it, otherwise raise error
    if variable:
        if variable in ds.variables:
            data_array = ds[variable]
        else:
            logger.error(f"{x_mark} Variable '{variable}' not found in the dataset!")
            raise typer.Exit(code=33)
    else:
        logger.error(f"{x_mark} No variable specified!")
        raise typer.Exit(code=33)

    # Select coordinates for longitude, latitude, and time if provided
    indexers = {}

    if "longitude" in ds.coords and longitude:
        indexers["longitude"] = longitude
    elif "lon" in ds.coords and longitude:
        indexers["lon"] = longitude

    if "latitude" in ds.coords and latitude:
        indexers["latitude"] = latitude
    elif "lat" in ds.coords and latitude:
        indexers["lat"] = latitude

    if time:
        indexers["time"] = time

    # Apply selection using nearest method and tolerance if required
    try:
        data_array = data_array.sel(**indexers, method=method, tolerance=tolerance)
    except Exception as e:
        logger.error(f"Error in selecting data with given coordinates: {str(e)}")
        raise typer.Exit(code=33)

    if column_numbers:
        try:
            if "-" in column_numbers:  # Handle range like '1-10'
                start, end = map(int, column_numbers.split("-"))
                data_array = data_array.isel(
                    center_wavelength=slice(start - 1, end)
                )  # Adjust to 0-based indexing
            elif "," in column_numbers:  # Handle list like '1,5,7'
                indices = list(map(int, column_numbers.split(",")))
                data_array = data_array.isel(
                    center_wavelength=[i - 1 for i in indices]
                )  # Adjust to 0-based indexing
            else:  # Handle single value like '1'
                index = int(column_numbers) - 1  # Adjust to 0-based indexing
                data_array = data_array.isel(center_wavelength=index)
        except Exception as e:
            logger.error(f"Error in processing column_numbers: {str(e)}")
            raise typer.Exit(code=33)

    if verbose > 0:
        logger.debug(f"Data successfully loaded for variable '{variable}'.")

    return data_array


def read_data_array_or_set(
    input_data: Path,
    mask_and_scale: bool = False,
    in_memory: bool = False,
    verbose: int = 0,
):
    """Open the data and determine if it's a DataArray or Dataset."""

    # try reading an array
    try:
        if in_memory:
            if verbose > 0:
                logger.debug(
                    f"  - {exclamation_mark} Trying to load {input_data} into memory as a DataArray...",
                    alt=f"  - {exclamation_mark} [bold]Trying[/bold] to load {input_data} into memory as a DataArray...",
                )
            return load_or_open_dataarray(
                function=xr.load_dataarray,
                filename_or_object=input_data,
                mask_and_scale=mask_and_scale,
            )
        else:
            if verbose > 0:
                logger.debug(
                    f"  - {exclamation_mark} Trying to open {input_data} as a DataArray...",
                    alt=f"  - {exclamation_mark} [bold]Trying[/bold] to open {input_data} as a DataArray...",
                )
            return load_or_open_dataarray(
                function=xr.open_dataarray,
                filename_or_object=input_data,
                mask_and_scale=mask_and_scale,
            )

    # or a set
    except:
        try:
            if in_memory:
                if verbose > 0:
                    logger.debug(
                        f"  - {exclamation_mark} Trying to load {input_data} into memory as a Dataset...",
                        alt=f"  - {exclamation_mark} [bold]Trying[/bold] to load {input_data} into memory as a Dataset...",
                    )
                return load_or_open_dataset(
                    function=xr.load_dataset,
                    filename_or_object=input_data,
                    mask_and_scale=mask_and_scale,
                )
            else:
                if verbose > 0:
                    logger.debug(
                        f"  - {exclamation_mark} Trying to open {input_data} as a Dataset...",
                        alt=f"  - {exclamation_mark} [bold]Trying[/bold] to open {input_data} as a Dataset...",
                    )
                return load_or_open_dataset(
                    function=xr.open_dataset,
                    filename_or_object=input_data,
                    mask_and_scale=mask_and_scale,
                )
        except Exception as e:
            logger.error(
                f"Error loading or opening data: {str(e)}",
                alt=f"Error loading or opening data: {str(e)}",
            )
            raise typer.Exit(code=33)


def get_scale_and_offset(netcdf):
    """Get scale and offset values from a netCDF file using xarray"""
    import xarray as xr

    # Open the dataset using xarray
    dataset = xr.open_dataset(netcdf)

    # Get all dimensions
    netcdf_dimensions = set(dataset.dims)

    # Get all variables
    netcdf_variables = set(dataset.data_vars)

    # Assuming the first variable that is not a dimension is the target variable
    variable = list(netcdf_variables.difference(netcdf_dimensions))[0]

    # Get the variable's attributes
    variable_attrs = dataset[variable].attrs

    # Retrieve scale_factor and add_offset attributes if they exist
    scale_factor = variable_attrs.get("scale_factor", None)
    add_offset = variable_attrs.get("add_offset", None)

    return (scale_factor, add_offset)


def filter_xarray(
    data: Dataset | DataArray,
    coordinate: str,
    minimum: float | None,
    maximum: float | None,
    drop: bool = True,
) -> Dataset | DataArray:
    """
    Filter a Dataset or DataArray based on a given coordinate with specified minimum and/or
    maximum values. If the `minimum` or `maximum` is None, the function will ignore that bound.

    Parameters
    ----------
    data : Dataset | DataArray
        The input xarray Dataset or DataArray to filter.
    coordinate : str
        The name of the coordinate within the Dataset or DataArray to apply the filter on.
    minimum : float or None
        The minimum value for the coordinate. If None, no lower bound is applied.
    maximum : float or None
        The maximum value for the coordinate. If None, no upper bound is applied.
    drop : bool, optional
        Whether to drop values that fall outside the range, by default True.

    Returns
    -------
    Dataset | DataArray
        The filtered xarray Dataset or DataArray, where values outside the
        [minimum, maximum] range are dropped or masked.

    Raises
    ------
    ValueError
        If the coordinate is not present in the input data.

    Notes
    -----
    - If both `minimum` and `maximum` are None, the input data is returned unfiltered.
    - Emits a warning via logger if any values exceed the bounds.
    """
    if coordinate not in data.coords:
        raise ValueError(f"Coordinate '{coordinate}' not found in the dataset.")

    condition = True  # Start with an always-true condition

    if minimum is not None:
        condition &= data[coordinate] >= minimum

    if maximum is not None:
        condition &= data[coordinate] <= maximum

    # values outside the requested range ?
    if numpy.any(~condition):
        warning_message = f"{x_mark} The input data exceed the reference range [{minimum}, {maximum}]."
        warning_alternative = f"{x_mark} [bold]The input data [red]exceed[/red] the reference range[/bold] [{minimum}, {maximum}]."
        typer.echo(warning_message)
        logger.warning(warning_message, alt=warning_alternative)
    else:
        success_message = f"{check_mark} The input data are within the reference range [{minimum}, {maximum}]."
        typer.echo(success_message)
        logger.debug(success_message)

    return data.where(condition, drop=drop)


def set_location_indexers(
    data_array,
    longitude: Longitude = None,
    latitude: Latitude = None,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
):
    """Select single pair of coordinates from a data array

    Will select center coordinates if none of (longitude, latitude) are
    provided.
    """
    # ----------------------------------------------------------- Deduplicate me
    # Ugly hack for when dimensions 'longitude', 'latitude' are not spelled out!
    # Use `coords` : a time series of a single pair of coordinates has only a `time` dimension!
    indexers = {}
    dimensions = [
        dimension for dimension in data_array.coords if isinstance(dimension, str)
    ]
    if set(["lon", "lat"]) & set(dimensions):
        x = "lon"
        y = "lat"
    elif set(["longitude", "latitude"]) & set(dimensions):
        x = "longitude"
        y = "latitude"

    if x and y:
        logger.debug(
            f"  {check_mark} Location specific dimensions detected in '{data_array.name}' : {x}, {y}"
        )

    if not (longitude and latitude):
        warning = f"  {check_mark} Coordinates (longitude, latitude) not provided. Selecting center coordinates."
        logger.warning(warning)

        center_longitude = float(data_array[x][len(data_array[x]) // 2])
        center_latitude = float(data_array[y][len(data_array[y]) // 2])
        indexers[x] = center_longitude
        indexers[y] = center_latitude

        text_coordinates = f"{check_mark} Center coordinates (longitude, latitude) : {center_longitude}, {center_latitude}."

    else:
        indexers[x] = longitude
        indexers[y] = latitude
        text_coordinates = f"  {check_mark} Coordinates : {longitude}, {latitude}."

    logger.debug(text_coordinates)

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return indexers


def select_coordinates(
    data_array,
    longitude: Longitude,
    latitude: Latitude,
    time: str | None = None,
    method: str = "nearest",
    tolerance: float = 0.1,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
):
    """Select single pair of coordinates from a data array

    Will select center coordinates if none of (longitude, latitude) are
    provided.
    """
    indexers = set_location_indexers(
        data_array=data_array,
        longitude=longitude,
        latitude=latitude,
        verbose=verbose,
    )

    try:
        if not time:
            data_array = data_array.sel(
                **indexers,
                method=method,
            )
        else:
            # Review-Me ------------------------------------------------------
            data_array = data_array.sel(time=time, method=method).sel(
                **indexers,
                method=method,
                tolerance=tolerance,
            )
            # Review-Me ------------------------------------------------------

    except Exception as exception:
        print(f"{x_mark} {ERROR_IN_SELECTING_DATA} : {exception}")
        raise SystemExit(33)

    return data_array


@log_function_call
def select_location_time_series(
    time_series: Path,
    variable: str | None = None,
    coordinate: str | None = None,
    minimum: float | None = None,
    maximum: float | None = None,
    drop: bool = True,
    longitude: Longitude = None,
    latitude: Latitude = None,
    neighbor_lookup: MethodForInexactMatches | None = MethodForInexactMatches.nearest,
    tolerance: float = 0.1,
    mask_and_scale: bool = False,
    in_memory: bool = False,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> DataArray:
    """Select a location from a time series data format supported by xarray"""
    context_message = (
        f"i Executing data selection function : select_location_time_series()"
    )
    context_message_alternative = f"[yellow]i[/yellow] Executing [underline]data selection function[/underline] : select_location_time_series()"
    logger.debug(context_message, alt=context_message_alternative)
    # data_array = open_data_array(
    #     time_series,
    #     mask_and_scale,
    #     in_memory,
    # )
    data = read_data_array_or_set(
        input_data=time_series,
        mask_and_scale=mask_and_scale,
        in_memory=in_memory,
        verbose=verbose,
    )
    if isinstance(data, xr.Dataset):
        if not variable:
            raise ValueError(
                "You must specify a variable when selecting from a Dataset."
            )
        if variable not in data:
            raise ValueError(f"Variable '{variable}' not found in the Dataset.")
        data_array = data[variable]  # Extract the DataArray from the Dataset
        logger.debug(
            f"  {check_mark} Successfully extracted '{variable}' from '{data_array.name}'.",
            alt=f"  {check_mark} [green]Successfully[/green] extracted '{variable}' from '{data_array.name}'.",
        )

    elif isinstance(data, xr.DataArray):
        data_array = data  # It's already a DataArray, use it directly

    else:
        raise ValueError("Unsupported data type. Must be a DataArray or Dataset.")

    # Is this correctly placed here ?
    if coordinate and (minimum or maximum):
        data_array = filter_xarray(
            data=data_array,
            coordinate=coordinate,
            minimum=minimum,
            maximum=maximum,
            drop=drop,
        )
    indexers = set_location_indexers(
        data_array=data_array,
        longitude=longitude,
        latitude=latitude,
        verbose=verbose,
    )
    try:
        location_time_series = data_array.sel(
            **indexers,
            method=neighbor_lookup,
            tolerance=tolerance,
        )
        if location_time_series.isnull().all():
            logger.warning("Selection returns an empty array or all NaNs.")
        location_time_series.load()  # load into memory for fast processing

    except Exception as exception:
        # Print the error message directly to stderr to ensure it's always shown
        error_message = f"Error in selecting data from {time_series} : {exception}."
        error_message_alternative = (
            f"Error in selecting data from [code]{time_series}[/code] : {exception}."
        )
        print(f"{error_message}\n")
        logger.error(
            error_message,
            alt=error_message_alternative,
        )
        raise SystemExit(33)

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    logger.debug(
        f"  < Returning selected location from time series : {location_time_series}",
        alt=f"  [green bold]<[/green bold] [bold]Returning[/bold] selected [brown]location[/brown] from time series : {location_time_series}",
    )

    return location_time_series
