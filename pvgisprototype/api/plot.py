from typing import List
from zoneinfo import ZoneInfo

import numpy
from numpy import full, arange, where, nan_to_num, finfo, float32
import xarray
from devtools import debug
from pandas import DatetimeIndex
from rich import print

from pvgisprototype.api.position.models import (
    SOLAR_POSITION_PARAMETER_COLUMN_NAMES,
    SolarPositionParameter,
)
from pvgisprototype.api.series.hardcodings import exclamation_mark
from pvgisprototype.constants import (
    AZIMUTH_ORIGIN_NAME,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    INCIDENCE_ALGORITHM_NAME,
    INCIDENCE_DEFINITION,
    NOT_AVAILABLE,
    SPECTRAL_FACTOR_COLUMN_NAME,
    TERMINAL_WIDTH_FRACTION,
    UNIT_NAME,
    UNITLESS,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_function_call, logger


def convert_and_resample(array, timestamps, resample_large_series, freq="1ME"):
    """ """
    # Ensure array and timestamps are of the same size
    if array.size != timestamps.size:
        # Handle empty array case
        if array.size == 0:
            print("Empty array provided.")
            return xarray.DataArray([])
        else:
            raise ValueError(f"The size of the data array {array.size} and timestamps {timestamps.size} must match.")

    # Create xarray DataArray with time dimension
    data_array = xarray.DataArray(array, coords=[timestamps], dims=["time"])
    if resample_large_series:
        return data_array.resample(time=freq).mean()
    return data_array


def safe_get_value(dictionary, key, index, default=NOT_AVAILABLE):
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


@log_function_call
def uniplot_data_array_series(
    data_array,
    list_extra_data_arrays = None,
    longitude: float | None = None,
    latitude: float | None = None,
    orientation: List[float] | float | None = None,
    tilt: List[float] | float | None = None,
    # time_series_2: Path = None,
    timestamps: DatetimeIndex = DatetimeIndex([]),
    resample_large_series: bool = False,
    lines: bool = True,
    supertitle: str | None = None,
    title: str | None = None,
    label: str | None = None,
    extra_legend_labels: List[str] | None = None,
    unit: str = UNIT_NAME,
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

    # Convert data_array to an Xarray DataArray, possible resample
    data_array = convert_and_resample(data_array, timestamps, resample_large_series)
    if list_extra_data_arrays:
        list_extra_data_arrays = [
            convert_and_resample(extra_array, timestamps, resample_large_series)
            for extra_array in list_extra_data_arrays
        ]

    y_series = [data_array] + (list_extra_data_arrays if list_extra_data_arrays else [])

    timestamps_series = [DatetimeIndex(data_array.time)] * len(y_series)  # list same DatetimeIndex for each series

    if isinstance(data_array, float):
        logger.error(
            f"{exclamation_mark} Aborting as I cannot plot the single float value {data_array}!",
            alt=f"{exclamation_mark} [red]Aborting[/red] as I [red]cannot[/red] plot the single float value {data_array}!",
        )
        return

    if longitude and latitude:
        title = (title or '') + f' observed from (longitude, latitude) {longitude}, {latitude}'
    
    # supertitle = getattr(photovoltaic_power_output_series, 'long_name', 'Untitled')
    # label = getattr(photovoltaic_power_output_series, 'name', None)
    # label_2 = getattr(photovoltaic_power_output_series_2, 'name', None) if photovoltaic_power_output_series_2 is not None else None
    # unit = getattr(photovoltaic_power_output_series, 'units', None)
    supertitle = getattr(data_array, "long_name", "Untitled")
    label = label if label else getattr(data_array, "name", None)
    list_extra_data_arrays = (
        list_extra_data_arrays if list_extra_data_arrays is not None else []
    )
    # legend_labels = [label] + [getattr(extra_array, 'name', None) for extra_array in list_extra_data_arrays]
    legend_labels = [label] + (extra_legend_labels if extra_legend_labels else [])
    unit = getattr(data_array, "units", None) or unit

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    infinite_values = numpy.isinf(y_series)
    if infinite_values.any():
        # y_series = [nan_to_num(array, nan=0.0, posinf=finfo(float32).max, neginf=-finfo(float32).max) for array in y_series]
        # stub_array = full(infinite_values.shape, -1, dtype=int)
        # index_array = arange(len(infinite_values))
        # infinite_values_indices = where(infinite_values, index_array, stub_array)

        error_message = f"Found infinite values in y_series :\n{y_series}"
        error_message += f"\nMaybe it is necessary to debug the upstream functions that generated this output ?"
        error_message_alternative = (
            f"Found infinite values in [code]y_series[/code] :\n{y_series}"
        )
        error_message_alternative += f"\n[bold yellow]Maybe it is necessary to debug the upstream functions that generated this output ?[/bold yellow]"
        logger.error(error_message, alt=error_message_alternative)

    print("[reverse]Uniplot[/reverse]")
    try:
        plot(
            xs=timestamps_series,
            ys=y_series,
            legend_labels=legend_labels,
            lines=lines,
            title=title if title else supertitle,
            y_unit=" " + str(unit),
            # force_ascii=True,
            # color=False,
        )
    except IOError as e:
        raise IOError(f"Could not _uniplot_ {data_array.value=}") from e


def uniplot_solar_position_series(
    solar_position_series,
    position_parameters: [SolarPositionParameter] = SolarPositionParameter.all,
    timestamps: DatetimeIndex | None = None,
    timezone: ZoneInfo | None = None,
    # index: bool = False,
    surface_orientation=None,
    surface_tilt=None,
    longitude: float = None,
    latitude: float = None,
    # time_series_2: Path = None,
    resample_large_series: bool = False,
    lines: bool = True,
    supertitle: str = None,
    title: str = None,
    label: str = None,
    legend_labels: str = None,
    # unit: str = UNIT_NAME,
    caption: bool = True,
    terminal_width_fraction: float = TERMINAL_WIDTH_FRACTION,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
):
    """ """
    individual_series = None
    individual_series_labels = None

    for model_name, model_result in solar_position_series.items():
        # First, chech if we received incidence series !
        solar_incidence_series = (
            model_result.get(SolarPositionParameter.incidence, numpy.array([]))
            if not isinstance(model_result.get(SolarPositionParameter.incidence), str)
            else None
        )

        # If this is the case, then adjust the label for the incidence series
        if solar_incidence_series.size > 0:
            label = (
                f"{model_result.get(INCIDENCE_DEFINITION, NOT_AVAILABLE)} "
                + "Incidence "
                + f" ({model_result.get(INCIDENCE_ALGORITHM_NAME, NOT_AVAILABLE)})"
            )

        # However, and except for the overview commmand, we expect one angular metric time series
        if len(position_parameters) == 1:
            solar_position_metric_series = model_result.get(position_parameters[0])

        else:
            solar_position_metric_series = (
                solar_incidence_series
                if solar_incidence_series is not None
                else model_result.pop(0)
            )
            individual_series = [
                model_result.get(parameter, numpy.array([]))
                for parameter in position_parameters
                if not isinstance(model_result.get(parameter), str)
                and parameter != SolarPositionParameter.incidence
            ]
            individual_series_labels = []
            for parameter in position_parameters:
                if (
                    parameter in SOLAR_POSITION_PARAMETER_COLUMN_NAMES
                    and parameter != SolarPositionParameter.incidence
                ):
                    metric_label = SOLAR_POSITION_PARAMETER_COLUMN_NAMES[parameter]
                    if parameter == SolarPositionParameter.azimuth:
                        metric_label = (
                            [
                                f"{label} {model_result.get(AZIMUTH_ORIGIN_NAME, NOT_AVAILABLE)}"
                                for label in metric_label
                            ]
                            if isinstance(metric_label, list)
                            else f"{metric_label} {model_result.get(AZIMUTH_ORIGIN_NAME, NOT_AVAILABLE)}"
                        )
                    if isinstance(metric_label, list):
                        individual_series_labels.extend(metric_label)
                    else:
                        individual_series_labels.append(metric_label)

        if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
            debug(locals())

        uniplot_data_array_series(
            data_array=solar_position_metric_series,
            list_extra_data_arrays=individual_series,
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            resample_large_series=resample_large_series,
            lines=True,
            supertitle=f"{supertitle} {model_name}",
            title=title,
            label=label,
            extra_legend_labels=individual_series_labels,
            unit=model_result.get(UNIT_NAME, UNITLESS),
            terminal_width_fraction=terminal_width_fraction,
            verbose=verbose,
        )
        # if caption:
        #     # Positioning
        #     from pvgisprototype.cli.print import (
        #         build_position_table,
        #         build_position_panel,
        #         build_time_table,
        #     )
        #     from pvgisprototype.api.utilities.conversions import round_float_values
        #     position_table = build_position_table()
        #     positioning_rounding_places = 3
        #     latitude = round_float_values(
        #         latitude, positioning_rounding_places
        #     )  # rounding_places)
        #     # position_table.add_row(f"{LATITUDE_NAME}", f"[bold]{latitude}[/bold]")
        #     longitude = round_float_values(
        #         longitude, positioning_rounding_places
        #     )  # rounding_places)
        #     surface_orientation = round_float_values(
        #         surface_orientation, positioning_rounding_places
        #     )
        #     surface_tilt = round_float_values(surface_tilt, positioning_rounding_places)
        #     position_table.add_row(
        #         f"{latitude}",
        #         f"{longitude}",
        #         # f"{elevation}",
        #         f"{surface_orientation}",
        #         f"{surface_tilt}",
        #     )
        #     # position_table.add_row("Time :", f"{timestamp[0]}")
        #     # position_table.add_row("Time zone :", f"{timezone}")

        #     # longest_label_length = max(len(key) for key in dictionary.keys())
        #     longest_label_length = max(
        #         len(key)
        #         for key in [SURFACE_ORIENTATION_COLUMN_NAME, SURFACE_TILT_COLUMN_NAME]
        #     )
        #     surface_position_keys = {
        #         SURFACE_ORIENTATION_NAME,
        #         SURFACE_TILT_NAME,
        #         ANGLE_UNIT_NAME,
        #         # INCIDENCE_DEFINITION,
        #         # UNIT_NAME,
        #     }
        #     for key, value in dictionary.items():
        #         if key in surface_position_keys:
        #             padded_key = f"{key} :".ljust(longest_label_length + 3, " ")
        #             if key == INCIDENCE_DEFINITION:
        #                 value = f"[yellow]{value}[/yellow]"
        #             position_table.add_row(padded_key, str(value))

        #     position_panel = build_position_panel(position_table)

        #     time_table = build_time_table()
        #     time_table.add_row(
        #         str(timestamps.strftime("%Y-%m-%d %H:%M").values[0]),
        #         str(timestamps.freqstr),
        #         str(timestamps.strftime("%Y-%m-%d %H:%M").values[-1]),
        #     )
        #     time_panel = Panel(
        #         time_table,
        #         # title="Time",
        #         # subtitle="Time",
        #         # subtitle_align="right",
        #         safe_box=True,
        #         expand=False,
        #         padding=(0, 2),
        #     )
        #     caption_columns = Columns(
        #         [position_panel, time_panel],
        #         # expand=True,
        #         # equal=True,
        #         padding=3,
        #     )

        #     # fingerprint = dictionary.get(FINGERPRINT_COLUMN_NAME, None)
        #     # columns = build_version_and_fingerprint_columns(fingerprint)

        #     from rich.console import Group

        #     group = Group(
        #         caption_columns,
        #     )
        #     # panel_group = Group(
        #     #         Panel(
        #     #             performance_table,
        #     #             title='Analysis of Performance',
        #     #             expand=False,
        #     #             # style="on black",
        #     #             ),
        #     #         columns,
        #     #     # Panel(table),
        #     #     # Panel(position_panel),
        #     # #     Panel("World", style="on red"),
        #     #         fit=False
        #     # )

        #     # Console().print(panel_group)
        #     # Console().print(Panel(performance_table))
        #     Console().print(group)


from typing import Dict

def uniplot_spectral_factor_series(
    spectral_factor_dictionary: Dict,
    spectral_factor_model: List,
    photovoltaic_module_type: List,
    timestamps: DatetimeIndex,
    resample_large_series: bool = False,
    supertitle: str = "Spectral Factor Series",
    title: str = "Spectral Factor",
    terminal_width_fraction: float = 0.9,
    verbose: int = 0,
):
    """Plot spectral factor series for different module types in the terminal using the uniplot library.

    Parameters
    ----------
    - spectral_factor: Dictionary containing spectral factor data.
    - spectral_factor_model: List of spectral factor models.
    - photovoltaic_module_type: List of photovoltaic module types.
    - timestamps: DatetimeIndex of the time series.
    - resample_large_series: Whether to resample large series.
    - supertitle: Supertitle for the plot.
    - title: Title for the plot.
    - terminal_width_fraction: Width of the terminal for plotting.
    - verbose: Verbosity level.
    """
    data_arrays = []
    labels = []

    for spectral_factor_model, result in spectral_factor_dictionary.items():
        title += f" ({spectral_factor_model.value})"
        for module_type in result:
            spectral_factor_for_module = spectral_factor_dictionary[spectral_factor_model][
                module_type
            ]
            spectral_factor_series = spectral_factor_for_module.get(
                SPECTRAL_FACTOR_COLUMN_NAME
            )

            # if needed
            if isinstance(spectral_factor_series, memoryview):
                spectral_factor_data = numpy.array(spectral_factor_series)

            data_array = xarray.DataArray(
                spectral_factor_series, coords=[timestamps], dims=["time"]
            )
            data_arrays.append(data_array)

            label = f"{module_type.value}"
            if len([spectral_factor_model]) > 1:
                label += f" {spectral_factor_model.name}"
            labels.append(label)

        uniplot_data_array_series(
            data_array=data_arrays[0],
            list_extra_data_arrays=data_arrays[1:],
            timestamps=timestamps,
            resample_large_series=resample_large_series,
            lines=True,
            supertitle=supertitle,
            title=title,
            label=labels[0],
            extra_legend_labels=labels[1:],
            unit="",
            terminal_width_fraction=terminal_width_fraction,
            verbose=verbose,
        )
