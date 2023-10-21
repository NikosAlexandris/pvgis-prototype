from devtools import debug

import typer
from typing_extensions import Annotated
from typing import Any
from typing import Optional
from typing import List
from typing import Tuple
from enum import Enum

from pvgisprototype.cli.typer_parameters import OrderCommands
from pvgisprototype.cli.typer_parameters import typer_argument_longitude
from pvgisprototype.cli.typer_parameters import typer_argument_longitude_in_degrees
from pvgisprototype.cli.typer_parameters import typer_argument_latitude
from pvgisprototype.cli.typer_parameters import typer_argument_latitude_in_degrees
from pvgisprototype.cli.typer_parameters import typer_argument_time_series
from pvgisprototype.cli.typer_parameters import typer_option_time_series
from pvgisprototype.cli.typer_parameters import typer_argument_timestamp
from pvgisprototype.cli.typer_parameters import typer_argument_timestamps
from pvgisprototype.cli.typer_parameters import typer_option_timestamps
from pvgisprototype.cli.typer_parameters import typer_option_start_time
from pvgisprototype.cli.typer_parameters import typer_option_end_time
from pvgisprototype.cli.typer_parameters import typer_option_convert_longitude_360
from pvgisprototype.cli.typer_parameters import typer_option_mask_and_scale
from pvgisprototype.cli.typer_parameters import typer_option_nearest_neighbor_lookup
from pvgisprototype.cli.typer_parameters import typer_option_inexact_matches_method
from pvgisprototype.cli.typer_parameters import typer_option_tolerance
from pvgisprototype.cli.typer_parameters import typer_option_in_memory
from pvgisprototype.cli.typer_parameters import typer_option_uniplot_lines
from pvgisprototype.cli.typer_parameters import typer_option_uniplot_title
from pvgisprototype.cli.typer_parameters import typer_option_uniplot_unit
from pvgisprototype.cli.typer_parameters import typer_option_statistics
from pvgisprototype.cli.typer_parameters import typer_option_csv
from pvgisprototype.cli.typer_parameters import typer_option_output_filename
from pvgisprototype.cli.typer_parameters import typer_option_variable_name_as_suffix
from pvgisprototype.cli.typer_parameters import typer_option_tufte_style
from pvgisprototype.cli.typer_parameters import typer_option_verbose

from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_advanced_options
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_output
from rich import print
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

from pvgisprototype.api.series.models import MethodsForInexactMatches
from pvgisprototype.api.series.utilities import get_scale_and_offset
from pvgisprototype.api.series.utilities import select_location_time_series
from pvgisprototype.api.series.select import select_time_series
from pvgisprototype.api.utilities.timestamp import parse_timestamp_series
from pvgisprototype.api.series.plot import plot_series

from pvgisprototype.api.series.hardcodings import exclamation_mark
from pvgisprototype.api.series.hardcodings import check_mark
from pvgisprototype.api.series.hardcodings import x_mark

from pvgisprototype.api.series.statistics import calculate_series_statistics
from pvgisprototype.api.series.statistics import print_series_statistics
from pvgisprototype.api.series.statistics import export_statistics_to_csv

from pvgisprototype.cli.messages import NOT_IMPLEMENTED_CLI
from pvgisprototype.cli.messages import ERROR_IN_PLOTTING_DATA
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype import Longitude
from pvgisprototype.constants import UNITS_NAME


app = typer.Typer(
    cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f':chart: Work with time series',
)


def warn_for_negative_longitude(
    longitude: Longitude = None,
):
    """Warn for negative longitude value

    Maybe the input dataset ranges in [0, 360] degrees ?
    """
    if longitude < 0:
        warning = Fore.YELLOW + f'{exclamation_mark} '
        warning += f'The longitude ' + Style.RESET_ALL
        warning += f'{longitude} ' + Fore.RED + f'is negative. ' + Style.RESET_ALL
        warning += Fore.YELLOW + f'If the input dataset\'s longitude values range in [0, 360], consider using `--convert-longitude-360`!' + Style.RESET_ALL
        # logger.warning(warning)
        typer.echo(Fore.YELLOW + warning)


