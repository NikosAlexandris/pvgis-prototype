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
def calculate_term_n_series_hofierka(
    kb_series: List[float],
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = 0,
    log: int = 0,
):
    """Define the N term for a period of time

    N = 0.00263 − 0.712 × kb − 0.6883 × kb2

    Parameters
    ----------
    kb_series: float
        Direct to extraterrestrial irradiance ratio

    Returns
    -------
    N: float
        The N term
    """
    kb_series = np.array(kb_series, dtype=dtype)
    term_n_series = (
        0.00263 - (0.712 * kb_series) - (0.6883 * np.power(kb_series, 2, dtype=dtype))
    )
    log_data_fingerprint(
        data=term_n_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return term_n_series
