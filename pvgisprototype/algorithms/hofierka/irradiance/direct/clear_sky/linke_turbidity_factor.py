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
from devtools import debug
from numpy import array as numpy_array

from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.log import log_data_fingerprint, log_function_call


@log_function_call
@custom_cached
def correct_linke_turbidity_factor_series(
    linke_turbidity_factor_series: LinkeTurbidityFactor = LinkeTurbidityFactor(),
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
) -> LinkeTurbidityFactor:
    """Calculate the air mass 2 Linke turbidity factor.

    Calculate the air mass 2 Linke atmospheric turbidity factor for a time series.

    Parameters
    ----------
    linke_turbidity_factor_series: List[LinkeTurbidityFactor] | LinkeTurbidityFactor
        The Linke turbidity factors as a list of LinkeTurbidityFactor objects
        or a single object.
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
    List[LinkeTurbidityFactor] or LinkeTurbidityFactor
        The corrected Linke turbidity factors as a list of LinkeTurbidityFactor
        objects or a single object.

    """
    corrected_linke_turbidity_factors = -0.8662 * numpy_array(
        linke_turbidity_factor_series.value, dtype=dtype
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=corrected_linke_turbidity_factors,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return LinkeTurbidityFactor(
        value=corrected_linke_turbidity_factors,
    )
