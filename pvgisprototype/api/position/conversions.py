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
