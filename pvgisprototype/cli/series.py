from datetime import datetime
from pathlib import Path

import typer
from devtools import debug
from pandas import DatetimeIndex, Timestamp
from rich import print
from typing_extensions import Annotated
from xarray import DataArray, open_dataset, open_dataarray

from pvgisprototype.api.series.hardcodings import check_mark, exclamation_mark, x_mark
from pvgisprototype import Longitude
from pvgisprototype.api.datetime.now import now_datetime
from pvgisprototype.api.series.csv import to_csv
from pvgisprototype.api.series.hardcodings import exclamation_mark
from pvgisprototype.api.series.models import MethodForInexactMatches
from pvgisprototype.api.series.plot import plot_series
from pvgisprototype.api.series.open import open_xarray_supported_time_series_data
from pvgisprototype.api.series.select import select_time_series
from pvgisprototype.api.series.statistics import print_series_statistics
from pvgisprototype.api.spectrum.constants import MAX_WAVELENGTH, MIN_WAVELENGTH
from pvgisprototype.cli.messages import ERROR_IN_PLOTTING_DATA, NOT_IMPLEMENTED_CLI
from pvgisprototype.cli.print.irradiance import print_irradiance_table_2, print_irradiance_xarray
from pvgisprototype.cli.typer.group import OrderCommands
from pvgisprototype.cli.typer.helpers import typer_option_convert_longitude_360
from pvgisprototype.cli.typer.location import (
    typer_argument_latitude_in_degrees,
    typer_argument_longitude_in_degrees,
)
from pvgisprototype.cli.typer.log import typer_option_log
from pvgisprototype.cli.typer.output import (
    typer_option_csv,
    typer_option_fingerprint,
    typer_option_output_filename,
    typer_option_rounding_places,
    typer_option_variable_name_as_suffix,
)
from pvgisprototype.cli.typer.plot import (
    typer_option_tufte_style,
    typer_option_uniplot,
    typer_option_uniplot_lines,
    typer_option_uniplot_terminal_width,
    typer_option_uniplot_title,
    typer_option_uniplot_unit,
)
from pvgisprototype.cli.typer.statistics import (
    typer_option_groupby,
    typer_option_statistics,
)
from pvgisprototype.cli.typer.time_series import (
    typer_argument_time_series,
    typer_option_data_variable,
    typer_option_in_memory,
    typer_option_mask_and_scale,
    typer_option_nearest_neighbor_lookup,
    typer_option_time_series,
    typer_option_tolerance,
)
from pvgisprototype.cli.typer.timestamps import (
    typer_argument_naive_timestamps,
    typer_argument_timestamps,
    typer_option_end_time,
    typer_option_frequency,
    typer_option_periods,
    typer_option_start_time,
)
from pvgisprototype.cli.typer.irradiance import (
    typer_option_minimum_spectral_irradiance_wavelength,
    typer_option_maximum_spectral_irradiance_wavelength,
)
from pvgisprototype.cli.typer.spectral_responsivity import (
    typer_option_wavelength_column_name,
)
from pvgisprototype.cli.typer.verbosity import typer_option_quiet, typer_option_verbose
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_series
from pvgisprototype.constants import (
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    FINGERPRINT_FLAG_DEFAULT,
    GROUPBY_DEFAULT,
    IN_MEMORY_FLAG_DEFAULT,
    MASK_AND_SCALE_FLAG_DEFAULT,
    NEIGHBOR_LOOKUP_DEFAULT,
    QUIET_FLAG_DEFAULT,
    ROUNDING_PLACES_DEFAULT,
    UNIPLOT_FLAG_DEFAULT,
    STATISTICS_FLAG_DEFAULT,
    SYMBOL_CHART_CURVE,
    SYMBOL_GROUP,
    SYMBOL_PLOT,
    SYMBOL_SELECT,
    TERMINAL_WIDTH_FRACTION,
    TOLERANCE_DEFAULT,
    UNIT_NAME,
    VERBOSE_LEVEL_DEFAULT,
    WAVELENGTHS_CSV_COLUMN_NAME_DEFAULT,
)
from pvgisprototype.log import logger
from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_introduction,
    rich_help_panel_plotting,
    rich_help_panel_spectrum,
)


