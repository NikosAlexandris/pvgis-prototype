from typing import Protocol
from math import pi

class HasRadians(Protocol):
    @property
    def radians(self) -> float:
        ...

def convert_north_to_east_radians_convention(
    north_based_angle: HasRadians,
):
    """Convert an azimuth from North-based to East-based.

    Parameters
    ----------

    Returns
    -------

    Notes
    -----

    """
    return (north_based_angle.radians - pi / 2) % (2 * pi)
    # return north_based_angle.radians


def convert_east_to_north_radians_convention(azimuth_east_radians):
    # return (pi/2 - east_based_angle + 360) % 360
    return (azimuth_east_radians + 3 * pi / 2) % (2 * pi)
