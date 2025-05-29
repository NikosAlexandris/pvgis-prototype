"""
This Python module is part of PVGIS' API. It implements functions to calculate
the refracted solar altitude.
"""

import numpy as np
from devtools import debug

from pvgisprototype import (
    RefractedSolarAltitude,
    SolarAltitude,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    DEGREES,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call


@log_function_call
@custom_cached
def calculate_refracted_solar_altitude_series(
    solar_altitude_series: SolarAltitude,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = 0,
    log: int = 0,
) -> RefractedSolarAltitude:
    """Adjust the solar altitude angle for atmospheric refraction.

    Adjust the solar altitude angle for atmospheric refraction for a time
    series.

    Notes
    -----
    This function :
    - requires solar altitude values in degrees.
    - The output _should_ expectedly be of the same `dtype` as the input
      `solar_altitude_series` array.

    """
    atmospheric_refraction = (
        0.061359
        * (
            0.1594
            + 1.123 * solar_altitude_series.degrees
            + 0.065656 * np.power(solar_altitude_series.degrees, 2)
        )
        / (
            1
            + 28.9344 * solar_altitude_series.degrees
            + 277.3971 * np.power(solar_altitude_series.degrees, 2)
        )
    )
    refracted_solar_altitude_series = (
        solar_altitude_series.degrees + atmospheric_refraction
    )

    # The refracted solar altitude
    # is used to calculate the optical air mass as per Kasten, 1989
    # In the "Revised optical air mass tables", the solar altitude denoted by
    # 'γ' ranges from 0 to 90 degrees.
    # refracted_solar_altitude_series = np.clip(
    #     refracted_solar_altitude_series, 0, 90
    # )

    log_data_fingerprint(
        data=refracted_solar_altitude_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return RefractedSolarAltitude(
        value=refracted_solar_altitude_series,  # ensure output is of input dtype !
        unit=DEGREES,
    )
