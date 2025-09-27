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
This Python module is part of PVGIS' API. It implements functions to calculate
the Rayleigh optical thickness.
"""

import numpy as np
from devtools import debug

from pvgisprototype import (
    OpticalAirMass,
    RayleighThickness,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    RAYLEIGH_OPTICAL_THICKNESS_UNIT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call


@log_function_call
@custom_cached
def calculate_rayleigh_optical_thickness_series(
    optical_air_mass_series: OpticalAirMass,  # OPTICAL_AIR_MASS_TIME_SERIES_DEFAULT
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
) -> RayleighThickness:
    """Calculate the Rayleigh optical thickness.

    Calculate Rayleigh optical thickness for a time series.

    """
    rayleigh_thickness_series = np.zeros_like(
        optical_air_mass_series.value, dtype=dtype
    )
    smaller_than_20 = optical_air_mass_series.value <= 20
    larger_than_20 = optical_air_mass_series.value > 20
    rayleigh_thickness_series[smaller_than_20] = 1 / (
        6.6296
        + 1.7513 * optical_air_mass_series.value[smaller_than_20]
        - 0.1202 * np.power(optical_air_mass_series.value[smaller_than_20], 2)
        + 0.0065 * np.power(optical_air_mass_series.value[smaller_than_20], 3)
        - 0.00013 * np.power(optical_air_mass_series.value[smaller_than_20], 4)
    )
    rayleigh_thickness_series[larger_than_20] = 1 / (
        10.4 + 0.718 * optical_air_mass_series.value[larger_than_20]
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=rayleigh_thickness_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )
    return RayleighThickness(
        value=rayleigh_thickness_series,
        unit=RAYLEIGH_OPTICAL_THICKNESS_UNIT,
    )
