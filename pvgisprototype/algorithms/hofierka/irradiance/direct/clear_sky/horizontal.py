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
"""
This Python module is part of PVGIS' Algorithms. It implements functions to calculate
the direct solar irradiance.

_Direct_ or _beam_ irradiance is one of the main components of solar
irradiance. It comes perpendicular from the Sun and is not scattered before it
irradiates a surface.

During a cloudy day the sunlight will be partially absorbed and scattered by
different air molecules. The latter part is defined as the _diffuse_
irradiance. The remaining part is the _direct_ irradiance.
"""

import numpy as np
from devtools import debug
from pandas import DatetimeIndex, Timestamp

from pvgisprototype import (
    DirectHorizontalIrradiance,
    LinkeTurbidityFactor,
    SolarAltitude,
    LocationShading,
)
from pvgisprototype.algorithms.hofierka.irradiance.direct.clear_sky.normal import calculate_direct_normal_irradiance_hofierka
from pvgisprototype.api.irradiance.direct.optical_air_mass import calculate_optical_air_mass_series
from pvgisprototype.api.irradiance.direct.refraction import calculate_refracted_solar_altitude_series
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    HOFIERKA_2002,
    LOG_LEVEL_DEFAULT,
    ECCENTRICITY_PHASE_OFFSET,
    SOLAR_CONSTANT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.core.arrays import create_array
from pvgisprototype.validation.values import identify_values_out_of_range


@log_function_call
@custom_cached
def calculate_clear_sky_direct_horizontal_irradiance_hofierka(
    elevation: float,
    timestamps: DatetimeIndex = DatetimeIndex([Timestamp.now(tz='UTC')]),
    solar_altitude_series: SolarAltitude | None = None,
    surface_in_shade_series: LocationShading | None = None,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LinkeTurbidityFactor(),
    solar_constant: float = SOLAR_CONSTANT,
    eccentricity_phase_offset: float = ECCENTRICITY_PHASE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> DirectHorizontalIrradiance:
    """Calculate the direct horizontal irradiance

    This function implements the algorithm described by Hofierka [1]_.

    Parameters
    ----------
    elevation : float
        elevation
    timestamps : DatetimeIndex
        timestamps
    solar_altitude_series : SolarAltitude | None
        solar_altitude_series
    surface_in_shade_series : LocationShading | None
        surface_in_shade_series
    linke_turbidity_factor_series : LinkeTurbidityFactor
        linke_turbidity_factor_series
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
    DirectHorizontalIrradiance

    Notes
    -----
    Known also as : SID, units : W*m-2

    References
    ----------
    .. [1] Hofierka, J. (2002). Some title of the paper. Journal Name, vol(issue), pages.

    """
    # expects solar altitude in degrees! ----------------------------------vvv
    #
    refracted_solar_altitude_series = calculate_refracted_solar_altitude_series(
        solar_altitude_series=solar_altitude_series,  # expects altitude in degrees!
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    optical_air_mass_series = calculate_optical_air_mass_series(
        elevation=elevation,
        refracted_solar_altitude_series=refracted_solar_altitude_series,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    #
    # ^^^ ---------------------------------------- expects solar altitude in degrees!

    direct_normal_irradiance_series = calculate_direct_normal_irradiance_hofierka(
        timestamps=timestamps,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        optical_air_mass_series=optical_air_mass_series,
        solar_constant=solar_constant,
        eccentricity_phase_offset=eccentricity_phase_offset,
        eccentricity_amplitude=eccentricity_amplitude,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
    )

    # Mask conditions
    mask_solar_altitude_positive = solar_altitude_series.radians > 0
    mask_not_in_shade = ~surface_in_shade_series.value
    mask_sunlit_surface_series = np.logical_and.reduce((mask_solar_altitude_positive, mask_not_in_shade))

    # Initialize the direct irradiance series to zeros
    array_parameters = {
        "shape": timestamps.shape,  # Borrow shape from timestamps
        "dtype": dtype,
        "init_method": "zeros",
        "backend": array_backend,
    }
    direct_horizontal_irradiance_series = create_array(**array_parameters)

    if np.any(mask_sunlit_surface_series):
        direct_horizontal_irradiance_series[mask_sunlit_surface_series] = (
            direct_normal_irradiance_series.value
            * np.sin(solar_altitude_series.radians)
        )[mask_sunlit_surface_series]

    out_of_range, out_of_range_index = identify_values_out_of_range(
        series=direct_horizontal_irradiance_series,
        shape=timestamps.shape,
        data_model=DirectHorizontalIrradiance(),
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=direct_horizontal_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return DirectHorizontalIrradiance(
        value=direct_horizontal_irradiance_series,
        out_of_range=out_of_range,
        out_of_range_index=out_of_range_index,
        elevation=elevation,
        solar_altitude=solar_altitude_series,
        refracted_solar_altitude=refracted_solar_altitude_series.value,
        optical_air_mass=optical_air_mass_series,
        direct_normal_irradiance=direct_normal_irradiance_series,
        surface_in_shade=surface_in_shade_series,
        solar_radiation_model=HOFIERKA_2002,
        data_source=HOFIERKA_2002,
    )
