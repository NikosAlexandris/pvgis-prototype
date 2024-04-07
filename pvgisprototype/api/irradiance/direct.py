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
from pvgisprototype.cli.messages import TO_MERGE_WITH_SINGLE_VALUE_COMMAND
from datetime import datetime
from zoneinfo import ZoneInfo
from math import sin
from math import asin
from math import cos
from math import atan
import numpy as np
from numpy import ndarray
from typing import Annotated
from typing import Optional
from typing import Union
from typing import Sequence
from typing import List
from pathlib import Path
from pvgisprototype import SolarAltitude
from pvgisprototype import RefractedSolarAltitude
from pvgisprototype import OpticalAirMass
from pvgisprototype import RayleighThickness
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype import Elevation
from pvgisprototype import Irradiance
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import AdjustElevationInputModel
from pvgisprototype.validation.functions import CalculateOpticalAirMassTimeSeriesInputModel
from pvgisprototype.api.position.models import validate_model
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.api.position.models import SolarIncidenceModel
from pvgisprototype.api.position.models import SOLAR_TIME_ALGORITHM_DEFAULT
from pvgisprototype.api.position.models import SOLAR_POSITION_ALGORITHM_DEFAULT
from pvgisprototype.api.position.models import SOLAR_INCIDENCE_ALGORITHM_DEFAULT
from pvgisprototype.api.position.altitude_series import model_solar_altitude_time_series
from pvgisprototype.api.position.azimuth_series import model_solar_azimuth_time_series
from pvgisprototype.api.position.incidence_series import model_solar_incidence_time_series
from pvgisprototype.api.irradiance.models import DirectIrradianceComponents
from pvgisprototype.api.irradiance.models import MethodsForInexactMatches
from pvgisprototype.api.irradiance.shade import is_surface_in_shade_time_series
from pvgisprototype.api.irradiance.extraterrestrial import calculate_extraterrestrial_normal_irradiance_time_series
from pvgisprototype.api.irradiance.loss import calculate_angular_loss_factor_for_direct_irradiance_time_series
from pvgisprototype.api.irradiance.limits import LOWER_PHYSICALLY_POSSIBLE_LIMIT
from pvgisprototype.api.irradiance.limits import UPPER_PHYSICALLY_POSSIBLE_LIMIT
from pvgisprototype.api.utilities.timestamp import timestamp_to_decimal_hours_time_series
# from pvgisprototype.api.utilities.progress import progress
# from rich.progress import Progress
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.api.utilities.conversions import convert_to_degrees_if_requested
from pvgisprototype.api.series.select import select_time_series
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.cli.print import print_irradiance_table_2
from pvgisprototype.constants import FINGERPRINT_COLUMN_NAME
from pvgisprototype.constants import TITLE_KEY_NAME
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import REFRACTED_SOLAR_ALTITUDE_COLUMN_NAME
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.constants import SOLAR_CONSTANT_COLUMN_NAME
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import PERIGEE_OFFSET_COLUMN_NAME
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME
from pvgisprototype.constants import LINKE_TURBIDITY_TIME_SERIES_DEFAULT
from pvgisprototype.constants import LINKE_TURBIDITY_UNIT
from pvgisprototype.constants import LINKE_TURBIDITY_COLUMN_NAME
from pvgisprototype.constants import LINKE_TURBIDITY_ADJUSTED_COLUMN_NAME
from pvgisprototype.constants import OPTICAL_AIR_MASS_TIME_SERIES_DEFAULT
from pvgisprototype.constants import OPTICAL_AIR_MASS_UNIT
from pvgisprototype.constants import OPTICAL_AIR_MASS_COLUMN_NAME
from pvgisprototype.constants import RAYLEIGH_OPTICAL_THICKNESS_UNIT
from pvgisprototype.constants import RAYLEIGH_OPTICAL_THICKNESS_COLUMN_NAME
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import IRRADIANCE_UNITS
from pvgisprototype.constants import ANGLE_UNITS_COLUMN_NAME
from pvgisprototype.constants import DEGREES
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import IRRADIANCE_SOURCE_COLUMN_NAME
from pvgisprototype.constants import RADIATION_MODEL_COLUMN_NAME
from pvgisprototype.constants import HOFIERKA_2002
from pvgisprototype.constants import LONGITUDE_COLUMN_NAME
from pvgisprototype.constants import LATITUDE_COLUMN_NAME
from pvgisprototype.constants import DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DIRECT_NORMAL_IRRADIANCE
from pvgisprototype.constants import DIRECT_NORMAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import LOSS_COLUMN_NAME
from pvgisprototype.constants import SURFACE_TILT_COLUMN_NAME
from pvgisprototype.constants import SURFACE_ORIENTATION_COLUMN_NAME
from pvgisprototype.constants import INCIDENCE_COLUMN_NAME
from pvgisprototype.constants import ALTITUDE_COLUMN_NAME
from pvgisprototype.constants import INCIDENCE_ALGORITHM_COLUMN_NAME
from pvgisprototype.constants import INCIDENCE_DEFINITION
from pvgisprototype.constants import POSITION_ALGORITHM_COLUMN_NAME
from pvgisprototype.constants import TIME_ALGORITHM_COLUMN_NAME
from pandas import DatetimeIndex
from cachetools import cached
from pvgisprototype.algorithms.caching import custom_hashkey
from pvgisprototype.validation.hashing import generate_hash
from rich import print
from pvgisprototype.constants import RANDOM_TIMESTAMPS_FLAG_DEFAULT


