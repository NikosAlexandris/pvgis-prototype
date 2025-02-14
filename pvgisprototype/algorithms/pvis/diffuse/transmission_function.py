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
def calculate_diffuse_transmission_function_series_hofierka(
    linke_turbidity_factor_series,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = 0,
    log: int = 0,
) -> np.array:
    """Diffuse transmission function over a period of time

    Notes
    -----
    From r.pv's source code:
    tn = -0.015843 + locLinke * (0.030543 + 0.0003797 * locLinke);

    From Hofierka (2002) :

        The estimate of the transmission function Tn(TLK) gives a theoretical
        diffuse irradiance on a horizontal surface with the sun vertically
        overhead for the air mass 2 Linke turbidity factor. The following
        second order polynomial expression is used:

        Tn(TLK) = -0.015843 + 0.030543 TLK + 0.0003797 TLK^2


    """
    linke_turbidity_factor_series_squared_array = np.power(
        linke_turbidity_factor_series.value, 2, dtype=dtype
    )
    diffuse_transmission_series = (
        -0.015843
        + 0.030543 * linke_turbidity_factor_series.value
        + 0.0003797 * linke_turbidity_factor_series_squared_array
    )
    log_data_fingerprint(
        data=diffuse_transmission_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return diffuse_transmission_series
