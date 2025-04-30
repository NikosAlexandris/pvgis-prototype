import numpy as np
from devtools import debug
from pvgisprototype import (
    Efficiency,
    InclinedIrradiance,
    SpectralFactorSeries,
    TemperatureSeries,
    WindSpeedSeries,
)
from pvgisprototype.api.irradiance.effective import calculate_spectrally_corrected_effective_irradiance
from pvgisprototype.api.irradiance.models import ModuleTemperatureAlgorithm
# from pvgisprototype.api.performance.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.algorithms.huld.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.algorithms.huld.efficiency_factor import calculate_efficiency_factor_series
# from pvgisprototype.api.power.photovoltaic_module import (
from pvgisprototype.algorithms.huld.photovoltaic_module import (
    PhotovoltaicModuleModel,
)
from pvgisprototype.api.power.temperature import adjust_temperature_series
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    RADIATION_CUTOFF_THRESHHOLD,
    SPECTRAL_FACTOR_DEFAULT,
    TEMPERATURE_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    WIND_SPEED_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call


@log_function_call
def calculate_photovoltaic_efficiency_series(
    irradiance_series: InclinedIrradiance,
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
) -> Efficiency:
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
        temperature_model=temperature_model,
        temperature_series=temperature_series,
        wind_speed_series=wind_speed_series,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
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

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=efficiency_series.value,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return Efficiency(
        value=efficiency_series.value,
        effective_irradiance=effective_irradiance_series,
        temperature_adjusted_series=temperature_adjusted_series,
        # photovoltaic_module=efficiency_series.photovoltaic_module,
        # photovoltaic_module_efficiency_coefficients=efficiency_series.photovoltaic_module_efficiency_coefficients,
        # power_model=efficiency_series.power_model,
        # radiation_cutoff_threshold=efficiency_series.radiation_cutoff_threshold,
        # temperature_model=temperature_model,
    )
