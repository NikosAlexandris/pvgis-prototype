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
from math import cos, pi, sin
from typing import List

import numpy as np
from devtools import debug

from pvgisprototype import LinkeTurbidityFactor, SolarAltitude
from pvgisprototype.algorithms.hofierka.irradiance.diffuse.clear_sky.transmission_function import calculate_diffuse_transmission_function_series_hofierka
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
def calculate_diffuse_solar_altitude_coefficients_series_hofierka(
    linke_turbidity_factor_series,
    verbose: int = 0,
    log: int = 0,
):
    """Calculate the diffuse solar altitude coefficients.

    Calculate the diffuse solar altitude coefficients over a period of time.

    Parameters
    ----------
    linke_turbidity_factor_series: (List[LinkeTurbidityFactor] or LinkeTurbidityFactor)
        The Linke turbidity factors as a list of LinkeTurbidityFactor objects
        or a single object.

    Returns
    -------

    """
    linke_turbidity_factor_series_squared_array = np.power(
        linke_turbidity_factor_series.value, 2
    )
    diffuse_transmission_series = calculate_diffuse_transmission_function_series_hofierka(
        linke_turbidity_factor_series
    )
    diffuse_transmission_series_array = np.array(diffuse_transmission_series)
    a1_prime_series = (
        0.26463
        - 0.061581 * linke_turbidity_factor_series.value
        + 0.0031408 * linke_turbidity_factor_series_squared_array
    )
    a1_series = np.where(
        a1_prime_series * diffuse_transmission_series < 0.0022,
        # 0.0022 / diffuse_transmission_series_array,
        np.maximum(0.0022 / diffuse_transmission_series_array, a1_prime_series),
        a1_prime_series,
    )
    a2_series = (
        2.04020
        + 0.018945 * linke_turbidity_factor_series.value
        - 0.011161 * linke_turbidity_factor_series_squared_array
    )
    a3_series = (
        -1.3025
        + 0.039231 * linke_turbidity_factor_series.value
        + 0.0085079 * linke_turbidity_factor_series_squared_array
    )
    
    if verbose == DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=(a1_series, a2_series, a3_series),
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return a1_series, a2_series, a3_series


@log_function_call
@custom_cached
def calculate_diffuse_solar_altitude_function_series_hofierka(
    solar_altitude_series: SolarAltitude,
    linke_turbidity_factor_series: LinkeTurbidityFactor,
    verbose: int = 0,
    log: int = 0,
):
    """Calculate the diffuse solar altitude

    Parameters
    ----------
    solar_altitude_series : SolarAltitude
        solar_altitude_series
    linke_turbidity_factor_series : LinkeTurbidityFactor
        linke_turbidity_factor_series
    verbose : int
        verbose
    log : int
        log

    Notes
    -----
    Other symbol: function Fd

    """
    a1_series, a2_series, a3_series = (
        calculate_diffuse_solar_altitude_coefficients_series_hofierka(
            linke_turbidity_factor_series
        )
    )

    if verbose == DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())
    
    log_data_fingerprint(
        data=(a1_series, a2_series, a3_series),
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return (
        a1_series
        + a2_series * np.sin(solar_altitude_series.radians)
        + a3_series * np.power(np.sin(solar_altitude_series.radians), 2)
    )
