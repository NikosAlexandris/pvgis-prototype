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
import numpy
from numpy._core.multiarray import ndarray
from pvgisprototype import DiffuseSkyReflectedHorizontalIrradianceFromExternalData
from pvgisprototype.api.series.hardcodings import exclamation_mark
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.validation.values import identify_values_out_of_range
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger


@log_function_call
@custom_cached
def calculate_diffuse_horizontal_irradiance_hofierka(
    global_horizontal_irradiance_series: ndarray,
    direct_horizontal_irradiance_series: ndarray,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,  # Not yet integrated !
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> DiffuseSkyReflectedHorizontalIrradianceFromExternalData:
    """Calculate the diffuse horizontal irradiance from SARAH time series.

    Calculate the diffuse horizontal irradiance incident on a solar surface
    from SARAH time series.

    Parameters
    ----------
    global_horizontal_irradiance_series : ndarray
        The global horizontal irradiance, also known as surface short-wave
        solar radiation downwards, is the solar radiation that reaches a
        horizontal plane at the surface of the Earth. This parameter comprises
        both direct and diffuse solar radiation.
    direct_horizontal_irradiance_series : ndarray
        direct_horizontal_irradiance_series
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
    DiffuseSkyReflectedHorizontalIrradianceFromExternalData
        The diffuse radiant flux incident on a surface per unit area in W/m².

    Notes
    -----
        The corresponding ECMWF product variable is named `ssrd`.

    """
    diffuse_horizontal_irradiance_series = (
        global_horizontal_irradiance_series - direct_horizontal_irradiance_series
    ).astype(dtype=dtype)

    if diffuse_horizontal_irradiance_series.size == 1 and diffuse_horizontal_irradiance_series.shape == ():
        diffuse_horizontal_irradiance_series = numpy.array(
            [diffuse_horizontal_irradiance_series], dtype=dtype
        )
        single_value = float(diffuse_horizontal_irradiance_series)
        warning = (
            f"{exclamation_mark} The selected timestamp "
            + " matches the single value "
            + f"{single_value}"
        )
        logger.warning(warning)

    out_of_range, out_of_range_index = identify_values_out_of_range(
        series=diffuse_horizontal_irradiance_series,
        shape=global_horizontal_irradiance_series.shape,
        data_model=DiffuseSkyReflectedHorizontalIrradianceFromExternalData(),
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=diffuse_horizontal_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return DiffuseSkyReflectedHorizontalIrradianceFromExternalData(
        value=diffuse_horizontal_irradiance_series,
        out_of_range=out_of_range,
        out_of_range_index=out_of_range_index,
        global_horizontal_irradiance=global_horizontal_irradiance_series,
        direct_horizontal_irradiance=direct_horizontal_irradiance_series,
    )
