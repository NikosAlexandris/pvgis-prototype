import numpy as np


def convert_to_degrees_if_requested(angle: float, output_units: str) -> float:
    """Convert angle from radians to degrees if requested."""

    return np.degrees(angle) if output_units == 'degrees' else angle


def convert_to_radians_if_requested(angle: float, output_units: str) -> float:
    """Convert angle from degrees to radians if requested."""
    return np.radians(angle) if output_units == 'radians' else angle
