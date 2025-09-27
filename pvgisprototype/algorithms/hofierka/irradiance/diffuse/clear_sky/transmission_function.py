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

from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.log import log_data_fingerprint, log_function_call


@log_function_call
@custom_cached
def calculate_diffuse_transmission_function_series_hofierka(
    linke_turbidity_factor_series,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = 0,
    log: int = 0,
) -> ndarray:
    """Diffuse transmission function over a period of time

    Parameters
    ----------
    linke_turbidity_factor_series :
        linke_turbidity_factor_series
    dtype : str
        dtype
    array_backend : str
        array_backend
    verbose : int
        verbose
    log : int
        log

    Returns
    -------
    ndarray

    Notes
    -----
    From Thomas Huld's custom `r.pv` source code:

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

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())
    
    log_data_fingerprint(
        data=diffuse_transmission_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return diffuse_transmission_series
