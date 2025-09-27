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
import numpy as np
from numpy import ndarray
from devtools import debug
from pydantic_numpy import NpNDArray

from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.log import log_data_fingerprint, log_function_call


@log_function_call
@custom_cached
def calculate_term_n_series_hofierka(
    kb_series: ndarray,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> NpNDArray:
    """Define the N term for a period of time

    N = 0.00263 − 0.712 × kb − 0.6883 × kb2

    Parameters
    ----------
    kb_series: float
        Direct horizontal to extraterrestrial horizontal irradiance ratio

    Returns
    -------
    N: float
        The N term

    Notes
    -----

    Muneer's model treats the shaded and sunlit surfaces separately and further
    distinguishes between overcast and non-overcast conditions of the sunlit
    surface.  The diffuse sky-reflected irradiance for both surfaces in-shade and
    sunlit under _overcast_ sky is computed as :

    and a sunlit surface under non-overcast sky as :


    According to Muneer (1990) the radiance distribution index `b` (dimensionless) 
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
