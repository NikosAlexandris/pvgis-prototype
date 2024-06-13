from pandas import DatetimeIndex
import pandas
from pvgisprototype.api.utilities.conversions import round_float_values
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT, DATA_TYPE_DEFAULT, EFFECTIVE_IRRADIANCE_NAME, ENERGY_NAME_WITH_SYMBOL, GLOBAL_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME, IN_PLANE_IRRADIANCE, IRRADIANCE_AFTER_REFLECTIVITY, IRRADIANCE_UNIT, IRRADIANCE_UNIT_K, NET_EFFECT, PEAK_POWER_COLUMN_NAME, PHOTOVOLTAIC_ENERGY_UNIT, PHOTOVOLTAIC_POWER_COLUMN_NAME, PHOTOVOLTAIC_POWER_UNIT, PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME, POWER_MODEL_COLUMN_NAME, POWER_NAME_WITH_SYMBOL, POWER_UNIT_K, REFLECTIVITY, REFLECTIVITY_COLUMN_NAME, SPECTRAL_EFFECT, SPECTRAL_EFFECT_COLUMN_NAME, SYSTEM_EFFICIENCY_COLUMN_NAME, SYSTEM_LOSS, TEMPERATURE_AND_LOW_IRRADIANCE_COLUMN_NAME
import numpy
from numpy import where


def calculate_statistics(
    series,
    timestamps,
    frequency,
    reference_series,
    rounding_places=None,
    dtype=DATA_TYPE_DEFAULT,
    array_backend=ARRAY_BACKEND_DEFAULT,
):
    """Calculate the sum, mean, standard deviation of a series based on a
    specified frequency and its percentage relative to a reference series.
    """
    pandas_series = pandas.Series(series, timestamps)
    resampled = pandas_series.resample(frequency)
    total = resampled.sum().sum()
    if isinstance(total, numpy.ndarray):
        total = total.astype(dtype)
    percentage = (total / reference_series * 100) if reference_series != 0 else 0
    if isinstance(percentage, numpy.ndarray):
        percentage.astype(dtype)
    if rounding_places is not None:
        total = round_float_values(total, rounding_places)
        percentage = round_float_values(percentage, rounding_places)
    mean = resampled.mean().mean()
    std_dev = resampled.std().mean()  # Mean of standard deviations over the period
    return total, mean, std_dev, percentage


def calculate_mean_of_series_per_time_unit(
    series: numpy.ndarray,
    timestamps: DatetimeIndex,
    frequency: str,
    ):
    """
    """
    pandas_series = pandas.Series(series, index=timestamps)
    return pandas_series.resample(frequency).sum().mean()


def kilofy_unit(value, unit="W", threshold=1000):
    """ Converts the unit of a given value to its kilo-equivalent if the
    absolute value is greater than or equal to 1000.

    Parameters
    ----------
    value : float
        The numerical value to potentially convert.
    unit : str
        The current unit of the value, defaulting to 'W' (Watts).

    Returns
    -------
    tuple :
        The converted value and its unit. If the value is 1000 or more, it
        converts the value and changes the unit to 'kW' (kilowatts).

    Examples
    --------
    >>> kilofy_unit(1500, "W", 1000)
    (1.5, "kW")
    >>> kilofy_unit(500, "W", 1000)
    (500, "W")
    """
    if value is not None:
        if abs(value) >= threshold and unit == IRRADIANCE_UNIT:
            return value / 1000, IRRADIANCE_UNIT_K  # update to kilo
        if abs(value) >= threshold and unit == POWER_UNIT_K:
            return value / 1000, POWER_UNIT_K  # update to kilo
    return value, unit


