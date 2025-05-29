from math import cos, pi, sin
from devtools import debug
from numpy import array, ndarray, power

from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    SURFACE_TILT_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.validation.values import identify_values_out_of_range


@log_function_call
@custom_cached
def calculate_diffuse_sky_irradiance_series_hofierka(
    n_series: ndarray,
    surface_tilt: float = SURFACE_TILT_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
):
    """Calculate the diffuse sky irradiance

    The diffuse sky irradiance function F(γN) depends on the surface tilt `γN`
    (in radians)

    Parameters
    ----------
    surface_tilt: float (radians)
        The tilt (also referred to as : inclination or slope) angle of a solar
        surface

    n_series: float
        The term N

    Returns
    -------

    Notes
    -----
    Internally the function calculates first the dimensionless fraction of the
    sky dome viewed by a tilted (or inclined) surface `ri(γN)`.

    The sky-view fraction as defined in Hofierka, 2002 [1]_ is :

        (1 + cos(surface_tilt)) / 2
    
    which in turn is trigonometrically identical to the definition in Muneer,
    1990 [2]_

        power(cos(surface_tilt / 2), 2)

    """
    diffuse_sky_irradiance_series = ((1 + cos(surface_tilt)) / 2) + (
        sin(surface_tilt)
        - surface_tilt * cos(surface_tilt)
        - pi * power((sin(surface_tilt / 2)), 2)
    ) * n_series

    # out_of_range, out_of_range_index = identify_values_out_of_range(
    #     series=diffuse_sky_irradiance_series,
    #     shape=n_series.shape,
    #     # data_model=DiffuseSkyReflectedHorizontalIrradianceFromExternalData(),
    # )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=diffuse_sky_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return array(diffuse_sky_irradiance_series, dtype=dtype)
