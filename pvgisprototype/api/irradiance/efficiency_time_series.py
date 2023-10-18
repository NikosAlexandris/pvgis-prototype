from devtools import debug
import typer
from typing import Annotated
from typing import List
from rich import print
from pvgisprototype.cli.typer_parameters import OrderCommands
from pvgisprototype.api.irradiance.efficiency_coefficients import STANDARD_EFFICIENCY_MODEL_COEFFICIENTS
from pvgisprototype.api.irradiance.efficiency_coefficients import EFFICIENCY_MODEL_COEFFICIENTS
from pvgisprototype.api.irradiance.efficiency_coefficients import EFFICIENCY_MODEL_COEFFICIENTS_DEFAULT
from pvgisprototype.constants import TEMPERATURE_DEFAULT
from pvgisprototype.api.irradiance.models import PVModuleEfficiencyAlgorithms
from pvgisprototype.cli.typer_parameters import typer_option_verbose
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
import numpy as np


app = typer.Typer(
    cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"Calculate the efficiency of a photovoltaic system",
)


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


@app.callback(
    'pv-efficiency-time-series',
    invoke_without_command=True,
    no_args_is_help=True,
    # context_settings={"ignore_unknown_options": True},
)
def calculate_pv_efficiency_time_series(
    irradiance_series: List[float],
    temperature_series: List[float] = [TEMPERATURE_DEFAULT],
    model_constants: List[float] = EFFICIENCY_MODEL_COEFFICIENTS_DEFAULT,
    standard_test_temperature: float = TEMPERATURE_DEFAULT,
    wind_speed_series: List[float] = None,
    model: PVModuleEfficiencyAlgorithms = PVModuleEfficiencyAlgorithms.faiman,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    model_constants = np.array(EFFICIENCY_MODEL_COEFFICIENTS['cSi']['Free standing'])
    # or add standard plus selected?
    # model_constants = np.array(STANDARD_EFFICIENCY_MODEL_COEFFICIENTS)
    # selected_model_constants = np.array(EFFICIENCY_MODEL_COEFFICIENTS['cSi']['Free standing'])
    # model_constants = add_unequal_arrays(model_constants, selected_model_constants) 

    if len(model_constants) < 7:
        raise ValueError("Insufficient number of model constants!")
    
    irradiance_series = np.array(irradiance_series)
    efficiency_series = np.zeros_like(irradiance_series)
    relative_irradiance_series = 0.001 * irradiance_series
    mask_zero_irradiance = relative_irradiance_series <= 0
    efficiency_series[mask_zero_irradiance] = 0
    log_relative_irradiance_series = np.log(relative_irradiance_series)

    # Adjust temperature based on conditions
    if model.value  == PVModuleEfficiencyAlgorithms.faiman:
        if wind_speed_series:
            if len(model_constants) < 9:
                return "Insufficient number of model constants for Faiman model with wind speed."
            temperature_series += irradiance_series / (
                model_constants[7] + model_constants[8] * wind_speed_series
            )
        else:
            if len(model_constants) < 8:
                return "Insufficient number of model constants for Faiman model."
            temperature_series += model_constants[7] * irradiance_series
    

    temperature_deviation_series = temperature_series - standard_test_temperature
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
    
    # # Mask where efficiency is out of range [0, 1]
    # mask_invalid_efficiency = (efficiency_series < 0) | (efficiency_series > 1)
    

    # if np.any(mask_invalid_efficiency):
    #     return "Some calculated efficiencies are out of the expected range [0, 1]!"
    
    if verbose > 0:
        print(f'Efficiency array: {efficiency_series}')
    
    return efficiency_series
