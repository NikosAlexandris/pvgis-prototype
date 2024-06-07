from rich import print
from pvgisprototype import Efficiency
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from devtools import debug
from pvgisprototype.constants import EFFECTIVE_IRRADIANCE_COLUMN_NAME, EFFECTIVE_IRRADIANCE_NAME, FINGERPRINT_COLUMN_NAME, FINGERPRINT_FLAG_DEFAULT, IRRADIANCE_UNIT, LOG_LEVEL_DEFAULT, LOW_IRRADIANCE_COLUMN_NAME, SPECTRAL_EFFECT_COLUMN_NAME, SPECTRAL_EFFECT_PERCENTAGE_COLUMN_NAME, SPECTRAL_FACTOR_NAME, UNITLESS
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
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
from pvgisprototype.constants import EFFICIENCY_NAME
from pvgisprototype.constants import EFFICIENCY_COLUMN_NAME
from pvgisprototype.constants import EFFICIENCY_FACTOR_COLUMN_NAME
from pvgisprototype.constants import SPECTRAL_FACTOR_DEFAULT
from pvgisprototype.constants import SPECTRAL_FACTOR_COLUMN_NAME
from pvgisprototype.constants import DIRECT_CURRENT_COLUMN_NAME
from pvgisprototype.constants import VOLTAGE_COLUMN_NAME
from pvgisprototype.constants import POWER_MODEL_COLUMN_NAME
from pvgisprototype.constants import TEMPERATURE_ALGORITHM_COLUMN_NAME
from pvgisprototype.constants import IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import RELATIVE_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import LOG_RELATIVE_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import TEMPERATURE_COLUMN_NAME
from pvgisprototype.constants import TEMPERATURE_ADJUSTED_COLUMN_NAME
from pvgisprototype.constants import TEMPERATURE_DEVIATION_COLUMN_NAME
from pvgisprototype.constants import WIND_SPEED_DEFAULT
from pvgisprototype.constants import WIND_SPEED_COLUMN_NAME
from pvgisprototype.constants import NOT_AVAILABLE
from pvgisprototype.api.irradiance.models import ModuleTemperatureAlgorithm
from pvgisprototype.api.irradiance.models import PVModuleEfficiencyAlgorithm
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.validation.arrays import create_array
from pvgisprototype.validation.hashing import generate_hash
import numpy as np
from numpy import where
from numpy import log as numpy_log
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.power.photovoltaic_module import get_coefficients_for_photovoltaic_module
from copy import deepcopy
from pvgisprototype import Irradiance
from pvgisprototype import SpectralFactorSeries
from pvgisprototype import TemperatureSeries
from pvgisprototype import WindSpeedSeries


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


