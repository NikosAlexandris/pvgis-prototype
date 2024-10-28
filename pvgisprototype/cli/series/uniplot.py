from typing_extensions import Annotated
import typer
from pvgisprototype.api.series.models import MethodForInexactMatches
from pandas import DatetimeIndex, Timestamp
from typing_extensions import Annotated
from pvgisprototype.cli.typer.location import (
    typer_argument_latitude_in_degrees,
    typer_argument_longitude_in_degrees,
)
from pvgisprototype.cli.typer.output import (
    typer_option_fingerprint,
)
from pvgisprototype.cli.typer.plot import (
    typer_option_uniplot_lines,
    typer_option_uniplot_terminal_width,
    typer_option_uniplot_title,
    typer_option_uniplot_unit,
)
from pvgisprototype.cli.typer.time_series import (
    typer_argument_time_series,
    typer_option_data_variable,
    typer_option_mask_and_scale,
    typer_option_nearest_neighbor_lookup,
    typer_option_time_series,
    typer_option_tolerance,
)
from pvgisprototype.cli.typer.timestamps import (
    typer_argument_timestamps,
    typer_option_end_time,
    typer_option_start_time,
)
from pvgisprototype.cli.typer.verbosity import typer_option_verbose
from pvgisprototype.constants import (
    FINGERPRINT_FLAG_DEFAULT,
    TERMINAL_WIDTH_FRACTION,
    UNIT_NAME,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.api.series.select import select_time_series
from pathlib import Path


def uniplot(
    time_series: Annotated[Path, typer_argument_time_series],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    time_series_2: Annotated[Path | None, typer_option_time_series] = None,
    timestamps: Annotated[DatetimeIndex | None, typer_argument_timestamps] = None,
    start_time: Annotated[Timestamp | None, typer_option_start_time] = None,
    end_time: Annotated[Timestamp | None, typer_option_end_time] = None,
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


