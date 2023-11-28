from devtools import debug
import typer
from typing import Annotated
from typing import List
from pvgisprototype.constants import TEMPERATURE_DEFAULT
from pvgisprototype.constants import RADIATION_CUTOFF_THRESHHOLD
from pvgisprototype.constants import POWER_AT_STANDARD_TEST_CONDITIONS
from pvgisprototype.constants import VOLTAGE_AT_STANDARD_TEST_CONDITIONS
from pvgisprototype.constants import VOLTAGE_AT_STANDARD_TEST_CONDITIONS_COEFFICIENT_1
from pvgisprototype.constants import VOLTAGE_AT_STANDARD_TEST_CONDITIONS_COEFFICIENT_2
from pvgisprototype.constants import CURRENT_AT_STANDARD_TEST_CONDITIONS
from pvgisprototype.constants import CURRENT_AT_STANDARD_TEST_CONDITIONS_TEMPERATURE_COEFFICIENT
from pvgisprototype.constants import VOLTAGE_AT_STANDARD_TEST_CONDITIONS_TEMPERATURE_COEFFICIENT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import TITLE_KEY_NAME
from pvgisprototype.constants import EFFICIENCY
from pvgisprototype.constants import EFFICIENCY_COLUMN_NAME
from pvgisprototype.constants import EFFICIENCY_FACTOR
from pvgisprototype.constants import EFFICIENCY_FACTOR_COLUMN_NAME
from pvgisprototype.constants import DIRECT_CURRENT_COLUMN_NAME
from pvgisprototype.constants import VOLTAGE_COLUMN_NAME
from pvgisprototype.constants import POWER_ALGORITHM_COLUMN_NAME
from pvgisprototype.constants import TEMPERATURE_ALGORITHM_COLUMN_NAME
from pvgisprototype.constants import IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import RELATIVE_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import LOG_RELATIVE_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import NEGATIVE_RELATIVE_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import TEMPERATURE_COLUMN_NAME
from pvgisprototype.constants import TEMPERATURE_ADJUSTED_COLUMN_NAME
from pvgisprototype.constants import TEMPERATURE_DEVIATION_COLUMN_NAME
from pvgisprototype.constants import WIND_SPEED_DEFAULT
from pvgisprototype.constants import WIND_SPEED_COLUMN_NAME
from pvgisprototype.constants import NOT_AVAILABLE
from pvgisprototype.cli.typer_parameters import typer_option_verbose
from pvgisprototype.api.irradiance.models import ModuleTemperatureAlgorithm
from pvgisprototype.api.irradiance.models import PVModuleEfficiencyAlgorithm
from pvgisprototype.api.irradiance.efficiency_coefficients import STANDARD_EFFICIENCY_MODEL_COEFFICIENTS
from pvgisprototype.api.irradiance.efficiency_coefficients import EFFICIENCY_MODEL_COEFFICIENT
from pvgisprototype.api.irradiance.efficiency_coefficients import EFFICIENCY_MODEL_COEFFICIENT_COLUMN_NAME
from pvgisprototype.api.irradiance.efficiency_coefficients import EFFICIENCY_MODEL_COEFFICIENTS
from pvgisprototype.api.irradiance.efficiency_coefficients import EFFICIENCY_MODEL_COEFFICIENTS_DEFAULT
import numpy as np


def add_unequal_arrays(array_1, array_2):
    """
    Add two NumPy arrays of unequal lengths by padding the shorter array with zeros.

    Parameters
    ----------
    array_1 : numpy.ndarray
        The first array to be added.
    array_2 : numpy.ndarray
        The second array to be added.

    Returns
    -------
    numpy.ndarray
        The resulting array after addition. The length of the resulting array
        will be the same as the longest of the two input arrays.

    Examples
    --------
    >>> import numpy as np
    >>> array_1 = np.array([1, 2, 3])
    >>> array_2 = np.array([1, 2])
    >>> add_unequal_arrays(array_1, array_2)
    array([2, 4, 3])
    """
    length_difference = len(array_1) - len(array_2)
    if length_difference > 0:  # array 2 is 'shorter'
        array_2 = np.pad(array_2, (0, length_difference), 'constant')
    elif length_difference < 0:  # array 1 is 'shorter'
        array_1 = np.pad(array_1, (0, -length_difference), 'constant')
    return array_1 + array_2


