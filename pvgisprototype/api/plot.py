from devtools import debug
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL, INCIDENCE_ALGORITHM_NAME, INCIDENCE_NAME
from typing import List
from pandas import DatetimeIndex
from pvgisprototype.constants import AZIMUTH_ORIGIN_NAME, INCIDENCE_DEFINITION, NOT_AVAILABLE, UNITS_NAME, UNITLESS
from pvgisprototype.constants import TERMINAL_WIDTH_FRACTION
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.api.series.hardcodings import exclamation_mark
from rich import print
import numpy
import xarray
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.api.position.models import SOLAR_POSITION_PARAMETER_COLUMN_NAMES, SolarPositionParameter
from typing import Sequence


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
        """
        """
        # Ensure array and timestamps are of the same size
        if array.size != timestamps.size:
            # Handle empty array case
            if array.size == 0:
                print("Empty array provided.")
                return xarray.DataArray([])
            else:
                raise ValueError("The size the data array and timestamps must match.")

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

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

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
    position_parameters: [SolarPositionParameter] = SolarPositionParameter.all,
    timestamps: DatetimeIndex = None,
    # index: bool = False,
    surface_orientation=None,
    surface_tilt=None,
    # longitude: float,
    # latitude: float,
    # time_series_2: Path = None,
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
    individual_series = None
    individual_series_labels = None

    for model_name, model_result in solar_position_series.items():

        # First, chech if we received incidence series !
        solar_incidence_series = model_result.get(SolarPositionParameter.incidence, numpy.array([])) if not isinstance(model_result.get(SolarPositionParameter.incidence), str) else None

        # If this is the case, then adjust the label for the incidence series
        if solar_incidence_series.size > 0:
            label = f'{model_result.get(INCIDENCE_DEFINITION, NOT_AVAILABLE)} ' + 'Incidence ' + f' ({model_result.get(INCIDENCE_ALGORITHM_NAME, NOT_AVAILABLE)})'

        # However, and except for the overview commmand, we expect one angular metric time series
        if len(position_parameters) == 1:
            solar_position_metric_series = model_result.get(position_parameters[0])

        else:
            solar_position_metric_series = solar_incidence_series if solar_incidence_series is not None else model_result.pop(0)
            individual_series = [
                model_result.get(parameter, numpy.array([]))
                for parameter in position_parameters if not isinstance(model_result.get(parameter), str)
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
            timestamps=timestamps,
            resample_large_series=resample_large_series,
            lines=True,
            supertitle=f'{supertitle} {model_name}',
            title=title,
            label=label,
            extra_legend_labels=individual_series_labels,
            unit=model_result.get(UNITS_NAME, UNITLESS),
            terminal_width_fraction=terminal_width_fraction,
            verbose=verbose,
        )
>>>>>>> main
