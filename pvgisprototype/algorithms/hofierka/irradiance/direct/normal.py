"""
This Python module is part of PVGIS' Algorithms. It implements a function to
calculate the direct normal solar irradiance.

_Direct_ or _beam_ irradiance is one of the main components of solar
irradiance. It comes perpendicular from the Sun and is not scattered before it
irradiates a surface.

During a cloudy day the sunlight will be partially absorbed and scattered by
different air molecules. The latter part is defined as the _diffuse_
irradiance. The remaining part is the _direct_ irradiance.
"""

import numpy as np
from devtools import debug
from numpy import ndarray

from pvgisprototype import (
    DirectNormalFromHorizontalIrradiance,
    Irradiance,
    SolarAltitude,
)
from pvgisprototype.api.irradiance.limits import (
    LOWER_PHYSICALLY_POSSIBLE_LIMIT,
    UPPER_PHYSICALLY_POSSIBLE_LIMIT,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    DIRECT_NORMAL_IRRADIANCE,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    HOFIERKA_2002,
    IRRADIANCE_UNIT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger
from pvgisprototype.validation.values import identify_values_out_of_range


@log_function_call
@custom_cached
def calculate_direct_normal_from_horizontal_irradiance_hofierka(
    direct_horizontal_irradiance: ndarray,
    solar_altitude_series: SolarAltitude | None = None,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
) -> Irradiance:
    """Calculate the direct normal from the horizontal irradiance.

    The direct normal irradiance represents the amount of solar radiation
    received per unit area by a surface that is perpendicular (normal) to the
    rays that come in a straight line from the direction of the sun at its
    current position in the sky.

    This function calculates the direct normal irradiance from the direct horizontal
    irradiance component and the solar altitude.

    Notes
    -----

    References
    ----------
    .. [1] Hofierka, J. (2002). Some title of the paper. Journal Name, vol(issue), pages.

    """
    mask_solar_altitude_positive = solar_altitude_series.radians > 0
    mask_not_in_shade = np.full_like(
        solar_altitude_series.radians, True
    )  # Stub, replace with actual condition
    mask = np.logical_and.reduce((mask_solar_altitude_positive, mask_not_in_shade))

    direct_normal_irradiance_series = np.zeros_like(solar_altitude_series.radians)
    if np.any(mask):
        direct_normal_irradiance_series[mask] = (
            direct_horizontal_irradiance / np.sin(solar_altitude_series.radians)
        )[mask]

    out_of_range, out_of_range_index = identify_values_out_of_range(
        series=direct_normal_irradiance_series,
        shape=solar_altitude_series.value.shape,
        data_model=DirectNormalFromHorizontalIrradiance(),
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=direct_normal_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return DirectNormalFromHorizontalIrradiance(
        value=direct_normal_irradiance_series,
        out_of_range=out_of_range,
        out_of_range_index=out_of_range_index,
        direct_horizontal_irradiance=direct_horizontal_irradiance,
        solar_altitude=solar_altitude_series,
    )
