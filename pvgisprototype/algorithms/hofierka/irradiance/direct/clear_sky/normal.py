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
from pandas import DatetimeIndex

from pvgisprototype import (
    DirectNormalIrradiance,
    LinkeTurbidityFactor,
    OpticalAirMass,
)
from pvgisprototype.algorithms.hofierka.irradiance.direct.clear_sky.linke_turbidity_factor import (
    correct_linke_turbidity_factor_series,
)
from pvgisprototype.api.irradiance.direct.rayleigh_optical_thickness import (
    calculate_rayleigh_optical_thickness_series,
)
from pvgisprototype.algorithms.hofierka.irradiance.extraterrestrial.normal import (
    calculate_extraterrestrial_normal_irradiance_hofierka,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    OPTICAL_AIR_MASS_TIME_SERIES_DEFAULT,
    ECCENTRICITY_PHASE_OFFSET,
    SOLAR_CONSTANT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.validation.values import identify_values_out_of_range


@log_function_call
@custom_cached
def calculate_direct_normal_irradiance_hofierka(
    timestamps: DatetimeIndex | None,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LinkeTurbidityFactor(),
    optical_air_mass_series: OpticalAirMass = [
        OPTICAL_AIR_MASS_TIME_SERIES_DEFAULT
    ],  # REVIEW-ME + ?
    clip_to_physically_possible_limits: bool = True,
    solar_constant: float = SOLAR_CONSTANT,
    eccentricity_phase_offset: float = ECCENTRICITY_PHASE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> DirectNormalIrradiance:
    """Calculate the direct normal irradiance.

    The direct normal irradiance attenuated by the cloudless atmosphere,
    represents the amount of solar radiation received per unit area by a
    surface that is perpendicular (normal) to the rays that come in a straight
    line from the direction of the sun at its current position in the sky.

    This function implements the algorithm described by Hofierka, 2002. [1]_

    Parameters
    ----------
    timestamps : DatetimeIndex | None
        timestamps
    linke_turbidity_factor_series : LinkeTurbidityFactor
        linke_turbidity_factor_series
    optical_air_mass_series : OpticalAirMass
        optical_air_mass_series
    clip_to_physically_possible_limits : bool
        clip_to_physically_possible_limits
    solar_constant : float
        solar_constant
    eccentricity_phase_offset : float
        eccentricity_phase_offset
    eccentricity_amplitude : float
        eccentricity_amplitude
    dtype : str
        dtype
    array_backend : str
        array_backend
    verbose : int
        verbose
    log : int
        log
    fingerprint : bool
        fingerprint

    Returns
    -------
    DirectNormalIrradiance

    Notes
    -----
    B0c = G0 exp {-0.8662 TLK m δR(m)}

    where :
    - -0.8662 TLK is the air mass 2 Linke atmospheric turbidity factor [dimensionless] corrected by Kasten [24].

    - m is the relative optical air mass [-] calculated using the formula:

      m = (p/p0)/(sin h0ref + 0.50572 (h0ref + 6.07995)-1.6364)
      
      where :
      
      - h0ref is the corrected solar altitude h0 in degrees by the atmospheric refraction component ∆h0ref

      where : 
      
      - ∆h0ref = 0.061359 (0.1594+1.123 h0 + 0.065656 h02)/(1 + 28.9344 h0 + 277.3971 h02)
      - h0ref = h0 + ∆h0ref

      - The p/p0 component is correction for given elevation z [m]:

        p/p0 = exp (-z/8434.5)

    - δR(m) is the Rayleigh optical thickness at air mass m and is calculated according to the improved formula by Kasten as follows:

    - for m <= 20:

      δR(m) = 1/(6.6296 + 1.7513 m - 0.1202 m2 + 0.0065 m3 - 0.00013 m4)

    - for m > 20

      δR(m) = 1/(10.4 + 0.718 m)

    References
    ----------
    .. [1] Hofierka, J. (2002). Some title of the paper. Journal Name, vol(issue), pages.

    """
    extraterrestrial_normal_irradiance_series = calculate_extraterrestrial_normal_irradiance_hofierka(
            timestamps=timestamps,
            solar_constant=solar_constant,
            eccentricity_phase_offset=eccentricity_phase_offset,
            eccentricity_amplitude=eccentricity_amplitude,
            dtype=dtype,
            array_backend=array_backend,
        )
    corrected_linke_turbidity_factor_series = correct_linke_turbidity_factor_series(
        linke_turbidity_factor_series,
        verbose=verbose,
    )
    rayleigh_optical_thickness_series = calculate_rayleigh_optical_thickness_series(
        optical_air_mass_series,
        verbose=verbose,
    )  # _quite_ high when the sun is below the horizon. Makes sense ?

    # Calculate
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        exponent = (
            corrected_linke_turbidity_factor_series.value
            * optical_air_mass_series.value
            * rayleigh_optical_thickness_series.value
        )
        direct_normal_irradiance_series = extraterrestrial_normal_irradiance_series.value * np.exp(exponent)

    out_of_range, out_of_range_index = identify_values_out_of_range(
        series=direct_normal_irradiance_series,
        shape=timestamps.shape,
        data_model=DirectNormalIrradiance(),
        clip_to_physically_possible_limits=clip_to_physically_possible_limits,
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=direct_normal_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return DirectNormalIrradiance(
        value=direct_normal_irradiance_series,
        out_of_range=out_of_range,
        out_of_range_index=out_of_range_index,
        #
        extraterrestrial_normal_irradiance=extraterrestrial_normal_irradiance_series,
        linke_turbidity_factor_adjusted=corrected_linke_turbidity_factor_series,
        linke_turbidity_factor=linke_turbidity_factor_series,
        rayleigh_optical_thickness=rayleigh_optical_thickness_series,
        optical_air_mass=optical_air_mass_series,
        #
        solar_constant=solar_constant,
        eccentricity_phase_offset=eccentricity_phase_offset,
        eccentricity_amplitude=eccentricity_amplitude,
    )
