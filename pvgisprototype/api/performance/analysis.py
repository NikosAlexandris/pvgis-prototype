import numpy
from devtools import debug
from numpy import where
from pandas import DatetimeIndex, Timestamp

from pvgisprototype.core.arrays import create_array
from pvgisprototype.api.performance.helpers import kilofy_unit
from pvgisprototype.api.statistics.polars import (
    calculate_mean_of_series_per_time_unit,
    calculate_statistics,
)
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    EFFECT_PERCENTAGE_COLUMN_NAME,
    EFFECTIVE_IRRADIANCE_COLUMN_NAME,
    GLOBAL_IN_PLANE_IRRADIANCE_AFTER_REFLECTIVITY_COLUMN_NAME,
    GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    GLOBAL_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    IRRADIANCE_UNIT,
    MEAN_EFFECT_COLUMN_NAME,
    MEAN_EFFECTIVE_IRRADIANCE_COLUMN_NAME,
    MEAN_GLOBAL_IN_PLANE_IRRADIANCE_AFTER_REFLECTIVITY_COLUMN_NAME,
    MEAN_GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    MEAN_PHOTOVOLTAIC_ENERGY_COLUMN_NAME,
    MEAN_PHOTOVOLTAIC_POWER_COLUMN_NAME,
    MEAN_PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME,
    MEAN_REFLECTIVITY_EFFECT_COLUMN_NAME,
    MEAN_SPECTRAL_EFFECT_COLUMN_NAME,
    MEAN_SYSTEM_EFFICIENCY_EFFECT_COLUMN_NAME,
    MEAN_TEMPERATURE_AND_LOW_IRRADIANCE_EFFECT_COLUMN_NAME,
    PEAK_POWER_COLUMN_NAME,
    PHOTOVOLTAIC_ENERGY_COLUMN_NAME,
    PHOTOVOLTAIC_ENERGY_UNIT,
    PHOTOVOLTAIC_POWER_COLUMN_NAME,
    PHOTOVOLTAIC_POWER_UNIT,
    PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME,
    POWER_MODEL_COLUMN_NAME,
    REFLECTIVITY_COLUMN_NAME,
    REFLECTIVITY_EFFECT_PERCENTAGE_COLUMN_NAME,
    SPECTRAL_EFFECT_COLUMN_NAME,
    SPECTRAL_EFFECT_PERCENTAGE_COLUMN_NAME,
    STANDARD_DEVIATION_GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    STANDARD_DEVIATION_PHOTOVOLTAIC_POWER_COLUMN_NAME,
    STANDARD_DEVIATION_PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME,
    STANDARD_DEVIATION_REFLECTIVITY_EFFECT_COLUMN_NAME,
    STANDARD_DEVIATION_SPECTRAL_EFFECT_COLUMN_NAME,
    SYSTEM_EFFICIENCY_COLUMN_NAME,
    SYSTEM_EFFICIENCY_EFFECT_PERCENTAGE_COLUMN_NAME,
    TEMPERATURE_AND_LOW_IRRADIANCE_EFFECT_PERCENTAGE_COLUMN_NAME,
    TOTAL_EFFECT_COLUMN_NAME,
    TOTAL_GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    TOTAL_PHOTOVOLTAIC_POWER_COLUMN_NAME,
    TOTAL_PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME,
    TOTAL_REFLECTIVITY_EFFECT_COLUMN_NAME,
    TOTAL_SPECTRAL_EFFECT_COLUMN_NAME,
    TOTAL_SYSTEM_EFFICIENCY_EFFECT_COLUMN_NAME,
    TOTAL_TEMPERATURE_AND_LOW_IRRADIANCE_EFFECT_COLUMN_NAME,
    UNIT_FOR_EFFECTIVE_IRRADIANCE_COLUMN_NAME,
    UNIT_FOR_GLOBAL_IN_PLANE_IRRADIANCE_AFTER_REFLECTIVITY_COLUMN_NAME,
    UNIT_FOR_MEAN_EFFECT_COLUMN_NAME,
    UNIT_FOR_MEAN_EFFECTIVE_IRRADIANCE_COLUMN_NAME,
    UNIT_FOR_MEAN_GLOBAL_IN_PLANE_IRRADIANCE_AFTER_REFLECTIVITY_COLUMN_NAME,
    UNIT_FOR_MEAN_GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    UNIT_FOR_MEAN_PHOTOVOLTAIC_ENERGY_COLUMN_NAME,
    UNIT_FOR_MEAN_PHOTOVOLTAIC_POWER_COLUMN_NAME,
    UNIT_FOR_MEAN_PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME,
    UNIT_FOR_MEAN_REFLECTIVITY_EFFECT_COLUMN_NAME,
    UNIT_FOR_MEAN_SYSTEM_EFFICIENCY_EFFECT_COLUMN_NAME,
    UNIT_FOR_MEAN_TEMPERATURE_AND_LOW_IRRADIANCE_EFFECT_COLUMN_NAME,
    UNIT_FOR_PHOTOVOLTAIC_ENERGY_COLUMN_NAME,
    UNIT_FOR_TEMPERATURE_AND_LOW_IRRADIANCE_EFFECT_COLUMN_NAME,
    UNIT_FOR_TOTAL_EFFECT_COLUMN_NAME,
    UNIT_FOR_TOTAL_GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    UNIT_FOR_TOTAL_PHOTOVOLTAIC_POWER_COLUMN_NAME,
    UNIT_FOR_TOTAL_PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME,
    UNIT_FOR_TOTAL_REFLECTIVITY_EFFECT_COLUMN_NAME,
    UNIT_FOR_TOTAL_SPECTRAL_EFFECT_COLUMN_NAME,
    UNIT_FOR_TOTAL_SYSTEM_EFFICIENCY_EFFECT_COLUMN_NAME,
    VERBOSE_LEVEL_DEFAULT,
)


