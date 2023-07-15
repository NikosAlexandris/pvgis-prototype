from devtools import debug

import typer
from typing_extensions import Annotated
from typing import Optional
from typing import Tuple
from colorama import Fore, Style
from datetime import datetime
from pathlib import Path
import xarray as xr
import numpy as np
from distributed import LocalCluster, Client
import dask

import logging
from .log import logger
import warnings
from .utils import get_scale_and_offset
from .utils import select_coordinates
from .plot import plot_series
from .hardcodings import exclamation_mark
from .hardcodings import check_mark
from .hardcodings import x_mark


app = typer.Typer(
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f'󰞱  Work with time series',
)


# def read_time_series(
#         netcdf,
#         longitude,
#         latitude,
#         time,
#         convert_longitude_360,
#         output_filename,
#         variable_name_as_suffix,
#     ):
#     """
#     Plot location series
#     """
#     data_array = xr.open_dataarray(netcdf)
#     data_array = select_coordinates(
#             data_array=data_array,
#             longitude=longitude,
#             latitude=latitude,
#             time=time,
#             )
#     if data_array.size == 1:
#         single_value = float(data_array.values)
#         warning = Fore.YELLOW + f'{exclamation_mark} The selection matches a single value : {single_value}' + Style.RESET_ALL
#         typer.echo(Fore.YELLOW + warning)
#         return single_value

#     return data_array


# @app.callback('series', invoke_without_command=True)
@app.command('select',
             no_args_is_help=True,
             help='  Select time series over a location',             
             )
def select_time_series(
        netcdf: Annotated[Path, typer.Argument(help='Input netCDF file')],
        longitude: Annotated[float, typer.Argument(
            help='Longitude in decimal degrees ranging in',
            min=-180, max=360)] = None,
        latitude: Annotated[float, typer.Argument(
            help='Latitude in decimal degrees, south is negative',
            min=-90, max=90)] = None,
        time: Annotated[Optional[str], typer.Argument(
            help='Time of data to extract from series (note: use quotes)')] = None,
        convert_longitude_360: Annotated[bool, typer.Option(
            help='Convert range of longitude values to [0, 360]',
            rich_help_panel="Helpers")] = False,
        output_filename: Annotated[Path, typer.Option(
            help='Figure output filename',
            rich_help_panel='Options')] = 'series_in',
        variable_name_as_suffix: Annotated[bool, typer.Option(
            help='Suffix the output filename with the variable',
            rich_help_panel='Options')] = True,
    ):
    """
    Plot location series
    """
    if convert_longitude_360:
        longitude = longitude % 360

    if longitude < 0:
        warning = Fore.YELLOW + f'{exclamation_mark} '
        warning += f'The longitude ' + Style.RESET_ALL
        warning += Fore.RED + f'{longitude} ' + f'is negative. ' + Style.RESET_ALL
        warning += Fore.YELLOW + f'Consider using `--convert-longitude-360` if the dataset in question is such!' + Style.RESET_ALL
        # logger.warning(warning)
        typer.echo(Fore.YELLOW + warning)

    logger.handlers = []  # Remove any existing handlers
    file_handler = logging.FileHandler(f'{output_filename}_{netcdf.name}.log')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s, %(msecs)d; %(levelname)-8s; %(lineno)4d: %(message)s", datefmt="%I:%M:%S")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.info(f'Dataset : {netcdf.name}')
    logger.info(f'Path to : {netcdf.parent.absolute()}')
    scale_factor, add_offset = get_scale_and_offset(netcdf)
    logger.info(f'Scale factor : {scale_factor}, Offset : {add_offset}')

    if (longitude and latitude):
        logger.info(f'Coordinates : {longitude}, {latitude}')

    data_array = xr.open_dataarray(netcdf)
    data_array = select_coordinates(
            data_array=data_array,
            longitude=longitude,
            latitude=latitude,
            time=time,
            )

    if data_array.size == 1:
        single_value = float(data_array.values)
        warning = Fore.YELLOW + f'{exclamation_mark} The selection matches a single value : {single_value}' + Style.RESET_ALL
        logger.warning(warning)
        typer.echo(Fore.YELLOW + warning)
        return single_value

    typer.echo(data_array)
    return data_array


@app.command('select-52',
             no_args_is_help=True,
             help='  Select PVGIS 5.2 native time series over a location',             
             )
