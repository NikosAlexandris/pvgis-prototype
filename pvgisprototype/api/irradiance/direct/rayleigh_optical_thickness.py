"""
This Python module is part of PVGIS' API. It implements functions to calculate
the direct solar irradiance.

_Direct_ or _beam_ irradiance is one of the main components of solar
irradiance. It comes perpendicular from the Sun and is not scattered before it
irradiates a surface.

During a cloudy day the sunlight will be partially absorbed and scattered by
different air molecules. The latter part is defined as the _diffuse_
irradiance. The remaining part is the _direct_ irradiance.
"""
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from devtools import debug
import numpy as np
from pvgisprototype import SolarAltitude
from pvgisprototype import RefractedSolarAltitude
from pvgisprototype import OpticalAirMass
from pvgisprototype import RayleighThickness
from pvgisprototype import Elevation
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import AdjustElevationInputModel
from pvgisprototype.validation.functions import CalculateOpticalAirMassTimeSeriesInputModel
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import OPTICAL_AIR_MASS_UNIT
from pvgisprototype.constants import RAYLEIGH_OPTICAL_THICKNESS_UNIT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEGREES
from cachetools import cached
from pvgisprototype.caching import custom_hashkey


@log_function_call
@validate_with_pydantic(AdjustElevationInputModel)
def adjust_elevation(
    elevation: float,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
):
    """Modifier component for the solar altitude as per Hofierka, 2002

    This function implements a modifier component for the solar altitude for
    the given elevation described by Hofierka, 2002 [1]_

    Notes
    -----
    In PVGIS C source code:

        elevationCorr = exp(-sunVarGeom->z_orig / 8434.5);

    References
    ----------
    .. [1] Hofierka, J. (2002). Some title of the paper. Journal Name, vol(issue), pages.

    """
    adjusted_elevation = np.array(np.exp(-elevation.value / 8434.5), dtype=dtype)

    log_data_fingerprint(
        data=adjusted_elevation,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return Elevation(value=adjusted_elevation, unit="meters")


@log_function_call
@cached(cache={}, key=custom_hashkey)
def calculate_refracted_solar_altitude_series(
    solar_altitude_series: SolarAltitude,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = 0,
    log: int = 0,
) -> RefractedSolarAltitude:
    """Adjust the solar altitude angle for atmospheric refraction.

    Adjust the solar altitude angle for atmospheric refraction for a time
    series.
    
    Notes
    -----
    This function :
    - requires solar altitude values in degrees.
    - The output _should_ expectedly be of the same `dtype` as the input
      `solar_altitude_series` array.

    """
    atmospheric_refraction = (
        0.061359
        * (
            0.1594
            + 1.123 * solar_altitude_series.degrees
            + 0.065656 * np.power(solar_altitude_series.degrees, 2)
        )
        / (
            1
            + 28.9344 * solar_altitude_series.degrees
            + 277.3971 * np.power(solar_altitude_series.degrees, 2)
        )
    )
    refracted_solar_altitude_series = (
        solar_altitude_series.degrees + atmospheric_refraction
    )

    log_data_fingerprint(
        data=refracted_solar_altitude_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return RefractedSolarAltitude(
        value=refracted_solar_altitude_series,  # ensure output is of input dtype !
        unit=DEGREES,
    )


@log_function_call
@cached(cache={}, key=custom_hashkey)
@validate_with_pydantic(CalculateOpticalAirMassTimeSeriesInputModel)
def calculate_optical_air_mass_series(
    elevation: float,
    refracted_solar_altitude_series: RefractedSolarAltitude,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
) -> OpticalAirMass:
    """Approximate the relative optical air mass.

    Approximate the relative optical air mass for a time series.

    This function implements the algorithm described by Minzer et al. [1]_ 
    and Hofierka [2]_ (equation 5) in which the relative optical air mass
    (unitless) is defined as follows :

        m = (p/p0) / (sin h0_ref + 0.50572 (h0_ref + 6.07995)^(- 1.6364))
    
        where :

        - h0_ref is the corrected solar altitude h0 in degrees by the
          atmospheric refraction component ∆h0_ref:

    References
    ----------
    .. [1] Minzer, A., Champion, K. S. W., & Pond, H. L. (1959). 
           The ARDC Model Atmosphere. Air Force Surveys in Geophysics, 115. AFCRL.

    .. [2] Hofierka, 2002

    """
    adjusted_elevation = adjust_elevation(elevation.value)
    degrees_plus_offset = refracted_solar_altitude_series.degrees + 6.07995
    # Handle negative values subjected to np.power()
    power_values = np.where(
        degrees_plus_offset > 0, np.power(degrees_plus_offset, -1.6364), 0
    )
    optical_air_mass_series = adjusted_elevation.value / (
        np.sin(refracted_solar_altitude_series.radians)  # in radians for NumPy
        + 0.50572 * power_values
    )

    log_data_fingerprint(
        data=optical_air_mass_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return OpticalAirMass(
        value=optical_air_mass_series,
        unit=OPTICAL_AIR_MASS_UNIT,
    )


@log_function_call
@cached(cache={}, key=custom_hashkey)
def calculate_rayleigh_optical_thickness_series(
    optical_air_mass_series: OpticalAirMass, # OPTICAL_AIR_MASS_TIME_SERIES_DEFAULT
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
) -> RayleighThickness:
    """Calculate the Rayleigh optical thickness.

    Calculate Rayleigh optical thickness for a time series.

    """
    rayleigh_thickness_series = np.zeros_like(optical_air_mass_series.value, dtype=dtype)
    smaller_than_20 = optical_air_mass_series.value <= 20
    larger_than_20 = optical_air_mass_series.value > 20
    rayleigh_thickness_series[smaller_than_20] = 1 / (
        6.6296
        + 1.7513 * optical_air_mass_series.value[smaller_than_20]
        - 0.1202 * np.power(optical_air_mass_series.value[smaller_than_20], 2)
        + 0.0065 * np.power(optical_air_mass_series.value[smaller_than_20], 3)
        - 0.00013 * np.power(optical_air_mass_series.value[smaller_than_20], 4)
    )
    rayleigh_thickness_series[larger_than_20] = 1 / (
        10.4 + 0.718 * optical_air_mass_series.value[larger_than_20]
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=rayleigh_thickness_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )
    return RayleighThickness(
        value=rayleigh_thickness_series,
        unit=RAYLEIGH_OPTICAL_THICKNESS_UNIT,
    )
