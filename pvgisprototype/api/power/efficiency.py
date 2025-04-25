from copy import deepcopy

import numpy as np
from devtools import debug
from numpy import log as numpy_log
from numpy import where

from pvgisprototype import (
    Efficiency,
    Irradiance,
    EffectiveIrradiance,
    SpectralFactorSeries,
    TemperatureSeries,
    WindSpeedSeries,
)
from pvgisprototype.api.irradiance.models import ModuleTemperatureAlgorithm
from pvgisprototype.api.performance.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.api.power.photovoltaic_module import (
    PhotovoltaicModuleModel,
    get_coefficients_for_photovoltaic_module,
)
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    CURRENT_AT_STANDARD_TEST_CONDITIONS,
    CURRENT_AT_STANDARD_TEST_CONDITIONS_TEMPERATURE_COEFFICIENT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    EFFECTIVE_IRRADIANCE_COLUMN_NAME,
    EFFECTIVE_IRRADIANCE_NAME,
    EFFICIENCY_COLUMN_NAME,
    EFFICIENCY_FACTOR_COLUMN_NAME,
    EFFICIENCY_NAME,
    FINGERPRINT_COLUMN_NAME,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    IRRADIANCE_COLUMN_NAME,
    IRRADIANCE_UNIT,
    LOG_LEVEL_DEFAULT,
    LOG_RELATIVE_IRRADIANCE_COLUMN_NAME,
    LOW_IRRADIANCE_COLUMN_NAME,
    NOT_AVAILABLE,
    POWER_AT_STANDARD_TEST_CONDITIONS,
    POWER_MODEL_COLUMN_NAME,
    RADIATION_CUTOFF_THRESHHOLD,
    RELATIVE_IRRADIANCE_COLUMN_NAME,
    SPECTRAL_EFFECT_COLUMN_NAME,
    SPECTRAL_EFFECT_PERCENTAGE_COLUMN_NAME,
    SPECTRAL_FACTOR_COLUMN_NAME,
    SPECTRAL_FACTOR_DEFAULT,
    SYMBOL_TEMPERATURE,
    TEMPERATURE_ADJUSTED_COLUMN_NAME,
    TEMPERATURE_ALGORITHM_COLUMN_NAME,
    TEMPERATURE_COLUMN_NAME,
    TEMPERATURE_DEFAULT,
    TEMPERATURE_DEVIATION_COLUMN_NAME,
    TITLE_KEY_NAME,
    UNITLESS,
    VERBOSE_LEVEL_DEFAULT,
    VOLTAGE_AT_STANDARD_TEST_CONDITIONS,
    VOLTAGE_AT_STANDARD_TEST_CONDITIONS_COEFFICIENT_1,
    VOLTAGE_AT_STANDARD_TEST_CONDITIONS_COEFFICIENT_2,
    VOLTAGE_AT_STANDARD_TEST_CONDITIONS_TEMPERATURE_COEFFICIENT,
    WIND_SPEED_COLUMN_NAME,
    WIND_SPEED_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.core.arrays import create_array
from pvgisprototype.core.hashing import generate_hash


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
        array_2 = np.pad(array_2, (0, length_difference), "constant")
    elif length_difference < 0:  # array 1 is 'shorter'
        array_1 = np.pad(array_1, (0, -length_difference), "constant")
    return array_1 + array_2


