from typing import List
from pvgisprototype import HorizonHeight
from pathlib import Path
from typing import Optional
import numpy as np
from pvgisprototype.constants import HORIZON_HEIGHT_UNIT


# @validate_with_pydantic()
def interpolate_horizon_height(
    solar_azimuth: float,
    horizon_heights: List[float],
    horizon_interval: float,
) -> HorizonHeight:
    """Interpolate the height of the horizon for a given sun azimuth angle.

    Interpolate the hiehgt of the horizon for a given sun azimuth angle based
    on existing horizon height values at a given interval.

    Parameters
    ----------
    solar_azimuth : float
        The azimuth angle of the sun.
    horizon_heights : list of float
        List of horizon height values.
    horizon_interval : float
        Interval between successive horizon data points.

    Returns
    -------
    float
        The interpolated horizon height.
    """
    position_in_interval = solar_azimuth / horizon_interval
    position_before = int(position_in_interval)
    position_after = position_before + 1

    # Handle wrap around
    position_after = 0 if position_after == len(horizon_heights) else position_after

    # Interpolate the horizon height (or weighted average)
    horizon_height = (
        (1 - (position_in_interval - position_before))
        * horizon_heights[position_before] 
        + (position_in_interval - position_before)
        * horizon_heights[position_after]
    )

    return HorizonHeight(horizon_height, HORIZON_HEIGHT_UNIT)


# @validate_with_pydantic()
def interpolate_horizon_height_series(
    solar_azimuth_series: float,
    horizon_heights: List[float],
    horizon_interval: float,
) -> HorizonHeight:
    """Interpolate the height of the horizon for a given sun azimuth angle.

    Interpolate the hiehgt of the horizon for a given sun azimuth angle based
    on existing horizon height values at a given interval.

    Parameters
    ----------
    solar_azimuth : float
        The azimuth angle of the sun.
    horizon_heights : list of float
        List of horizon height values.
    horizon_interval : float
        Interval between successive horizon data points.

    Returns
    -------
    float
        The interpolated horizon height.
    """
    positions_in_interval = solar_azimuth_series / horizon_interval
    positions_before = np.floor(positions_in_interval).astype(int)
    positions_after = positions_before + 1

    # Handle wrap around
    # positions_after = 0 if positions_after == len(horizon_heights) else positions_after ?
    positions_after[positions_after >= len(horizon_heights)] = 0

    # Interpolate the horizon height (or weighted average)
    weights_after = positions_in_interval - positions_before
    weights_before = 1 - weights_after
    interpolated_horizon_heights = (
        weights_before
        * horizon_heights[positions_before]
        + weights_after
        * horizon_heights[positions_after]
    )

    return HorizonHeight(interpolated_horizon_heights, HORIZON_HEIGHT_UNIT)




def is_surface_in_shade(
    solar_altitude: float,
    solar_azimuth: float,
    shadow_indicator: Path = None,
    horizon_heights: Optional[List[float]] = None,
    horizon_interval: Optional[float] = None,
) -> bool:
    """Determine whether the solar surface is in shade

    Determine if the solar surface is in shade based the solar altitude and the
    horizon_height. The solar azimuth is required to interpolate the horizon
    height based on existing horizon height values at a given interval.

    Parameters
    ----------
    shadow_indicator : int, optional
        Shadow data indicating presence of shadow, by default None.
    solar_altitude : float
        The altitude of the sun.
    solar_azimuth : float
        The azimuth angle of the sun.
    horizon_heights : list of float, optional
        List of horizon height values, by default None.
    horizon_interval : float, optional
        Interval between successive horizon data points, by default None.

    Returns
    -------
    bool
        True if the solar surface is in shade, otherwise False.
    """
    if shadow_indicator is not None and bool(shadow_indicator):
        return True

    if horizon_heights is not None:
        horizon_height = interpolate_horizon_height(solar_azimuth, horizon_heights, horizon_interval)
        if horizon_height > solar_altitude:
            return True
    
    return False


def is_surface_in_shade_time_series(
    solar_altitude_series,
    solar_azimuth_series,
    shadow_indicator: Path = None,
    horizon_heights: Optional[List[float]] = None,
    horizon_interval: Optional[float] = None,
) -> List[bool]:
    """
    Determine if a surface is in shade based on solar altitude for each timestamp.

    Parameters:
    - solar_altitude_series_array (numpy array): Array of solar altitude angles for each timestamp.

    Returns:
    - numpy array: Boolean array indicating whether the surface is in shade at each timestamp.
    """
    return np.full(solar_altitude_series.value.shape, False)
