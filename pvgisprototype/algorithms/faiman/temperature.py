#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
from copy import deepcopy

import numpy as np
from devtools import debug

from pvgisprototype import (
    InclinedIrradiance,
    TemperatureSeries,
    WindSpeedSeries,
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
def calculate_photovoltaic_module_temperature_faiman(
    irradiance_series: InclinedIrradiance,
    photovoltaic_module_efficiency_coefficients,
    temperature_series: TemperatureSeries = TemperatureSeries().average_air_temperature,
    wind_speed_series: WindSpeedSeries = np.array(WindSpeedSeries().average_wind_speed),
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> TemperatureSeries:
    """
    Calculate photovoltaic module operating temperature using the Faiman
    thermal model.
    
    The Faiman model calculates photovoltaic module operating temperature based
    on ambient temperature, incident irradiance, and optionally wind speed. It
    models the thermal balance between absorbed solar radiation and heat loss
    through convection and radiation.
    
    **Equations:**
    
    With wind speed:
    
    .. math::
        T_{module} = T_{ambient} + \\frac{G}{U_0 + U_1 \\cdot v_{wind}}
    
    Without wind speed (simplified):
    
    .. math::
        T_{module} = T_{ambient} + k_7 \\cdot G
    
    Where:

    - :math:`T_{module}` is the module operating temperature (°C)
    - :math:`T_{ambient}` is the ambient air temperature (°C)
    - :math:`G` is the incident irradiance on the module plane (W/m²)
    - :math:`U_0` is the constant heat loss factor (W/m²K) [coefficient 7]
    - :math:`U_1` is the convective heat loss factor (W/m³K/s) [coefficient 8]
    - :math:`v_{wind}` is the wind speed (m/s)
    - :math:`k_7` is the simplified temperature coefficient (°C·m²/W) [coefficient 7]
    
    Parameters
    ----------
    irradiance_series : InclinedIrradiance
        The inclined (or incident) solar irradiance series on the module plane (W/m²).
        This represents the total irradiance (global, direct, or effective) reaching 
        the photovoltaic module surface.
        
    photovoltaic_module_efficiency_coefficients : array-like
        Array of photovoltaic module performance model coefficients. For the Faiman 
        model, requires at least 8 coefficients (without wind) or 9 coefficients 
        (with wind):
        
        - Coefficients [0-6]: Other module performance parameters (e.g., King model)
        - Coefficient [7] (U_0 or k_7): Constant heat loss factor (W/m²K) or 
          simplified temperature coefficient (°C·m²/W)
        - Coefficient [8] (U_1): Convective heat loss coefficient (W/m³K/s), 
          only required when `wind_speed_series` is provided
        
    temperature_series : TemperatureSeries, optional
        Ambient air temperature series (°C). Default uses the average air temperature 
        from the TemperatureSeries data model.
        
    wind_speed_series : WindSpeedSeries, optional
        Wind speed series (m/s) ideally at module height or reference height.
        When provided, the model accounts for convective cooling. Default is
        average wind speed from the WindSpeedSeries data model. Set to None to
        use the simplified model without wind speed dependency.
        
    dtype : str, optional
        Data type for numerical arrays. Default is DATA_TYPE_DEFAULT.
        
    array_backend : str, optional
        Array computation backend (e.g., 'numpy', 'cupy', 'dask'). 
        Default is ARRAY_BACKEND_DEFAULT.
        
    verbose : int, optional
        Verbosity level for debugging output. Higher values produce more detailed 
        output. Default is VERBOSE_LEVEL_DEFAULT.
        
    log : int, optional
        Logging level for data fingerprinting and traceability. 
        Default is LOG_LEVEL_DEFAULT.

    Returns
    -------
    TemperatureSeries
        Adjusted temperature series representing the estimated photovoltaic
        module operating temperature (°C). This accounts for heating due to
        absorbed solar irradiance and cooling from convection and radiation.
        
    Raises
    ------
    ValueError
        If insufficient number of model coefficients are provided for the
        selected Faiman model variant (8 without wind, 9 with wind).

    Notes
    -----
    The Faiman model is an empirical steady-state thermal model that assumes:
    
    1. Uniform module temperature across the surface
    2. Steady-state heat transfer (no thermal mass effects)
    3. Linear relationship between temperature rise and irradiance
    4. Wind speed measured at module height or appropriately scaled
    
    The model is particularly useful for:
    
    - Hourly or sub-hourly photovoltaic performance modeling
    - Systems without detailed thermal characterization
    - Comparative studies across different locations
    
    **Typical coefficient values** (for crystalline silicon modules):
    
    - U_0 (constant loss): 25-35 W/m²K
    - U_1 (wind loss): 5-15 W/m³K/s
    
    References
    ----------
    .. [1] Faiman, D. (2008). "Assessing the outdoor operating temperature of 
           photovoltaic modules." Progress in Photovoltaics: Research and 
           Applications, 16(4), 307-315. DOI: 10.1002/pip.813
    
    .. [2] King, D.L., Boyson, W.E., Kratochvil, J.A. (2004). "Photovoltaic Array 
           Performance Model." Sandia Report SAND2004-3535.

    Examples
    --------
    >>> import numpy as np
    >>> from pvgisprototype import TemperatureSeries, WindSpeedSeries
    >>> from pvgisprototype.algorithms.faiman.temperature import calculate_photovoltaic_module_temperature_faiman
    >>>
    >>> # Create sample data with explicit float dtype
    >>> ambient_temperature = TemperatureSeries(value=np.array([20.0, 22.0, 25.0, 23.0]))
    >>> irradiance = np.array([800.0, 900.0, 1000.0, 850.0])
    >>> wind_speed = WindSpeedSeries(value=np.array([2.0, 3.0, 1.5, 2.5]))
    >>>
    >>> # Faiman coefficients (example for cSi module)
    >>> coefficients = [0, 0, 0, 0, 0, 0, 0, 29.0, 8.0]  # U_0=29, U_1=8
    >>>
    >>> # Calculate module temperature with wind
    >>> module_temp = calculate_photovoltaic_module_temperature_faiman(
    ...     irradiance_series=irradiance,
    ...     photovoltaic_module_efficiency_coefficients=coefficients,
    ...     temperature_series=ambient_temperature,
    ...     wind_speed_series=wind_speed
    ... )
    >>>
    >>> print(f"Module temperatures: {module_temp.value}")
    >>>
    >>> # Without wind (simplified model)
    >>> coefficients_simple = [0, 0, 0, 0, 0, 0, 0, 0.035]  # k_7 coefficient
    >>> module_temperature_simple = calculate_photovoltaic_module_temperature_faiman(
    ...     irradiance_series=irradiance,
    ...     photovoltaic_module_efficiency_coefficients=coefficients_simple,
    ...     temperature_series=ambient_temperature,
    ...     wind_speed_series=None
    ... )
    >>>
    >>> print(f"Module temperatures (simplified): {module_temperature_simple.value}")

    See Also
    --------
    TemperatureSeries : Container for temperature time series data
    WindSpeedSeries : Container for wind speed time series data
    InclinedIrradiance : Container for inclined irradiance data
    """
    temperature_adjusted_series = deepcopy(temperature_series)  # Safe !
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
        temperature_adjusted_series.value += (
            photovoltaic_module_efficiency_coefficients[7] * irradiance_series
        )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=temperature_adjusted_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    temperature_adjusted_series.data_source = 'Faiman 2008'
    # temperature_adjusted_series.photovoltaic_module_operating_temperature = True
    # temperature_adjusted_series.air_temperature = False

    return temperature_adjusted_series
