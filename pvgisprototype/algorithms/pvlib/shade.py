from devtools import debug
from pathlib import Path
from typing import List

from numpy import ndarray, floor, where

from pvgisprototype import LocationShade, HorizonHeight
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    DEGREES,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    HORIZON_HEIGHT_UNIT,
    LOG_LEVEL_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.core.arrays import create_array

@log_function_call
@custom_cached
# @validate_with_pydantic(CalculateShadeTimeSeriesInputModel)
def calculate_shade_series_pvlib(
    solar_altitude_series,
    solar_azimuth_series,
    shadow_indicator: Path = None,
    horizon_height: ndarray | None = None,
    horizon_interval: float | None = 15,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
) -> LocationShade:
    """Calculate location shade"""
    in_shade_series = is_surface_in_shade_series(
            solar_altitude_series,
            solar_azimuth_series,
            horizon_height=horizon_height,
            horizon_interval=horizon_interval,
            validate_output=validate_output,
        )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=in_shade_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )
    return LocationShade(
        value=in_shade_series,
        unit=DEGREES,
        position_algorithm="pvlib",
        timing_algorithm="pvlib",
    )



@log_function_call
def is_surface_in_shade_series(
    solar_altitude_series,
    solar_azimuth_series,
    shadow_indicator: Path = None,
    horizon_height: ndarray | None = None,
    horizon_interval: float | None = 15,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
) -> List[bool]:
    """
    Determine if a surface is in shade based on solar altitude for each timestamp.

    Parameters
    ----------
    solar_altitude_series_array: numpy array
        Array of solar altitude angles for each timestamp.

    Returns
    -------
    NumPy array: Boolean array indicating whether the surface is in shade at
    each timestamp.

    """
    assert solar_altitude_series.unit == 'radians'
    assert solar_azimuth_series.unit == 'radians'
    import numpy as np
    _horizon_interval = np.radians(horizon_interval)
    # horizon_height is in radians

    array_parameters = {
        "shape": solar_altitude_series.value.shape,  # Borrow shape from it
        "dtype": "bool",
        "init_method": False,
        "backend": array_backend,
    }
    surface_in_shade_series = create_array(**array_parameters)

    import xarray as xr
    horizon_da = xr.DataArray(
        horizon_height,
        coords={
            'azimuth': _horizon_interval,
        },
        dims=['azimuth'],
        name='horizon_height'
    )
    interpolated_horizon_height_series = horizon_da.interp(azimuth=solar_azimuth_series.value)
    
    # interpolated_horizon_height_series = interpolate_horizon_height_series(
    #     solar_azimuth_series=solar_azimuth_series,
    #     horizon_height=horizon_height,
    #     horizon_interval=horizon_interval,
    # )
    # print(list(zip(solar_altitude_series.value, interpolated_horizon_height_series.values)))
    surface_in_shade_series = where(
            solar_altitude_series.value < interpolated_horizon_height_series.values,
            True,
            False
    )

    log_data_fingerprint(
        data=surface_in_shade_series,  ### FixMe!
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    from devtools import debug
    debug(locals())
    return surface_in_shade_series




# @validate_with_pydantic()
def interpolate_horizon_height_series(
    solar_azimuth_series: ndarray,
    horizon_height: ndarray | None,
    horizon_interval: float | None = 15,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
) -> HorizonHeight:
    """Interpolate the height of the horizon for the given solar azimuth time
    series

    Interpolate the hiehgt of the horizon for a given sun azimuth angle based
    on existing horizon height values at a given interval.

    Parameters
    ----------
    solar_azimuth : float
        The azimuth angle of the sun.
    horizon_height : list of float
        List of horizon height values.
    horizon_interval : float
        Interval between successive horizon data points.

    Returns
    -------
    float
        The interpolated horizon height.

    """
    from pvgisprototype.api.utilities.conversions import convert_to_radians_if_requested
    horizon_interval = convert_to_radians_if_requested(horizon_interval, 'radians')

    positions_in_interval = solar_azimuth_series.value / horizon_interval
    positions_before = floor(positions_in_interval).astype(int)
    positions_after = positions_before + 1

    # Handle wrap around
    # positions_after = 0 if positions_after == len(horizon_heights) else positions_after ?
    # if isinstance(horizon_height, str):
    #     horizon_height = [float(x.strip()) for x in horizon_height.split(',')]
    positions_after[positions_after >= len(horizon_height)] = 0

    # Interpolate the horizon height (or weighted average)
    weights_after = positions_in_interval - positions_before
    weights_before = 1 - weights_after
    interpolated_horizon_heights = (
        weights_before * horizon_height[positions_before[0]]
        + weights_after * horizon_height[positions_after[0]]
    )

    return HorizonHeight(value=interpolated_horizon_heights, unit=HORIZON_HEIGHT_UNIT)
