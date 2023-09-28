from devtools import debug
import typer
from pvgisprototype.cli.typer_parameters import OrderCommands
from pvgisprototype.constants import EFFICIENCY_MODEL_COEFFICIENTS_DEFAULT
from pvgisprototype.constants import TEMPERATURE_DEFAULT
import numpy as np


app = typer.Typer(
    cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"Calculate the efficiency of a photovoltaic system",
)


@app.callback(
    'pv-efficiency',
    invoke_without_command=True,
    no_args_is_help=True,
    # context_settings={"ignore_unknown_options": True},
)
def calculate_pv_efficiency(
    irradiance: float,
    temperature: float,
    model_constants = EFFICIENCY_MODEL_COEFFICIENTS_DEFAULT,
    standard_test_temperature: float = TEMPERATURE_DEFAULT,
    wind_speed: float = None,
    use_faiman_model: bool = False,
):
    """
    Calculate the efficiency of a photovoltaic system under varying
    environmental conditions as a function of total irradiance, temperature,
    and wind speed.

    Parameters
    ----------
    irradiance : float
        The solar irradiance in W/m^2.
    temperature : float
        The ambient temperature in degrees Celsius.
    model_constants : list
        Constants used in the model calculation.
    standard_test_temperature : float
        The temperature under standard test conditions in degrees Celsius.
    wind_speed : float, optional
        The wind speed in m/s. If None, the wind speed effect is ignored. Default is None.
    use_faiman_model : bool, optional
        Whether to use the Faiman model for module temperature. Default is False.

    Returns
    -------
    float or str
        The calculated efficiency of the photovoltaic system or an error message if the efficiency is out of range.

    Examples
    --------
    >>> calculate_pv_efficiency(1000, 30, [1, 2, 3, 4, 5, 6, 7, 8, 9], 25, wind_speed=5, use_faiman_model=True)
    'Calculated efficiency is out of logical range (0 to 1).'

    >>> calculate_pv_efficiency(1000, 30, [1, 2, 3, 4, 5, 6, 7, 8, 9], 25, wind_speed=None, use_faiman_model=False)
    'Calculated efficiency is out of logical range (0 to 1).'
    """
    # Validate model constants -----------------------------------------------
    if len(model_constants) < 7:
        return "Insufficient number of model constants."
    # ------------------------------------------------------------------------
    
    relative_irradiance = 0.001 * irradiance
    if relative_irradiance <= 0:
        return 0

    log_relative_irradiance = np.log(relative_irradiance)

    # Adjust the temperature based on the model
    if use_faiman_model and wind_speed is not None:
        if len(model_constants) < 9:
            return "Insufficient number of model constants for Faiman model with wind speed."
        temperature += irradiance / (model_constants[7] + model_constants[8] * wind_speed)

    elif use_faiman_model:
        if len(model_constants) < 8:
            return "Insufficient number of model constants for Faiman model."
        temperature += model_constants[7] * irradiance

    else:
        temperature += irradiance * model_constants[7] 

    temperature_deviation = temperature - standard_test_temperature
    efficiency_factor = (
        model_constants[0]
        + log_relative_irradiance
        * (model_constants[1] + log_relative_irradiance * model_constants[2])
        + temperature_deviation
        * (
            model_constants[3]
            + log_relative_irradiance
            * (model_constants[4] + log_relative_irradiance * model_constants[5])
            + model_constants[6] * temperature_deviation
        )
    )
    efficiency = efficiency_factor / model_constants[0]

    if 0 > efficiency > 1:
        return "The calculated efficiency is out of the expected range [0, 1]!"

    return efficiency
