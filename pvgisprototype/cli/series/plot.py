from pvgisprototype.log import logger
import typer
from pathlib import Path
from pandas import DatetimeIndex, Timestamp
from typing_extensions import Annotated
from pvgisprototype.api.series.models import MethodForInexactMatches
from pvgisprototype.api.series.select import select_time_series
from pvgisprototype.cli.messages import ERROR_IN_PLOTTING_DATA
from pvgisprototype.api.series.plot import plot_series
from pvgisprototype.cli.typer.helpers import typer_option_convert_longitude_360
from pvgisprototype.cli.typer.location import (
    typer_argument_latitude_in_degrees,
    typer_argument_longitude_in_degrees,
)
from pvgisprototype.cli.typer.log import typer_option_log
from pvgisprototype.cli.typer.output import (
    typer_option_fingerprint,
    typer_option_output_filename,
    typer_option_variable_name_as_suffix,
)
from pvgisprototype.cli.typer.plot import (
    typer_option_tufte_style,
)
from pvgisprototype.cli.typer.time_series import (
    typer_argument_time_series,
    typer_option_data_variable,
    typer_option_mask_and_scale,
    typer_option_nearest_neighbor_lookup,
    typer_option_tolerance,
)
from pvgisprototype.cli.typer.timestamps import (
    typer_argument_naive_timestamps,
    typer_option_end_time,
    typer_option_frequency,
    typer_option_periods,
    typer_option_start_time,
)
from pvgisprototype.cli.typer.verbosity import typer_option_verbose
from pvgisprototype.constants import (
    FINGERPRINT_FLAG_DEFAULT,
    MASK_AND_SCALE_FLAG_DEFAULT,
    NEIGHBOR_LOOKUP_DEFAULT,
    TOLERANCE_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)


def plot(
    time_series: Annotated[Path, typer_argument_time_series],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    timestamps: Annotated[DatetimeIndex, typer_argument_naive_timestamps] = str(Timestamp.now()),
    start_time: Annotated[
        Timestamp | None, typer_option_start_time
    ] = None,  # Used by a callback function
    periods: Annotated[
        int | None, typer_option_periods
    ] = None,  # Used by a callback function
    frequency: Annotated[
        str | None, typer_option_frequency
    ] = None,  # Used by a callback function
    end_time: Annotated[
        Timestamp | None, typer_option_end_time
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
            figure_name=output_filename.name,
            save_path=output_filename.parent,
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
        logger.error(
                f"{ERROR_IN_PLOTTING_DATA} : {exception}",
                alt=f"{ERROR_IN_PLOTTING_DATA} : {exception}"
                )
        raise SystemExit(33)