def analyse_photovoltaic_performance(
    dictionary,
    timestamps: DatetimeIndex | Timestamp,
    frequency: str,
    rounding_places=1,
    dtype=DATA_TYPE_DEFAULT,
    array_backend=ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
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
    │ Reflectivity Effect
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
    # In-Plane irradiance (before effects)
    # ------------------------------------------------------------------------
    # To Do : In-Plane "Irradiation" ?
    # Add Standard Deviation in kWh ? Monthly, Yearly ?
    # ------------------------------------------------------------------------

    # from devtools import debug
    # debug(locals())
    inclined_irradiance_series = dictionary.get(
        GLOBAL_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME, numpy.array([])
    )
    inclined_irradiance, inclined_irradiance_mean, inclined_irradiance_std, _ = (
        calculate_statistics(
            inclined_irradiance_series,
            timestamps,
            frequency,
            1,
            rounding_places,
        )
    )

    # Reflectivity

    reflectivity_series = dictionary.get(REFLECTIVITY_COLUMN_NAME, numpy.array([]))
    (
        reflectivity_effect,
        reflectivity_effect_mean,
        reflectivity_effect_std,
        reflectivity_effect_percentage,
    ) = calculate_statistics(
        reflectivity_series,
        timestamps,
        frequency,
        inclined_irradiance,
        rounding_places,
    )

    # After reflectivity

    irradiance_after_reflectivity = inclined_irradiance + reflectivity_effect
    irradiance_after_reflectivity_mean = calculate_mean_of_series_per_time_unit(
        inclined_irradiance_series + reflectivity_series,
        timestamps=timestamps,
        frequency=frequency,
    )

    # Spectral effect

    spectral_effect_series = dictionary.get(
        SPECTRAL_EFFECT_COLUMN_NAME, numpy.array([])
    )
    (
        spectral_effect,
        spectral_effect_mean,
        spectral_effect_std,
        spectral_effect_percentage,
    ) = calculate_statistics(
        spectral_effect_series,
        timestamps,
        frequency,
        irradiance_after_reflectivity,
        rounding_places,
    )

    effective_irradiance = irradiance_after_reflectivity + spectral_effect
    # effective_irradiance_percentage = (
    #     (effective_irradiance / inclined_irradiance * 100)
    #     if inclined_irradiance != 0
    #     else 0
    # )
    effective_irradiance_mean = (
        irradiance_after_reflectivity_mean + spectral_effect_mean
    )
    effective_irradiance_effect = effective_irradiance - inclined_irradiance
    # with numpy.errstate(divide="ignore", invalid="ignore"):  # if irradiance == 0
    #     effective_irradiance_effect_percentage = where(
    #         inclined_irradiance != 0,
    #         100 * effective_irradiance_effect / inclined_irradiance,
    #         0,
    #     ).item()  # get a Python float

    # "Effective" Power without System Loss

    photovoltaic_power_without_system_loss_series = dictionary.get(
        PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME, numpy.array([])
    )
    (
        photovoltaic_power_without_system_loss,
        photovoltaic_power_without_system_loss_mean,
        photovoltaic_power_without_system_loss_std,
        _,
    ) = calculate_statistics(
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
    temperature_and_low_irradiance_effect = (
        photovoltaic_power_without_system_loss - effective_irradiance
    )
    temperature_and_low_irradiance_effect_mean = (
        photovoltaic_power_without_system_loss_mean - effective_irradiance_mean
    )
    with numpy.errstate(divide="ignore", invalid="ignore"):  # if irradiance == 0
        temperature_and_low_irradiance_effect_percentage = where(
            effective_irradiance != 0,
            100
            * temperature_and_low_irradiance_effect
            / numpy.array(
                effective_irradiance
            ),  # still need to handle the case when effective_irradiance == 0  <-- single float
            0,
        ).item()  # get a Python float

    # System efficiency

    # Currently, the default system efficiency SYSTEM_EFFICIENCY
    # is a single and constant floating point number.
    
    # Nevertheless, we convert it to a series for the following two reasons :
    
    # 1. to make it easier for the function calculate_mean_of_series_per_time_unit()
    # to derive the quantity 'system_efficiency_effect_mean' : 
    # essentially, the function polars.DataFrame() expects all input "data series" to be of the same length.
    
    # 2. to support scenarios of a fine-grained system efficiency time series

    array_parameters = {
        "shape": timestamps.shape,
        "dtype": dtype,
        "init_method": dictionary.get(SYSTEM_EFFICIENCY_COLUMN_NAME, None),
        "backend": array_backend,
    }  # Borrow shape from timestamps
    system_efficiency_series = create_array(**array_parameters)
    system_efficiency = numpy.nanmedian(system_efficiency_series).astype(dtype)
    system_efficiency_effect = numpy.array(
        photovoltaic_power_without_system_loss * system_efficiency
        - photovoltaic_power_without_system_loss,
        dtype=dtype
    ).item()  # Important !
    system_efficiency_effect_mean = calculate_mean_of_series_per_time_unit(
        photovoltaic_power_without_system_loss_mean * system_efficiency_series
        - photovoltaic_power_without_system_loss_mean,
        timestamps=timestamps,
        frequency=frequency,
    )
    with numpy.errstate(divide="ignore", invalid="ignore"):  # if irradiance == 0
        system_efficiency_effect_percentage = where(
            photovoltaic_power_without_system_loss != 0,
            100
            * system_efficiency_effect
            / numpy.array(
                photovoltaic_power_without_system_loss
            ),  # still need to handle the case when photovoltaic_power_without_system_loss == 0  <-- single float
            0,
        ).item()  # get a Python float

    # Photovoltaic Power
    photovoltaic_power_series = dictionary.get(
        PHOTOVOLTAIC_POWER_COLUMN_NAME, numpy.array([])
    )
    photovoltaic_power, photovoltaic_power_mean, photovoltaic_power_std, _ = (
        calculate_statistics(
            photovoltaic_power_series,
            timestamps,
            frequency,
            1,
            rounding_places,
        )
    )
    peak_power = dictionary.get(PEAK_POWER_COLUMN_NAME, numpy.array([]))
    photovoltaic_energy = photovoltaic_power * peak_power
    photovoltaic_energy_mean = photovoltaic_power_mean * peak_power

    # Total effect
    total_effect = photovoltaic_power - inclined_irradiance
    total_effect_mean = photovoltaic_power_mean - inclined_irradiance_mean
    with numpy.errstate(divide="ignore", invalid="ignore"):  # if irradiance == 0
        total_effect_percentage = where(
            inclined_irradiance != 0,
            total_effect
            / numpy.array(inclined_irradiance)
            * 100,  # still need to handle the case when inclined_irradiance == 0  <-- single floar
            0,
        ).item()

    # Handle units

    inclined_irradiance, inclined_irradiance_unit = kilofy_unit(
        inclined_irradiance, IRRADIANCE_UNIT
    )
    inclined_irradiance_mean, inclined_irradiance_mean_unit = kilofy_unit(
        inclined_irradiance_mean, IRRADIANCE_UNIT
    )

    reflectivity_effect, reflectivity_effect_unit = kilofy_unit(
        reflectivity_effect, IRRADIANCE_UNIT
    )
    reflectivity_effect_mean, reflectivity_effect_mean_unit = kilofy_unit(
        reflectivity_effect_mean, IRRADIANCE_UNIT
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
        temperature_and_low_irradiance_effect,
        temperature_and_low_irradiance_effect_unit,
    ) = kilofy_unit(temperature_and_low_irradiance_effect, IRRADIANCE_UNIT)
    (
        temperature_and_low_irradiance_effect_mean,
        temperature_and_low_irradiance_effect_mean_unit,
    ) = kilofy_unit(temperature_and_low_irradiance_effect_mean, IRRADIANCE_UNIT)

    system_efficiency_effect, system_efficiency_effect_unit = kilofy_unit(
        system_efficiency_effect, PHOTOVOLTAIC_POWER_UNIT
    )
    system_efficiency_effect_mean, system_efficiency_effect_mean_unit = kilofy_unit(
        system_efficiency_effect_mean, PHOTOVOLTAIC_POWER_UNIT
    )

    photovoltaic_power, photovoltaic_power_unit = kilofy_unit(
        photovoltaic_power, PHOTOVOLTAIC_POWER_UNIT
    )
    photovoltaic_power_mean, photovoltaic_power_mean_unit = kilofy_unit(
        photovoltaic_power_mean, PHOTOVOLTAIC_POWER_UNIT
    )

    photovoltaic_energy, photovoltaic_energy_unit = kilofy_unit(
        photovoltaic_energy, PHOTOVOLTAIC_ENERGY_UNIT
    )
    photovoltaic_energy_mean, photovoltaic_energy_mean_unit = kilofy_unit(
        photovoltaic_energy_mean, PHOTOVOLTAIC_ENERGY_UNIT
    )

    total_effect, total_effect_unit = kilofy_unit(total_effect, IRRADIANCE_UNIT)
    total_effect_mean, total_effect_mean_unit = kilofy_unit(
        total_effect_mean, IRRADIANCE_UNIT
    )
    performance_analysis = {
        TOTAL_GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME: inclined_irradiance,
        UNIT_FOR_TOTAL_GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME: inclined_irradiance_unit,
        MEAN_GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME: inclined_irradiance_mean,
        UNIT_FOR_MEAN_GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME: inclined_irradiance_mean_unit,
        STANDARD_DEVIATION_GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME: inclined_irradiance_std,
        GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME: inclined_irradiance_series,
        #
        TOTAL_REFLECTIVITY_EFFECT_COLUMN_NAME: reflectivity_effect,
        UNIT_FOR_TOTAL_REFLECTIVITY_EFFECT_COLUMN_NAME: reflectivity_effect_unit,
        MEAN_REFLECTIVITY_EFFECT_COLUMN_NAME: reflectivity_effect_mean,
        UNIT_FOR_MEAN_REFLECTIVITY_EFFECT_COLUMN_NAME: reflectivity_effect_mean_unit,
        STANDARD_DEVIATION_REFLECTIVITY_EFFECT_COLUMN_NAME: reflectivity_effect_std,
        REFLECTIVITY_EFFECT_PERCENTAGE_COLUMN_NAME: reflectivity_effect_percentage,
        REFLECTIVITY_COLUMN_NAME: reflectivity_series,
        #
        GLOBAL_IN_PLANE_IRRADIANCE_AFTER_REFLECTIVITY_COLUMN_NAME: irradiance_after_reflectivity,
        UNIT_FOR_GLOBAL_IN_PLANE_IRRADIANCE_AFTER_REFLECTIVITY_COLUMN_NAME: irradiance_after_reflectivity_unit,
        MEAN_GLOBAL_IN_PLANE_IRRADIANCE_AFTER_REFLECTIVITY_COLUMN_NAME: irradiance_after_reflectivity_mean,
        UNIT_FOR_MEAN_GLOBAL_IN_PLANE_IRRADIANCE_AFTER_REFLECTIVITY_COLUMN_NAME: irradiance_after_reflectivity_mean_unit,
        #
        TOTAL_SPECTRAL_EFFECT_COLUMN_NAME: spectral_effect,
        UNIT_FOR_TOTAL_SPECTRAL_EFFECT_COLUMN_NAME: spectral_effect_unit,
        MEAN_SPECTRAL_EFFECT_COLUMN_NAME: spectral_effect_mean,
        STANDARD_DEVIATION_SPECTRAL_EFFECT_COLUMN_NAME: spectral_effect_std,
        SPECTRAL_EFFECT_PERCENTAGE_COLUMN_NAME: spectral_effect_percentage,
        SPECTRAL_EFFECT_COLUMN_NAME: spectral_effect_series,
        #
        EFFECTIVE_IRRADIANCE_COLUMN_NAME: effective_irradiance,
        UNIT_FOR_EFFECTIVE_IRRADIANCE_COLUMN_NAME: effective_irradiance_unit,
        MEAN_EFFECTIVE_IRRADIANCE_COLUMN_NAME: effective_irradiance_mean,
        UNIT_FOR_MEAN_EFFECTIVE_IRRADIANCE_COLUMN_NAME: effective_irradiance_mean_unit,
        #
        TOTAL_TEMPERATURE_AND_LOW_IRRADIANCE_EFFECT_COLUMN_NAME: temperature_and_low_irradiance_effect,
        UNIT_FOR_TEMPERATURE_AND_LOW_IRRADIANCE_EFFECT_COLUMN_NAME: temperature_and_low_irradiance_effect_unit,
        MEAN_TEMPERATURE_AND_LOW_IRRADIANCE_EFFECT_COLUMN_NAME: temperature_and_low_irradiance_effect_mean,
        UNIT_FOR_MEAN_TEMPERATURE_AND_LOW_IRRADIANCE_EFFECT_COLUMN_NAME: temperature_and_low_irradiance_effect_mean_unit,
        TEMPERATURE_AND_LOW_IRRADIANCE_EFFECT_PERCENTAGE_COLUMN_NAME: temperature_and_low_irradiance_effect_percentage,
        #
        TOTAL_PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME: photovoltaic_power_without_system_loss,
        UNIT_FOR_TOTAL_PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME: photovoltaic_power_without_system_loss_unit,
        MEAN_PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME: photovoltaic_power_without_system_loss_mean,
        UNIT_FOR_MEAN_PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME: photovoltaic_power_without_system_loss_mean_unit,
        STANDARD_DEVIATION_PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME: photovoltaic_power_without_system_loss_std,
        PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME: photovoltaic_power_without_system_loss_series,
        #
        TOTAL_SYSTEM_EFFICIENCY_EFFECT_COLUMN_NAME: system_efficiency_effect,
        UNIT_FOR_TOTAL_SYSTEM_EFFICIENCY_EFFECT_COLUMN_NAME: system_efficiency_effect_unit,
        MEAN_SYSTEM_EFFICIENCY_EFFECT_COLUMN_NAME: system_efficiency_effect_mean,
        UNIT_FOR_MEAN_SYSTEM_EFFICIENCY_EFFECT_COLUMN_NAME: system_efficiency_effect_mean_unit,
        SYSTEM_EFFICIENCY_EFFECT_PERCENTAGE_COLUMN_NAME: system_efficiency_effect_percentage,
        #
        TOTAL_PHOTOVOLTAIC_POWER_COLUMN_NAME: photovoltaic_power,
        UNIT_FOR_TOTAL_PHOTOVOLTAIC_POWER_COLUMN_NAME: photovoltaic_power_unit,
        MEAN_PHOTOVOLTAIC_POWER_COLUMN_NAME: photovoltaic_power_mean,
        UNIT_FOR_MEAN_PHOTOVOLTAIC_POWER_COLUMN_NAME: photovoltaic_power_mean_unit,
        STANDARD_DEVIATION_PHOTOVOLTAIC_POWER_COLUMN_NAME: photovoltaic_power_std,
        PHOTOVOLTAIC_POWER_COLUMN_NAME: photovoltaic_power_series,
        #
        PHOTOVOLTAIC_ENERGY_COLUMN_NAME: photovoltaic_energy,
        UNIT_FOR_PHOTOVOLTAIC_ENERGY_COLUMN_NAME: photovoltaic_energy_unit,
        MEAN_PHOTOVOLTAIC_ENERGY_COLUMN_NAME: photovoltaic_energy_mean,
        UNIT_FOR_MEAN_PHOTOVOLTAIC_ENERGY_COLUMN_NAME: photovoltaic_energy_mean_unit,
        #
        TOTAL_EFFECT_COLUMN_NAME: total_effect,
        UNIT_FOR_TOTAL_EFFECT_COLUMN_NAME: total_effect_unit,
        MEAN_EFFECT_COLUMN_NAME: total_effect_mean,
        UNIT_FOR_MEAN_EFFECT_COLUMN_NAME: total_effect_mean_unit,
        EFFECT_PERCENTAGE_COLUMN_NAME: total_effect_percentage,
    }
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return performance_analysis