def select_52_time_series(
        pvgis_cube: Annotated[Path, typer.Argument(help='Input PVGIS <= 5.2 space-time cube file')],
        longitude: Annotated[float, typer.Argument(
            help='Longitude in decimal degrees ranging in',
            min=-180, max=360)] = None,
        latitude: Annotated[float, typer.Argument(
            help='Latitude in decimal degrees, south is negative',
            min=-90, max=90)] = None,
        time: Annotated[Optional[str], typer.Argument(
            help='Time of data to extract from series (note: use quotes)')] = None,
        convert_longitude_360: Annotated[bool, typer.Option(
            help='Convert range of longitude values to [0, 360]',
            rich_help_panel="Helpers")] = False,
        output_filename: Annotated[Path, typer.Option(
            help='Figure output filename',
            rich_help_panel='Options')] = 'series_in',
        variable_name_as_suffix: Annotated[bool, typer.Option(
            help='Suffix the output filename with the variable',
            rich_help_panel='Options')] = True,
    ):
    """
    Plot location series
    """
    if convert_longitude_360:
        longitude = longitude % 360

    if longitude < 0:
        warning = Fore.YELLOW + f'{exclamation_mark} '
        warning += f'The longitude ' + Style.RESET_ALL
        warning += Fore.RED + f'{longitude} ' + f'is negative. ' + Style.RESET_ALL
        warning += Fore.YELLOW + f'Consider using `--convert-longitude-360` if the dataset in question is such!' + Style.RESET_ALL
        # logger.warning(warning)
        typer.echo(Fore.YELLOW + warning)

    logger.handlers = []  # Remove any existing handlers
    file_handler = logging.FileHandler(f'{output_filename}_{pvgis_cube.name}.log')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s, %(msecs)d; %(levelname)-8s; %(lineno)4d: %(message)s", datefmt="%I:%M:%S")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.info(f'Dataset : {pvgis_cube.name}')
    logger.info(f'Path to : {pvgis_cube.parent.absolute()}')
    # scale_factor, add_offset = get_scale_and_offset(pvgis_cube)
    # logger.info(f'Scale factor : {scale_factor}, Offset : {add_offset}')

    if (longitude and latitude):
        logger.info(f'Coordinates : {longitude}, {latitude}')

    # read time series cube -- without scaling as to not remove the nodata attribute
    import pvgis
    cube = pvgis.load_bz2_tile(pvgis_cube)  # it is a cube, not a tile
    data_array = pvgis.da_from_bz2_tile(cube)
    data_array = select_coordinates(
            data_array=data_array,
            longitude=longitude,
            latitude=latitude,
            time=time,
            )

    if data_array.size == 1:
        single_value = float(data_array.values)
        warning = Fore.YELLOW + f'{exclamation_mark} The selection matches a single value : {single_value}' + Style.RESET_ALL
        logger.warning(warning)
        typer.echo(Fore.YELLOW + warning)
        return single_value

    typer.echo(data_array)
    return data_array


@app.command(
        no_args_is_help=True,
        help='󰾂  Group-by of time series over a location',
 )
def resample(
    indexer: str = None,  # The offset string or object representing target conversion.
    # or : Mapping from a date-time dimension to resample frequency [1]
):
    """Time-based groupby of solar radiation and PV output power time series over a location.

    For example:
    - solar radiation on horizontal and inclined planes
    - Direct Normal Irradiation (DNI) and more in various
    - the daily variation in the clear-sky radiation

    - hourly
    - daily
    - monthly


    Parameters
    ----------
    indexer: str
    """
    pass


@app.command(
    no_args_is_help=True,
    help=f':chart_increasing: Plot time series',
)
def plot(
        netcdf: Annotated[Path, typer.Argument(help='Input netCDF file')],
        longitude: Annotated[float, typer.Argument(
            help='Longitude in decimal degrees ranging in',
            min=-180, max=360)] = None,
        latitude: Annotated[float, typer.Argument(
            help='Latitude in decimal degrees, south is negative',
            min=-90, max=90)] = None,
        time: Annotated[Optional[str], typer.Argument(
            help='Time of data to extract from series (note: use quotes)')] = None,
        convert_longitude_360: Annotated[bool, typer.Option(
            help='Convert range of longitude values to [0, 360]',
            rich_help_panel="Helpers")] = False,
        output_filename: Annotated[Path, typer.Option(
            help='Figure output filename',
            rich_help_panel='Options')] = 'series_in',
        variable_name_as_suffix: Annotated[bool, typer.Option(
            help='Suffix the output filename with the variable',
            rich_help_panel='Options')] = True,
        tufte_style: Annotated[bool, typer.Option(
            help='Try to mimic Edward Tufte style',
            rich_help_panel='Options')] = False,
        ):
    """ """
    data_array = select_time_series(
            netcdf,
            longitude,
            latitude,
            time,
            convert_longitude_360,
            output_filename,
            variable_name_as_suffix,
            )
    try:
        output_filename = plot_series(
                data_array=data_array,
                time=time,
                figure_name=output_filename,
                # add_offset=add_offset,
                variable_name_as_suffix=variable_name_as_suffix,
                tufte_style=tufte_style,
                )
    except Exception as exc:
        typer.echo(f"Something went wrong in plotting the data: {str(exc)}")
        raise SystemExit(33)


@app.command(
    no_args_is_help=True,
    help=f'  Plot time series in the terminal',)
def uniplot(
        netcdf: Annotated[Path, typer.Argument(help='Input netCDF file')],
        longitude: Annotated[float, typer.Argument(
            help='Longitude in decimal degrees ranging in',
            min=-180, max=360)] = None,
        latitude: Annotated[float, typer.Argument(
            help='Latitude in decimal degrees, south is negative',
            min=-90, max=90)] = None,
        time: Annotated[Optional[str], typer.Argument(
            help='Time of data to extract from series (note: use quotes)')] = None,
        convert_longitude_360: Annotated[bool, typer.Option(
            help='Convert range of longitude values to [0, 360]',
            rich_help_panel="Helpers")] = False,
        output_filename: Annotated[Path, typer.Option(
            help='Figure output filename',
            rich_help_panel='Options')] = 'series_in',
        variable_name_as_suffix: Annotated[bool, typer.Option(
            help='Suffix the output filename with the variable',
            rich_help_panel='Options')] = True,
        tufte_style: Annotated[bool, typer.Option(
            help='Try to mimic Edward Tufte style',
            rich_help_panel='Options')] = False,
        lines: bool = True,
        title: str = 'Uniplot',
        unit: str = 'Units',  #" °C")
        ):
    """
    """
    from uniplot import plot
    data_array = select_time_series(
            netcdf,
            longitude,
            latitude,
            time,
            convert_longitude_360,
            output_filename,
            variable_name_as_suffix,
            )
    supertitle = f'{data_array.long_name}'
    y_label = data_array.units
    plot(
        # x=data_array,
        # xs=data_array,
        ys=data_array,
        lines=True,
        title=supertitle,
        y_unit=" °C",
    )


if __name__ == "__main__":
    app()