@log_function_call
def compare_temporal_resolution(
    timestamps: DatetimeIndex = None,
    array: ndarray = None,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
):
    """
    Check if the frequency of `timestamps` matches the temporal resolution of the `array`.
    
    Parameters
    ----------
    timestamps:
        An array of generated timestamps.
    array:
        An array of data corresponding to some time series.
    
    Raises
    ------
        ValueError: If the lengths of the timestamps and data_series don't match.
    """
    if len(timestamps) != len(array):
        raise ValueError(
            f"The frequency of `timestamps` ({len(timestamps)}) does not match the temporal resolution of the `array` ({len(array)}). Please ensure they have the same temporal resolution."
        )


@log_function_call
@validate_with_pydantic(AdjustElevationInputModel)
def adjust_elevation(
    elevation: float,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
):
    """Some correction for the given solar altitude 

    [1]_

    Notes
    -----

    In PVGIS C source code:

	elevationCorr = exp(-sunVarGeom->z_orig / 8434.5);

    References
    ----------

    .. [1] Hofierka, 2002
    """
    adjusted_elevation = np.array(np.exp(-elevation.value / 8434.5), dtype=dtype)

    log_data_fingerprint(
        data=adjusted_elevation,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return Elevation(value=adjusted_elevation, unit="meters")


@log_function_call
def correct_linke_turbidity_factor_time_series(
    linke_turbidity_factor_series: LinkeTurbidityFactor,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
) -> LinkeTurbidityFactor:
    """Calculate the air mass 2 Linke turbidity factor.

    Calculate the air mass 2 Linke atmospheric turbidity factor for a time series.

    Parameters
    ----------
    linke_turbidity_factor_series: (List[LinkeTurbidityFactor] or LinkeTurbidityFactor)
        The Linke turbidity factors as a list of LinkeTurbidityFactor objects
        or a single object.

    Returns
    -------
    List[LinkeTurbidityFactor] or LinkeTurbidityFactor
        The corrected Linke turbidity factors as a list of LinkeTurbidityFactor
        objects or a single object.

    """
    corrected_linke_turbidity_factors = -0.8662 * np.array(linke_turbidity_factor_series.value, dtype=dtype)

    log_data_fingerprint(
        data=corrected_linke_turbidity_factors,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return LinkeTurbidityFactor(
        value=corrected_linke_turbidity_factors,
        unit=LINKE_TURBIDITY_UNIT,
    )
    

@log_function_call
@cached(cache={}, key=custom_hashkey)
def calculate_refracted_solar_altitude_time_series(
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
def calculate_optical_air_mass_time_series(
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
def calculate_rayleigh_optical_thickness_time_series(
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


@log_function_call
@cached(cache={}, key=custom_hashkey)
def calculate_direct_normal_irradiance_time_series(
    timestamps: DatetimeIndex = None,
    # start_time: Optional[datetime] = None,
    # frequency: Optional[str] = None,
    # end_time: Optional[datetime] = None,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT, # REVIEW-ME + Typer Parser
    optical_air_mass_series: OpticalAirMass = [OPTICAL_AIR_MASS_TIME_SERIES_DEFAULT], # REVIEW-ME + ?
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    random_timestamps: bool = RANDOM_TIMESTAMPS_FLAG_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
    fingerprint: bool = False,
    show_progress: bool = True,
) -> np.array:
    """Calculate the direct normal irradiance.

    The direct normal irradiance represents the amount of solar radiation
    received per unit area by a surface that is perpendicular (normal) to the
    rays that come in a straight line from the direction of the sun at its
    current position in the sky.

    This function implements the algorithm described by Hofierka [1]_.

    Notes
    -----
    Known also as : SID, units : W*m-2

    References
    ----------
    .. [1] Hofierka, J. (2002). Some title of the paper. Journal Name, vol(issue), pages.

    """
    # with Progress(disable=not show_progress):
    extraterrestrial_normal_irradiance_series = (
        calculate_extraterrestrial_normal_irradiance_time_series(
            timestamps=timestamps,
            solar_constant=solar_constant,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            random_timestamps=random_timestamps,
            dtype=dtype,
            array_backend=array_backend,
        )
    )
    corrected_linke_turbidity_factor_series = correct_linke_turbidity_factor_time_series(
        linke_turbidity_factor_series,
        verbose=verbose,
    )
    rayleigh_optical_thickness_series = calculate_rayleigh_optical_thickness_time_series(
        optical_air_mass_series,
        verbose=verbose,
    )  # _quite_ high when the sun is below the horizon. Makes sense ?

    # Calculate
    direct_normal_irradiance_series = (
        extraterrestrial_normal_irradiance_series.value
        * np.exp(
            corrected_linke_turbidity_factor_series.value
            * optical_air_mass_series.value
            * rayleigh_optical_thickness_series.value
        )
    )
    # Warning
    if (
        (direct_normal_irradiance_series < LOWER_PHYSICALLY_POSSIBLE_LIMIT)
        | (direct_normal_irradiance_series > UPPER_PHYSICALLY_POSSIBLE_LIMIT)
    ).any():
        out_of_range_values = direct_normal_irradiance_series[
            (direct_normal_irradiance_series < LOWER_PHYSICALLY_POSSIBLE_LIMIT)
            | (direct_normal_irradiance_series > UPPER_PHYSICALLY_POSSIBLE_LIMIT)
        ]
        warning_unstyled = (
                f"\n"
                f"{WARNING_OUT_OF_RANGE_VALUES} "
                f"[{LOWER_PHYSICALLY_POSSIBLE_LIMIT}, {UPPER_PHYSICALLY_POSSIBLE_LIMIT}]"
                f" in direct_normal_irradiance_series : "
                f"{out_of_range_values}"
                f"\n"
                )
        warning = (
                f"\n"
                f"{WARNING_OUT_OF_RANGE_VALUES} "
                f"[{LOWER_PHYSICALLY_POSSIBLE_LIMIT}, {UPPER_PHYSICALLY_POSSIBLE_LIMIT}]"
                f" in [code]direct_normal_irradiance_series[/code] : "
                f"{out_of_range_values}"
                f"\n"
                )
        logger.warning(warning_unstyled, alt=warning)

    # Building the output dictionary=========================================

    components_container = {
        'main': lambda: {
            TITLE_KEY_NAME: DIRECT_NORMAL_IRRADIANCE,
            DIRECT_NORMAL_IRRADIANCE_COLUMN_NAME: direct_normal_irradiance_series,
            RADIATION_MODEL_COLUMN_NAME: HOFIERKA_2002,
        },

        'extended': lambda: {
            EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME: extraterrestrial_normal_irradiance_series,
        } if verbose > 1 else {},

        'more_extended': lambda: {
            LINKE_TURBIDITY_ADJUSTED_COLUMN_NAME: corrected_linke_turbidity_factor_series.value,
            LINKE_TURBIDITY_COLUMN_NAME: linke_turbidity_factor_series.value,
            RAYLEIGH_OPTICAL_THICKNESS_COLUMN_NAME: rayleigh_optical_thickness_series.value,
            OPTICAL_AIR_MASS_COLUMN_NAME: optical_air_mass_series.value,
        } if verbose > 2 else {},

        'even_more_extended': lambda: {
            SOLAR_CONSTANT_COLUMN_NAME: solar_constant,
            PERIGEE_OFFSET_COLUMN_NAME: perigee_offset,
            ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME: eccentricity_correction_factor,
        } if verbose > 3 else {},

        'fingerprint': lambda: {
            FINGERPRINT_COLUMN_NAME: generate_hash(direct_normal_irradiance_series),
        } if fingerprint else {},
    }

    components = {}
    for key, component in components_container.items():
        components.update(component())

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=direct_normal_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return Irradiance(
            value=direct_normal_irradiance_series,
            unit=IRRADIANCE_UNITS,
            position_algorithm="",
            timing_algorithm="",
            elevation=None,
            surface_orientation=None,
            surface_tilt=None,
            components=components,
            )


@log_function_call
@cached(cache={}, key=custom_hashkey)
def calculate_direct_horizontal_irradiance_time_series(
    longitude: float,
    latitude: float,
    elevation: float,
    timestamps: DatetimeIndex = None,
    start_time: Optional[datetime] = None,  # reuse callback inside function?
    frequency: Optional[str] = None,  # reuse callback inside function?
    end_time: Optional[datetime] = None,  # reuse callback inside function?
    timezone: Optional[str] = None,
    solar_time_model: SolarTimeModel = SOLAR_TIME_ALGORITHM_DEFAULT,
    time_offset_global: float = 0,
    hour_offset: float = 0,
    solar_position_model: SolarPositionModel = SOLAR_POSITION_ALGORITHM_DEFAULT,
    linke_turbidity_factor_series: LinkeTurbidityFactor = None, # [LINKE_TURBIDITY_TIME_SERIES_DEFAULT], # REVIEW-ME + Typer Parser
    apply_atmospheric_refraction: Optional[bool] = True,
    refracted_solar_zenith: Optional[float] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: str = 'minutes',
    angle_units: str = RADIANS,
    angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
    fingerprint: bool = False,
    index: bool = False,
    show_progress: bool = True,
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
    solar_time_model = validate_model(SolarTimeModel, solar_time_model)  # can be only one of!
    solar_altitude_series = model_solar_altitude_time_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        solar_time_model=solar_time_model,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
    )
    
    # expects solar altitude in degrees! ----------------------------------vvv
    refracted_solar_altitude_series = calculate_refracted_solar_altitude_time_series(
        solar_altitude_series=solar_altitude_series,   # expects altitude in degrees!
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    optical_air_mass_series = calculate_optical_air_mass_time_series(
        elevation=elevation,
        refracted_solar_altitude_series=refracted_solar_altitude_series,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    # ^^^ --------------------------------- expects solar altitude in degrees!
    direct_normal_irradiance_series = calculate_direct_normal_irradiance_time_series(
        timestamps=timestamps,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        optical_air_mass_series=optical_air_mass_series,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        dtype=dtype,
        array_backend=array_backend,
        verbose=0,
        show_progress=show_progress,
    )

    # Mask conditions -------------------------------------------------------
    mask_solar_altitude_positive = solar_altitude_series.radians > 0
    mask_not_in_shade = np.full_like(solar_altitude_series.radians, True)  # Stub, replace with actual condition
    mask = np.logical_and.reduce((mask_solar_altitude_positive, mask_not_in_shade))

    # Initialize the direct irradiance series to zeros
    direct_horizontal_irradiance_series = np.zeros_like(solar_altitude_series.radians)
    if np.any(mask):
        direct_horizontal_irradiance_series[mask] = (
            direct_normal_irradiance_series.value * np.sin(solar_altitude_series.radians)
        )[mask]

    # Building the output dictionary=========================================

    components_container = {
        'main': lambda: {
            TITLE_KEY_NAME: DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
            DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME: direct_horizontal_irradiance_series,
        },

        'extended': lambda: {
            TITLE_KEY_NAME: DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME + ' & relevant components',
            DIRECT_NORMAL_IRRADIANCE_COLUMN_NAME: direct_normal_irradiance_series.value,  # Important
            ALTITUDE_COLUMN_NAME: getattr(solar_altitude_series, angle_output_units),
            ANGLE_UNITS_COLUMN_NAME: angle_output_units,
        } if verbose > 1 else {},

        'more_extended': lambda: {
            LINKE_TURBIDITY_COLUMN_NAME: linke_turbidity_factor_series.value,
            OPTICAL_AIR_MASS_COLUMN_NAME: optical_air_mass_series.value,
            REFRACTED_SOLAR_ALTITUDE_COLUMN_NAME: refracted_solar_altitude_series.value if apply_atmospheric_refraction else np.full_like(refracted_solar_altitude_series.value, np.nan),#else np.array(["-"]),
        } if verbose > 2 else {},

        'even_more_extended': lambda: {
            RADIATION_MODEL_COLUMN_NAME: HOFIERKA_2002,
            POSITION_ALGORITHM_COLUMN_NAME: solar_position_model.value,
            TIME_ALGORITHM_COLUMN_NAME: solar_time_model.value,
            # "Shade": in_shade,
        } if verbose > 3 else {},

        'and_even_more_extended': lambda: {
            SOLAR_CONSTANT_COLUMN_NAME: solar_constant,
            PERIGEE_OFFSET_COLUMN_NAME: perigee_offset,
            ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME: eccentricity_correction_factor,
        } if verbose > 4 else {},

        'fingerprint': lambda: {
            FINGERPRINT_COLUMN_NAME: generate_hash(direct_horizontal_irradiance_series),
        } if fingerprint else {},
    }

    components = {}
    for key, component in components_container.items():
        components.update(component())

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=direct_horizontal_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return Irradiance(
            value=direct_horizontal_irradiance_series,
            unit=IRRADIANCE_UNITS,
            position_algorithm="",
            timing_algorithm="",
            elevation=elevation,
            surface_orientation=None,
            surface_tilt=None,
            components=components,
            )


@log_function_call
@cached(cache={}, key=custom_hashkey)
def calculate_direct_inclined_irradiance_time_series_pvgis(
    longitude: float,
    latitude: float,
    elevation: float,
    timestamps: DatetimeIndex = None,
    # start_time: Optional[datetime] = None,
    # frequency: Optional[str] = None,
    # end_time: Optional[datetime] = None,
    timezone: Optional[str] = None,
    random_timestamps: bool = False,
    convert_longitude_360: bool = False,
    direct_horizontal_component: Optional[Path] = None,
    neighbor_lookup: MethodsForInexactMatches = None,
    tolerance: Optional[float] = TOLERANCE_DEFAULT,
    mask_and_scale: bool = False,
    in_memory: bool = False,
    surface_orientation: Optional[float] = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: Optional[float] = SURFACE_TILT_DEFAULT,
    linke_turbidity_factor_series: LinkeTurbidityFactor = None,  # Changed this to np.ndarray
    apply_atmospheric_refraction: Optional[bool] = True,
    refracted_solar_zenith: Optional[float] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    apply_angular_loss_factor: Optional[bool] = True,
    solar_position_model: SolarPositionModel = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: SolarIncidenceModel = SOLAR_INCIDENCE_ALGORITHM_DEFAULT,
    complementary_incidence_angle: bool = True,  # Let Me Hardcoded, Read the docstring!
    solar_time_model: SolarTimeModel = SOLAR_TIME_ALGORITHM_DEFAULT,
    time_offset_global: float = 0,
    hour_offset: float = 0,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: str = 'minutes',
    angle_units: str = RADIANS,
    angle_output_units: str = RADIANS,
    rounding_places: Optional[int] = ROUNDING_PLACES_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
    fingerprint: bool = False,
    index: bool = False,
    show_progress: bool = True,
) -> np.array:
    """Calculate the direct irradiance incident on a tilted surface [W*m-2].

    This function implements the algorithm described by Hofierka [1]_.

    Notes
    -----

              B   ⋅ sin ⎛δ   ⎞                    
               hc       ⎝ exp⎠         ⎛ W ⎞
        B   = ────────────────     in  ⎜───⎟
         ic       sin ⎛h ⎞             ⎜ -2⎟           
                      ⎝ 0⎠             ⎝m  ⎠           

        or else :

        Direct Inclined = Direct Horizontal * sin( Solar Incidence ) / sin( Solar Altitude )

    The implementation by Hofierka (2002) uses the solar incidence angle
    between the sun-vetor and plance of the reference surface (as per Jenco,
    1992). This is very important and relates to the hardcoded value `True` for
    the `complementary_incidence_angle` input parameter of the function. We
    call this angle (definition) the _complementary_ incidence angle.

    For the losses due to reflectivity, the incidence angle modifier by Martin
    & Ruiz (2005) expects the incidence angle between the sun-vector and the
    surface-normal. Hence, the respective call of the function
    `calculate_angular_loss_factor_for_direct_irradiance_time_series()`,
    expects the complement of the angle defined by Jenco (1992). We call the
    incidence angle expected by the incidence angle modifier by Martin & Ruiz
    (2005) the _typical_ incidence angle.

    See also the documentation of the function
    `calculate_solar_incidence_time_series_jenco()`.

    References
    ----------
    .. [1] Hofierka, J. (2002). Some title of the paper. Journal Name, vol(issue), pages.

    """
    solar_incidence_series = model_solar_incidence_time_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        random_timestamps=random_timestamps,
        solar_incidence_model=solar_incidence_model,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
        complementary_incidence_angle=True,  # = between sun-vector and surface-plane!
        dtype=dtype,
        array_backend=array_backend,
        verbose=0,
        log=log,
    )
    solar_altitude_series = model_solar_altitude_time_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        solar_time_model=solar_time_model,
        # time_offset_global=time_offset_global,
        # hour_offset=hour_offset,
        # perigee_offset=perigee_offset,
        # eccentricity_correction_factor=eccentricity_correction_factor,
        # time_output_units=time_output_units,
        # angle_units=angle_units,
        # angle_output_units=angle_output_units,
        dtype=dtype,
        array_backend=array_backend,
        verbose=0,
        log=log,
    )
    solar_azimuth_series = model_solar_azimuth_time_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        solar_time_model=solar_time_model,
        # time_offset_global=time_offset_global,
        # hour_offset=hour_offset,
        # perigee_offset=perigee_offset,
        # eccentricity_correction_factor=eccentricity_correction_factor,
        # time_output_units=time_output_units,
        # angle_units=angle_units,
        # angle_output_units=angle_output_units,
        dtype=dtype,
        array_backend=array_backend,
        verbose=0,
        log=log,
    )

    # ========================================================================
    # Essentially, perform calculations for when:
    # - solar altitude > 0
    # - not in shade
    # - solar incidence > 0
    #
    # To add : ---------------------------------------------------------------
    mask_solar_altitude_positive = solar_altitude_series.radians > 0

    # Following, the _complementary_ solar incidence angle is used (Jenco, 1992)!
    mask_solar_incidence_positive = solar_incidence_series.radians > 0
    in_shade = is_surface_in_shade_time_series(
            solar_altitude_series,
            solar_azimuth_series,
            )
    mask_not_in_shade = ~in_shade
    mask = np.logical_and.reduce(
        (mask_solar_altitude_positive, mask_solar_incidence_positive, mask_not_in_shade)
    )
    # Else, the following runs:
    # --------------------------------- Review & Add ?
    # 1. surface is shaded
    # 3. solar incidence = 0
    # --------------------------------- Review & Add ?
    # ========================================================================

    if not direct_horizontal_component:
        if verbose > 0:
            logger.info(':information: [bold][magenta]Modelling[/magenta] direct horizontal irradiance[/bold]...')
        direct_horizontal_irradiance_series = calculate_direct_horizontal_irradiance_time_series(
            longitude=longitude,  # required by some of the solar time algorithms
            latitude=latitude,
            elevation=elevation,
            timestamps=timestamps,
            # start_time=start_time,
            # frequency=frequency,
            # end_time=end_time,
            timezone=timezone,
            solar_position_model=solar_position_model,
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            refracted_solar_zenith=refracted_solar_zenith,
            solar_time_model=solar_time_model,
            time_offset_global=time_offset_global,
            hour_offset=hour_offset,
            solar_constant=solar_constant,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            time_output_units=time_output_units,
            angle_units=angle_units,
            angle_output_units=angle_output_units,
            dtype=dtype,
            array_backend=array_backend,
            verbose=0,  # no verbosity here by choice!
            log=log,
            show_progress=show_progress,
        ).value  # Important
    else:  # read from a time series dataset
        if verbose > 0:
            logger.info(':information: [bold]Reading[/bold] the [magenta]direct horizontal irradiance[/magenta] from [bold]external dataset[/bold]...')
        direct_horizontal_irradiance_series = select_time_series(
            time_series=direct_horizontal_component,
            # longitude=longitude_for_selection,
            # latitude=latitude_for_selection,
            longitude=convert_float_to_degrees_if_requested(longitude, DEGREES),
            latitude=convert_float_to_degrees_if_requested(latitude, DEGREES),
            timestamps=timestamps,
            # start_time=start_time,
            # end_time=end_time,
            # convert_longitude_360=convert_longitude_360,
            neighbor_lookup=neighbor_lookup,
            tolerance=tolerance,
            mask_and_scale=mask_and_scale,
            in_memory=in_memory,
            verbose=0,  # no verbosity here by choice!
            log=log,
        ).to_numpy().astype(dtype=dtype)

    try:
        # the number of timestamps should match the number of "x" values
        if verbose > 0:
            logger.info('\ni [bold]Calculating[/bold] the [magenta]direct inclined irradiance[/magenta] ..')
        compare_temporal_resolution(
            timestamps, direct_horizontal_irradiance_series
        )
        direct_inclined_irradiance_series = (
            direct_horizontal_irradiance_series
            * np.sin(solar_incidence_series.radians)
            / np.sin(solar_altitude_series.radians)
        )

    except ZeroDivisionError:
        logger.error(f"Error: Division by zero in calculating the direct inclined irradiance!")
        logger.debug("Is the solar altitude angle zero?")
        print("Is the solar altitude angle zero?")
        # should this return something? Like in r.sun's simpler's approach?
        raise ValueError

    if apply_angular_loss_factor:

        try:
            # per Martin & Ruiz 2005,
            # expects the _typical_ sun-vector-to-normal-of-surface incidence angles
            # which is the _complementary_ of the incidence angle per Hofierka 2002
            angular_loss_factor_series = (
                calculate_angular_loss_factor_for_direct_irradiance_time_series(
                    solar_incidence_series=(np.pi/2 - solar_incidence_series.value),
                    verbose=0,
                )
            )
            direct_inclined_irradiance_series *= angular_loss_factor_series

        except ZeroDivisionError as e:
            logger.error(f"Which Error? {e}")
            raise ValueError

    if np.any(direct_inclined_irradiance_series < 0):
        logger.info("\n[red]Warning: Negative values found in `direct_inclined_irradiance_series`![/red]")

    components_container = {
        'main': lambda: {
            TITLE_KEY_NAME: DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME,
            DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME: direct_inclined_irradiance_series,
            RADIATION_MODEL_COLUMN_NAME: 'External data' if direct_horizontal_component else HOFIERKA_2002,
        },

        'extended': lambda: {
            LOSS_COLUMN_NAME: 1 - angular_loss_factor_series if apply_angular_loss_factor else ['-'],
        } if verbose > 1 else {},

        'more_extended': lambda: {
            SURFACE_ORIENTATION_COLUMN_NAME: convert_float_to_degrees_if_requested(surface_orientation, angle_output_units),
            SURFACE_TILT_COLUMN_NAME: convert_float_to_degrees_if_requested(surface_tilt, angle_output_units),
            ANGLE_UNITS_COLUMN_NAME: angle_output_units,
        } if verbose > 2 else {},

        'even_more_extended': lambda: {
            TITLE_KEY_NAME: DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME + ' & relevant components',
            DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME: direct_horizontal_irradiance_series,
            # "Shade": in_shade,
        } if verbose > 3 else {},

        'and_even_more_extended': lambda: {
            INCIDENCE_COLUMN_NAME: getattr(solar_incidence_series, angle_output_units),
            INCIDENCE_ALGORITHM_COLUMN_NAME: solar_incidence_model.value,
            INCIDENCE_DEFINITION: 'Sun-to-Plane' if complementary_incidence_angle else 'Sun-to-Surface-Normal',
            ALTITUDE_COLUMN_NAME: getattr(solar_altitude_series, angle_output_units),
        } if verbose > 4 else {},
        
        'extra': lambda: {
            POSITION_ALGORITHM_COLUMN_NAME: solar_position_model.value,
            TIME_ALGORITHM_COLUMN_NAME: solar_time_model.value,
            SOLAR_CONSTANT_COLUMN_NAME: solar_constant,
            PERIGEE_OFFSET_COLUMN_NAME: perigee_offset,
            ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME: eccentricity_correction_factor,
        } if verbose > 5 else {},

        'fingerprint': lambda: {
            FINGERPRINT_COLUMN_NAME: generate_hash(direct_inclined_irradiance_series),
        } if fingerprint else {},
    }

    components = {}
    for key, component in components_container.items():
        components.update(component())

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=direct_inclined_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return Irradiance(
            value=direct_inclined_irradiance_series,
            unit=IRRADIANCE_UNITS,
            position_algorithm="",
            timing_algorithm="",
            elevation=elevation,
            surface_orientation=surface_orientation,
            surface_tilt=surface_tilt,
            components=components,
            )