app = typer.Typer(
    cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"{SYMBOL_CHART_CURVE} Work with time series",
)


def warn_for_negative_longitude(
    longitude: Longitude = None,
):
    """Warn for negative longitude value

    Maybe the input dataset ranges in [0, 360] degrees ?
    """
    if longitude < 0:
        warning = f"{exclamation_mark} "
        warning += "The longitude "
        warning += f"{longitude} " + "is negative. "
        warning += "If the input dataset's longitude values range in [0, 360], consider using `--convert-longitude-360`!"
        logger.warning(warning)
        # print(warning)


@app.command(
        name="introduction",
    # no_args_is_help=False,
    help="  Introduction on the [cyan]series[/cyan] command",
    rich_help_panel=rich_help_panel_introduction,
)
def series_introduction():
    """A short introduction on the series command"""
    introduction = """
    The [code]series[/code] command is a convenience wrapper around Xarray's
    data processing capabilities.

    Explain [bold cyan]timestamps[/bold cyan].

    And more ...

    """

    note = """
    Timestamps are retrieved from the input data series. If the series are not
    timestamped, then stamps are generated based on the user requested
    combination of a three out of the four relevant parameters : `start-time`,
    `end-time`, `frequency` and `period`.

    """
    from rich.panel import Panel

    note_in_a_panel = Panel(
        "[italic]{}[/italic]".format(note),
        title="[bold cyan]Note[/bold cyan]",
        width=78,
    )
    from rich.console import Console

    console = Console()
    # introduction.wrap(console, 30)
    console.print(introduction)
    console.print(note_in_a_panel)


app.command(
    name="info",
    help="Read an Xarray-supported data file format",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series,
)(open_xarray_supported_time_series_data)
# app.command(
#     name="inspect",
#     help="Inspect Xarray-supported data",
#     no_args_is_help=True,
#     rich_help_panel=rich_help_panel_series,
# )(inspect_netcdf_data)


