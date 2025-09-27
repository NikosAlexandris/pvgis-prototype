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
from enum import Enum
from math import degrees, pi, radians
from typing import Any, List

import numpy as np
import typer
from rich import box
from rich.table import Table

from pvgisprototype.constants import DEGREES, RADIANS


def convert_to_radians(
    ctx: typer.Context, param: typer.CallbackParam, angle: float
) -> float:
    """Convert floating point angular measurement from degrees to radians."""
    if ctx.resilient_parsing:
        return
    if not isinstance(angle, float):
        raise typer.BadParameter("Input should be a float!")

    return np.radians(angle)


def convert_to_degrees(
    ctx: typer.Context, param: typer.CallbackParam, angle: float
) -> float:
    """Convert angle to degrees."""
    if ctx.resilient_parsing:
        return
    if not isinstance(angle, float):
        raise typer.BadParameter(
            "The input value {angle} for an angular measurement is not of the expected type float!"
        )

    return np.degrees(angle)


def convert_to_radians_fastapi(angle: float) -> float:
    """Convert angle to radians."""
    if not isinstance(angle, (float, int)):
        raise typer.BadParameter("Angle should be a float!")

    return np.radians(angle)


def convert_float_to_degrees_if_requested(angle: int | float | None, output_units: str) -> float:
    """Convert angle from radians to degrees if requested"""
    if isinstance(angle, (int, float)):
        return degrees(angle) if output_units == DEGREES else angle


def convert_to_degrees_if_requested(data_class: Any, output_units: str) -> Any:
    """Convert angle from radians to degrees if requested"""
    from copy import deepcopy

    copy_of_data_class = deepcopy(data_class)
    if output_units == DEGREES and not data_class.unit == DEGREES:
        copy_of_data_class.value = degrees(data_class.value)
        copy_of_data_class.unit = DEGREES

    return copy_of_data_class


def convert_series_to_degrees_if_requested(
    data_class_series: List[Any],
    angle_output_units: str,
) -> List[Any]:
    """
    Vectorized conversion of a series of angle data from radians to degrees if requested.

    Parameters
    ----------
    data_class_series : List[Any]
        A list of data classes containing the angle value and unit.
    angle_output_units : str
        The desired output unit ('degrees' or 'radians').

    Returns
    -------
    List[Any]
        A list of converted data classes.
    """
    from copy import deepcopy

    copy_of_data_class_series = deepcopy(data_class_series)

    if angle_output_units == DEGREES:
        values_to_convert = np.array(
            [
                data_class.value
                for data_class in copy_of_data_class_series
                if data_class.unit != DEGREES
            ]
        )
        converted_values = np.degrees(values_to_convert)

        for i, data_class in enumerate(copy_of_data_class_series):
            if data_class.unit != DEGREES:
                data_class.value = converted_values[i]
                data_class.unit = DEGREES

    return copy_of_data_class_series


def convert_series_to_degrees_arrays_if_requested(
    data_class_series: List[Any],
    angle_output_units: str,
) -> np.ndarray:
    """
    Vectorized conversion of a series of angle data from radians to degrees if requested.

    Parameters
    ----------
    data_class_series : List[Any]
        A list of data classes containing the angle value and unit.
    angle_output_units : str
        The desired output unit ('degrees' or 'radians').

    Returns
    -------
    List[Any]
        A list of converted data classes.
    """
    converted_series = convert_series_to_degrees_if_requested(
        data_class_series, angle_output_units
    )
    # an array of values is friendly (currently) for print_irradiance_table_2()
    array = np.array([x.value for x in converted_series])

    return array


def convert_float_to_radians_if_requested(angle: float, output_units: str) -> float:
    """Convert angle from radians to radians if requested"""
    return radians(angle) if output_units == RADIANS else angle


def convert_to_radians_if_requested(data_input: Any, output_units: str) -> Any:
    """Convert angle from degrees to radians for a single or an array of custom data structures if requested."""
    if output_units != RADIANS:
        return data_input

    if isinstance(data_input, np.ndarray):
        for data_class in data_input:
            if data_class.unit != RADIANS:
                data_class.value = radians(data_class.value)
                data_class.unit = RADIANS
    else:
        if data_input.unit != RADIANS:
            # data_class = replace(data_class, value=radians(data_class.value), unit='radians')
            data_input.value = radians(data_input.value)
            data_input.unit = RADIANS

    return data_input


def convert_series_to_radians_if_requested(
    data_class_series: List[Any],
    angle_output_units: str,
) -> List[Any]:
    """
    Vectorized conversion of a series of angle data from radians to radians if requested.

    Parameters
    ----------
    data_class_series : List[Any]
        A list of data classes containing the angle value and unit.
    angle_output_units : str
        The desired output unit ('radians' or 'radians').

    Returns
    -------
    List[Any]
        A list of converted data classes.
    """

    from copy import deepcopy

    copy_of_data_class_series = deepcopy(data_class_series)
    if angle_output_units == RADIANS:
        values_to_convert = np.array(
            [
                data_class.value
                for data_class in copy_of_data_class_series
                if data_class.unit != RADIANS
            ]
        )
        converted_values = np.radians(values_to_convert)

        for i, data_class in enumerate(copy_of_data_class_series):
            if data_class.unit != RADIANS:
                data_class.value = converted_values[i]
                data_class.unit = RADIANS

    return copy_of_data_class_series


def convert_dictionary_to_table(dictionary):
    table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE_HEAD)
    table.add_column("Parameter", style="dim")
    table.add_column("Value")

    # for key, value in track(dictionary.items(), description="Converting dictionary to table..."):
    for key, value in dictionary.items():
        table.add_row(str(key), str(value))

    return table


def round_float_values(data, decimal_places=3):
    """Recursively round float attributes in a custom data class or any float."""
    if isinstance(data, float):
        return round(data, decimal_places)

    if isinstance(data, np.floating):
        return np.around(
            data, decimals=decimal_places
        )  # See also Notes in numpy.round?

    if isinstance(data, np.ndarray) and data.dtype.kind in "if":
        # if not data.size == 1:
        return np.around(
            data, decimals=decimal_places
        )  # See also Notes in numpy.round?
        # else:
        #     return np.format_float_positional(data, precision=decimal_places)

    if isinstance(data, dict):
        return {
            key: round_float_values(value, decimal_places)
            for key, value in data.items()
            if not isinstance(value, Enum)
        }

    if isinstance(data, list):
        return [
            round_float_values(item, decimal_places)
            for item in data
            if not isinstance(item, Enum)
        ]

    if hasattr(data, "__dict__") and not isinstance(data, Enum):
        for key, value in vars(data).items():
            setattr(data, key, round_float_values(value, decimal_places))
        return data

    return data


def convert_south_to_north_degrees_convention(azimuth_south_degrees):
    return (azimuth_south_degrees + 180) % 360


def convert_south_to_north_radians_convention(azimuth_south_radians):
    return (azimuth_south_radians + pi) % (2 * pi)
