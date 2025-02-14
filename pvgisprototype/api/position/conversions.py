from math import pi
from typing import Protocol

import numpy
from numpy.typing import NDArray


class HasRadians(Protocol):
    @property
    def radians(self) -> float: ...


def convert_north_to_east_radians_convention(north_based_angle: HasRadians) -> NDArray:
    """Convert an azimuth angle from North-based to East-based radians.

    Parameters
    ----------
    north_based_angle : HasRadians
        The angle with a north-based reference where North is 0 radians.

    Returns
    -------
    float
        The converted angle in radians where East is 0 radians.

    Notes
    -----
    This conversion subtracts π/2 from the angle and takes modulo 2π.
    """
    return numpy.mod((north_based_angle.radians - pi / 2), 2 * pi)


def convert_north_to_south_radians_convention(north_based_angle: HasRadians) -> NDArray:
    """Convert an azimuth angle from North-based to South-based radians.

    Parameters
    ----------
    north_based_angle : HasRadians
        The angle with a north-based reference where North is 0 radians.

    Returns
    -------
    float
        The converted angle in radians where South is 0 radians.

    Notes
    -----
    This conversion subtracts π from the angle and takes modulo 2π.
    """
    return numpy.mod((north_based_angle.radians - pi), 2 * pi)


def convert_east_to_north_radians_convention(
    east_based_angle: NDArray,
) -> NDArray:
    """Convert an azimuth from East-based to North-based radians.

    Parameters
    ----------
    azimuth_east_radians : float
        The angle with an east-based reference where East is 0 radians.

    Returns
    -------
    float
        The converted angle in radians where North is 0 radians.

    Notes
    -----
    This conversion adds 3π/2 to the angle and takes modulo 2π.
    """
    return numpy.mod((east_based_angle + 3 * pi / 2), 2 * pi)