def analyse_photovoltaic_performance(
    dictionary,
    timestamps: DatetimeIndex,
    frequency: str,
    rounding_places=1,
    dtype=DATA_TYPE_DEFAULT,
    array_backend=ARRAY_BACKEND_DEFAULT,
):
    """Analyze the photovoltaic performance from time-series data.

    Parameters
    ----------
    dictionary :
		Data containing time-series for various PV metrics.
    timestamps :
		Timestamps corresponding to the data points.
    frequency :
		Resampling frequency for mean calculations.
    rounding_places :
		Decimal places for rounding results.
    dtype :
		Data type for numerical calculations.

    Returns
    -------
    A dictionary with performance analysis results.

    Notes
    -----
    Workflow

    In-Plane Irradiance                           

    ┌───────────┘
    │ Reflectivity Loss             
    └┐─────────────────
     ▼

    Irradiance After Reflectivity Loss            

    ┌───────────┘
    │ Spectral Effect               
    └┐───────────────
     ▼

    Effective Irradiance                          

    ┌───────────┘
    │ Temp. & Low Irradiance Coefficients 
    └┐───────────────────────────────────
     ▼

    Effective Power                                         

    ┌───────────┘
    │ System Loss                   
    └┐───────────
     ▼

    Photovoltaic Power Output

    ------------
    Total Change
    ------------

    """
        
    # In-Plane irradiance (before changes)
    # ------------------------------------------------------------------------
    # To Do : In-Plane "Irradiation" ?
    # Add Standard Deviation in kWh ? Monthly, Yearly ?
    # ------------------------------------------------------------------------
    inclined_irradiance_series = dictionary.get(
        GLOBAL_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME, numpy.array([])
    )
    inclined_irradiance, inclined_irradiance_mean, inclined_irradiance_std, _ = calculate_statistics(
        inclined_irradiance_series,
        timestamps,
        frequency,
        1,
        rounding_places,
    )

    # Reflectivity

    reflectivity_series = dictionary.get(REFLECTIVITY_COLUMN_NAME, numpy.array([]))
    reflectivity_change, reflectivity_change_mean, reflectivity_change_std, reflectivity_change_percentage = calculate_statistics(
            reflectivity_series,
        timestamps,
        frequency,
            inclined_irradiance,
            rounding_places,
    )

    # After reflectivity

    irradiance_after_reflectivity = inclined_irradiance + reflectivity_change
    irradiance_after_reflectivity_mean = calculate_mean_of_series_per_time_unit(
        inclined_irradiance_series + reflectivity_series,
        timestamps=timestamps,
        frequency=frequency,
    )

    # Spectral effect

    spectral_effect_series = dictionary.get(SPECTRAL_EFFECT_COLUMN_NAME, numpy.array([]))
    spectral_effect, spectral_effect_mean, spectral_effect_std, spectral_effect_percentage = calculate_statistics(
        spectral_effect_series, 
        timestamps,
        frequency,
        irradiance_after_reflectivity,
        rounding_places,
    )

    effective_irradiance = irradiance_after_reflectivity + spectral_effect
    effective_irradiance_percentage = (
        (effective_irradiance / inclined_irradiance * 100)
        if inclined_irradiance != 0
        else 0
    )
    effective_irradiance_mean = (
        irradiance_after_reflectivity_mean + spectral_effect_mean
    )
    effective_irradiance_change = effective_irradiance - inclined_irradiance
    with numpy.errstate(divide="ignore", invalid="ignore"):  # if irradiance == 0
        effective_irradiance_change_percentage = where(
            inclined_irradiance != 0,
            100 * effective_irradiance_change / inclined_irradiance,
            0,
        )
    # "Effective" Power without System Loss
    photovoltaic_power_without_system_loss_series = dictionary.get(
        PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME, numpy.array([])
    )
    photovoltaic_power_without_system_loss, photovoltaic_power_without_system_loss_mean, photovoltaic_power_without_system_loss_std, _ = calculate_statistics(
        photovoltaic_power_without_system_loss_series,
        timestamps,
        frequency,
        reference_series=1,
        rounding_places=rounding_places,
        dtype=dtype,
        array_backend=array_backend,
    )

    # Temperature & Low Irradiance
    photovoltaic_power_rating_model = dictionary.get(POWER_MODEL_COLUMN_NAME, None)
    temperature_and_low_irradiance_change = (
        photovoltaic_power_without_system_loss - effective_irradiance
    )
    temperature_and_low_irradiance_change_mean = (
        photovoltaic_power_without_system_loss_mean - effective_irradiance_mean
    )
    with numpy.errstate(divide="ignore", invalid="ignore"):  # if irradiance == 0
        temperature_and_low_irradiance_change_percentage = where(
            effective_irradiance != 0,
            100 * temperature_and_low_irradiance_change / effective_irradiance,
            0,
        )

    # System efficiency
    system_efficiency_series = dictionary.get(SYSTEM_EFFICIENCY_COLUMN_NAME, None)
    system_efficiency = numpy.nanmedian(system_efficiency_series).astype(
        dtype
    )  # Just in case we ever get time series of `system_efficiency` !
    system_efficiency_change = (
        photovoltaic_power_without_system_loss * system_efficiency
        - photovoltaic_power_without_system_loss
    )
    system_efficiency_change_mean = calculate_mean_of_series_per_time_unit(
        photovoltaic_power_without_system_loss_mean * system_efficiency
        - photovoltaic_power_without_system_loss_mean,
        timestamps=timestamps,
        frequency=frequency,
    )
    with numpy.errstate(divide="ignore", invalid="ignore"):  # if irradiance == 0
        system_efficiency_change_percentage = where(
            photovoltaic_power_without_system_loss != 0,
            100 * system_efficiency_change / photovoltaic_power_without_system_loss,
            0,
        )

    # Photovoltaic Power
    photovoltaic_power_series = dictionary.get(
        PHOTOVOLTAIC_POWER_COLUMN_NAME, numpy.array([])
    )
    photovoltaic_power, photovoltaic_power_mean, photovoltaic_power_std, _ = calculate_statistics(
        photovoltaic_power_series,
        timestamps,
        frequency,
        1,
        rounding_places,
    )
    peak_power = dictionary.get(PEAK_POWER_COLUMN_NAME, numpy.array([]))
    photovoltaic_energy_mean = photovoltaic_power_mean * peak_power

    # From PVGIS v5.2 --------------------------------------------------------
    # 'SD_m': annual[i]['y_dc_var'] * data['peakpower'] / 12,
    # 'SD_y': annual[i]['y_dc_var'] * data['peakpower'],
    # ------------------------------------------------------------------------

    # Total change
    total_change = photovoltaic_power - inclined_irradiance
    total_change_mean = photovoltaic_power_mean - inclined_irradiance_mean
    with numpy.errstate(divide="ignore", invalid="ignore"):  # if irradiance == 0
        total_change_percentage = where(
            inclined_irradiance != 0, total_change / inclined_irradiance * 100, 0
        )

    # Handle units

    inclined_irradiance, inclined_irradiance_unit = kilofy_unit(
        inclined_irradiance, IRRADIANCE_UNIT
    )
    inclined_irradiance_mean, inclined_irradiance_mean_unit = kilofy_unit(
        inclined_irradiance_mean, IRRADIANCE_UNIT
    )

    reflectivity_change, reflectivity_change_unit = kilofy_unit(
        reflectivity_change, IRRADIANCE_UNIT
    )
    reflectivity_change_mean, reflectivity_change_mean_unit = kilofy_unit(
        reflectivity_change_mean, IRRADIANCE_UNIT
    )

    irradiance_after_reflectivity, irradiance_after_reflectivity_unit = kilofy_unit(
        irradiance_after_reflectivity, IRRADIANCE_UNIT
    )
    irradiance_after_reflectivity_mean, irradiance_after_reflectivity_mean_unit = (
        kilofy_unit(irradiance_after_reflectivity_mean, IRRADIANCE_UNIT)
    )

    spectral_effect, spectral_effect_unit = kilofy_unit(
        spectral_effect, IRRADIANCE_UNIT
    )
    spectral_effect_mean, spectral_effect_mean_unit = kilofy_unit(
        spectral_effect_mean, IRRADIANCE_UNIT
    )

    effective_irradiance, effective_irradiance_unit = kilofy_unit(
        effective_irradiance, IRRADIANCE_UNIT
    )
    effective_irradiance_mean, effective_irradiance_mean_unit = kilofy_unit(
        effective_irradiance_mean, IRRADIANCE_UNIT
    )

    (
        photovoltaic_power_without_system_loss,
        photovoltaic_power_without_system_loss_unit,
    ) = kilofy_unit(photovoltaic_power_without_system_loss, PHOTOVOLTAIC_POWER_UNIT)
    (
        photovoltaic_power_without_system_loss_mean,
        photovoltaic_power_without_system_loss_mean_unit,
    ) = kilofy_unit(
        photovoltaic_power_without_system_loss_mean, PHOTOVOLTAIC_POWER_UNIT
    )

    (
        temperature_and_low_irradiance_change,
        temperature_and_low_irradiance_change_unit,
    ) = kilofy_unit(temperature_and_low_irradiance_change, IRRADIANCE_UNIT)
    (
        temperature_and_low_irradiance_change_mean,
        temperature_and_low_irradiance_change_mean_unit,
    ) = kilofy_unit(temperature_and_low_irradiance_change_mean, IRRADIANCE_UNIT)

    system_efficiency_change, system_efficiency_change_unit = kilofy_unit(
        system_efficiency_change, PHOTOVOLTAIC_POWER_UNIT
    )
    system_efficiency_change_mean, system_efficiency_change_mean_unit = kilofy_unit(
        system_efficiency_change_mean, PHOTOVOLTAIC_POWER_UNIT
    )

    photovoltaic_power, photovoltaic_power_unit = kilofy_unit(
        photovoltaic_power, PHOTOVOLTAIC_POWER_UNIT
    )
    photovoltaic_power_mean, photovoltaic_power_mean_unit = kilofy_unit(
        photovoltaic_power_mean, PHOTOVOLTAIC_POWER_UNIT
    )

    total_change, total_change_unit = kilofy_unit(total_change, IRRADIANCE_UNIT)
    total_change_mean, total_change_mean_unit = kilofy_unit(
        total_change_mean, IRRADIANCE_UNIT
    )

    return {
        f"[bold purple]{IN_PLANE_IRRADIANCE}": (            # Label
            (inclined_irradiance, "bold purple"),           # Value, Style
            (inclined_irradiance_unit, "purple"),
            (inclined_irradiance_mean, "bold purple"),      # Mean Value, Style
            (inclined_irradiance_mean_unit, "purple"),
            inclined_irradiance_std,
            None,                                           # %
            "bold",                                         # Style for
            None,# f"100 {GLOBAL_IRRADIANCE_NAME}",         # % of (which) Quantity
            inclined_irradiance_series,                     # input series
            None,                                           # source
        ),
        f"{REFLECTIVITY}": (
            (reflectivity_change, "magenta"),
            (reflectivity_change_unit, "cyan dim"),
            (reflectivity_change_mean, "magenta"),
            (reflectivity_change_mean_unit, "cyan dim"),
            reflectivity_change_std,
            reflectivity_change_percentage,
            "bold",
            IN_PLANE_IRRADIANCE,
            reflectivity_series,
            None,
        ),
        f"[white dim]{IRRADIANCE_AFTER_REFLECTIVITY}": (
            (irradiance_after_reflectivity, "white dim"),
            (irradiance_after_reflectivity_unit, "white dim"),
            (irradiance_after_reflectivity_mean, "white dim"),
            (irradiance_after_reflectivity_mean_unit, "white dim"),
            None,
            None,
            "bold",
            IN_PLANE_IRRADIANCE,
            numpy.array([], dtype=dtype),
            None,
        ),
        f"{SPECTRAL_EFFECT}": (
            (spectral_effect, "magenta"),
            (spectral_effect_unit, "cyan dim"),
            (spectral_effect_mean, "magenta"),
            (spectral_effect_mean_unit, "cyan dim"),
            spectral_effect_std,
            spectral_effect_percentage,
            "bold",
            IN_PLANE_IRRADIANCE,
            spectral_effect_series,
            None,
        ),
        f"[white dim]{EFFECTIVE_IRRADIANCE_NAME}": (
            (effective_irradiance, "white dim"),
            (effective_irradiance_unit, "white dim"),
            (effective_irradiance_mean, "white dim"),
            (effective_irradiance_mean_unit, "white dim"),
            None,
            None,
            "bold",
            None,
            numpy.array([]),
            None,
        ),
        f"{TEMPERATURE_AND_LOW_IRRADIANCE_COLUMN_NAME}": (
            (temperature_and_low_irradiance_change, "magenta"),
            (temperature_and_low_irradiance_change_unit, "cyan dim"),
            (temperature_and_low_irradiance_change_mean, "magenta"),
            (temperature_and_low_irradiance_change_mean_unit, "cyan dim"),
            None,
            temperature_and_low_irradiance_change_percentage,
            "bold",
            EFFECTIVE_IRRADIANCE_NAME,
            numpy.array([]),
            None,
        ),
        f"[white dim]{PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME}": (
            (photovoltaic_power_without_system_loss, "white dim"),
            (photovoltaic_power_without_system_loss_unit, "white dim"),
            (photovoltaic_power_without_system_loss_mean, "white dim"),
            (photovoltaic_power_without_system_loss_mean_unit, "white dim"),
            photovoltaic_power_without_system_loss_std,
            None,
            "bold",
            EFFECTIVE_IRRADIANCE_NAME,
            photovoltaic_power_without_system_loss_series,
            None,
        ),
        f"{SYSTEM_LOSS}": (
            (system_efficiency_change, "magenta"),
            (system_efficiency_change_unit, "cyan dim"),
            (system_efficiency_change_mean, "magenta"),
            (system_efficiency_change_mean_unit, "cyan dim"),
            None,
            system_efficiency_change_percentage,
            "bold",
            PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME,
            numpy.array([]),
            None,
        ),
        f"[white dim]{POWER_NAME_WITH_SYMBOL}": (
            (photovoltaic_power, "white dim"),
            (photovoltaic_power_unit, "white dim"),
            (photovoltaic_power_mean, "white dim"),
            (photovoltaic_power_mean_unit, "white dim"),
            photovoltaic_power_std,
            None,
            "bold",
            EFFECTIVE_IRRADIANCE_NAME,
            photovoltaic_power_series,
            None,
        ),
        f"[green bold]{ENERGY_NAME_WITH_SYMBOL}": (
            (photovoltaic_power * peak_power, "green"),
            (PHOTOVOLTAIC_ENERGY_UNIT, "green"),
            (photovoltaic_energy_mean, "bold green"),
            (PHOTOVOLTAIC_ENERGY_UNIT, "green"),
            None,
            None,
            "bold",
            EFFECTIVE_IRRADIANCE_NAME,
            numpy.array([]),
            None,
        ),
        f"[white dim]{NET_EFFECT}": (
            (total_change, "white dim"),
            (total_change_unit, "white dim"),
            (total_change_mean, "white dim"),
            (total_change_mean_unit, "white dim"),
            None,
            total_change_percentage,
            "dim",
            IN_PLANE_IRRADIANCE,
            numpy.array([]),
            None,
        ),
    }