@app.command(
    "select",
    no_args_is_help=True,
    help="  Select time series over a location",
    rich_help_panel=rich_help_panel_series,
)
def select(
    time_series: Annotated[Path, typer_argument_time_series],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    time_series_2: Annotated[Path, typer_option_time_series] = None,
    timestamps: Annotated[DatetimeIndex | None, typer_argument_naive_timestamps] = str(Timestamp.now()),
    start_time: Annotated[
        datetime | None, typer_option_start_time
    ] = None,  # Used by a callback function
    periods: Annotated[
        int | None, typer_option_periods
    ] = None,  # Used by a callback function
    frequency: Annotated[
        str | None, typer_option_frequency
    ] = None,  # Used by a callback function
    end_time: Annotated[
        datetime | None, typer_option_end_time
    ] = None,  # Used by a callback function
    convert_longitude_360: Annotated[bool, typer_option_convert_longitude_360] = False,
    variable: Annotated[str | None, typer_option_data_variable] = None,
    variable_2: Annotated[str | None, typer_option_data_variable] = None,
    coordinate: Annotated[
        str,
        typer_option_wavelength_column_name,  # Update Me
    ] = None,
    filter_coordinate: Annotated[
        bool,
        typer.Option(
            help="Limit the range of input data by filtering the requested Xarray `coordinate`. See options `minimum`, `maximum`.",
            rich_help_panel=rich_help_panel_spectrum,
        ),
    ] = False,
    minimum: Annotated[
        float | None, typer_option_minimum_spectral_irradiance_wavelength  # Update Me
    ] = None,
    maximum: Annotated[
        float | None, typer_option_maximum_spectral_irradiance_wavelength  # Update Me
    ] = None,
    neighbor_lookup: Annotated[
        MethodForInexactMatches | None, typer_option_nearest_neighbor_lookup
    ] = None, # NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: Annotated[float | None, typer_option_tolerance] = TOLERANCE_DEFAULT,
    mask_and_scale: Annotated[
        bool, typer_option_mask_and_scale
    ] = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: Annotated[bool, typer_option_in_memory] = IN_MEMORY_FLAG_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[str | None, typer_option_groupby] = GROUPBY_DEFAULT,
    output_filename: Annotated[
        Path, typer_option_output_filename
    ] = None,
    variable_name_as_suffix: Annotated[
        bool, typer_option_variable_name_as_suffix
    ] = True,
    rounding_places: Annotated[
        int | None, typer_option_rounding_places
    ] = ROUNDING_PLACES_DEFAULT,
    uniplot: Annotated[bool, typer_option_uniplot] = UNIPLOT_FLAG_DEFAULT,
    resample_large_series: Annotated[bool, "Resample large time series?"] = False,
    lines: Annotated[bool, typer_option_uniplot_lines] = True,
    title: Annotated[str | None, typer_option_uniplot_title] = 'Selected data',
    unit: Annotated[str, typer_option_uniplot_unit] = UNIT_NAME,  # " °C")
    terminal_width_fraction: Annotated[
        float, typer_option_uniplot_terminal_width
    ] = TERMINAL_WIDTH_FRACTION,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    quiet: Annotated[bool, typer_option_quiet] = QUIET_FLAG_DEFAULT,
    log: Annotated[int, typer_option_log] = VERBOSE_LEVEL_DEFAULT,
    data_source: Annotated[str, typer.Option(help="Data source text to print in the footer of the plot.")] = '',
    fingerprint: Annotated[bool, typer_option_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    # quick_response_code: Annotated[
    #     QuickResponseCode, typer_option_quick_response
    # ] = QuickResponseCode.NoneValue,
):
    """Select location series"""
    if convert_longitude_360:
        longitude = longitude % 360
    warn_for_negative_longitude(longitude)

    if not variable:
        dataset = open_dataset(time_series)
        # ----------------------------------------------------- Review Me ----    
        #
        if len(dataset.data_vars) >= 2:
            variables = list(dataset.data_vars.keys())
            print(f"The dataset contains more than one variable : {variables}")
            variable = typer.prompt(
                "Please specify the variable you are interested in from the above list"
            )
        else:
            variable = list(dataset.data_vars)
        #
        # ----------------------------------------------------- Review Me ----    
    location_time_series = select_time_series(
        time_series=time_series,
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        start_time=start_time,
        end_time=end_time,
        # convert_longitude_360=convert_longitude_360,
        variable=variable,
        coordinate=coordinate,
        minimum=minimum,
        maximum=maximum,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        mask_and_scale=mask_and_scale,
        in_memory=in_memory,
        # variable_name_as_suffix=variable_name_as_suffix,
        verbose=verbose,
        log=log,
    )
    if resample_large_series:
        location_time_series = location_time_series.resample(time="1M").mean()
    location_time_series_2 = select_time_series(
        time_series=time_series_2,
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        start_time=start_time,
        end_time=end_time,
        # convert_longitude_360=convert_longitude_360,
        variable=variable_2,
        coordinate=coordinate,
        minimum=minimum,
        maximum=maximum,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        mask_and_scale=mask_and_scale,
        in_memory=in_memory,
        # variable_name_as_suffix=variable_name_as_suffix,
        verbose=verbose,
        log=log,
    )
    if resample_large_series:
        location_time_series_2 = location_time_series_2.resample(time="1M").mean()

    results = {
        location_time_series.name: location_time_series.to_numpy(),
    }
    if location_time_series_2 is not None:
        more_results = {
            location_time_series_2.name: (
                location_time_series_2.to_numpy()
                if location_time_series_2 is not None
                else None
            )
        }
        results = results | more_results
        print(f"Results : {results}")

    # if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
    #     debug(locals())

    if not quiet:
        if verbose > 0:
            # special case!
            if location_time_series is not None and timestamps is None:
                timestamps = location_time_series.time.to_numpy()

            if isinstance(location_time_series, DataArray):
                print_irradiance_xarray(
                    location_time_series=location_time_series,
                    longitude=longitude,
                    latitude=latitude,
                    # elevation=elevation,
                    title=title,
                    rounding_places=rounding_places,
                    verbose=verbose,
                    # index=index,
                )
                if isinstance(location_time_series_2, DataArray):
                    print_irradiance_xarray(
                        location_time_series=location_time_series_2,
                        longitude=longitude,
                        latitude=latitude,
                        # elevation=elevation,
                        title=title,
                        rounding_places=rounding_places,
                        verbose=verbose,
                        # index=index,
                    )
            else:
                print_irradiance_table_2(
                    longitude=longitude,
                    latitude=latitude,
                    timestamps=timestamps,
                    dictionary=results,
                    title=title,
                    rounding_places=rounding_places,
                    verbose=verbose,
                )
                # if location_time_series_2 is not None:
                #     print_irradiance_table_2(
                #         longitude=longitude,
                #         latitude=latitude,
                #         timestamps=timestamps,
                #         dictionary=results,
                #         title=title,
                #         rounding_places=rounding_places,
                #         verbose=verbose,
                #     )
        else:
            flat_list = location_time_series.to_numpy().flatten().astype(str)
            csv_str = ",".join(flat_list)
            print(csv_str)

    # statistics after echoing series which might be Long!

    if statistics:
        print_series_statistics(
            data_array=location_time_series,
            timestamps=timestamps,
            groupby=groupby,
            title="Selected series",
            rounding_places=rounding_places,
        )
    output_handlers = {
        ".nc": lambda location_time_series, path: location_time_series.to_netcdf(path),
        ".csv": lambda location_time_series, path: to_csv(
            x=location_time_series, path=path
        ),
    }
    if fingerprint:
        from pvgisprototype.cli.print.fingerprint import print_finger_hash

        print_finger_hash(dictionary=results)
    if uniplot:
        import os

        terminal_columns, _ = os.get_terminal_size()  # we don't need lines!
        terminal_length = int(terminal_columns * terminal_width_fraction)
        from functools import partial

        from uniplot import plot as default_plot

        plot = partial(default_plot, width=terminal_length)
        if isinstance(location_time_series, DataArray) and location_time_series.size == 1:
            print(
                f"{exclamation_mark} I [red]cannot[/red] plot a single scalar value {location_time_series.item()}!"
            )
            raise typer.Abort()

        if not isinstance(location_time_series, DataArray):
            print("Selected variable did not return a DataArray. Check your selection.")
            return

        if isinstance(location_time_series, DataArray):
            supertitle = getattr(location_time_series, "long_name", "Untitled")
            title += f'  at ({longitude}, {latitude})'
            label = getattr(location_time_series, "name", None)
            label_2 = (
                getattr(location_time_series_2, "name", None)
                if isinstance(location_time_series_2, DataArray)
                else None
            )
            data_source_text = ''
            if data_source:
                data_source_text = f" · {data_source}"

            if fingerprint:
                from pvgisprototype.core.hashing import generate_hash
                data_source_text += f" · Fingerprint : {generate_hash(location_time_series)}"

            if label_2:
                label_2 += data_source_text

            else:
                label += data_source_text

            unit = getattr(location_time_series, "units", None)
            if coordinate in location_time_series.coords:
                y_series = (
                    [location_time_series, location_time_series_2]
                    if location_time_series_2 is not None
                    else location_time_series
                )

                if location_time_series.time.size == 1:
                    x_series = location_time_series[coordinate].values
                    title += f'  on {str(timestamps[0])}'
                    x_unit = ' ' + getattr(location_time_series[coordinate], 'units', '')

                else:
                    x_unit = ''
                    if location_time_series[coordinate].size == 1:
                        # Case 2: One level of coordinate, time on x-axis
                        # x_series = location_time_series.time.values
                        # x_series = [[str(timestamp)] for timestamp in location_time_series['time'].values]
                        x_series = location_time_series.time.values
                        y_series = y_series.values.flatten()
                        title += f'  at {location_time_series[coordinate].item()}'
                    else:
                        # Case 3: Multiple levels of the coordinate and multiple timestamps
                        # # x_series = [location_time_series[coordinate].values] * len(y_series)
                        # x_series = [location_time_series[coordinate].values]
                        for level in location_time_series[coordinate].values:
                            level_data = location_time_series.sel({coordinate: level})
                            x_series = level_data.time.values
                            y_series = level_data.values.flatten()  # Flatten to 1D
                            plot_title = f'{title}  at {level} {getattr(location_time_series[coordinate], "units", "")}'
                            plot_x_unit = 'time'
                            plot(
                                xs=x_series,
                                ys=y_series,
                                legend_labels=[label],
                                lines=lines,
                                title=plot_title,
                                x_unit=plot_x_unit,
                                y_unit=' ' + str(unit),
                            )
                        return
                plot(
                    # x=location_time_series,
                    xs=x_series,
                    ys=y_series,
                    legend_labels=[label, label_2],
                    lines=lines,
                    title=title if title else supertitle,
                    x_unit=x_unit,
                    y_unit=' ' + str(unit),
                    # force_ascii=True,
                )
            else:
                # plot over time
                plot(
                    # x=location_time_series,
                    # xs=location_time_series,
                    ys=[location_time_series, location_time_series_2] if location_time_series_2 is not None else location_time_series,
                    legend_labels=[label, label_2],
                    lines=lines,
                    title=title if title else supertitle,
                    y_unit=" " + str(unit),
                    # force_ascii=True,
                )
    if output_filename:
        extension = output_filename.suffix.lower()
        if extension in output_handlers:
            output_handlers[extension](location_time_series, output_filename)
        else:
            raise ValueError(f"Unsupported file extension: {extension}")


@app.command(
    "select-sarah",
    no_args_is_help=True,
    help="  Select SARAH time series over a location",
)
def select_sarah(
    time_series: Annotated[Path, typer_argument_time_series],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    time_series_2: Annotated[Path, typer_option_time_series] = None,
    timestamps: Annotated[DatetimeIndex, typer_argument_naive_timestamps] = str(
        now_datetime()
    ),
    start_time: Annotated[
        datetime | None, typer_option_start_time
    ] = None,  # Used by a callback function
    periods: Annotated[
        int | None, typer_option_periods
    ] = None,  # Used by a callback function
    frequency: Annotated[
        str | None, typer_option_frequency
    ] = None,  # Used by a callback function
    end_time: Annotated[
        datetime | None, typer_option_end_time
    ] = None,  # Used by a callback function
    convert_longitude_360: Annotated[bool, typer_option_convert_longitude_360] = False,
    variable: Annotated[str | None, typer_option_data_variable] = None,
    variable_2: Annotated[str | None, typer_option_data_variable] = None,
    wavelength_column: Annotated[
        str,
        typer_option_wavelength_column_name,
    ] = WAVELENGTHS_CSV_COLUMN_NAME_DEFAULT,
    limit_spectral_range: Annotated[
            bool,
            typer.Option(help="Limit the spectral range of the irradiance input data. Default for `spectral_mismatch_model = Pelland`")
            ] = True,
    min_wavelength: Annotated[
        float, typer_option_minimum_spectral_irradiance_wavelength
    ] = MIN_WAVELENGTH,
    max_wavelength: Annotated[
        float, typer_option_maximum_spectral_irradiance_wavelength
    ] = MAX_WAVELENGTH,
    neighbor_lookup: Annotated[
        MethodForInexactMatches, typer_option_nearest_neighbor_lookup
    ] = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: Annotated[float | None, typer_option_tolerance] = TOLERANCE_DEFAULT,
    mask_and_scale: Annotated[
        bool, typer_option_mask_and_scale
    ] = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: Annotated[bool, typer_option_in_memory] = IN_MEMORY_FLAG_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[str | None, typer_option_groupby] = GROUPBY_DEFAULT,
    output_filename: Annotated[Path, typer_option_output_filename] = None,
    variable_name_as_suffix: Annotated[
        bool, typer_option_variable_name_as_suffix
    ] = True,
    rounding_places: Annotated[
        int | None, typer_option_rounding_places
    ] = ROUNDING_PLACES_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    log: Annotated[int, typer_option_log] = VERBOSE_LEVEL_DEFAULT,
):
    """Select location series"""
    if convert_longitude_360:
        longitude = longitude % 360
    warn_for_negative_longitude(longitude)

    if not variable:
        dataset = open_dataset(time_series)
        # ----------------------------------------------------- Review Me ----    
        #
        if len(dataset.data_vars) >= 2:
            variables = list(dataset.data_vars.keys())
            print(f"The dataset contains more than one variable : {variables}")
            variable = typer.prompt(
                "Please specify the variable you are interested in from the above list"
            )
        else:
            variable = list(dataset.data_vars)
        #
        # ----------------------------------------------------- Review Me ----    
    location_time_series = select_time_series(
        time_series=time_series,
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        start_time=start_time,
        end_time=end_time,
        # convert_longitude_360=convert_longitude_360,
        variable=variable,
        coordinate=wavelength_column,
        minimum=min_wavelength,
        maximum=max_wavelength,
        drop=limit_spectral_range,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        mask_and_scale=mask_and_scale,
        in_memory=in_memory,
        # variable_name_as_suffix=variable_name_as_suffix,
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
        variable=variable_2,
        coordinate=wavelength_column,
        minimum=min_wavelength,
        maximum=max_wavelength,
        drop=limit_spectral_range,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        mask_and_scale=mask_and_scale,
        in_memory=in_memory,
        # variable_name_as_suffix=variable_name_as_suffix,
        verbose=verbose,
        log=log,
    )
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    results = {
        location_time_series.name: location_time_series.to_numpy(),
    }
    if location_time_series_2 is not None:
        more_results = {
            location_time_series_2.name: (
                location_time_series_2.to_numpy()
                if location_time_series_2 is not None
                else None
            )
        }
        results = results | more_results

    title = "Location time series"

    if verbose:
        # special case!
        if location_time_series is not None and timestamps is None:
            timestamps = location_time_series.time.to_numpy()

        # if isinstance(location_time_series, DataArray):
        #     print_irradiance_xarray(
        #         location_time_series=location_time_series,
        #         longitude=longitude,
        #         latitude=latitude,
        #         # elevation=elevation,
        #         title=title,
        #         rounding_places=rounding_places,
        #         verbose=verbose,
        #         # index=index,
        #     )
        # else:
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
            timestamps=timestamps,
            groupby=groupby,
            title="Selected series",
            rounding_places=rounding_places,
        )

    # if csv:
        # export_statistics_to_csv(
        #     data_array=location_time_series,
        #     filename=csv,
        # )

    output_handlers = {
        ".nc": lambda location_time_series, path: location_time_series.to_netcdf(path),
        ".csv": lambda location_time_series, path: to_csv(
            x=location_time_series, path=path
        ),
    }
    if output_filename:
        extension = output_filename.suffix.lower()
        if extension in output_handlers:
            output_handlers[extension](location_time_series, output_filename)
        else:
            raise ValueError(f"Unsupported file extension: {extension}")


