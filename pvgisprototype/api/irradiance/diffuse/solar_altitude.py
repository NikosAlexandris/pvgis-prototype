from pvgisprototype.log import logger
from pvgisprototype.api.series.hardcodings import exclamation_mark
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from devtools import debug
from pandas import DatetimeIndex
from pathlib import Path
from typing import Optional
from typing import List
from rich import print
import numpy as np
from math import cos, sin, pi
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype import Irradiance
from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.api.position.models import SolarIncidenceModel
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.api.position.models import SOLAR_TIME_ALGORITHM_DEFAULT
from pvgisprototype.api.position.models import SOLAR_POSITION_ALGORITHM_DEFAULT
from pvgisprototype.api.position.models import SOLAR_INCIDENCE_ALGORITHM_DEFAULT
from pvgisprototype.api.position.altitude import model_solar_altitude_series
from pvgisprototype.api.position.incidence import model_solar_incidence_series
from pvgisprototype.api.position.azimuth import model_solar_azimuth_series
from pvgisprototype.api.irradiance.direct.horizontal import calculate_direct_horizontal_irradiance_series
from pvgisprototype.api.irradiance.extraterrestrial import calculate_extraterrestrial_normal_irradiance_series
from pvgisprototype.api.irradiance.limits import LOWER_PHYSICALLY_POSSIBLE_LIMIT
from pvgisprototype.api.irradiance.limits import UPPER_PHYSICALLY_POSSIBLE_LIMIT
from pvgisprototype.api.irradiance.loss import calculate_angular_loss_factor_for_nondirect_irradiance
from pvgisprototype.api.series.select import select_time_series
from pvgisprototype.api.series.models import MethodForInexactMatches
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.api.utilities.conversions import convert_series_to_degrees_arrays_if_requested
from pvgisprototype.validation.hashing import generate_hash
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.constants import FINGERPRINT_COLUMN_NAME
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_COLUMN_NAME
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RANDOM_DAY_FLAG_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import IRRADIANCE_UNITS
from pvgisprototype.constants import TERM_N_IN_SHADE
from pvgisprototype.constants import LINKE_TURBIDITY_UNIT
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import DEGREES
from pvgisprototype.constants import MASK_AND_SCALE_FLAG_DEFAULT
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.constants import NOT_AVAILABLE
from pvgisprototype.constants import ANGLE_UNITS_COLUMN_NAME
from pvgisprototype.constants import TITLE_KEY_NAME
from pvgisprototype.constants import LOSS_COLUMN_NAME
from pvgisprototype.constants import SURFACE_TILT_COLUMN_NAME
from pvgisprototype.constants import AZIMUTH_COLUMN_NAME
from pvgisprototype.constants import ALTITUDE_COLUMN_NAME
from pvgisprototype.constants import GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DIFFUSE_INCLINED_IRRADIANCE
from pvgisprototype.constants import DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DIFFUSE_INCLINED_IRRADIANCE_BEFORE_LOSS_COLUMN_NAME
from pvgisprototype.constants import DIFFUSE_HORIZONTAL_IRRADIANCE
from pvgisprototype.constants import DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DIFFUSE_CLEAR_SKY_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import EXTRATERRESTRIAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import LINKE_TURBIDITY_COLUMN_NAME
from pvgisprototype.constants import LINKE_TURBIDITY_TIME_SERIES_DEFAULT
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import ANGULAR_LOSS_FACTOR_FLAG_DEFAULT
from pvgisprototype.constants import INCIDENCE_COLUMN_NAME
from pvgisprototype.constants import INCIDENCE_ALGORITHM_COLUMN_NAME
from pvgisprototype.constants import OUT_OF_RANGE_INDICES_COLUMN_NAME
from pvgisprototype.constants import TERM_N_COLUMN_NAME
from pvgisprototype.constants import KB_RATIO_COLUMN_NAME
from pvgisprototype.constants import AZIMUTH_DIFFERENCE_COLUMN_NAME
from pvgisprototype.constants import RADIATION_MODEL_COLUMN_NAME
from pvgisprototype.constants import HOFIERKA_2002
from pvgisprototype.constants import RANDOM_TIMESTAMPS_FLAG_DEFAULT
from pvgisprototype.constants import MINUTES
from pvgisprototype.constants import MULTI_THREAD_FLAG_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT
from pvgisprototype.constants import FINGERPRINT_FLAG_DEFAULT
from pvgisprototype.constants import NEIGHBOR_LOOKUP_DEFAULT
from pvgisprototype.constants import IN_MEMORY_FLAG_DEFAULT


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
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    kb_series = np.array(kb_series, dtype=dtype)
    term_n_series = 0.00263 - (0.712 * kb_series) - (0.6883 * np.power(kb_series, 2, dtype=dtype))

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
    surface_tilt: Optional[float] = np.radians(45),
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
    # sky_view_fraction = (1 + cos(surface_tilt)) / 2
    diffuse_sky_irradiance_series = ((1 + cos(surface_tilt)) / 2) + (
        sin(surface_tilt)
        - surface_tilt
        * cos(surface_tilt)
        - pi * np.power((sin(surface_tilt / 2)), 2)
    ) * n_series

    return np.array(diffuse_sky_irradiance_series, dtype=dtype)


@log_function_call
def diffuse_transmission_function_series(
    linke_turbidity_factor_series,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = 0,
    log: int = 0,
) -> np.array:
    """ Diffuse transmission function over a period of time

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
    linke_turbidity_factor_series_squared_array = np.power(
        linke_turbidity_factor_series.value, 2, dtype=dtype
    )
    diffuse_transmission_series = (
        -0.015843
        + 0.030543 * linke_turbidity_factor_series.value
        + 0.0003797 * linke_turbidity_factor_series_squared_array
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
    linke_turbidity_factor_series_squared_array = np.power(linke_turbidity_factor_series.value, 2)
    diffuse_transmission_series = diffuse_transmission_function_series(linke_turbidity_factor_series)
    diffuse_transmission_series_array = np.array(diffuse_transmission_series)
    a1_prime_series = (
        0.26463
        - 0.061581 * linke_turbidity_factor_series.value
        + 0.0031408 * linke_turbidity_factor_series_squared_array
    )
    a1_series = np.where(
        a1_prime_series * diffuse_transmission_series < 0.0022, 
        np.maximum(0.0022 / diffuse_transmission_series_array, a1_prime_series), 
        a1_prime_series
    )
    a2_series = (
        2.04020
        + 0.018945 * linke_turbidity_factor_series.value
        - 0.011161 * linke_turbidity_factor_series_squared_array
    )
    a3_series = (
        -1.3025
        + 0.039231 * linke_turbidity_factor_series.value
        + 0.0085079 * linke_turbidity_factor_series_squared_array
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
    a1_series, a2_series, a3_series = calculate_diffuse_solar_altitude_coefficients_series(
        linke_turbidity_factor_series
    )

    return (
        a1_series
        + a2_series * np.sin(solar_altitude_series.radians)
        + a3_series * np.power(np.sin(solar_altitude_series.radians), 2)
    )
