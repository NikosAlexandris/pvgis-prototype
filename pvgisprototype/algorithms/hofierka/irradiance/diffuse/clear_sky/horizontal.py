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

from pvgisprototype import LinkeTurbidityFactor, SolarAltitude, DiffuseSkyReflectedHorizontalIrradiance
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
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
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
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    solar_altitude_series: SolarAltitude | None = None,
    solar_constant: float = SOLAR_CONSTANT,
    eccentricity_phase_offset: float = ECCENTRICITY_PHASE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> DiffuseSkyReflectedHorizontalIrradiance:
    """Calculate clear-sky diffuse sky-reflected horizontal irradiance.

    Parameters
    ----------
    timestamps : DatetimeIndex
        timestamps
    linke_turbidity_factor_series : LinkeTurbidityFactor
        linke_turbidity_factor_series
    solar_altitude_series : SolarAltitude | None
        solar_altitude_series
    solar_constant : float
        solar_constant
    eccentricity_phase_offset : float
        eccentricity_phase_offset
    eccentricity_amplitude : float
        eccentricity_amplitude
    dtype : str
        dtype
    array_backend : str
        array_backend
    verbose : int
        verbose
    log : int
        log

    Returns
    -------
    DiffuseSkyReflectedHorizontalIrradiance

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
            linke_turbidity_factor_series=linke_turbidity_factor_series
        )
        * calculate_diffuse_solar_altitude_function_series_hofierka(
            solar_altitude_series=solar_altitude_series,
            linke_turbidity_factor_series=linke_turbidity_factor_series,
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
