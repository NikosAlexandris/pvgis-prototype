from devtools import debug

import typer
from typing_extensions import Annotated
from pandas import DatetimeIndex
from pvgisprototype.api.utilities.timestamp import now_datetime
from typing import Optional
from typing import List
from typing import Tuple
from enum import Enum

from pvgisprototype.cli.typer.group import OrderCommands
from pvgisprototype.cli.typer.location import typer_argument_longitude
from pvgisprototype.cli.typer.location import typer_argument_longitude_in_degrees
from pvgisprototype.cli.typer.location import typer_argument_latitude
from pvgisprototype.cli.typer.location import typer_argument_latitude_in_degrees
from pvgisprototype.cli.typer.timestamps import typer_argument_timestamp
from pvgisprototype.cli.typer.timestamps import typer_argument_timestamps
from pvgisprototype.cli.typer.timestamps import typer_argument_naive_timestamps
from pvgisprototype.cli.typer.timestamps import typer_option_timestamps
from pvgisprototype.cli.typer.timestamps import typer_option_start_time
from pvgisprototype.cli.typer.timestamps import typer_option_periods
from pvgisprototype.cli.typer.timestamps import typer_option_frequency
from pvgisprototype.cli.typer.timestamps import typer_option_end_time
from pvgisprototype.cli.typer.time_series import typer_argument_time_series
from pvgisprototype.cli.typer.time_series import typer_option_data_variable
from pvgisprototype.cli.typer.time_series import typer_option_time_series
from pvgisprototype.cli.typer.time_series import typer_option_nearest_neighbor_lookup
from pvgisprototype.cli.typer.time_series import typer_option_tolerance
from pvgisprototype.cli.typer.time_series import typer_option_mask_and_scale
from pvgisprototype.cli.typer.time_series import typer_option_in_memory
from pvgisprototype.cli.typer.helpers import typer_option_convert_longitude_360
from pvgisprototype.cli.typer.plot import typer_option_uniplot_lines
from pvgisprototype.cli.typer.plot import typer_option_uniplot_title
from pvgisprototype.cli.typer.plot import typer_option_uniplot_unit
from pvgisprototype.cli.typer.plot import typer_option_uniplot_terminal_width
from pvgisprototype.cli.typer.plot import typer_option_tufte_style
from pvgisprototype.cli.typer.statistics import typer_option_statistics
from pvgisprototype.cli.typer.statistics import typer_option_groupby
from pvgisprototype.cli.typer.output import typer_option_rounding_places
from pvgisprototype.cli.typer.output import typer_option_csv
from pvgisprototype.cli.typer.output import typer_option_output_filename
from pvgisprototype.cli.typer.output import typer_option_variable_name_as_suffix
from pvgisprototype.cli.typer.verbosity import typer_option_verbose
from pvgisprototype.cli.typer.log import typer_option_log

from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_advanced_options
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_output
from pvgisprototype.cli.print import print_irradiance_table_2
from rich import print
from datetime import datetime
from pathlib import Path
import xarray as xr
import xarray_extras
from pvgisprototype.api.series.csv import to_csv
import numpy as np
from distributed import LocalCluster, Client
import dask

from pvgisprototype.log import logger
import warnings

from pvgisprototype.api.series.models import MethodForInexactMatches
from pvgisprototype.api.series.utilities import get_scale_and_offset
from pvgisprototype.api.series.utilities import select_location_time_series
from pvgisprototype.api.series.select import select_time_series
from pvgisprototype.api.series.plot import plot_series

from pvgisprototype.api.series.hardcodings import exclamation_mark
from pvgisprototype.api.series.hardcodings import check_mark
from pvgisprototype.api.series.hardcodings import x_mark

from pvgisprototype.api.series.statistics import calculate_series_statistics
from pvgisprototype.api.series.statistics import print_series_statistics
from pvgisprototype.api.series.statistics import export_statistics_to_csv

from pvgisprototype.cli.messages import NOT_IMPLEMENTED_CLI
from pvgisprototype.cli.messages import ERROR_IN_PLOTTING_DATA
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT, SYMBOL_CHART_CURVE, SYMBOL_GROUP, SYMBOL_PLOT, SYMBOL_SELECT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype import Longitude
from pvgisprototype.constants import UNIT_NAME
from pvgisprototype.constants import TERMINAL_WIDTH_FRACTION
from pvgisprototype.constants import NEIGHBOR_LOOKUP_DEFAULT
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.constants import MASK_AND_SCALE_FLAG_DEFAULT
from pvgisprototype.constants import IN_MEMORY_FLAG_DEFAULT
from pvgisprototype.constants import STATISTICS_FLAG_DEFAULT
from pvgisprototype.constants import GROUPBY_DEFAULT
from pvgisprototype.constants import CSV_PATH_DEFAULT
from pvgisprototype.cli.typer.output import typer_option_fingerprint
from pvgisprototype.constants import FINGERPRINT_FLAG_DEFAULT


