from pathlib import Path
from typing import List, Optional
from pandas import DatetimeIndex
from pandas import Timestamp
from pvgisprototype.api.series.models import MethodForInexactMatches
from pvgisprototype.constants import AZIMUTH_ORIGIN_NAME, INCIDENCE_DEFINITION, NOT_AVAILABLE, UNITS_NAME, UNITLESS
from pvgisprototype.constants import TERMINAL_WIDTH_FRACTION
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.api.series.hardcodings import exclamation_mark
from pvgisprototype.api.series.hardcodings import check_mark
from pvgisprototype.api.series.hardcodings import x_mark
from rich import print
import numpy
import xarray
from numpy import ndarray
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call


@log_function_call
def uniplot_data_array_time_series(
    data_array,
    list_extra_data_arrays,
    # longitude: float,
    # latitude: float,
    orientation: List[float] | float = None,
    tilt: List[float] | float = None,
    # time_series_2: Path = None,
    timestamps: DatetimeIndex = None,
    # start_time: Timestamp = None,
    # end_time: Timestamp = None,
    resample_large_series: bool = False,
    lines: bool = True,
    supertitle: str = None,
    title: str = None,
    label: str = None,
    extra_legend_labels: List[str] | None = None,
    unit: str = UNITS_NAME,
    terminal_width_fraction: float = TERMINAL_WIDTH_FRACTION,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
):
    """Plot time series in the terminal"""
    import shutil
    from functools import partial
    from uniplot import plot as default_plot

    terminal_columns, _ = shutil.get_terminal_size()  # we don't need lines!
    terminal_length = int(terminal_columns * terminal_width_fraction)
    plot = partial(default_plot, width=terminal_length)

    def convert_and_resample(array, timestamps, freq='1ME'):
        # Create xarray DataArray with time dimension
        data_array = xarray.DataArray(array, coords=[timestamps], dims=["time"])
        if resample_large_series:
            return data_array.resample(time=freq).mean()
        return data_array

    data_array = convert_and_resample(data_array, timestamps)
    if list_extra_data_arrays:
        list_extra_data_arrays = [convert_and_resample(extra_array, timestamps) for extra_array in list_extra_data_arrays]

    y_series = (
        [data_array] + (list_extra_data_arrays if list_extra_data_arrays else [])
    )

    if isinstance(data_array, float):
        logger.error(f"{exclamation_mark} Aborting as I cannot plot the single float value {float}!", alt=f"{exclamation_mark} [red]Aborting[/red] as I [red]cannot[/red] plot the single float value {float}!")
        return

    # supertitle = getattr(photovoltaic_power_output_series, 'long_name', 'Untitled')
    # label = getattr(photovoltaic_power_output_series, 'name', None)
    # label_2 = getattr(photovoltaic_power_output_series_2, 'name', None) if photovoltaic_power_output_series_2 is not None else None
    # unit = getattr(photovoltaic_power_output_series, 'units', None)
    supertitle = getattr(data_array, 'long_name', 'Untitled')
    label = label if label else getattr(data_array, 'name', None)
    list_extra_data_arrays = list_extra_data_arrays if list_extra_data_arrays is not None else []
    # legend_labels = [label] + [getattr(extra_array, 'name', None) for extra_array in list_extra_data_arrays]
    legend_labels = [label] + (extra_legend_labels if extra_legend_labels else [])
    unit = getattr(data_array, 'units', None) or unit
    print(f'[reverse]Uniplot[/reverse]')
    try:
        plot(
            # xs=timestamps,
            ys=y_series,
            legend_labels=legend_labels,
            lines=lines,
            title=title if title else supertitle,
            y_unit=' ' + str(unit),
        )
    except IOError as e:
        raise IOError(
            f"Could not _uniplot_ {data_array.value=}"
        ) from e


def uniplot_solar_position_series(
    solar_position_series,
    # index: bool = False,
    timing=None,
    declination=None,
    hour_angle=None,
    zenith=None,
    altitude=None,
    azimuth=None,
    surface_orientation=None,
    surface_tilt=None,
    incidence=None,
    # longitude: float,
    # latitude: float,
    # time_series_2: Path = None,
    timestamps: DatetimeIndex = None,
    # start_time: Timestamp = None,
    # end_time: Timestamp = None,
    resample_large_series: bool = False,
    lines: bool = True,
    supertitle: str = None,
    title: str = None,
    label: str = None,
    legend_labels: str = None,
    # unit: str = UNITS_NAME,
    terminal_width_fraction: float = TERMINAL_WIDTH_FRACTION,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    ):
    """
    """
    from pvgisprototype.constants import (
        DECLINATION_NAME,
        HOUR_ANGLE_NAME,
        ZENITH_NAME,
        ALTITUDE_NAME,
        AZIMUTH_NAME,
        INCIDENCE_NAME,
    )
    solar_position_metrics = {
        DECLINATION_NAME: declination,
        HOUR_ANGLE_NAME: hour_angle,
        ZENITH_NAME: zenith,
        ALTITUDE_NAME: altitude,
        AZIMUTH_NAME: azimuth,
        INCIDENCE_NAME: incidence,
    }
    def safe_get_value(dictionary, key, index, default='NA'):
        """
        Parameters
        ----------
        dictionary: dict
            Input dictionary
        key: str
            key to retrieve from the dictionary
        index: int
            index ... ?

        Returns
        -------
        The value corresponding to the given `key` in the `dictionary` or the
        default value if the key does not exist.

        """
        value = dictionary.get(key, default)
        if isinstance(value, (list, numpy.ndarray)) and len(value) > index:
            return value[index]
        return value

    for model_name, model_result in solar_position_series.items():
        solar_incidence_series = model_result.get(INCIDENCE_NAME, numpy.array([]))
        solar_incidence_label = label + f' {model_result.get(INCIDENCE_DEFINITION, NOT_AVAILABLE)}'
        individual_series = [
            model_result.get(solar_position_metric_name, numpy.array([]))
            for solar_position_metric_name, include in solar_position_metrics.items()
            if include and solar_position_metric_name != INCIDENCE_NAME
        ]
        individual_metrics_labels = [
            (solar_position_metric_name + f' {model_result.get(AZIMUTH_ORIGIN_NAME, NOT_AVAILABLE)}')
            if solar_position_metric_name == AZIMUTH_NAME and include
            else solar_position_metric_name
            for solar_position_metric_name, include in solar_position_metrics.items()
            if include and solar_position_metric_name != INCIDENCE_NAME
        ]

        uniplot_data_array_time_series(
            data_array=solar_incidence_series,
            list_extra_data_arrays=individual_series,
            timestamps=timestamps,
            resample_large_series=resample_large_series,
            lines=True,
            supertitle=f'{supertitle} {model_name}',
            title=title,
            label=solar_incidence_label,
            extra_legend_labels=individual_metrics_labels,
            unit=model_result.get(UNITS_NAME, UNITLESS),
            terminal_width_fraction=terminal_width_fraction,
            verbose=verbose,
        )
