#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
from typing import List, Dict
from zoneinfo import ZoneInfo
import numpy
from pydantic_numpy import NpNDArray
import xarray
from devtools import debug
from pandas import DatetimeIndex
from xarray.core.types import ResampleCompatible
from pvgisprototype.api.position.models import (
    SOLAR_POSITION_PARAMETER_COLUMN_NAMES,
    SolarPositionParameter,
    SolarPositionParameterColumnName,
)
from pvgisprototype.api.series.hardcodings import exclamation_mark
from pvgisprototype.cli.print.irradiance.data import flatten_dictionary
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


def convert_and_resample(
    array: NpNDArray,
    timestamps: DatetimeIndex,
    convert_false_to_none: bool = False,
    resample_large_series: bool = False,
    frequency: ResampleCompatible = "1ME",  # Sane default ?
) -> xarray.DataArray:
    """
    Parameters
    ----------
    convert_false_to_none : bool
        Convert False to None for arrays of type bool. This is meaningful in
        the context of Uniplot in order to plot series of Boolean values along
        with numeric ones.  For example, plot series of _surface in-shade_,
        which is a series of True or False _states_, alongside other soloar
        position series, i.e. solar altitude.  Only True entries are then
        visualised which shows when the solar surface in question
        is directly sunlit.
    """
    # Ensure array and timestamps are of the same size
    if array.size != timestamps.size:
        
        # Handle empty array case
        if array.size == 0:
            logger.warning("The provided array is empty!")
            return xarray.DataArray([])
        
        else:
            raise ValueError(f"The size of the data array {array.size} and timestamps {timestamps.size} must match.")

    # In the context of Uniplot : convert False to None
    # This is meaningful to plot series of Boolean values alongside with numeric ones.
    if convert_false_to_none:
        if array.dtype == bool:
            array = numpy.where(array, True, None)

    # Create xarray DataArray with time dimension
    data_array = xarray.DataArray(array, coords=[timestamps], dims=["time"])
    if resample_large_series:
        return data_array.resample(time=frequency).mean()

    return data_array