app = typer.Typer(
    cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f'{SYMBOL_CHART_CURVE} Work with time series',
)


def warn_for_negative_longitude(
    longitude: Longitude = None,
):
    """Warn for negative longitude value

    Maybe the input dataset ranges in [0, 360] degrees ?
    """
    if longitude < 0:
        warning = f'{exclamation_mark} '
        warning += f'The longitude '
        warning += f'{longitude} ' + f'is negative. '
        warning += f'If the input dataset\'s longitude values range in [0, 360], consider using `--convert-longitude-360`!'
        logger.warning(warning)
        # print(warning)


@app.command(
    'select',
    no_args_is_help=True,
    help='  Select time series over a location',
)
def select(
    time_series: Annotated[Path, typer_argument_time_series],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    time_series_2: Annotated[Path, typer_option_time_series] = None,
    timestamps: Annotated[DatetimeIndex, typer_argument_naive_timestamps] = str(now_datetime()),
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,  # Used by a callback function
    periods: Annotated[Optional[int], typer_option_periods] = None,  # Used by a callback function
    frequency: Annotated[Optional[str], typer_option_frequency] = None,  # Used by a callback function
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,  # Used by a callback function
    convert_longitude_360: Annotated[bool, typer_option_convert_longitude_360] = False,
    variable: Annotated[Optional[str], typer_option_data_variable] = None,
    neighbor_lookup: Annotated[MethodForInexactMatches, typer_option_nearest_neighbor_lookup] = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = TOLERANCE_DEFAULT,
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: Annotated[bool, typer_option_in_memory] = IN_MEMORY_FLAG_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[Optional[str], typer_option_groupby] = GROUPBY_DEFAULT,
    csv: Annotated[Path, typer_option_csv] = CSV_PATH_DEFAULT,
    output_filename: Annotated[Path, typer_option_output_filename] = 'series_in',  #Path(),
    variable_name_as_suffix: Annotated[bool, typer_option_variable_name_as_suffix] = True,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    log: Annotated[int, typer_option_log] = VERBOSE_LEVEL_DEFAULT,
):
    """Select location series"""
    if convert_longitude_360:
        longitude = longitude % 360
    warn_for_negative_longitude(longitude)

    if not variable:
        dataset = xr.open_dataset(time_series)
        if len(dataset.data_vars) >= 2:
            variables = list(dataset.data_vars.keys())
            print(f"The dataset contains more than one variable : {variables}")
            variable = typer.prompt("Please specify the variable you are interested in from the above list")
        else:
            variable = list(dataset.data_vars)
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
        tolerance=tolerance,
        in_memory=in_memory,
        variable_name_as_suffix=variable_name_as_suffix,
        verbose=verbose,
        log=log,
    )
    location_time_series_2 = select_time_series(
        time_series=time_series_2,
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        start_time=start_time,
        end_time=end_time,
        # convert_longitude_360=convert_longitude_360,
        mask_and_scale=mask_and_scale,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        in_memory=in_memory,
        variable_name_as_suffix=variable_name_as_suffix,
        verbose=verbose,
        log=log,
    )
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
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

    # if isinstance(location_time_series, float):
    #     print(float)

    # if isinstance(location_time_series, xr.DataArray):
    #     # print(f'Series : {location_time_series.values}')

    results = {
        location_time_series.name: location_time_series.to_numpy(),
    }
    if location_time_series_2 is not None:
        more_results = {
        location_time_series_2.name: location_time_series_2.to_numpy() if location_time_series_2 is not None else None
        }
        results = results | more_results

    title = 'Location time series'
    
    if verbose:
        # special case!
        if location_time_series is not None and timestamps is None:
            timestamps = location_time_series.time.to_numpy()

        print_irradiance_table_2(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            dictionary=results,
            title=title,
            rounding_places=rounding_places,
            verbose=verbose,
        )

    # statistics after echoing series which might be Long!

    if statistics:
        print_series_statistics(
            data_array=location_time_series,
            groupby=groupby,
            title='Selected series',
            rounding_places=rounding_places,
        )

    if csv:
        # export_statistics_to_csv(
        #     data_array=location_time_series,
        #     filename=csv,
        # )
        to_csv(
            x=location_time_series,
            path=str(csv),
        )