def adjust_temperature_series(
    irradiance_series: Irradiance,
    photovoltaic_module: PhotovoltaicModuleModel = PhotovoltaicModuleModel.CSI_FREE_STANDING,
    temperature_model: ModuleTemperatureAlgorithm = ModuleTemperatureAlgorithm.faiman,
    temperature_series: TemperatureSeries = TemperatureSeries(
        value=TEMPERATURE_DEFAULT, unit=SYMBOL_TEMPERATURE
    ),
    standard_test_temperature: float = TEMPERATURE_DEFAULT,
    wind_speed_series: WindSpeedSeries = np.array(WIND_SPEED_DEFAULT),
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
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

    return temperature_adjusted_series


def calculate_efficiency_factor_series(
    irradiance_series: Irradiance,  # effective irradiance
    radiation_cutoff_threshold: float = RADIATION_CUTOFF_THRESHHOLD,
    photovoltaic_module: PhotovoltaicModuleModel = PhotovoltaicModuleModel.CSI_FREE_STANDING,
    power_model: PhotovoltaicModulePerformanceModel = PhotovoltaicModulePerformanceModel.king,
    temperature_series: TemperatureSeries = TemperatureSeries(
        value=TEMPERATURE_DEFAULT
    ),
    standard_test_temperature: float = TEMPERATURE_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
) -> Efficiency:
    """Calculate the efficiency factor series specific to the photovoltaic
    module technology.

    Calculate the photovoltaic efficiency factor series for a solar irradiance
    component specific to the photovoltaic module technology, the photovoltaic
    power rating model and the (adjusted) temperature series. The implemented
    power rating model [0] is a variant of King's model [1, 2].

    References
    ----------

    [0] Thomas Huld, Gabi Friesen, Artur Skoczek, Robert P. Kenny, Tony Sample,
    Michael Field, Ewan D. Dunlop, A power-rating model for crystalline silicon
    PV modules, Solar Energy Materials and Solar Cells, Volume 95, Issue 12,
    2011, Pages 3359-3369, ISSN 0927-0248,
    https://doi.org/10.1016/j.solmat.2011.07.026.

    [1] D.L. King, J.A. Kratochvil, W.E. Boyson, W.I. Bower, Field experience
    with a new performance characterization procedure for photovoltaic arrays,
    in: Proceedings of the second World Conference and Exhibition on
    Photovoltaic Solar Energy Conversion, Vienna, 1998, pp. 1947–1952.

    [2] D.L. King, W.E. Boyson, J.A. Kratochvil, Photovoltaic Array
    Performance Model, SAND2004-3535, Sandia National Laboratories, 2004.

    """
    array_parameters = {
        "shape": irradiance_series.shape,
        "dtype": dtype,
        "init_method": "ones",
        "backend": array_backend,
    }
    efficiency_factor_series = create_array(**array_parameters)

    # Radiation cutoff handling
    relative_irradiance_series = (
        0.001 * irradiance_series
    )  # Conversion to Unit PV Power ?
    efficiency_factor_series = where(
        relative_irradiance_series <= radiation_cutoff_threshold,
        0,
        efficiency_factor_series,
    )
    radiation_cutoff_loss_series = efficiency_factor_series - 1
    radiation_cutoff_loss_percentage_series = 100 * radiation_cutoff_loss_series

    # low_irradiance_series = ((irradiance_series * efficiency_factor_series) - irradiance_series)
    # low_irradiance_percentage_series = 100 * where(
    #         irradiance_series != 0,
    #     ((irradiance_series * efficiency_factor_series) - irradiance_series) / irradiance_series,
    #     0
    # )

    photovoltaic_module_efficiency_coefficients = (
        get_coefficients_for_photovoltaic_module(photovoltaic_module)
    )
    # --------------------------------------------------- Is this safe ? -
    with np.errstate(divide="ignore", invalid="ignore"):
        log_relative_irradiance_series = where(
            relative_irradiance_series > 0,
            numpy_log(relative_irradiance_series),
            0,  # -numpy_inf,
        )
    temperature_deviation_series = temperature_series.value - standard_test_temperature

    # power output fom King (using PV eff coeffs for a specific tech) -  ... ?
    # difference between real conditions and stadard conditions -- should be close to zero

    if power_model.value == PhotovoltaicModulePerformanceModel.king:
        efficiency_factor_series = (
            photovoltaic_module_efficiency_coefficients[0]
            + log_relative_irradiance_series
            * (
                photovoltaic_module_efficiency_coefficients[1]
                + log_relative_irradiance_series
                * photovoltaic_module_efficiency_coefficients[2]
            )
            + temperature_deviation_series
            * (
                photovoltaic_module_efficiency_coefficients[3]
                + log_relative_irradiance_series
                * (
                    photovoltaic_module_efficiency_coefficients[4]
                    + log_relative_irradiance_series
                    * photovoltaic_module_efficiency_coefficients[5]
                )
                + photovoltaic_module_efficiency_coefficients[6]
                * temperature_deviation_series
            )
        )

        efficiency_factor_series /= photovoltaic_module_efficiency_coefficients[0]

    if (
        power_model.value == PhotovoltaicModulePerformanceModel.iv
    ):  # 'IV' Model ( Name ? )
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
        efficiency_factor_series = (
            current_series * voltage_series
        ) / POWER_AT_STANDARD_TEST_CONDITIONS

    # # Mask where efficiency is out of range [0, 1]
    # mask_invalid_efficiency = (efficiency_series < 0) | (efficiency_series > 1)
    # if np.any(mask_invalid_efficiency):
    #     return "Some calculated efficiencies are out of the expected range [0, 1]!"

    components_container = {
        "main": lambda: {
            TITLE_KEY_NAME: EFFICIENCY_NAME,
            EFFICIENCY_FACTOR_COLUMN_NAME: efficiency_factor_series,
        },  # if verbose > 0 else {},
        "more_extended": lambda: (
            {
                TITLE_KEY_NAME: EFFICIENCY_NAME + " & components",
                LOG_RELATIVE_IRRADIANCE_COLUMN_NAME: log_relative_irradiance_series,
                TEMPERATURE_DEVIATION_COLUMN_NAME: temperature_deviation_series,
            }
            if verbose > 2
            else {}
        ),
        "even_more_extended": lambda: (
            {
                RELATIVE_IRRADIANCE_COLUMN_NAME: relative_irradiance_series,
                "Radiation cutoff": radiation_cutoff_loss_percentage_series,
                LOW_IRRADIANCE_COLUMN_NAME: relative_irradiance_series
                <= radiation_cutoff_threshold,
                IRRADIANCE_COLUMN_NAME: irradiance_series,
            }
            if verbose > 3
            else {}
        ),
        "fingerprint": lambda: (
            {
                FINGERPRINT_COLUMN_NAME: generate_hash(efficiency_factor_series),
            }
            if fingerprint
            else {}
        ),
    }

    components = {}
    for _, component in components_container.items():
        components.update(component())

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=efficiency_factor_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return Efficiency(
        value=efficiency_factor_series,
        unit=UNITLESS,
        solar_positioning_algorithm=NOT_AVAILABLE,
        solar_timing_algorithm=NOT_AVAILABLE,
        # irradiance=irradiance_series,
        components=components,
        photovoltaic_module=photovoltaic_module,
        photovoltaic_module_efficiency_coefficients=photovoltaic_module_efficiency_coefficients,
        power_model=power_model,
        radiation_cutoff_threshold=radiation_cutoff_threshold,
    )


def calculate_spectrally_corrected_effective_irradiance(
    irradiance_series: Irradiance,
    spectral_factor_series: SpectralFactorSeries = SpectralFactorSeries(
        value=SPECTRAL_FACTOR_DEFAULT
    ),
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
):
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

    # components_container = {
    #     "main": lambda: {
    #         TITLE_KEY_NAME: EFFECTIVE_IRRADIANCE_NAME,
    #         EFFECTIVE_IRRADIANCE_COLUMN_NAME: effective_irradiance_series,
    #     },  # if verbose > 0 else {},
    #     "extended": lambda: (
    #         {
    #             SPECTRAL_FACTOR_COLUMN_NAME: spectral_factor_series.value,
    #             SPECTRAL_EFFECT_COLUMN_NAME: (
    #                 spectral_effect_series
    #                 if (verbose > 1 and spectral_effect_series.size > 0)
    #                 else NOT_AVAILABLE
    #             ),
    #             SPECTRAL_EFFECT_PERCENTAGE_COLUMN_NAME: (
    #                 spectral_effect_percentage_series
    #                 if (verbose > 1 and spectral_effect_percentage_series.size > 0)
    #                 else NOT_AVAILABLE
    #             ),
    #         }
    #         if verbose > 1
    #         else {}
    #     ),
    # }

    # components = {}
    # for _, component in components_container.items():
    #     components.update(component())

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


@log_function_call
def calculate_pv_efficiency_series(
    irradiance_series: Irradiance,
    photovoltaic_module: PhotovoltaicModuleModel = PhotovoltaicModuleModel.CSI_FREE_STANDING,
    power_model: PhotovoltaicModulePerformanceModel = PhotovoltaicModulePerformanceModel.king,
    spectral_factor_series: SpectralFactorSeries = SpectralFactorSeries(
        value=SPECTRAL_FACTOR_DEFAULT
    ),
    radiation_cutoff_threshold: float = RADIATION_CUTOFF_THRESHHOLD,
    temperature_model: ModuleTemperatureAlgorithm = ModuleTemperatureAlgorithm.faiman,
    temperature_series: TemperatureSeries = TemperatureSeries(
        value=TEMPERATURE_DEFAULT
    ),
    standard_test_temperature: float = TEMPERATURE_DEFAULT,
    wind_speed_series: WindSpeedSeries = np.array(WIND_SPEED_DEFAULT),
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
):
    """Calculate the photovoltaic (PV) module efficiency for a time series.

    Calculate the photovoltaic (PV) module efficiency for a time series based
    on solar irradiance and PV technology-specific efficiency coefficients, the
    spectral effect factor, temperature and wind speed including detailed
    gain/loss report.

    The spectral effect arises from differences between the sunlight spectrum
    and standardised artificial light spectrum.

    Parameters
    ----------
    irradiance_series : List[float]
        List of irradiance values over time.
    spectral_factor_series: SpectralFactorSeries
        List of spectral factors corresponding to the irradiance series.
    model_constants : List[float], optional
        List of coefficients for the efficiency model. Default is EFFICIENCY_MODEL_COEFFICIENTS_DEFAULT.
    temperature_model : ModuleTemperatureAlgorithm, optional
        Algorithm used for temperature correction. Default is ModuleTemperatureAlgorithm.faiman.
    temperature_series : np.ndarray, optional
        Numpy array of temperature values over time. Default is np.array(TEMPERATURE_DEFAULT).
    standard_test_temperature : float, optional
        Temperature used in standard test conditions. Default is TEMPERATURE_DEFAULT.
    wind_speed_series : np.ndarray, optional
        Numpy array of wind speed values over time. Default is np.array(WIND_SPEED_DEFAULT).
    power_model : PhotovoltaicModulePerformanceModel, optional
        Algorithm used for calculating PV module power. Default is PhotovoltaicModulePerformanceModel.king.
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

    """
    temperature_adjusted_series = adjust_temperature_series(
        irradiance_series=irradiance_series,  # without considering the spectral effect !
        photovoltaic_module=photovoltaic_module,
        temperature_series=temperature_series,
        wind_speed_series=wind_speed_series,
        standard_test_temperature=standard_test_temperature,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
        fingerprint=fingerprint,
    )
    # temperature_adjustment_series = temperature_adjusted_series.value - temperature_series.value
    # temperature_adjustment_percentage_series = 100 * where(
    #     temperature_series != 0,
    #     (temperature_adjusted_series.value - temperature_series.value)
    #     / (temperature_series.value),
    #     0,
    # )

    effective_irradiance_series = calculate_spectrally_corrected_effective_irradiance(
        irradiance_series=irradiance_series,
        spectral_factor_series=spectral_factor_series,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
        fingerprint=fingerprint,
    )
    efficiency_series = calculate_efficiency_factor_series(
        irradiance_series=effective_irradiance_series.value,
        radiation_cutoff_threshold=radiation_cutoff_threshold,
        photovoltaic_module=photovoltaic_module,
        power_model=power_model,
        temperature_series=temperature_adjusted_series,  # important !
        standard_test_temperature=standard_test_temperature,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
        fingerprint=fingerprint,
    )

    components_container = {
        "main": lambda: {
            TITLE_KEY_NAME: EFFICIENCY_NAME,
            EFFICIENCY_COLUMN_NAME: efficiency_series.value,
            POWER_MODEL_COLUMN_NAME: power_model.value,
            TEMPERATURE_ALGORITHM_COLUMN_NAME: temperature_model.value,
        },  # if verbose > 0 else {},
        "extended": lambda: (
            {
                # EFFICIENCY_MODEL_COEFFICIENT_COLUMN_NAME: efficiency_series.photovoltaic_module_efficiency_coefficients,
            }
            if verbose > 1
            else {}
        ),
        "power_model_results": lambda: (
            {
                EFFICIENCY_FACTOR_COLUMN_NAME: (
                    efficiency_series.value
                    if (
                        verbose > 1
                        and power_model.value == PhotovoltaicModulePerformanceModel.king
                    )
                    else NOT_AVAILABLE
                ),
                # DIRECT_CURRENT_COLUMN_NAME: current_series if (verbose > 1 and power_model.value == PhotovoltaicModulePerformanceModel.iv) else NOT_AVAILABLE, # FIXME UNBOUND current_series
                # VOLTAGE_COLUMN_NAME: voltage_series if (verbose > 1 and power_model.value == PhotovoltaicModulePerformanceModel.iv) else NOT_AVAILABLE, # FIXME UNBOUND current_series
            }
            if verbose > 1
            else {}
        ),
        "more_extended": lambda: (
            {
                TITLE_KEY_NAME: EFFICIENCY_NAME + " & components",
                TEMPERATURE_DEVIATION_COLUMN_NAME: efficiency_series.components[
                    TEMPERATURE_DEVIATION_COLUMN_NAME
                ],
            }
            if verbose > 2
            else {}
        ),
        "even_more_extended": lambda: (
            {
                IRRADIANCE_COLUMN_NAME: irradiance_series,
            }
            if verbose > 3
            else {}
        ),
        "and_even_more_extended": lambda: (
            {
                TEMPERATURE_ADJUSTED_COLUMN_NAME: temperature_adjusted_series.value,
                TEMPERATURE_COLUMN_NAME: temperature_series.value,
                WIND_SPEED_COLUMN_NAME: (
                    wind_speed_series.value
                    if wind_speed_series is not None
                    else NOT_AVAILABLE
                ),
            }
            if verbose > 4
            else {}
        ),
        "fingerprint": lambda: (
            {
                FINGERPRINT_COLUMN_NAME: generate_hash(efficiency_series.value),
            }
            if fingerprint
            else {}
        ),
    }

    components = efficiency_series.components
    for key, component in components_container.items():
        components.update(component())

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=efficiency_series.value,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return Efficiency(
        value=efficiency_series.value,
        unit=efficiency_series.unit,
        solar_positioning_algorithm=efficiency_series.solar_positioning_algorithm,
        solar_timing_algorithm=efficiency_series.solar_timing_algorithm,
        # elevation=efficiency_series.elevation,
        # surface_orientation=efficiency_series.surface_orientation,
        # surface_tilt=efficiency_series.surface_tilt,
        # irradiance=efficiency_series.irradiance,
        components=components,  # Above, did we "merge" correctly ?
        photovoltaic_module=efficiency_series.photovoltaic_module,
        photovoltaic_module_efficiency_coefficients=efficiency_series.photovoltaic_module_efficiency_coefficients,
        power_model=efficiency_series.power_model,
        radiation_cutoff_threshold=efficiency_series.radiation_cutoff_threshold,
        temperature_model=temperature_model,
    )