@log_function_call
def calculate_pv_efficiency_series(
    irradiance_series: List[float],
    spectral_factor_series: SpectralFactorSeries = SpectralFactorSeries(value=SPECTRAL_FACTOR_DEFAULT),
    temperature_series: TemperatureSeries = TemperatureSeries(value=TEMPERATURE_DEFAULT),
    photovoltaic_module: PhotovoltaicModuleModel = PhotovoltaicModuleModel.CSI_FREE_STANDING,
    standard_test_temperature: float = TEMPERATURE_DEFAULT,
    wind_speed_series: WindSpeedSeries = np.array(WIND_SPEED_DEFAULT),
    power_model: PVModuleEfficiencyAlgorithm = PVModuleEfficiencyAlgorithm.king,
    temperature_model: ModuleTemperatureAlgorithm = ModuleTemperatureAlgorithm.faiman,
    radiation_cutoff_threshold: float = RADIATION_CUTOFF_THRESHHOLD,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
    fingerprint: bool = False,
):
    """Calculate the time series efficiency of a photovoltaic (PV) module

    Calculate the time series efficiency of a photovoltaic (PV) module based on
    irradiance, temperature, and other factors.

    Parameters
    ----------
    irradiance_series : List[float]
        List of irradiance values over time.
    spectral_factor_series: SpectralFactorSeries
        List of spectral factors corresponding to the irradiance series.
    temperature_series : np.ndarray, optional
        Numpy array of temperature values over time. Default is np.array(TEMPERATURE_DEFAULT).
    model_constants : List[float], optional
        List of coefficients for the efficiency model. Default is EFFICIENCY_MODEL_COEFFICIENTS_DEFAULT.
    standard_test_temperature : float, optional
        Temperature used in standard test conditions. Default is TEMPERATURE_DEFAULT.
    wind_speed_series : np.ndarray, optional
        Numpy array of wind speed values over time. Default is np.array(WIND_SPEED_DEFAULT).
    power_model : PVModuleEfficiencyAlgorithm, optional
        Algorithm used for calculating PV module power. Default is PVModuleEfficiencyAlgorithm.king.
    temperature_model : ModuleTemperatureAlgorithm, optional
        Algorithm used for temperature correction. Default is ModuleTemperatureAlgorithm.faiman.
    radiation_cutoff_threshold : float, optional
        Minimum irradiance threshold for calculations. Default is RADIATION_CUTOFF_THRESHOLD.
    verbose : int, optional
        Level of verbosity for output data. Default is VERBOSE_LEVEL_DEFAULT.

    Returns
    -------
    efficiency_series : np.ndarray
        Array of calculated efficiency values for the PV module.
    results : dict, optional
        Dictionary containing detailed results and intermediate calculations. Provided when `verbose > 0`.

    Raises
    ------
    ValueError
        If an insufficient number of model constants is provided.

    Notes
    -----
    Currently, external time series of monthly spectral factors are centered in
    the beginning of the month and applied plus/minus half a month.

    Examples
    --------
    >>> calculate_pv_efficiency_series([1000, 950], [1.1, 1.05], temperature_series=np.array([25, 26]))
    # Returns efficiency series and possibly detailed results based on the verbose level.

    Notes
    -----
    This function is part of a larger system for analyzing PV module
    performance. It takes into account spectral factors, temperature
    variations, and wind speed, applying different models to calculate the
    efficiency of a PV module under varying conditions.

    """
    photovoltaic_module_efficiency_coefficients = (
        get_coefficients_for_photovoltaic_module(photovoltaic_module)
    )
    irradiance_series = np.array(irradiance_series)
    relative_irradiance_series = 0.001 * irradiance_series
    if np.any(spectral_factor_series):
        relative_irradiance_series *= spectral_factor_series.value
    log_relative_irradiance_series = np.where(
        relative_irradiance_series > 0, np.log(relative_irradiance_series), 0
    )

    negative_relative_irradiance = relative_irradiance_series <= radiation_cutoff_threshold
    efficiency_series = np.zeros_like(irradiance_series)
    efficiency_series[negative_relative_irradiance] = 0

    temperature_series_adjusted = deepcopy(temperature_series)  # Safer! ----

    # Adjust temperature based on conditions
    if temperature_model.value  == ModuleTemperatureAlgorithm.faiman:
        if wind_speed_series is not None:
            if len(photovoltaic_module_efficiency_coefficients) < 9:
                return "Insufficient number of model constants for Faiman model with wind speed."
            # temperature_series_adjusted = ... # safer !
            temperature_series_adjusted.value += irradiance_series / (
                photovoltaic_module_efficiency_coefficients[7] + photovoltaic_module_efficiency_coefficients[8] * wind_speed_series.value
            )
        else:
            if len(photovoltaic_module_efficiency_coefficients) < 8:
                return "Insufficient number of model constants for Faiman model."
            temperature_series_adjusted += photovoltaic_module_efficiency_coefficients[7] * irradiance_series

    temperature_deviation_series = temperature_series_adjusted.value - standard_test_temperature
    
    if power_model.value  == PVModuleEfficiencyAlgorithm.king:
        efficiency_factor_series = (
            photovoltaic_module_efficiency_coefficients[0]
            + log_relative_irradiance_series
            * (photovoltaic_module_efficiency_coefficients[1] + log_relative_irradiance_series * photovoltaic_module_efficiency_coefficients[2])
            + temperature_deviation_series
            * (
                photovoltaic_module_efficiency_coefficients[3]
                + log_relative_irradiance_series
                * (photovoltaic_module_efficiency_coefficients[4] + log_relative_irradiance_series * photovoltaic_module_efficiency_coefficients[5])
                + photovoltaic_module_efficiency_coefficients[6] * temperature_deviation_series
            )
        )
        efficiency_series = efficiency_factor_series / photovoltaic_module_efficiency_coefficients[0]

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

    components_container = {
        'main': lambda: {
            TITLE_KEY_NAME: EFFICIENCY,
            EFFICIENCY_COLUMN_NAME: efficiency_series,
        },# if verbose > 0 else {},

        'extended': lambda: {
            EFFICIENCY_MODEL_COEFFICIENT_COLUMN_NAME: photovoltaic_module_efficiency_coefficients[0],
            POWER_MODEL_COLUMN_NAME: power_model.value,
            TEMPERATURE_ALGORITHM_COLUMN_NAME: temperature_model.value,
        } if verbose > 1 else {},

        'power_model_results': lambda: {
            EFFICIENCY_FACTOR_COLUMN_NAME: efficiency_factor_series if (verbose > 1 and power_model.value == PVModuleEfficiencyAlgorithm.king) else NOT_AVAILABLE,
            DIRECT_CURRENT_COLUMN_NAME: current_series if (verbose > 1 and power_model.value == PVModuleEfficiencyAlgorithm.iv) else NOT_AVAILABLE,
            VOLTAGE_COLUMN_NAME: voltage_series if (verbose > 1 and power_model.value == PVModuleEfficiencyAlgorithm.iv) else NOT_AVAILABLE,
        } if verbose > 1 else {},

        'more_extended': lambda: {
            TITLE_KEY_NAME: EFFICIENCY + ' & components',
            LOG_RELATIVE_IRRADIANCE_COLUMN_NAME: log_relative_irradiance_series,
            TEMPERATURE_DEVIATION_COLUMN_NAME: temperature_deviation_series,
        } if verbose > 2 else {},

        'even_more_extended': lambda: {
            SPECTRAL_FACTOR_COLUMN_NAME: spectral_factor_series.value,
            RELATIVE_IRRADIANCE_COLUMN_NAME: relative_irradiance_series,
            NEGATIVE_RELATIVE_IRRADIANCE_COLUMN_NAME: negative_relative_irradiance,
            IRRADIANCE_COLUMN_NAME: irradiance_series,
        } if verbose > 3 else {},

        'and_even_more_extended': lambda: {
            TEMPERATURE_ADJUSTED_COLUMN_NAME: temperature_series_adjusted.value,
            TEMPERATURE_COLUMN_NAME: temperature_series.value,
            WIND_SPEED_COLUMN_NAME: wind_speed_series.value if wind_speed_series is not None else NOT_AVAILABLE,
        } if verbose > 4 else {},

        'fingerprint': lambda: {
            FINGERPRINT_COLUMN_NAME: generate_hash(efficiency_series),
        } if fingerprint else {},
    }

    components = {}
    for key, component in components_container.items():
        components.update(component())

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    if verbose > 0:
        return components
    
    log_data_fingerprint(
            data=efficiency_series,
            log_level=log,
            hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )
    return efficiency_series
