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
"""
Diffuse Solar Altitude Function

This module implements the diffuse solar altitude function and associated
coefficients from Hofierka's clear-sky radiation model (2002). These functions
characterize how diffuse irradiance varies with solar elevation under cloudless
atmospheric conditions.

Theoretical Background
----------------------
Under cloudless skies, atmospheric turbidity affects the partitioning of solar
radiation into direct and diffuse components. As turbidity increases, diffuse
irradiance increases while direct irradiance decreases.

See Also
--------
pvgisprototype.algorithms.hofierka.irradiance.diffuse.clear_sky.transmission_function
    Implements Tₙ(T_LK) diffuse transmission function
pvgisprototype.algorithms.hofierka.irradiance.diffuse.clear_sky.horizontal
    Combines transmission and altitude functions for total diffuse irradiance
"""

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
    # linke_turbidity_factor_series: LinkeTurbidityFactor = LinkeTurbidityFactor(),
    linke_turbidity_factor_series: LinkeTurbidityFactor,
    verbose: int = 0,
    log: int = 0,
) -> tuple:
    """Calculate the diffuse solar altitude coefficients.

    Calculates the diffuse solar altitude coefficients (a1, a2, a3) over a time
    series required for calculating the diffuse solar altitude function in
    Hofierka's model.

    These coefficients are derived from the Linke Turbidity factor and the
    diffuse transmission function.

    Parameters
    ----------
    linke_turbidity_factor_series: (List[LinkeTurbidityFactor] or LinkeTurbidityFactor)
        The Linke turbidity factors as a list of LinkeTurbidityFactor objects
        or a single object.
    verbose : int, optional
        Verbosity level for debugging output. When set to 
        `DEBUG_AFTER_THIS_VERBOSITY_LEVEL`, prints local variables.
        Default is 0.
    log : int, optional
        Logging level for data fingerprinting. When exceeding 
        `HASH_AFTER_THIS_VERBOSITY_LEVEL`, logs data hashes for traceability.
        Default is 0.

    Returns
    -------
    tuple of numpy.ndarray
        Three arrays containing the coefficient series:
        
        - a1_series : First coefficient, bounded by diffuse transmission
        - a2_series : Second coefficient  
        - a3_series : Third coefficient

    Notes
    -----
    The coefficients are calculated using empirical formulas from Hofierka's
    model :
    
    - a1 is constrained to ensure `a1 * Td >= 0.0022` where Td is diffuse
      transmission
    - a2 and a3 are derived from quadratic functions of the Linke turbidity
      factor
    
    See Also
    --------
    calculate_diffuse_transmission_function_series_hofierka : Computes diffuse
    transmission
    calculate_diffuse_solar_altitude_function_series_hofierka : Uses these
    coefficients

    References
    ----------
    .. [1] Hofierka, J., & Šúri, M. (2002). The solar radiation model for Open
           source GIS: implementation and applications. *Proceedings of the
           Open source GIS - GRASS users conference*, Trento, Italy.

    Examples
    --------
    >>> from pvgisprototype import LinkeTurbidityFactor
    >>> from pvgisprototype.algorithms.hofierka.irradiance.diffuse.clear_sky.altitude import calculate_diffuse_solar_altitude_function_series_hofierka
    >>> from pvgisprototype.algorithms.hofierka.irradiance.diffuse.clear_sky.transmission_function import calculate_diffuse_transmission_function_series_hofierka
    >>> ltf = LinkeTurbidityFactor(value=np.array([2.0, 2.5, 3.0]))
    >>> a1, a2, a3 = calculate_diffuse_solar_altitude_coefficients_series_hofierka(ltf)
    >>> print(a1.shape)
    (3,)
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
    
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
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
    # linke_turbidity_factor_series: LinkeTurbidityFactor = LinkeTurbidityFactor(),
    linke_turbidity_factor_series: LinkeTurbidityFactor,
    verbose: int = 0,
    log: int = 0,
) -> np.ndarray:
    """Calculate the diffuse solar altitude function.

    Calculates the diffuse solar altitude function (Fd) for a time series using
    Hofierka's empirical model. This function combines solar altitude angles
    with turbidity-dependent coefficients to estimate diffuse irradiance
    patterns.

    Parameters
    ----------
    solar_altitude_series : SolarAltitude
        Solar altitude angles for the time series. Must contain `radians` attribute
        with angle values in radians.
    linke_turbidity_factor_series : LinkeTurbidityFactor
        Linke turbidity factor values corresponding to the solar altitude time points.
    verbose : int, optional
        Verbosity level for debugging output. When set to 
        `DEBUG_AFTER_THIS_VERBOSITY_LEVEL`, prints local variables.
        Default is 0.
    log : int, optional
        Logging level for data fingerprinting. When exceeding 
        `HASH_AFTER_THIS_VERBOSITY_LEVEL`, logs data hashes for traceability.
        Default is 0.

    Returns
    -------
    numpy.ndarray
        Diffuse solar altitude function values (Fd) for each time point in the series.
        Array shape matches input series dimensions.

    Notes
    -----
    The diffuse solar altitude function Fₐ(Solar Altitude) characterizes the
    angular distribution of diffuse radiation :

    .. math::
        F_d(Solar Altitude) = a_1 + a_2 \sin(Solar Altitude) + a_3 \sin^2(Solar Altitude)
    
    where:
    
    - :math:`a_1, a_2, a_3` are coefficients derived from Linke turbidity, the
      a₁ coefficient is bounded to ensure physical validity when multiplied by
      the transmission function.

    See Also
    --------
    calculate_diffuse_solar_altitude_coefficients_series_hofierka : Computes
    the a1, a2, a3 coefficients
    SolarAltitude : Solar altitude data model
    LinkeTurbidityFactor : Linke turbidity factor data model

    References
    ----------
    .. [1] Hofierka, J., & Šúri, M. (2002). The solar radiation model for Open
           source GIS: implementation and applications. *Proceedings of the
           Open source GIS - GRASS users conference*, Trento, Italy.
    
    Examples
    --------
    >>> from pvgisprototype import SolarAltitude, LinkeTurbidityFactor
    >>> import numpy as np
    >>> from pvgisprototype.algorithms.hofierka.irradiance.diffuse.clear_sky.altitude import (
    >>> calculate_diffuse_solar_altitude_coefficients_series_hofierka,
    >>> calculate_diffuse_solar_altitude_function_series_hofierka,
    >>> )
    >>> from pvgisprototype.algorithms.hofierka.irradiance.diffuse.clear_sky.transmission_function import calculate_diffuse_transmission_function_series_hofierka
    >>> altitude = SolarAltitude(value=np.array([0.5, 0.8, 1.0]), unit='radians')
    >>> ltf = LinkeTurbidityFactor(value=np.array([2.0, 2.5, 3.0]))
    >>> fd = calculate_diffuse_solar_altitude_function_series_hofierka(altitude, ltf)
    >>> print(fd.shape)
    (3,)
    """
    a1_series, a2_series, a3_series = (
        calculate_diffuse_solar_altitude_coefficients_series_hofierka(
            linke_turbidity_factor_series,
            verbose=verbose,
        )
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
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
