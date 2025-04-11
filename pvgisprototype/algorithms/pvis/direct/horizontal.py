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

from pvgisprototype import DirectHorizontalIrradiance, LinkeTurbidityFactor, SolarAltitude
from pvgisprototype.api.irradiance.direct.normal import (
    calculate_direct_normal_irradiance_series,
)
from pvgisprototype.api.irradiance.direct.rayleigh_optical_thickness import (
    calculate_optical_air_mass_series,
    calculate_refracted_solar_altitude_series,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    DIRECT_HORIZONTAL_IRRADIANCE,
    ECCENTRICITY_CORRECTION_FACTOR,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    HOFIERKA_2002,
    IRRADIANCE_UNIT,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    PERIGEE_OFFSET,
    SOLAR_CONSTANT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.core.arrays import create_array
from numpy import ndarray


@log_function_call
@custom_cached
def calculate_direct_horizontal_irradiance_series_pvgis(
    elevation: float,
    timestamps: DatetimeIndex | None = DatetimeIndex([Timestamp.now(tz='UTC')]),
    solar_altitude_series: SolarAltitude | None = None,
    surface_in_shade_series: ndarray | None = None,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
) -> np.ndarray:
    """Calculate the direct horizontal irradiance

    This function implements the algorithm described by Hofierka [1]_.

    Notes
    -----
    Known also as : SID, units : W*m-2

    References
    ----------
    .. [1] Hofierka, J. (2002). Some title of the paper. Journal Name, vol(issue), pages.

    """
    # expects solar altitude in degrees! ----------------------------------vvv
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
    # ^^^ --------------------------------- expects solar altitude in degrees!
    direct_normal_irradiance_series = calculate_direct_normal_irradiance_series(
        timestamps=timestamps,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        optical_air_mass_series=optical_air_mass_series,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
    )

    # Mask conditions -------------------------------------------------------
    mask_solar_altitude_positive = solar_altitude_series.radians > 0
    mask_not_in_shade = ~surface_in_shade_series
    mask = np.logical_and.reduce((mask_solar_altitude_positive, mask_not_in_shade))

    # Initialize the direct irradiance series to zeros
    array_parameters = {
        "shape": timestamps.shape,
        "dtype": dtype,
        "init_method": "zeros",
        "backend": array_backend,
    }  # Borrow shape from timestamps
    direct_horizontal_irradiance_series = create_array(**array_parameters)
    if np.any(mask):
        direct_horizontal_irradiance_series[mask] = (
            direct_normal_irradiance_series.value
            * np.sin(solar_altitude_series.radians)
        )[mask]

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=direct_horizontal_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return DirectHorizontalIrradiance(
        name='Direct horizontal irradiance',
        title=DIRECT_HORIZONTAL_IRRADIANCE,
        value=direct_horizontal_irradiance_series,
        unit=IRRADIANCE_UNIT,
        elevation=elevation,
        solar_altitude=solar_altitude_series,
        refracted_solar_altitude=refracted_solar_altitude_series.value,
        optical_air_mass=optical_air_mass_series,
        direct_normal_irradiance=direct_normal_irradiance_series,
        surface_in_shade=surface_in_shade_series,
        solar_radiation_model=HOFIERKA_2002,
        data_source=HOFIERKA_2002,
    )