@log_function_call
def uniplot_data_array_series(
    data_array,
    list_extra_data_arrays = None,
    longitude: float | None = None,
    latitude: float | None = None,
    orientation: List[float] | float | None = None,
    tilt: List[float] | float | None = None,
    # time_series_2: Path = None,
    timestamps: DatetimeIndex | None = DatetimeIndex([]),
    convert_false_to_none: bool = True,
    resample_large_series: bool = False,
    frequency: ResampleCompatible = "1ME",  # Sane default ?
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
    data_array = convert_and_resample(
        array=data_array,
        timestamps=timestamps,
        convert_false_to_none=convert_false_to_none,
        resample_large_series=resample_large_series,
        frequency=frequency,
    )
    if list_extra_data_arrays:
        list_extra_data_arrays = [
            convert_and_resample(
                array=extra_array,
                timestamps=timestamps,
                convert_false_to_none=convert_false_to_none,
                resample_large_series=resample_large_series,
            )
            for extra_array in list_extra_data_arrays
            if extra_array.size > 0  # Process only non-empty arrays
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

    infinite_values = [
        # numpy.isinf(array)
        numpy.isinf(array.values)
        if array.dtype != "object" else False
        for array in y_series
    ]

    # Check for infinite values
    if any(numpy.any(infinites) for infinites in infinite_values):
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
            legend_placement='auto',
            lines=lines,
            title=title if title else supertitle,
            y_unit=" " + str(unit),
            # force_ascii=True,
            # color=False,
        )
    except IOError as e:
        raise IOError(f"Could not _uniplot_ {data_array.value=}") from e


def uniplot_solar_position_series(
    solar_position_series: dict,
    position_parameters: [SolarPositionParameter] = SolarPositionParameter.all,
    timestamps: DatetimeIndex | None = None,
    timezone: ZoneInfo | None = None,
    # index: bool = False,
    surface_orientation=None,
    surface_tilt=None,
    longitude: float = None,
    latitude: float = None,
    # time_series_2: Path = None,
    convert_false_to_none: bool = True,
    resample_large_series: bool = False,
    frequency: ResampleCompatible = None,
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
    """
    """
    individual_series = None
    individual_series_labels = None

    for model_name, model_result in solar_position_series.items():
        # Important ! Flatten the structure !
        model_result = flatten_dictionary(model_result)

        # First, _pop_ solar incidence series, if any and not a string !
        solar_incidence_series = (
            model_result.pop(SolarPositionParameterColumnName.incidence, numpy.array([]))
            if not isinstance(model_result.get(SolarPositionParameterColumnName.incidence), str)
            else None
        )

        # If this is the case : adjust the label for the incidence series
        if solar_incidence_series.size > 0:
            label = (
                f"{model_result.get(INCIDENCE_DEFINITION, NOT_AVAILABLE)} "
                + "Incidence "
                + f" ({model_result.get(INCIDENCE_ALGORITHM_NAME, NOT_AVAILABLE)})"
            )

        # However, and except for the overview commmand, we expect _one_ angular metric time series
        if len(position_parameters) == 1:
            first_position_parameter_column_name = SolarPositionParameterColumnName[position_parameters[0].name]
            solar_position_metric_series = model_result.pop(first_position_parameter_column_name)

        else:  # pop the first item from the `model_result`
            solar_position_metric_series = (
                solar_incidence_series
                if solar_incidence_series is not None
                else model_result.pop(0)
            )
            # get the rest of metrics too -- Why not pop ? ReviewMe ----------
            individual_series = [
                # Attention : SolarPositionParameterColumnName is an Enum class !
                # Here :
                # `some_parameter.name` is the SolarPositionParameter's member name !'
                # `SolarPositionParameter[some_parameter].value` _is_ the column name we want !
                model_result.get(SolarPositionParameterColumnName[parameter.name].value, numpy.array([]))
                for parameter in position_parameters
                if not isinstance(model_result.get(parameter), str)
                and parameter != SolarPositionParameterColumnName.incidence
            ]
            # ----------------------------------------------------------------
            individual_series_labels = []
            for parameter in position_parameters:
                # Note : pop-ing the parameter from position_parameters causes
                # missing labels in the final "uniplot" !
                # position_parameters.pop(position_parameters.index(parameter))
                if (
                    parameter.name in SolarPositionParameterColumnName.__members__.keys()
                    and parameter.name != SolarPositionParameterColumnName.incidence.name
                ):
                    metric_label = SOLAR_POSITION_PARAMETER_COLUMN_NAMES[parameter]
                    # Add the origin-of-azimuth in the label for solar azimuth series
                    if parameter == SolarPositionParameterColumnName.azimuth:
                        metric_label = (
                            [
                                f"{label} {model_result.get(AZIMUTH_ORIGIN_NAME, NOT_AVAILABLE)}"
                                for label in metric_label
                            ]
                            if isinstance(metric_label, list)
                            else f"{metric_label} {model_result.get(AZIMUTH_ORIGIN_NAME, NOT_AVAILABLE)}"
                        )
                    # extend or append to the list of labels
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
            convert_false_to_none=convert_false_to_none,
            resample_large_series=resample_large_series,
            frequency=frequency,
            lines=True,
            supertitle=f"{supertitle} {model_name}",
            title=title,
            label=label,
            extra_legend_labels=individual_series_labels,
            unit=model_result.get(UNIT_NAME, UNITLESS),
            terminal_width_fraction=terminal_width_fraction,
            verbose=verbose,
        )


def uniplot_spectral_factor_series(
    spectral_factor_dictionary: Dict,
    spectral_factor_model: List,
    photovoltaic_module_type: List,
    timestamps: DatetimeIndex,
    convert_false_to_none: bool = True,
    resample_large_series: bool = False,
    frequency: str = None,
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
    convert_false_to_none : bool
        Convert False to None for arrays of type bool. This is meaningful in
        the context of Uniplot in order to plot series of Boolean values along
        with numeric ones.  For example, plot series of _surface in-shade_,
        which is a series of True or False _states_, alongside other soloar
        position series, i.e. solar altitude.  Only True entries are then
        visualised which shows when the solar surface in question
        is directly sunlit.
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
            convert_false_to_none=convert_false_to_none,
            resample_large_series=resample_large_series,
            frequency=frequency,
            lines=True,
            supertitle=supertitle,
            title=title,
            label=labels[0],
            extra_legend_labels=labels[1:],
            unit="",
            terminal_width_fraction=terminal_width_fraction,
            verbose=verbose,
        )
