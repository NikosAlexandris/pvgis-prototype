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
    NormalIrradiance,
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
    ECCENTRICITY_CORRECTION_FACTOR,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    HOFIERKA_2002,
    IRRADIANCE_UNIT,
    PERIGEE_OFFSET,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger


@log_function_call
@custom_cached
def calculate_direct_normal_from_horizontal_irradiance_series_pvgis(
    direct_horizontal_irradiance: ndarray,
    solar_altitude_series: SolarAltitude | None = None,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
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

    This function calculates the normal irradiance from the given horizontal
    irradiance component.

    Notes
    -----
    Known also as : SID, units : W*m-2

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

    # Warning
    out_of_range = (
        direct_normal_irradiance_series < LOWER_PHYSICALLY_POSSIBLE_LIMIT
    ) | (direct_normal_irradiance_series > UPPER_PHYSICALLY_POSSIBLE_LIMIT)
    if out_of_range.size > 0:
        out_of_range_values = direct_normal_irradiance_series[out_of_range]
        stub_array = np.full(out_of_range.shape, -1, dtype=int)
        index_array = np.arange(len(out_of_range))
        out_of_range_indices = np.where(out_of_range, index_array, stub_array)
        warning_unstyled = (
            f"\n"
            f"{WARNING_OUT_OF_RANGE_VALUES} "
            f"[{LOWER_PHYSICALLY_POSSIBLE_LIMIT}, {UPPER_PHYSICALLY_POSSIBLE_LIMIT}]"
            f" in direct_normal_irradiance_series : "
            f"{out_of_range_values}"
            f"\n"
        )
        warning = (
            f"\n"
            f"{WARNING_OUT_OF_RANGE_VALUES} "
            f"[{LOWER_PHYSICALLY_POSSIBLE_LIMIT}, {UPPER_PHYSICALLY_POSSIBLE_LIMIT}]"
            f" in [code]direct_normal_irradiance_series[/code] : "
            f"{out_of_range_values}"
            f"\n"
        )
        logger.warning(warning_unstyled, alt=warning)

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=direct_normal_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return NormalIrradiance(
        value=direct_normal_irradiance_series,
        unit=IRRADIANCE_UNIT,
        title=DIRECT_NORMAL_IRRADIANCE,
        solar_radiation_model=HOFIERKA_2002,
        direct_horizontal_irradiance=direct_horizontal_irradiance,
        solar_altitude=solar_altitude_series,
        # solar_position_algorithm=solar_position_model,
        # solar_time_algorithm=solar_time_model,
        out_of_range=out_of_range,
        out_of_range_index=out_of_range_indices,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
    )
