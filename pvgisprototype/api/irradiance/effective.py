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
from devtools import debug
from numpy import where
from pvgisprototype import (
    InclinedIrradiance,
    EffectiveIrradiance,
    SpectralFactorSeries,
)
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    SPECTRAL_FACTOR_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.core.arrays import create_array
from pvgisprototype.core.hashing import generate_hash


@log_function_call
def calculate_spectrally_corrected_effective_irradiance(
    irradiance_series: InclinedIrradiance,
    spectral_factor_series: SpectralFactorSeries = SpectralFactorSeries(
        value=SPECTRAL_FACTOR_DEFAULT
    ),
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
) -> EffectiveIrradiance:
    """Calculate the effective irradiance after the spectral effect

    Calculate the effective irradiance by applying the spectral effect factor/s
    on the inclined global irradiance and before change/s due to the
    reflectivity effect.

    """
    # A stub for the effective irradiance series used in the output dictionary
    # array_parameters = {
    #     "shape": irradiance_series.shape,
    #     "dtype": dtype,
    #     "init_method": "empty",
    #     "backend": array_backend,
    # }
    # effective_irradiance_series =  create_array(**array_parameters)
    # The following is programmatically more "expensive" in order to
    # re-use the `irradiance_series` to avoid a possibly unbound variable !
    effective_irradiance_series = irradiance_series * spectral_factor_series.value
    spectral_effect_series = irradiance_series - (
        irradiance_series / spectral_factor_series.value
    )
    # --------------------------------------------------- Is this safe ? -
    with np.errstate(divide="ignore", invalid="ignore"):
        spectral_effect_percentage_series = 100 * where(
            irradiance_series != 0,
            (effective_irradiance_series - irradiance_series) / irradiance_series,
            0,
        )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=effective_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return EffectiveIrradiance(
        value=effective_irradiance_series,
        spectral_factor=spectral_factor_series,
        spectral_effect=spectral_effect_series,
        spectral_effect_percentage=spectral_effect_percentage_series,
        spectral_factor_algorithm="",
    )