@app.command(
    "select-fast",
    no_args_is_help=True,
    help=f"{SYMBOL_SELECT} Retrieve series over a location.-",
    rich_help_panel=rich_help_panel_series,
)
def select_fast(
    time_series: Annotated[Path, typer_argument_time_series],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    time_series_2: Annotated[Path, typer_option_time_series] = None,
    tolerance: Annotated[
        float | None, typer_option_tolerance
    ] = 0.1,  # Customize default if needed
    # in_memory: Annotated[bool, typer_option_in_memory] = False,
    output_filename: Annotated[Path, typer_option_output_filename] = None,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """Bare read & write"""
    try:
        series = open_dataarray(time_series).sel(
            lon=longitude, lat=latitude, method="nearest"
        )
        if time_series_2:
            series_2 = open_dataarray(time_series_2).sel(
                lon=longitude, lat=latitude, method="nearest"
            )
        # Is .nc needed in the context of this command ? ---------------------
        output_handlers = {
            # ".nc": lambda location_time_series, path: location_time_series.to_netcdf(path),
            ".csv": lambda location_time_series, path: to_csv(
                x=location_time_series, path=path
            ),
        }
        if output_filename:
            extension = output_filename.suffix.lower()
            if extension in output_handlers:
                output_handlers[extension](location_time_series, output_filename)
            else:
                raise ValueError(f"Unsupported file extension: {extension}")
        print("Done.-")
    except Exception as e:
        print(f"An error occurred: {e}")


@app.command(
    no_args_is_help=True,
    help=f"{SYMBOL_GROUP} Group-by of time series over a location {NOT_IMPLEMENTED_CLI}",
    rich_help_panel=rich_help_panel_series,
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
    help=f"{SYMBOL_PLOT} Plot time series",
    rich_help_panel=rich_help_panel_plotting,
)
def plot(
    time_series: Annotated[Path, typer_argument_time_series],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    timestamps: Annotated[DatetimeIndex, typer_argument_naive_timestamps] = str(
        now_datetime()
    ),
    start_time: Annotated[
        datetime | None, typer_option_start_time
    ] = None,  # Used by a callback function
    periods: Annotated[
        int | None, typer_option_periods
    ] = None,  # Used by a callback function
    frequency: Annotated[
        str | None, typer_option_frequency
    ] = None,  # Used by a callback function
    end_time: Annotated[
        datetime | None, typer_option_end_time
    ] = None,  # Used by a callback function
    convert_longitude_360: Annotated[bool, typer_option_convert_longitude_360] = False,
    variable: Annotated[str | None, typer_option_data_variable] = None,
    default_dimension: Annotated[str, 'Default dimension'] = 'time',
    ask_for_dimension: Annotated[bool, "Ask to plot a specific dimension"] = True,
    # slice_options: Annotated[bool, "Slice data dimensions"] = False,
    neighbor_lookup: Annotated[
        MethodForInexactMatches, typer_option_nearest_neighbor_lookup
    ] = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: Annotated[float | None, typer_option_tolerance] = TOLERANCE_DEFAULT,
    mask_and_scale: Annotated[
        bool, typer_option_mask_and_scale
    ] = MASK_AND_SCALE_FLAG_DEFAULT,
    resample_large_series: Annotated[bool, "Resample large time series?"] = False,
    output_filename: Annotated[Path, typer_option_output_filename] = None,
    variable_name_as_suffix: Annotated[
        bool, typer_option_variable_name_as_suffix
    ] = True,
    width: Annotated[int, "Width for the plot"] = 16,
    height: Annotated[int, "Height for the plot"] = 3,
    tufte_style: Annotated[bool, typer_option_tufte_style] = False,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    data_source: Annotated[str, typer.Option(help="Data source text to print in the footer of the plot.")] = '',
    fingerprint: Annotated[bool, typer_option_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    log: Annotated[int, typer_option_log] = VERBOSE_LEVEL_DEFAULT,
):
    """Plot selected time series"""
    data_array = select_time_series(
        time_series=time_series,
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        start_time=start_time,
        end_time=end_time,
        variable=variable,
        # convert_longitude_360=convert_longitude_360,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        mask_and_scale=mask_and_scale,
        # in_memory=in_memory,
        verbose=verbose,
        log=log,
    )
    try:
        plot_series(
            data_array=data_array,
            time=timestamps,
            default_dimension=default_dimension,
            ask_for_dimension=ask_for_dimension,
            # slice_options=slice_options,
            figure_name=output_filename,
            # add_offset=add_offset,
            variable_name_as_suffix=variable_name_as_suffix,
            tufte_style=tufte_style,
            width=width,
            height=height,
            resample_large_series=resample_large_series,
            data_source=data_source,
            fingerprint=fingerprint,
        )
    except Exception as exception:
        print(f"{ERROR_IN_PLOTTING_DATA} : {exception}")
        raise SystemExit(33)


@app.command(
    no_args_is_help=True,
    help="  Plot time series in the terminal",
    rich_help_panel=rich_help_panel_plotting,
)
def uniplot(
    time_series: Annotated[Path, typer_argument_time_series],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    time_series_2: Annotated[Path | None, typer_option_time_series] = None,
    timestamps: Annotated[DatetimeIndex | None, typer_argument_timestamps] = None,
    start_time: Annotated[datetime | None, typer_option_start_time] = None,
    end_time: Annotated[datetime | None, typer_option_end_time] = None,
    variable: Annotated[str | None, typer_option_data_variable] = None,
    coordinate: str | None = None,
    # convert_longitude_360: Annotated[bool, typer_option_convert_longitude_360] = False,
    neighbor_lookup: Annotated[
        MethodForInexactMatches | None, typer_option_nearest_neighbor_lookup
    ] = None,
    tolerance: Annotated[
        float | None, typer_option_tolerance
    ] = 0.1,  # Customize default if needed
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = False,
    resample_large_series: Annotated[bool, "Resample large time series?"] = False,
    lines: Annotated[bool, typer_option_uniplot_lines] = True,
    title: Annotated[str | None, typer_option_uniplot_title] = None,
    unit: Annotated[str, typer_option_uniplot_unit] = UNIT_NAME,  # " °C")
    terminal_width_fraction: Annotated[
        float, typer_option_uniplot_terminal_width
    ] = TERMINAL_WIDTH_FRACTION,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    data_source: Annotated[str, typer.Option(help="Data source text to print in the footer of the plot.")] = '',
    fingerprint: Annotated[bool, typer_option_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
):
    """Plot time series in the terminal"""
    import os

    terminal_columns, _ = os.get_terminal_size()  # we don't need lines!
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
        variable=variable,
        # convert_longitude_360=convert_longitude_360,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        mask_and_scale=mask_and_scale,
        # in_memory=in_memory,
        verbose=verbose,
    )
    if resample_large_series:
        data_array = data_array.resample(time="1M").mean()
    data_array_2 = select_time_series(
        time_series=time_series_2,
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        start_time=start_time,
        end_time=end_time,
        variable=variable,
        # convert_longitude_360=convert_longitude_360,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        mask_and_scale=mask_and_scale,
        # in_memory=in_memory,
        verbose=verbose,
    )
    if resample_large_series:
        data_array_2 = data_array_2.resample(time="1M").mean()

    if isinstance(data_array, float):
        print(
            f"⚠️{exclamation_mark} [red]Aborting[/red] as I [red]cannot[/red] plot the single float value {float}!"
        )
        typer.Abort()

    if not isinstance(data_array, DataArray):
        print("Selected variable did not return a DataArray. Check your selection.")
        return

    if isinstance(data_array, DataArray):
        supertitle = getattr(data_array, "long_name", "Untitled")
        label = getattr(data_array, "name", None)
        label_2 = (
            getattr(data_array_2, "name", None)
            if isinstance(data_array_2, DataArray)
            else None
        )
        data_source_text = ''
        if data_source:
            data_source_text = f" · {data_source}"

        if fingerprint:
            from pvgisprototype.core.hashing import generate_hash
            data_source_text += f" · Fingerprint : {generate_hash(data_array)}"

        if label_2:
            label_2 += data_source_text

        else:
            label += data_source_text

        unit = getattr(data_array, "units", None)
        if coordinate in data_array.coords:
            plot(
                # x=data_array,
                xs=data_array[coordinate],
                ys=[data_array, data_array_2] if data_array_2 is not None else data_array,
                legend_labels=[label, label_2],
                lines=lines,
                title=title if title else supertitle,
                x_unit=' ' + getattr(data_array[coordinate], 'units', ''),
                y_unit=' ' + str(unit),
                # force_ascii=True,
            )
        else:
            # plot over time
            plot(
                # x=data_array,
                # xs=data_array,
                ys=[data_array, data_array_2] if data_array_2 is not None else data_array,
                legend_labels=[label, label_2],
                lines=lines,
                title=title if title else supertitle,
                y_unit=" " + str(unit),
                # force_ascii=True,
            )

if __name__ == "__main__":
    app()
