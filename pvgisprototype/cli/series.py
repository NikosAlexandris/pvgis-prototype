from devtools import debug

import typer
from typing_extensions import Annotated
from typing import Optional
from typing import Tuple
from enum import Enum

from .typer_parameters import OrderCommands
from .typer_parameters import typer_argument_longitude
from .typer_parameters import typer_argument_longitude_in_degrees
from .typer_parameters import typer_argument_latitude
from .typer_parameters import typer_argument_latitude_in_degrees
from .typer_parameters import typer_argument_time_series
from .typer_parameters import typer_argument_time
from .typer_parameters import typer_option_convert_longitude_360
from .typer_parameters import typer_option_mask_and_scale
from .typer_parameters import typer_option_inexact_matches_method
from .typer_parameters import typer_option_tolerance
from .typer_parameters import typer_option_in_memory
from .typer_parameters import typer_option_statistics
from .typer_parameters import typer_option_output_filename
from .typer_parameters import typer_option_variable_name_as_suffix
from .typer_parameters import typer_option_tufte_style
from .typer_parameters import typer_option_verbose

from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_advanced_options
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_output
from colorama import Fore, Style
from datetime import datetime
from pathlib import Path
import xarray as xr
import xarray_extras
import numpy as np
from distributed import LocalCluster, Client
import dask

import logging
from pvgisprototype.api.series.log import logger
import warnings

from pvgisprototype.api.series.utilities import open_data_array
from pvgisprototype.api.series.utilities import get_scale_and_offset
from pvgisprototype.api.series.utilities import select_coordinates
from pvgisprototype.api.series.plot import plot_series

from pvgisprototype.api.series.hardcodings import exclamation_mark
from pvgisprototype.api.series.hardcodings import check_mark
from pvgisprototype.api.series.hardcodings import x_mark

from pvgisprototype.api.series.statistics import calculate_series_statistics
from pvgisprototype.api.series.statistics import print_series_statistics
from pvgisprototype.api.series.statistics import export_statistics_to_csv


app = typer.Typer(
    cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f':chart: Work with time series',
)


class MethodsForInexactMatches(str, Enum):
    none = None # only exact matches
    pad = 'pad' # ffill: propagate last valid index value forward
    backfill = 'backfill' # bfill: propagate next valid index value backward
    nearest = 'nearest' # use nearest valid index value


