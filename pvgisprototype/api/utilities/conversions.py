import typer
from rich.table import Table
from rich.progress import track
from rich import box
from math import degrees
from math import radians
import numpy as np
from typing import Any


def convert_to_radians(ctx: typer.Context, param: typer.CallbackParam, angle: float) -> float:
    """Convert floating point angular measurement from degrees to radians."""
    if ctx.resilient_parsing:
        return
    if type(angle) != float:
        raise typer.BadParameter("Input should be a float!")

    return np.radians(angle)


def convert_to_degrees(ctx: typer.Context, param: typer.CallbackParam, angle: float) -> float:
    """Convert angle to degrees."""
    if ctx.resilient_parsing:
        return
    if type(angle) != float:
        raise typer.BadParameter("The input value {angle} for an angular measurement is not of the expected type float!")

    return np.degrees(angle)


def convert_to_radians_fastapi(angle: float) -> float:
    """Convert angle to radians."""
    if type(angle) != float:
        raise typer.BadParameter("Latitude should be a float!")

    return np.radians(angle)


def convert_float_to_degrees_if_requested(angle: float, output_units: str) -> float:
    """Convert angle from radians to degrees if requested"""
    return degrees(angle) if output_units == 'degrees' else angle


def convert_to_degrees_if_requested(data_class: Any, output_units: str) -> Any:
    """Convert angle from radians to degrees if requested"""
    if output_units == 'degrees' and not data_class.unit == 'degrees':
        data_class.value = degrees(data_class.value)
        data_class.unit = 'degrees'
    return data_class


# def convert_to_radians_if_requested(angle: float, output_units: str) -> float:
#     """Convert angle from degrees to radians if requested."""
#     return np.radians(angle) if output_units == 'radians' else angle


def convert_float_to_radians_if_requested(angle: float, output_units: str) -> float:
    """Convert angle from radians to radians if requested"""
    return radians(angle) if output_units == 'radians' else angle


def convert_to_radians_if_requested(data_input: Any, output_units: str) -> Any:
    """Convert angle from degrees to radians for a single or an array of custom data structures if requested."""
    if output_units != 'radians':
        return data_input

    if isinstance(data_input, np.ndarray):
        for data_class in data_input:
            if data_class.unit != 'radians':
                data_class.value = radians(data_class.value)
                data_class.unit = 'radians'
    else:
        if data_input.unit != 'radians':
            # data_class = replace(data_class, value=radians(data_class.value), unit='radians')
            data_input.value = radians(data_input.value)
            data_input.unit = 'radians'
            
    return data_input


def convert_dictionary_to_table(dictionary):
    table = Table(show_header=True, header_style="bold magenta",
                                 box=box.SIMPLE_HEAD)
    table.add_column("Parameter", style="dim")
    table.add_column("Value")

    # for key, value in dictionary.items():
    # for key, value in track(dictionary.items(), description="Converting dictionary to table..."):
    for key, value in dictionary.items():
        table.add_row(str(key), str(value))

    return table


def round_float_values(obj, decimal_places=3):
    if isinstance(obj, float):
        return f"{round(obj, decimal_places):.{decimal_places}f}"
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, dict):
                for key, value in v.items():
                    if isinstance(value, float):
                        v[key] = f"{round(value, decimal_places):.{decimal_places}f}"
            elif isinstance(v, float):
                obj[i] = f"{round(v, decimal_places):.{decimal_places}f}"
        return obj
    else:
        return obj


# def round_float_values(obj, decimal_places=3):
#     if isinstance(obj, float):
#         return round(obj, decimal_places)
#     elif isinstance(obj, list):
#         for i, v in enumerate(obj):
#             if isinstance(v, dict):
#                 for key, value in v.items():
#                     if isinstance(value, float):
#                         v[key] = round(value, decimal_places)
#             elif isinstance(v, float):
#                 obj[i] = round(v, decimal_places)
#         return obj
#     else:
#         return obj