@app.command(
    'select-fast',
    no_args_is_help=True,
    help=f'{SYMBOL_SELECT} Retrieve series over a location.-',
)
def select_fast(
    time_series: Annotated[Path, typer_argument_time_series],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    time_series_2: Annotated[Path, typer_option_time_series] = None,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = 0.1, # Customize default if needed
    # in_memory: Annotated[bool, typer_option_in_memory] = False,
    csv: Annotated[Path, typer_option_csv] = 'series.csv',
    tocsv: Annotated[Path, typer_option_csv] = 'seriesto.csv',
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """Bare read & write"""
    try:
        series = xr.open_dataarray(time_series).sel(lon=longitude, lat=latitude, method='nearest')
        if time_series_2:
            series_2 = xr.open_dataarray(time_series_2).sel(lon=longitude, lat=latitude, method='nearest')
        if csv:
            series.to_pandas().to_csv(csv)
            if time_series_2:
                series_2.to_pandas().to_csv(csv.name+'2')
        elif tocsv:
            to_csv(x=series, path=str(tocsv))
            if time_series_2:
                to_csv(x=series_2, path=str(tocsv)+'2')
        print('Done.-')
    except Exception as e:
        print(f"An error occurred: {e}")


@app.command(
    no_args_is_help=True,
    help=f'{SYMBOL_GROUP} Group-by of time series over a location {NOT_IMPLEMENTED_CLI}',
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
    help=f'{SYMBOL_PLOT} Plot time series',
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
    neighbor_lookup: Annotated[MethodForInexactMatches, typer_option_nearest_neighbor_lookup] = None,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = 0.1, # Customize default if needed
    resample_large_series: Annotated[bool, 'Resample large time series?'] = False,
    output_filename: Annotated[Path, typer_option_output_filename] = None,
    variable_name_as_suffix: Annotated[bool, typer_option_variable_name_as_suffix] = True,
    width: Annotated[int, 'Width for the plot'] = 16,
    height: Annotated[int, 'Height for the plot'] = 3,
    tufte_style: Annotated[bool, typer_option_tufte_style] = False,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    fingerprint: Annotated[bool, typer_option_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
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
            width=width,
            height=height,
            resample_large_series=resample_large_series,
            fingerprint=fingerprint,
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
    time_series_2: Annotated[Path, typer_option_time_series] = None,
    timestamps: Annotated[Optional[datetime], typer_argument_timestamps] = None,
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    convert_longitude_360: Annotated[bool, typer_option_convert_longitude_360] = False,
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = False,
    neighbor_lookup: Annotated[MethodForInexactMatches, typer_option_nearest_neighbor_lookup] = None,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = 0.1, # Customize default if needed
    resample_large_series: Annotated[bool, 'Resample large time series?'] = False,
    lines: Annotated[bool, typer_option_uniplot_lines] = True,
    title: Annotated[str, typer_option_uniplot_title] = None,
    unit: Annotated[str, typer_option_uniplot_unit] = UNIT_NAME,  #" °C")
    terminal_width_fraction: Annotated[float, typer_option_uniplot_terminal_width] = TERMINAL_WIDTH_FRACTION,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """Plot time series in the terminal"""
    import os 
    terminal_columns, _ = os.get_terminal_size() # we don't need lines!
    terminal_length = int(terminal_columns * terminal_width_fraction)
    from functools import partial
    from uniplot import plot as default_plot
    plot = partial(default_plot, width=terminal_length)
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
    if resample_large_series:
        data_array = data_array.resample(time='1M').mean()
    data_array_2 = select_time_series(
        time_series=time_series_2,
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
    if resample_large_series:
        data_array_2 = data_array_2.resample(time='1M').mean()
    if isinstance(data_array, float):
        print(f"{exclamation_mark} [red]Aborting[/red] as I [red]cannot[/red] plot the single float value {float}!")
        typer.Abort()

    if isinstance(data_array, xr.DataArray):
        supertitle = getattr(data_array, 'long_name', 'Untitled')
        label = getattr(data_array, 'name', None)
        label_2 = getattr(data_array_2, 'name', None) if data_array_2 is not None else None
        unit = getattr(data_array, 'units', None)
        plot(
            # x=data_array,
            # xs=data_array,
            ys=[data_array, data_array_2] if data_array_2 is not None else data_array,
            legend_labels = [label, label_2],
            lines=lines,
            title=title if title else supertitle,
            y_unit=' ' + str(unit),
            force_ascii=True,
        )


if __name__ == "__main__":
    app()
