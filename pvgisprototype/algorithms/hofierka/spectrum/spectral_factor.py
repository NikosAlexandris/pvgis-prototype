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
from numpy.typing import NDArray

from pvgisprototype.algorithms.hofierka.constants import (
    STANDARD_CONDITIONS_EFFECTIVE_IRRADIANCE,
)


def integrate_spectrum_response(
    spectral_response_frequencies: NDArray[np.float32] = None,
    spectral_response: NDArray[np.float32] = None,
    kato_limits: NDArray[np.float32] = None,
    spectral_power_density: NDArray[np.float32] = None,
) -> float:
    """ """
    m = 0
    n = 0
    # nu_high = float()
    # response_low = float()
    # response_high = float()
    photovoltaic_power = 0
    response_low = spectral_response[0]
    # nu_low = float()
    nu_low = spectral_response_frequencies[0]

    number_of_response_values = len(spectral_response_frequencies)
    # number_of_kato_limits = len(kato_limits)

    while n < number_of_response_values - 1:
        if spectral_response_frequencies[n + 1] < kato_limits[m + 1]:
            nu_high = spectral_response_frequencies[n + 1]
            response_high = spectral_response[n + 1]

        else:
            nu_high = kato_limits[m + 1]
            response_high = spectral_response[n] + (
                nu_high - spectral_response_frequencies[n]
            ) / (
                spectral_response_frequencies[n + 1] - spectral_response_frequencies[n]
            ) * (
                spectral_response[n + 1] - spectral_response[n]
            )
        photovoltaic_power += (
            spectral_power_density[m]
            * 0.5
            * (response_high + response_low)
            * (nu_high - nu_low)
        )

        if spectral_response_frequencies[n + 1] < kato_limits[m + 1]:
            n += 1
        else:
            m += 1

        nu_low = nu_high
        response_low = response_high

    return photovoltaic_power


def calculate_minimum_spectral_mismatch(
    response_wavelengths,
    spectral_response,
    number_of_junctions: int,
    spectral_power_density,
):
    """
    Returns
    -------
    minimum_spectral_mismatch: float

    minimum_junction:

        By Kirchoff’s Law the overall current produced by the device is only
        equal to the smallest current produced by an individual junction. This
        means that the least productive layer in a multi-junction device limits
        the performance of a multijunction cell [1]_

    References
    ----------
    .. [1] Jardine, C.N. & Gottschalg, Ralph & Betts, Thomas & Infield, David.
      (2002). Influence of Spectral Effects on the Performance of Multijunction
      Amorphous Silicon Cells. to be published.
    """
    minimum_spectral_mismatch = 0  # FixMe
    minimum_junction = 1  # FixMe
    for junction in range(number_of_junctions):
        spectral_mismatch = integrate_spectrum_response(
            spectral_response_frequencies=response_wavelengths,
            spectral_response=spectral_response,
            kato_limits=junction,
            spectral_power_density=spectral_power_density,
        )
        if spectral_mismatch < minimum_spectral_mismatch:
            minimum_spectral_mismatch = spectral_mismatch
            minimum_junction = junction

    return minimum_spectral_mismatch, minimum_junction


def calculate_spectral_factor(
    # minimum_spectral_mismatch,
    response_wavelengths,
    spectral_response,
    number_of_junctions: int,
    spectral_power_density,
    global_total_power,
    standard_conditions_response,
):
    (
        minimum_spectral_mismatch,
        minimum_junction,
    ) = calculate_minimum_spectral_mismatch(
        response_wavelengths=response_wavelengths,
        spectral_response=spectral_response,
        number_of_junctions=number_of_junctions,
        spectral_power_density=spectral_power_density,
    )
    spectral_factor = (
        minimum_spectral_mismatch
        * STANDARD_CONDITIONS_EFFECTIVE_IRRADIANCE
        / (global_total_power * standard_conditions_response)
    )

    return spectral_factor
