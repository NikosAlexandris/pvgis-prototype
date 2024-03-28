from pathlib import Path
from typing import Optional
from pandas import DatetimeIndex
from pandas import Timestamp
from pvgisprototype.api.series.models import MethodsForInexactMatches
from pvgisprototype.constants import UNITS_NAME
from pvgisprototype.constants import TERMINAL_WIDTH_FRACTION
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.api.series.hardcodings import exclamation_mark
from pvgisprototype.api.series.hardcodings import check_mark
from pvgisprototype.api.series.hardcodings import x_mark
from rich import print
from numpy import ndarray
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call


@log_function_call
def uniplot_data_array_time_series(
    data_array,
    data_array_2,
    # longitude: float,
    # latitude: float,
    # time_series_2: Path = None,
    # timestamps: DatetimeIndex = None,
    # start_time: Timestamp = None,
    # end_time: Timestamp = None,
    resample_large_series: bool = False,
    lines: bool = True,
    supertitle: str = None,
    title: str = None,
    label: str = None,
    label_2: str = None,
    unit: str = UNITS_NAME,
    terminal_width_fraction: float = TERMINAL_WIDTH_FRACTION,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
):
    """Plot time series in the terminal"""
    import shutil
    terminal_columns, _ = shutil.get_terminal_size()  # we don't need lines!
    terminal_length = int(terminal_columns * terminal_width_fraction)
    from functools import partial
    from uniplot import plot as default_plot
    plot = partial(default_plot, width=terminal_length)

    if resample_large_series:
        data_array = data_array.resample(time='1M').mean()

    if resample_large_series:
        data_array_2 = data_array_2.resample(time='1M').mean()

    if isinstance(data_array, float):
        logger.error(f"{exclamation_mark} Aborting as I cannot plot the single float value {float}!", alt=f"{exclamation_mark} [red]Aborting[/red] as I [red]cannot[/red] plot the single float value {float}!")
        return

    if isinstance(data_array, ndarray):
        # supertitle = getattr(photovoltaic_power_output_series, 'long_name', 'Untitled')
        # label = getattr(photovoltaic_power_output_series, 'name', None)
        # label_2 = getattr(photovoltaic_power_output_series_2, 'name', None) if photovoltaic_power_output_series_2 is not None else None
        # unit = getattr(photovoltaic_power_output_series, 'units', None)
        supertitle = getattr(data_array, 'long_name', 'Untitled')
        label = getattr(data_array, 'name', None)
        label_2 = getattr(data_array_2, 'name', None) if data_array_2 is not None else None
        unit = getattr(data_array, 'units', None)
        print(f'[reverse]Uniplot[/reverse]')
        try:
            plot(
                # xs=timestamps,
                ys=[data_array, data_array_2] if data_array_2 is not None else data_array,
                legend_labels = [label, label_2] if label_2 else label,
                lines=lines,
                title=title if title else supertitle,
                y_unit=' ' + str(unit),
            )
        except IOError as e:
            raise IOError(
                f"Could not _uniplot_ {data_array.value=}"
            ) from e