# @app.callback('series', invoke_without_command=True)
@app.command(
    'select',
    no_args_is_help=True,
    help='  Select time series over a location',             
)
def select_time_series(
    time_series: Annotated[Path, typer_argument_time_series],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    time: Annotated[Optional[str], typer_argument_time] = None,
    convert_longitude_360: Annotated[bool, typer_option_convert_longitude_360] = False,
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = False,
    inexact_matches_method: Annotated[MethodsForInexactMatches, typer_option_inexact_matches_method] = MethodsForInexactMatches.nearest,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = 0.1, # Customize default if needed
    in_memory: Annotated[bool, typer_option_in_memory] = False,
    statistics: Annotated[bool, typer_option_statistics] = False,
    # csv: Annotated[Path, typer_option_csv] = 'series_in',
    output_filename: Annotated[Path, typer_option_output_filename] = 'series_in',  #Path(),
    variable_name_as_suffix: Annotated[bool, typer_option_variable_name_as_suffix] = True,
    verbose: Annotated[Optional[bool], typer_option_verbose] = False,
):
    """
    Plot location series
    """
    if convert_longitude_360:
        longitude = longitude % 360

    if longitude < 0:
        warning = Fore.YELLOW + f'{exclamation_mark} '
        warning += f'The longitude ' + Style.RESET_ALL
        warning += f'{longitude} ' + Fore.RED + f'is negative. ' + Style.RESET_ALL
        warning += Fore.YELLOW + f'If the input dataset\'s longitude values range in [0, 360], consider using `--convert-longitude-360`!' + Style.RESET_ALL
        # logger.warning(warning)
        typer.echo(Fore.YELLOW + warning)

    logger.handlers = []  # Remove any existing handlers
    file_handler = logging.FileHandler(f'{output_filename}_{time_series.name}.log')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s, %(msecs)d; %(levelname)-8s; %(lineno)4d: %(message)s", datefmt="%I:%M:%S")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.info(f'Dataset : {time_series.name}')
    logger.info(f'Path to : {time_series.parent.absolute()}')
    scale_factor, add_offset = get_scale_and_offset(time_series)
    logger.info(f'Scale factor : {scale_factor}, Offset : {add_offset}')

    if (longitude and latitude):
        logger.info(f'Coordinates : {longitude}, {latitude}')

    data_array = open_data_array(
            time_series,
            mask_and_scale,
            in_memory,
            )
    data_array = select_coordinates(
        data_array=data_array,
        longitude=longitude,
        latitude=latitude,
        time=time,
        method=inexact_matches_method,
        tolerance=tolerance,
        verbose=verbose,
    )

    if data_array.size == 1:
        single_value = float(data_array.values)
        warning = Fore.YELLOW + f'{exclamation_mark} The selection matches a single value : {single_value}' + Style.RESET_ALL
        logger.warning(warning)
        if verbose:
            typer.echo(Fore.YELLOW + warning)
        return single_value

    # # if statistics_to_csv:
    # #     series_statistics = calculate_series_statistics(data_array)
    # #     export_statistics_to_csv(series_statistics)

    # if csv:
    #     data_array.to_pandas().to_csv(csv)

    # ---------------------------------------------------------- Remove Me ---
    typer.echo(data_array.values)
    # ---------------------------------------------------------- Remove Me ---

    # echo statistics after series which might be Long!
    if statistics:
        series_statistics = calculate_series_statistics(data_array)
        print_series_statistics(series_statistics)
        # return print_series_statistics(series_statistics)

    # if output_filename:
    #     output_filename = Path(output_filename)
    #     extension = output_filename.suffix.lower()

    #     if extension.lower() == '.nc':
    #         data_array.to_time_series(output_filename)

    #     elif extension.lower() == '.csv':
    #         data_array.to_pandas().to_csv(output_filename)

    #     else:
    #         raise ValueError(f'Unsupported file extension: {extension}')

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
    time_series: Annotated[Path, typer_argument_time_series],
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    time: Annotated[Optional[str], typer_argument_time] = None,
    convert_longitude_360: Annotated[bool, typer_option_convert_longitude_360] = False,
    output_filename: Annotated[Path, typer_option_output_filename] = 'series_in',  #Path(),
    variable_name_as_suffix: Annotated[bool, typer_option_variable_name_as_suffix] = True,
    tufte_style: Annotated[bool, typer_option_tufte_style] = False,
):
    """Plot selected time series"""
    data_array = select_time_series(
            time_series,
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
    time_series: Annotated[Path, typer_argument_time_series],
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    time: Annotated[Optional[str], typer_argument_time] = None,
    convert_longitude_360: Annotated[bool, typer_option_convert_longitude_360] = False,
    output_filename: Annotated[Path, typer_option_output_filename] = 'series_in',  #Path(),
    variable_name_as_suffix: Annotated[bool, typer_option_variable_name_as_suffix] = True,
    tufte_style: Annotated[bool, typer_option_tufte_style] = False,
    lines: bool = True,
    title: str = 'Uniplot',
    unit: str = 'Units',  #" °C")
    verbose: Annotated[Optional[bool], typer_option_verbose] = False,
):
    """Plot time series in the terminal"""
    from uniplot import plot
    data_array = select_time_series(
            time_series=time_series,
            longitude=longitude,
            latitude=latitude,
            time=time,
            convert_longitude_360=convert_longitude_360,
            statistics=False,
            output_filename=None,
            variable_name_as_suffix=variable_name_as_suffix,
            verbose=verbose,
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
