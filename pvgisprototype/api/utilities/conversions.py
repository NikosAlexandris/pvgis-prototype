import typer
from rich.table import Table
from rich.progress import track
from rich import box
import numpy as np


def convert_to_radians(ctx: typer.Context, param: typer.CallbackParam, angle: float) -> float:
    """Convert angle to radians."""
    if ctx.resilient_parsing:
        return
    if type(angle) != float:
        raise typer.BadParameter("Latitude should be a float!")

    return np.radians(angle)


def convert_to_degrees_if_requested(angle: float, output_units: str) -> float:
    """Convert angle from radians to degrees if requested."""

    return np.degrees(angle) if output_units == 'degrees' else angle


def convert_to_radians_if_requested(angle: float, output_units: str) -> float:
    """Convert angle from degrees to radians if requested."""
    return np.radians(angle) if output_units == 'radians' else angle


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

