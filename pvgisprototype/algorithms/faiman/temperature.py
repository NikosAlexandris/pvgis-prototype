from copy import deepcopy

import numpy as np
from devtools import debug

from pvgisprototype import (
    InclinedIrradiance,
    TemperatureSeries,
    WindSpeedSeries,
)
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    WIND_SPEED_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call


@log_function_call
def adjust_temperature_series_faiman(
    irradiance_series: InclinedIrradiance,
    photovoltaic_module_efficiency_coefficients,
    temperature_series: TemperatureSeries = TemperatureSeries().average_air_temperature,
    wind_speed_series: WindSpeedSeries = np.array(WIND_SPEED_DEFAULT),
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
):
    """
    """
    temperature_adjusted_series = deepcopy(temperature_series)  # Safe !
    if wind_speed_series is not None:
        expected_number_of_coefficients = 9
        if (
            len(photovoltaic_module_efficiency_coefficients)
            < expected_number_of_coefficients
        ):
            return "Insufficient number of model constants for Faiman model with wind speed."
        # temperature_adjusted_series = ... # safer !
        temperature_adjusted_series.value += irradiance_series / (
            photovoltaic_module_efficiency_coefficients[7]
            + photovoltaic_module_efficiency_coefficients[8]
            * wind_speed_series.value
        )
    else:
        expected_number_of_coefficients = 8
        if (
            len(photovoltaic_module_efficiency_coefficients)
            < expected_number_of_coefficients
        ):
            return "Insufficient number of model constants for Faiman model."
        temperature_adjusted_series += (
            photovoltaic_module_efficiency_coefficients[7] * irradiance_series
        )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=temperature_adjusted_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return temperature_adjusted_series
