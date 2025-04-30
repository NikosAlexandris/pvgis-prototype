import numpy as np
from devtools import debug
from numpy import log as numpy_log
from numpy import where
from pvgisprototype import (
    Efficiency,
    EffectiveIrradiance,
    TemperatureSeries,
)
from pvgisprototype.algorithms.huld.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.algorithms.huld.photovoltaic_module import (
    PhotovoltaicModuleModel,
    get_coefficients_for_photovoltaic_module,
)
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    CURRENT_AT_STANDARD_TEST_CONDITIONS,
    CURRENT_AT_STANDARD_TEST_CONDITIONS_TEMPERATURE_COEFFICIENT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    EFFICIENCY_FACTOR_COLUMN_NAME,
    EFFICIENCY_NAME,
    FINGERPRINT_COLUMN_NAME,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    IRRADIANCE_COLUMN_NAME,
    LOG_LEVEL_DEFAULT,
    LOG_RELATIVE_IRRADIANCE_COLUMN_NAME,
    LOW_IRRADIANCE_COLUMN_NAME,
    NOT_AVAILABLE,
    POWER_AT_STANDARD_TEST_CONDITIONS,
    RADIATION_CUTOFF_THRESHHOLD,
    RELATIVE_IRRADIANCE_COLUMN_NAME,
    TEMPERATURE_DEFAULT,
    TEMPERATURE_DEVIATION_COLUMN_NAME,
    TITLE_KEY_NAME,
    UNITLESS,
    VERBOSE_LEVEL_DEFAULT,
    VOLTAGE_AT_STANDARD_TEST_CONDITIONS,
    VOLTAGE_AT_STANDARD_TEST_CONDITIONS_COEFFICIENT_1,
    VOLTAGE_AT_STANDARD_TEST_CONDITIONS_COEFFICIENT_2,
    VOLTAGE_AT_STANDARD_TEST_CONDITIONS_TEMPERATURE_COEFFICIENT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.core.arrays import create_array
from pvgisprototype.core.hashing import generate_hash


@log_function_call
def calculate_efficiency_factor_series(
    irradiance_series: EffectiveIrradiance,  # effective irradiance
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