def calculate_pv_efficiency_time_series(
    irradiance_series: List[float],
    temperature_series: np.ndarray = np.array(TEMPERATURE_DEFAULT),
    model_constants: List[float] = EFFICIENCY_MODEL_COEFFICIENTS_DEFAULT,
    standard_test_temperature: float = TEMPERATURE_DEFAULT,
    wind_speed_series: np.ndarray = np.array(WIND_SPEED_DEFAULT),
    power_model: PVModuleEfficiencyAlgorithm = PVModuleEfficiencyAlgorithm.king,
    temperature_model: ModuleTemperatureAlgorithm = ModuleTemperatureAlgorithm.faiman,
    radiation_cutoff_threshold: float = RADIATION_CUTOFF_THRESHHOLD,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
):
    model_constants = np.array(EFFICIENCY_MODEL_COEFFICIENTS['cSi']['Free standing'])
    # or add standard plus selected?
    # model_constants = np.array(STANDARD_EFFICIENCY_MODEL_COEFFICIENTS)
    # selected_model_constants = np.array(EFFICIENCY_MODEL_COEFFICIENTS['cSi']['Free standing'])
    # model_constants = add_unequal_arrays(model_constants, selected_model_constants) 

    if len(model_constants) < 7:
        raise ValueError("Insufficient number of model constants!")
    
    irradiance_series = np.array(irradiance_series)
    relative_irradiance_series = 0.001 * irradiance_series
    log_relative_irradiance_series = np.log(relative_irradiance_series)

    negative_relative_irradiance = relative_irradiance_series <= radiation_cutoff_threshold
    efficiency_series = np.zeros_like(irradiance_series)
    efficiency_series[negative_relative_irradiance] = 0

    # temperature_series = temperature_series.value  # the array in the custom data class TemperatureSeries
    # wind_speed_series = wind_speed_series.value

    # temperature_series_adjusted = np.copy(temperature_series)  # Safer! ----

    # Adjust temperature based on conditions
    if temperature_model.value  == ModuleTemperatureAlgorithm.faiman:
        if wind_speed_series is not None:
            if len(model_constants) < 9:
                return "Insufficient number of model constants for Faiman model with wind speed."
            # temperature_series_adjusted = ... # safer !
            temperature_series.value += irradiance_series / (
                model_constants[7] + model_constants[8] * wind_speed_series.value
            )
        else:
            if len(model_constants) < 8:
                return "Insufficient number of model constants for Faiman model."
            # temperature_series_adjusted = ...  # safer !
            temperature_series += model_constants[7] * irradiance_series
        temperature_series_adjusted = temperature_series  # for the output dictionary!

    temperature_deviation_series = temperature_series.value - standard_test_temperature
    
    if power_model.value  == PVModuleEfficiencyAlgorithm.king:
        # temperature_deviation_series = temperature_series_adjusted - standard_test_temperature
        efficiency_factor_series = (
            model_constants[0]
            + log_relative_irradiance_series
            * (model_constants[1] + log_relative_irradiance_series * model_constants[2])
            + temperature_deviation_series
            * (
                model_constants[3]
                + log_relative_irradiance_series
                * (model_constants[4] + log_relative_irradiance_series * model_constants[5])
                + model_constants[6] * temperature_deviation_series
            )
        )
        efficiency_series = efficiency_factor_series / model_constants[0]

    if power_model.value == PVModuleEfficiencyAlgorithm.iv:  # 'IV' Model ( Name ? )
        current_series = (
            CURRENT_AT_STANDARD_TEST_CONDITIONS
            + CURRENT_AT_STANDARD_TEST_CONDITIONS_TEMPERATURE_COEFFICIENT
            * temperature_deviation_series
        )
        voltage_series = (
            VOLTAGE_AT_STANDARD_TEST_CONDITIONS
            + VOLTAGE_AT_STANDARD_TEST_CONDITIONS_COEFFICIENT_1
            * log_relative_irradiance_series
            + VOLTAGE_AT_STANDARD_TEST_CONDITIONS_COEFFICIENT_2
            * log_relative_irradiance_series**2
            + VOLTAGE_AT_STANDARD_TEST_CONDITIONS_TEMPERATURE_COEFFICIENT
            * temperature_deviation_series
        )
        efficiency_series = (
            current_series * voltage_series
        ) / POWER_AT_STANDARD_TEST_CONDITIONS

    # # Mask where efficiency is out of range [0, 1]
    # mask_invalid_efficiency = (efficiency_series < 0) | (efficiency_series > 1)

    # if np.any(mask_invalid_efficiency):
    #     return "Some calculated efficiencies are out of the expected range [0, 1]!"

    if verbose > 0: results = {
            TITLE_KEY_NAME: EFFICIENCY,
            EFFICIENCY_COLUMN_NAME: efficiency_series,
        }

    if verbose > 1:
        if power_model.value == PVModuleEfficiencyAlgorithm.king:
            power_model_results = {
            EFFICIENCY_FACTOR_COLUMN_NAME: efficiency_factor_series if power_model.value == PVModuleEfficiencyAlgorithm.king else NOT_AVAILABLE,
            }
        if power_model.value == PVModuleEfficiencyAlgorithm.iv:
            power_model_results = {
            DIRECT_CURRENT_COLUMN_NAME: current_series,
            VOLTAGE_COLUMN_NAME: voltage_series,
            }
        extended_results = {
            EFFICIENCY_MODEL_COEFFICIENT_COLUMN_NAME: model_constants[0],
            POWER_ALGORITHM_COLUMN_NAME: power_model.value,
            TEMPERATURE_ALGORITHM_COLUMN_NAME: temperature_model.value,
        }
        results = results | power_model_results | extended_results

    if verbose > 2:
        more_extended_results = {
            LOG_RELATIVE_IRRADIANCE_COLUMN_NAME: log_relative_irradiance_series,
            TEMPERATURE_DEVIATION_COLUMN_NAME: temperature_deviation_series,
        }
        results = results | more_extended_results
        results[TITLE_KEY_NAME] += ' & components'

    if verbose > 3:
        even_more_extended_results = {
            RELATIVE_IRRADIANCE_COLUMN_NAME: relative_irradiance_series,
            NEGATIVE_RELATIVE_IRRADIANCE_COLUMN_NAME: negative_relative_irradiance,
            IRRADIANCE_COLUMN_NAME: irradiance_series,
        }
        results = results | even_more_extended_results

    if verbose > 4:
        even_even_more_extended_results = {
            TEMPERATURE_ADJUSTED_COLUMN_NAME: temperature_series_adjusted.value,
            TEMPERATURE_COLUMN_NAME: temperature_series.value,
            WIND_SPEED_COLUMN_NAME: wind_speed_series.value if wind_speed_series is not None else NOT_AVAILABLE,
        }
        results = results | even_even_more_extended_results
    
    if verbose > 0:
        return results 
    
    return efficiency_series
