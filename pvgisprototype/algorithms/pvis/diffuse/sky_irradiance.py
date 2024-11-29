from math import cos, pi, sin
from typing import List

import numpy as np
from devtools import debug

from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call


@log_function_call
def calculate_diffuse_sky_irradiance_series_hofierka(
    n_series: List[float],
    surface_tilt: float | None = np.radians(45),
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    log: int = 0,
):
    """Calculate the diffuse sky irradiance

    The diffuse sky irradiance function F(γN) depends on the surface tilt `γN`
    (in radians)

    Parameters
    ----------
    surface_tilt: float (radians)
        The tilt (also referred to as : inclination or slope) angle of a solar
        surface

    n_series: float
        The term N

    Returns
    -------

    Notes
    -----
    Internally the function calculates first the dimensionless fraction of the
    sky dome viewed by a tilted (or inclined) surface `ri(γN)`.
    """
    # sky_view_fraction = (1 + cos(surface_tilt)) / 2
    diffuse_sky_irradiance_series = ((1 + cos(surface_tilt)) / 2) + (
        sin(surface_tilt)
        - surface_tilt * cos(surface_tilt)
        - pi * np.power((sin(surface_tilt / 2)), 2)
    ) * n_series
    log_data_fingerprint(
        data=diffuse_sky_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return np.array(diffuse_sky_irradiance_series, dtype=dtype)