@app.command(
    'select',
    no_args_is_help=True,
    help='  Select time series over a location',
)
def select(
    time_series: Annotated[Path, typer_argument_time_series],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    timestamps: Annotated[Optional[Any], typer_argument_timestamps] = None,
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    convert_longitude_360: Annotated[bool, typer_option_convert_longitude_360] = False,
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = False,
    neighbor_lookup: Annotated[MethodsForInexactMatches, typer_option_nearest_neighbor_lookup] = None,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = 0.1, # Customize default if needed
    in_memory: Annotated[bool, typer_option_in_memory] = False,
    statistics: Annotated[bool, typer_option_statistics] = False,
    csv: Annotated[Path, typer_option_csv] = 'series_in',
    output_filename: Annotated[Path, typer_option_output_filename] = 'series_in',  #Path(),
    variable_name_as_suffix: Annotated[bool, typer_option_variable_name_as_suffix] = True,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """Select location series"""
    if convert_longitude_360:
        longitude = longitude % 360
    warn_for_negative_longitude(longitude)

    location_time_series = select_time_series(
        time_series=time_series,
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        start_time=start_time,
        end_time=end_time,
        # convert_longitude_360=convert_longitude_360,
        mask_and_scale=mask_and_scale,
        neighbor_lookup=neighbor_lookup,
        # inexact_matches_method=inexact_matches_method,
        tolerance=tolerance,
        in_memory=in_memory,
        variable_name_as_suffix=variable_name_as_suffix,
        verbose=verbose,
    )

    if verbose == 5:
        debug(locals())


    # if output_filename:
    #     output_filename = Path(output_filename)
    #     extension = output_filename.suffix.lower()

    #     if extension.lower() == '.nc':
    #         location_time_series.to_time_series(output_filename)

    #     elif extension.lower() == '.csv':
    #         location_time_series.to_pandas().to_csv(output_filename)

    #     else:
    #         raise ValueError(f'Unsupported file extension: {extension}')

    # statistics after echoing series which might be Long!
    if statistics:
        data_statistics = calculate_series_statistics(location_time_series)
        print_series_statistics(data_statistics)
        if csv:
            export_statistics_to_csv(data_statistics, 'location_time_series_statistics')

    if isinstance(location_time_series, float):
        print(float)

    if isinstance(location_time_series, xr.DataArray):
        print(f'Series : {location_time_series.values}')


@app.command(
    no_args_is_help=True,
    help=f'󰾂  Group-by of time series over a location {NOT_IMPLEMENTED_CLI}',
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
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    timestamps: Annotated[Optional[datetime], typer_argument_timestamps] = None,
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    convert_longitude_360: Annotated[bool, typer_option_convert_longitude_360] = False,
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = False,
    neighbor_lookup: Annotated[MethodsForInexactMatches, typer_option_nearest_neighbor_lookup] = None,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = 0.1, # Customize default if needed
    output_filename: Annotated[Path, typer_option_output_filename] = 'series_in',  #Path(),
    variable_name_as_suffix: Annotated[bool, typer_option_variable_name_as_suffix] = True,
    tufte_style: Annotated[bool, typer_option_tufte_style] = False,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """Plot selected time series"""
    data_array = select_time_series(
        time_series=time_series,
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        start_time=start_time,
        end_time=end_time,
        # convert_longitude_360=convert_longitude_360,
        mask_and_scale=mask_and_scale,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        # in_memory=in_memory,
        verbose=verbose,
    )
    try:
        plot_series(
            data_array=data_array,
            time=timestamps,
            figure_name=output_filename,
            # add_offset=add_offset,
            variable_name_as_suffix=variable_name_as_suffix,
            tufte_style=tufte_style,
        )
    except Exception as exception:
        print(f"{ERROR_IN_PLOTTING_DATA} : {exception}")
        raise SystemExit(33)


@app.command(
    no_args_is_help=True,
    help=f'  Plot time series in the terminal',)
def uniplot(
    time_series: Annotated[Path, typer_argument_time_series],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    timestamps: Annotated[Optional[datetime], typer_argument_timestamps] = None,
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    convert_longitude_360: Annotated[bool, typer_option_convert_longitude_360] = False,
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = False,
    nearest_neighbor_lookup: Annotated[bool, typer_option_nearest_neighbor_lookup] = False,
    inexact_matches_method: Annotated[MethodsForInexactMatches, typer_option_inexact_matches_method] = MethodsForInexactMatches.nearest,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = 0.1, # Customize default if needed
    lines: Annotated[bool, typer_option_uniplot_lines] = True,
    title: Annotated[str, typer_option_uniplot_title] = None,
    unit: Annotated[str, typer_option_uniplot_unit] = UNITS_NAME,  #" °C")
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """Plot time series in the terminal"""
    from uniplot import plot
    data_array = select_time_series(
        time_series=time_series,
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        start_time=start_time,
        end_time=end_time,
        # convert_longitude_360=convert_longitude_360,
        mask_and_scale=mask_and_scale,
        nearest_neighbor_lookup=nearest_neighbor_lookup,
        inexact_matches_method=inexact_matches_method,
        tolerance=tolerance,
        # in_memory=in_memory,
        verbose=verbose,
    )
    if isinstance(data_array, float):
        print(f"{exclamation_mark} [red]Aborting[/red] as I [red]cannot[/red] plot the single float value {float}!")
        typer.Abort()

    if isinstance(data_array, xr.DataArray):
        supertitle = f'{data_array.long_name}'
        unit = data_array.units
        plot(
            # x=data_array,
            # xs=data_array,
            ys=data_array,
            lines=lines,
            title=supertitle,
            y_unit=' ' + unit,
        )


if __name__ == "__main__":
    app()
