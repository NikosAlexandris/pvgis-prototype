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
from pvgisprototype.log import log_function_call, logger, log_data_fingerprint
import numpy as np
from pvgisprototype import (
    ExtraterrestrialHorizontalIrradiance,
    ExtraterrestrialNormalIrradiance,
    SolarAltitude,
)
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.validation.values import identify_values_out_of_range


@log_function_call
@custom_cached
def calculate_extraterrestrial_horizontal_irradiance_series_hofierka(
    extraterrestrial_normal_irradiance: ExtraterrestrialNormalIrradiance = ExtraterrestrialNormalIrradiance(),
    solar_altitude_series: SolarAltitude = SolarAltitude(),
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
) -> ExtraterrestrialHorizontalIrradiance:
    """
    Calculate the horizontal extraterrestrial irradiance over a period of time.
    This function implements the algorithm described by Hofierka [1]_.

    Notes
    -----
    In [1]_ : G0h = G0 ⋅ sin(h0)  or else : G0 horizontal = G0 normal ⋅ sin(solar altitude)


    In the context of PVGIS, one question is : does it make sense to have negative
    extraterrestrial horizontal irradiance for moments in time when the sun is
    below the horizon (i.e. solar altitude < 0 radians or degrees) ?

    For PVGIS the answer is no, hence the output horizontal extraterrestrial
    irradiance is set to 0 for this moments.

    References
    ----------
    .. [1] Hofierka, J. (2002). Some title of the paper. Journal Name, vol(issue), pages.

    """
    if verbose > 0:
        logger.info(
            ":information: Modelling the horizontal extraterrestrial irradiance",
            alt=":information: [bold]Modelling[/bold] the horizontal extraterrestrial irradiance",
        )
    extraterrestrial_horizontal_irradiance = (
        extraterrestrial_normal_irradiance.value * np.sin(solar_altitude_series.radians)
    )
    extraterrestrial_horizontal_irradiance[solar_altitude_series.radians < 0] = (
        0  # In the context of PVGIS, does it make sense to have negative extraterrestrial horizontal irradiance
    )

    out_of_range, out_of_range_index = identify_values_out_of_range(
        series=extraterrestrial_horizontal_irradiance,
        shape=solar_altitude_series.value.shape,
        data_model=ExtraterrestrialHorizontalIrradiance(),
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=extraterrestrial_horizontal_irradiance,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return ExtraterrestrialHorizontalIrradiance(
        value=extraterrestrial_horizontal_irradiance,
        out_of_range=out_of_range,
        out_of_range_index=out_of_range_index,
        normal=extraterrestrial_normal_irradiance,
        quality="Not validated!",
    )
