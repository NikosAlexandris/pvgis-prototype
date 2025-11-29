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
import numpy as np
from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import (
    LinkeTurbidityFactor,
    SolarAltitude,
    DiffuseSkyReflectedHorizontalIrradiance,
)
from pvgisprototype.algorithms.hofierka.irradiance.diffuse.clear_sky.altitude import (
    calculate_diffuse_solar_altitude_function_series_hofierka,
)
from pvgisprototype.algorithms.hofierka.irradiance.diffuse.clear_sky.transmission_function import (
    calculate_diffuse_transmission_function_series_hofierka,
)
from pvgisprototype.api.irradiance.extraterrestrial.normal import (
    calculate_extraterrestrial_normal_irradiance_series,
)
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    ECCENTRICITY_PHASE_OFFSET,
    SOLAR_CONSTANT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.validation.values import identify_values_out_of_range


@log_function_call
@custom_cached
def calculate_clear_sky_diffuse_horizontal_irradiance_hofierka(
    timestamps: DatetimeIndex,
    # linke_turbidity_factor_series: LinkeTurbidityFactor = LinkeTurbidityFactor(),
    linke_turbidity_factor_series: LinkeTurbidityFactor,
    solar_altitude_series: SolarAltitude | None = None,
    solar_constant: float = SOLAR_CONSTANT,
    eccentricity_phase_offset: float = ECCENTRICITY_PHASE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> DiffuseSkyReflectedHorizontalIrradiance:
    """
    Calculate clear-sky diffuse sky-reflected horizontal irradiance using
    Hofierka's model.

    Calculates the diffuse sky-reflected component of solar irradiance on a
    horizontal surface under cloudless sky conditions using Hofierka's
    empirical clear-sky model. This implementation follows the theoretical
    framework where diffuse irradiance is the product of extraterrestrial
    irradiance, a diffuse transmission function, and a solar altitude function.

    The model estimates diffuse horizontal irradiance (Dₕc) as:

    .. math::
        D_{hc} = G_0 \cdot T_n(T_{LK}) \cdot F_d(h_0)

    where G₀ is the extraterrestrial normal irradiance, Tₙ is the diffuse
    transmission function dependent on Linke turbidity, and Fₐ is the solar
    altitude function.

    Parameters
    ----------
    timestamps : pandas.DatetimeIndex
        Time series index for which to calculate diffuse irradiance. Must be
        timezone-aware for accurate solar position calculations.
    linke_turbidity_factor_series : LinkeTurbidityFactor, optional
        Linke turbidity factor values for each timestamp, characterizing
        atmospheric turbidity. Typical values range from 1.0 (clean) to 6.0
        (very turbid). Default is set in ``LinkeTurbidityFactor()``.
    solar_altitude_series : SolarAltitude or None, optional
        Pre-calculated solar altitude angles in radians. If None, must be
        calculated externally before calling this function. Negative values
        (sun below horizon) are automatically set to NaN. Default is None.
    solar_constant : float, optional
        Solar constant in W·m⁻². Represents the solar irradiance at mean
        Earth-Sun distance outside the atmosphere. Default is ``SOLAR_CONSTANT``
        (typically 1361 W·m⁻²).
    eccentricity_phase_offset : float, optional
        Phase offset for Earth's orbital eccentricity correction in radians.
        Accounts for perihelion timing. Default is ``ECCENTRICITY_PHASE_OFFSET``.
    eccentricity_amplitude : float, optional
        Amplitude of Earth's orbital eccentricity correction factor. Adjusts
        for varying Earth-Sun distance throughout the year. Default is
        ``ECCENTRICITY_CORRECTION_FACTOR``.
    dtype : str, optional
        NumPy data type for array operations (e.g., 'float32', 'float64').
        Default is ``DATA_TYPE_DEFAULT``.
    array_backend : str, optional
        Array backend to use for computations ('numpy', 'cupy', 'dask').
        Default is ``ARRAY_BACKEND_DEFAULT``.
    verbose : int, optional
        Verbosity level for debugging output. When exceeding
        ``DEBUG_AFTER_THIS_VERBOSITY_LEVEL``, prints all local variables.
        Default is ``VERBOSE_LEVEL_DEFAULT``.
    log : int, optional
        Logging level for data fingerprinting. When exceeding
        ``HASH_AFTER_THIS_VERBOSITY_LEVEL``, logs data hashes for
        reproducibility tracking. Default is ``LOG_LEVEL_DEFAULT``.

    Returns
    -------
    DiffuseSkyReflectedHorizontalIrradiance
        Data model containing:
        
        - **value** : numpy.ndarray
            Diffuse horizontal irradiance values in W·m⁻² for each timestamp
        - **out_of_range** : bool
            Flag indicating if any values exceed physical bounds
        - **out_of_range_index** : numpy.ndarray
            Indices of out-of-range values
        - **extraterrestrial_normal_irradiance** : array
            Calculated extraterrestrial irradiance values
        - **linke_turbidity_factor** : LinkeTurbidityFactor
            Input turbidity values used in calculation
        - **solar_altitude** : SolarAltitude
            Solar altitude angles used in calculation
        - **solar_positioning_algorithm** : str
            Algorithm used for solar position calculations
        - **adjust_for_atmospheric_refraction** : bool
            Whether atmospheric refraction correction was applied

    Notes
    -----
    **Implementation Details**
    
    - Negative solar altitudes (sun below horizon) are automatically set to NaN,
      then converted to zero irradiance
    - Out-of-range values are identified and flagged based on physical constraints
    - The function is cached for performance optimization
    - All calculations are vectorized for efficiency over time series
    
    **Physical Validity**
    
    - Valid only for cloudless sky conditions
    - Results are physically meaningful only when sun is above horizon
    - Linke turbidity should be within [1.0, 6.0] range
    - Output irradiance cannot exceed extraterrestrial values
    
    **Model Limitations**
    
    - Assumes horizontally homogeneous atmosphere
    - Does not include ground-reflected component
    - Model calibrated for mid-latitude conditions (?)

    See Also
    --------
    calculate_diffuse_transmission_function_series_hofierka : Calculates Tₙ(T_LK)
    calculate_diffuse_solar_altitude_function_series_hofierka : Calculates Fₐ(h₀)
    calculate_extraterrestrial_normal_irradiance_series : Calculates G₀
    pvgisprototype.algorithms.hofierka.irradiance.diffuse.clear_sky.altitude : Altitude function module

    References
    ----------
    .. [1] Hofierka, J., & Šúri, M. (2002). The solar radiation model for Open
           source GIS: implementation and applications. *Proceedings of the
           Open source GIS - GRASS users conference*, Trento, Italy.
    .. [2] Rigollier, C., Bauer, O., & Wald, L. (2000). On the clear sky model
           of the ESRA—European Solar Radiation Atlas—with respect to the
           Heliosat method. *Solar Energy*, 68(1), 33-48.

    Examples
    --------
    Calculate diffuse irradiance for a single day :

    >>> import pandas as pd
    >>> import numpy as np
    >>> from pvgisprototype import SolarAltitude, LinkeTurbidityFactor
    >>> from pvgisprototype.algorithms.hofierka.irradiance.diffuse.clear_sky.horizontal import (
    ...     calculate_clear_sky_diffuse_horizontal_irradiance_hofierka
    ... )
    >>>
    >>> # Create hourly timestamps for one day
    >>> timestamps = pd.date_range(
    ...     '2024-06-21', periods=24, freq='h', tz='UTC'
    ... )
    >>>
    >>> # Calculate solar altitude (normally done via solar position function)
    >>> # Here using example values for demonstration
    >>> altitude_values = np.array([
    ...     -0.5, -0.3, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.1, 1.2, 1.2, 1.15,
    ...     1.1, 1.0, 0.8, 0.6, 0.4, 0.2, 0.0, -0.2, -0.4, -0.5, -0.6, -0.6
    ... ])
    >>> solar_altitude = SolarAltitude(value=altitude_values, unit='radians')
    >>>
    >>> # Constant moderate turbidity
    >>> turbidity = LinkeTurbidityFactor(value=np.full(24, 3.0))
    >>>
    >>> # Calculate diffuse irradiance
    >>> result = calculate_clear_sky_diffuse_horizontal_irradiance_hofierka(
    ...     timestamps=timestamps,
    ...     solar_altitude_series=solar_altitude,
    ...     linke_turbidity_factor_series=turbidity
    ... )
    >>>
    >>> # Display results
    >>> print(f"Max diffuse irradiance: {result.value.max():.1f} W/m²")

    >>> print(f"Daily total: {result.value.sum():.1f} Wh/m²")

    >>>
    >>> # Check for out-of-range values
    >>> if result.out_of_range is not None:
    ...     print(f"Warning: {len(result.out_of_range_index)} values out of range")

    Calculate with time-varying turbidity :

    >>> # Simulate varying atmospheric conditions
    >>> turbidity_varying = LinkeTurbidityFactor(
    ...     value=np.linspace(2.5, 3.5, 24)  # Increasing turbidity
    ... )
    >>> 
    >>> result_varying = calculate_clear_sky_diffuse_horizontal_irradiance_hofierka(
    ...     timestamps=timestamps,
    ...     solar_altitude_series=solar_altitude,
    ...     linke_turbidity_factor_series=turbidity_varying
    ... )
    >>> 
    >>> print(f"Turbidity effect: {result_varying.value.max() - result.value.max():.1f} W/m²")

    Warnings
    --------
    - Negative solar altitudes are automatically converted to zero irradiance
    - Input arrays (timestamps, turbidity, altitude) must have matching
      dimensions
    - Very high turbidity values (>6.0) may produce physically unrealistic
      results (?)
    """
    extraterrestrial_normal_irradiance_series = (
        calculate_extraterrestrial_normal_irradiance_series(
            timestamps=timestamps,
            solar_constant=solar_constant,
            eccentricity_phase_offset=eccentricity_phase_offset,
            eccentricity_amplitude=eccentricity_amplitude,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )
    )
    # Should this maybe happen already outside this function ? ---------------
    # Suppress negative solar altitude, else we get high-negative diffuse output
    solar_altitude_series.value[solar_altitude_series.value < 0] = np.nan
    # ------------------------------------------------------------------------

    diffuse_horizontal_irradiance_series = (
        extraterrestrial_normal_irradiance_series.value
        * calculate_diffuse_transmission_function_series_hofierka(
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            verbose=verbose,
        )
        * calculate_diffuse_solar_altitude_function_series_hofierka(
            solar_altitude_series=solar_altitude_series,
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            verbose=verbose,
        )
    )
    # ------------------------------------------------------------------------
    diffuse_horizontal_irradiance_series = np.nan_to_num(
        diffuse_horizontal_irradiance_series, nan=0
    )  # safer ? -------------------------------------------------------------

    out_of_range, out_of_range_index = identify_values_out_of_range(
        series=diffuse_horizontal_irradiance_series,
        shape=timestamps.shape,
        data_model=DiffuseSkyReflectedHorizontalIrradiance(),
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=diffuse_horizontal_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return DiffuseSkyReflectedHorizontalIrradiance(
        value=diffuse_horizontal_irradiance_series,
        out_of_range=out_of_range,
        out_of_range_index=out_of_range_index,
        extraterrestrial_normal_irradiance=extraterrestrial_normal_irradiance_series,
        linke_turbidity_factor=linke_turbidity_factor_series,
        solar_altitude=solar_altitude_series,
        solar_positioning_algorithm=solar_altitude_series.solar_positioning_algorithm,
        adjust_for_atmospheric_refraction=solar_altitude_series.adjusted_for_atmospheric_refraction,
    )
