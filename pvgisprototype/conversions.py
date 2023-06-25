import typer
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
