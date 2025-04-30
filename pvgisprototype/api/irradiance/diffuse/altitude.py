from math import cos, pi, sin
from typing import List

import numpy as np
from devtools import debug

from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.algorithms.muneer.irradiance.diffuse.term_n import (
    calculate_term_n_series_hofierka,
)
from pvgisprototype.algorithms.muneer.irradiance.diffuse.sky_irradiance import (
    calculate_diffuse_sky_irradiance_series_hofierka,
)
from pvgisprototype.algorithms.hofierka.irradiance.diffuse.clear_sky.transmission_function import (
    calculate_diffuse_transmission_function_series_hofierka,
)
from pvgisprototype.algorithms.hofierka.irradiance.diffuse.clear_sky.altitude import (
    calculate_diffuse_solar_altitude_coefficients_series_hofierka,
    calculate_diffuse_solar_altitude_function_series_hofierka,
)
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call


@log_function_call
def calculate_term_n_series(
    kb_series: List[float],
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = 0,
    log: int = 0,
):
    """Define the N term for a period of time

    N = 0.00263 − 0.712 × kb − 0.6883 × kb2

    Parameters
    ----------
    kb_series: float
        Direct to extraterrestrial irradiance ratio

    Returns
    -------
    N: float
        The N term
    """
    term_n_series = calculate_term_n_series_hofierka(
            kb_series=kb_series,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
            )
    log_data_fingerprint(
        data=term_n_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return term_n_series


@log_function_call
def calculate_diffuse_sky_irradiance_series(
    n_series: List[float],
    surface_tilt: float | None = np.radians(45),
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    log: int = 0,
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
    """
    diffuse_sky_irradiance_series = calculate_diffuse_sky_irradiance_series_hofierka(
        n_series=n_series,
        surface_tilt=surface_tilt,
        dtype=dtype,
        array_backend=array_backend,
        log=log,
    )
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return diffuse_sky_irradiance_series


@log_function_call
def calculate_diffuse_transmission_function_series(
    linke_turbidity_factor_series,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = 0,
    log: int = 0,
) -> np.array:
    """Diffuse transmission function over a period of time

    Notes
    -----
    From r.pv's source code:

        tn = -0.015843 + locLinke * (0.030543 + 0.0003797 * locLinke);

    From Hofierka (2002) :

        The estimate of the transmission function Tn(TLK) gives a theoretical
        diffuse irradiance on a horizontal surface with the sun vertically
        overhead for the air mass 2 Linke turbidity factor. The following
        second order polynomial expression is used:

            Tn(TLK) = -0.015843 + 0.030543 TLK + 0.0003797 TLK^2

    """
    diffuse_transmission_series = calculate_diffuse_transmission_function_series_hofierka(
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        dtype=dtype,
        array_backend=array_backend,
        log=log,
    )
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return diffuse_transmission_series


@log_function_call
def calculate_diffuse_solar_altitude_coefficients_series(
    linke_turbidity_factor_series,
    verbose: int = 0,
    log: int = 0,
):
    """Calculate the diffuse solar altitude coefficients.

    Calculate the diffuse solar altitude coefficients over a period of time.

    Parameters
    ----------
    linke_turbidity_factor_series: (List[LinkeTurbidityFactor] or LinkeTurbidityFactor)
        The Linke turbidity factors as a list of LinkeTurbidityFactor objects
        or a single object.

    Returns
    -------

    """
    a1_series, a2_series, a3_series = (
        calculate_diffuse_solar_altitude_coefficients_series_hofierka(
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            verbose=verbose,
            log=log,
        )
    )
    if verbose == DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return a1_series, a2_series, a3_series


@log_function_call
def calculate_diffuse_solar_altitude_function_series(
    solar_altitude_series: List[float],
    linke_turbidity_factor_series: LinkeTurbidityFactor,
    verbose: int = 0,
    log: int = 0,
):
    """Calculate the diffuse solar altitude

    Notes
    -----
    Other symbol: function Fd

    """
    a1_series, a2_series, a3_series = (
        calculate_diffuse_solar_altitude_function_series_hofierka(
            solar_altitude_series=solar_altitude_series,
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            verbose=verbose,
            log=log,
        )
    )
    if verbose == DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return (
        a1_series
        + a2_series * np.sin(solar_altitude_series.radians)
        + a3_series * np.power(np.sin(solar_altitude_series.radians), 2)
    )
