from copy import deepcopy

import numpy as np
from devtools import debug

from pvgisprototype import (
    InclinedIrradiance,
    TemperatureSeries,
    WindSpeedSeries,
)
from pvgisprototype.algorithms.faiman.temperature import adjust_temperature_series_faiman
from pvgisprototype.api.irradiance.models import ModuleTemperatureAlgorithm
# from pvgisprototype.algorithms.huld.photovoltaic_module import (
from pvgisprototype.algorithms.huld.photovoltaic_module import (
    PhotovoltaicModuleModel,
    get_coefficients_for_photovoltaic_module,
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
def adjust_temperature_series(
    irradiance_series: InclinedIrradiance,
    photovoltaic_module: PhotovoltaicModuleModel = PhotovoltaicModuleModel.CSI_FREE_STANDING,
    temperature_model: ModuleTemperatureAlgorithm = ModuleTemperatureAlgorithm.faiman,
    temperature_series: TemperatureSeries = TemperatureSeries().average_air_temperature,
    wind_speed_series: WindSpeedSeries = np.array(WIND_SPEED_DEFAULT),
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
):
    """
    Note that the irradiance series input should be the _uncorrected_
    irradiance, i.e. not adjusted for spectral effects.
    """
    photovoltaic_module_efficiency_coefficients = (
        get_coefficients_for_photovoltaic_module(photovoltaic_module)
    )
    temperature_adjusted_series = deepcopy(temperature_series)  # Safe !
    if temperature_model.value == ModuleTemperatureAlgorithm.faiman:
        temperature_adjusted_series = adjust_temperature_series_faiman(
                temperature_series=temperature_series,
                wind_speed_series=wind_speed_series,
                photovoltaic_module_efficiency_coefficients=photovoltaic_module_efficiency_coefficients,
                irradiance_series=irradiance_series,
                )

    # temperature_adjustment_series = temperature_adjusted_series.value - temperature_series.value
    # temperature_adjustment_percentage_series = 100 * where(
    #     temperature_series != 0,
    #     (temperature_adjusted_series.value - temperature_series.value)
    #     / (temperature_series.value),
    #     0,
    # )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=temperature_adjusted_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return temperature_adjusted_series
