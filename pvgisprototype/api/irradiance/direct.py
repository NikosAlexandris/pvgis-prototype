"""
_Direct_ or _beam_ irradiance is one of the main components of solar
irradiance. It comes perpendicular from the Sun and is not scattered before it
irradiates a surface.

During a cloudy day the sunlight will be partially absorbed and scattered by
different air molecules. The latter part is defined as the _diffuse_
irradiance. The remaining part is the _direct_ irradiance.
"""
from devtools import debug
from loguru import logger
from pvgisprototype.cli.messages import TO_MERGE_WITH_SINGLE_VALUE_COMMAND
from datetime import datetime
from math import sin
from math import asin
from math import cos
from math import atan
import numpy as np
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.validation.parameters import BaseTimestampSeriesModel
from pvgisprototype.cli.typer_parameters import OrderCommands
from pvgisprototype.api.geometry.models import validate_model
from pvgisprototype.api.geometry.models import SolarTimeModels
from pvgisprototype.api.geometry.models import SolarPositionModels
from pvgisprototype.api.geometry.models import SolarIncidenceModels
from pvgisprototype.api.geometry.models import SOLAR_TIME_ALGORITHM_DEFAULT
from pvgisprototype.api.geometry.models import SOLAR_POSITION_ALGORITHM_DEFAULT
from pvgisprototype.api.geometry.models import SOLAR_INCIDENCE_ALGORITHM_DEFAULT
from pvgisprototype.api.irradiance.models import DirectIrradianceComponents
from pvgisprototype.api.irradiance.models import MethodsForInexactMatches
from typing import Annotated
from typing import Optional
from typing import Union
from typing import Sequence
from typing import List
from pvgisprototype.api.geometry.altitude_series import model_solar_altitude_time_series
from pvgisprototype.api.geometry.incidence_series import model_solar_incidence_time_series
from pvgisprototype.api.utilities.timestamp import timestamp_to_decimal_hours_time_series
from pvgisprototype.api.utilities.progress import progress
from pvgisprototype.api.irradiance.extraterrestrial import calculate_extraterrestrial_normal_irradiance_time_series
from pvgisprototype.api.irradiance.loss import calculate_angular_loss_factor_for_direct_irradiance_time_series
from rich import print
from pvgisprototype.api.series.statistics import print_series_statistics
from pvgisprototype.cli.csv import write_irradiance_csv
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_series_irradiance
from pvgisprototype.cli.typer_parameters import typer_argument_longitude
from pvgisprototype.cli.typer_parameters import typer_argument_latitude
from pvgisprototype.cli.typer_parameters import typer_argument_elevation
from pvgisprototype.cli.typer_parameters import typer_argument_timestamps
from pvgisprototype.cli.typer_parameters import typer_option_start_time
from pvgisprototype.cli.typer_parameters import typer_option_frequency
from pvgisprototype.cli.typer_parameters import typer_option_end_time
from pvgisprototype.cli.typer_parameters import typer_option_convert_longitude_360
from pvgisprototype.cli.typer_parameters import typer_option_timezone
from pvgisprototype.cli.typer_parameters import typer_option_direct_horizontal_irradiance
from pvgisprototype.cli.typer_parameters import typer_option_mask_and_scale
from pvgisprototype.cli.typer_parameters import typer_option_nearest_neighbor_lookup
from pvgisprototype.cli.typer_parameters import typer_option_inexact_matches_method
from pvgisprototype.cli.typer_parameters import typer_option_tolerance
from pvgisprototype.cli.typer_parameters import typer_option_in_memory
from pvgisprototype.cli.typer_parameters import typer_option_linke_turbidity_factor_series
from pvgisprototype.cli.typer_parameters import typer_option_optical_air_mass_series
from pvgisprototype.cli.typer_parameters import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer_parameters import typer_option_refracted_solar_zenith
from pvgisprototype.cli.typer_parameters import typer_option_apply_angular_loss_factor
from pvgisprototype.cli.typer_parameters import typer_option_surface_tilt
from pvgisprototype.cli.typer_parameters import typer_option_surface_orientation
from pvgisprototype.cli.typer_parameters import typer_option_solar_incidence_model
from pvgisprototype.cli.typer_parameters import typer_option_solar_position_model
from pvgisprototype.cli.typer_parameters import typer_option_solar_time_model
from pvgisprototype.cli.typer_parameters import typer_option_global_time_offset
from pvgisprototype.cli.typer_parameters import typer_option_hour_offset
from pvgisprototype.cli.typer_parameters import typer_option_solar_constant
from pvgisprototype.cli.typer_parameters import typer_option_perigee_offset
from pvgisprototype.cli.typer_parameters import typer_option_eccentricity_correction_factor
from pvgisprototype.cli.typer_parameters import typer_option_time_output_units
from pvgisprototype.cli.typer_parameters import typer_option_angle_units
from pvgisprototype.cli.typer_parameters import typer_option_angle_output_units
from pvgisprototype.cli.typer_parameters import typer_option_rounding_places
from pvgisprototype.cli.typer_parameters import typer_option_statistics
from pvgisprototype.cli.typer_parameters import typer_option_csv
from pvgisprototype.cli.typer_parameters import typer_option_verbose
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.cli.typer_parameters import typer_option_index
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
from pvgisprototype.constants import RANDOM_DAY_SERIES_FLAG_DEFAULT
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
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import IRRADIANCE_UNITS
from pvgisprototype.constants import DEGREES
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import IRRADIANCE_SOURCE_COLUMN_NAME
from pvgisprototype.constants import IRRADIANCE_ALGORITHM_HOFIERKA_2002
from pvgisprototype.constants import LONGITUDE_COLUMN_NAME
from pvgisprototype.constants import LATITUDE_COLUMN_NAME
from pvgisprototype.constants import DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DIRECT_NORMAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import LOSS_COLUMN_NAME
from pvgisprototype.constants import SURFACE_TILT_COLUMN_NAME
from pvgisprototype.constants import SURFACE_ORIENTATION_COLUMN_NAME
from pvgisprototype.constants import INCIDENCE_COLUMN_NAME
from pvgisprototype.constants import ALTITUDE_COLUMN_NAME
from pvgisprototype.constants import INCIDENCE_ALGORITHM_COLUMN_NAME
from pvgisprototype.constants import POSITION_ALGORITHM_COLUMN_NAME
from pvgisprototype.constants import TIME_ALGORITHM_COLUMN_NAME
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.api.utilities.conversions import convert_to_degrees_if_requested
from pvgisprototype.api.utilities.conversions import convert_series_to_degrees_if_requested
from pvgisprototype.api.utilities.conversions import convert_series_to_degrees_arrays_if_requested
from pvgisprototype.api.utilities.conversions import convert_series_to_radians_if_requested
from zoneinfo import ZoneInfo
from pvgisprototype import SolarAltitude
from pvgisprototype import RefractedSolarAltitude
from pvgisprototype import OpticalAirMass
from pvgisprototype import RayleighThickness
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.api.series.select import select_time_series
# from pvgisprototype.api.series.utilities import select_location_time_series
from pathlib import Path
from pvgisprototype.validation.functions import CalculateOpticalAirMassTimeSeriesInputModel
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.cli.print import print_irradiance_table_2
from pvgisprototype.validation.functions import AdjustElevationInputModel
from pvgisprototype import Elevation


def compare_temporal_resolution(timestamps, array):
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


@validate_with_pydantic(AdjustElevationInputModel)
def adjust_elevation(
    elevation: Annotated[float, typer_argument_elevation],
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
    adjusted_elevation = np.exp(-elevation.value / 8434.5)
    return Elevation(value=adjusted_elevation, unit="meters")


def correct_linke_turbidity_factor_time_series(
    linke_turbidity_factor_series: LinkeTurbidityFactor,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
) -> LinkeTurbidityFactor:
    """
    Vectorized function to calculate the air mass 2 Linke atmospheric turbidity factor for a time series.

    Parameters:
    - linke_turbidity_factor_series (List[LinkeTurbidityFactor] or LinkeTurbidityFactor): 
      The Linke turbidity factors as a list of LinkeTurbidityFactor objects or a single object.

    Returns:
    - List[LinkeTurbidityFactor] or LinkeTurbidityFactor: 
      The corrected Linke turbidity factors as a list of LinkeTurbidityFactor objects or a single object.
    """
    # Perform calculations
    corrected_linke_turbidity_factors_array = -0.8662 * linke_turbidity_factor_series.value

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    corrected_linke_turbidity_factors = LinkeTurbidityFactor(
        value=corrected_linke_turbidity_factors_array,
        unit=LINKE_TURBIDITY_UNIT,
    )
    return corrected_linke_turbidity_factors


def calculate_refracted_solar_altitude_time_series(
    solar_altitude_series:SolarAltitude,
    verbose: int = 0,
) -> RefractedSolarAltitude:
    """Adjust the solar altitude angle for atmospheric refraction for a time series.
    
    Note
    ----
    This function is vectorized to handle arrays of solar altitudes.
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
    refracted_solar_altitude_series_array = (
        solar_altitude_series.degrees + atmospheric_refraction
    )

    refracted_solar_altitude_series = RefractedSolarAltitude(
        value=refracted_solar_altitude_series_array,
        unit=DEGREES,
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return refracted_solar_altitude_series


@validate_with_pydantic(CalculateOpticalAirMassTimeSeriesInputModel)
def calculate_optical_air_mass_time_series(
    elevation: Annotated[float, typer_argument_elevation],
    refracted_solar_altitude_series: RefractedSolarAltitude,
    verbose: Annotated[int, typer_option_verbose] = 0,
) -> OpticalAirMass:
    """Vectorized function to approximate the relative optical air mass for a time series.
    This function implements the algorithm described by Minzer et al. [1]_ 
    and Hofierka [2]_ in which the relative optical air mass (unitless) is
    defined as follows :

        m = (p / p0) / (sin h0_ref + 0.50572 (h0_ref + 6.07995) - 1.6364)
    
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
    optical_air_mass_series = adjusted_elevation.value / (
        np.sin(refracted_solar_altitude_series.radians)
        + 0.50572
        * np.power((refracted_solar_altitude_series.degrees + 6.07995), -1.6364)
    )

    optical_air_mass_series = OpticalAirMass(
        value=optical_air_mass_series,
        unit=OPTICAL_AIR_MASS_UNIT,
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    if verbose > 1:
        print(f'Optical air mass series : {optical_air_mass_series}')

    return optical_air_mass_series


def calculate_rayleigh_optical_thickness_time_series(
    optical_air_mass_series: OpticalAirMass, # OPTICAL_AIR_MASS_TIME_SERIES_DEFAULT
    verbose: int = VERBOSE_LEVEL_DEFAULT,
) -> RayleighThickness:
    """Vectorized function to calculate Rayleigh optical thickness for a time series."""
    # Perform calculations
    rayleigh_thickness_series_array = np.zeros_like(optical_air_mass_series.value, dtype=float)
    smaller_than_20 = optical_air_mass_series.value <= 20
    larger_than_20 = optical_air_mass_series.value > 20
    rayleigh_thickness_series_array[smaller_than_20] = 1 / (
        6.6296
        + 1.7513 * optical_air_mass_series.value[smaller_than_20]
        - 0.1202 * np.power(optical_air_mass_series.value[smaller_than_20], 2)
        + 0.0065 * np.power(optical_air_mass_series.value[smaller_than_20], 3)
        - 0.00013 * np.power(optical_air_mass_series.value[smaller_than_20], 4)
    )
    rayleigh_thickness_series_array[larger_than_20] = 1 / (
        10.4 + 0.718 * optical_air_mass_series.value[larger_than_20]
    )
    rayleigh_thickness_series = RayleighThickness(
        value=rayleigh_thickness_series_array,
        unit=RAYLEIGH_OPTICAL_THICKNESS_UNIT,
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    if verbose > 1:
        print(f'Rayleigh thickness series : {rayleigh_thickness_series}')

    return rayleigh_thickness_series


def calculate_direct_normal_irradiance_time_series(
    timestamps: BaseTimestampSeriesModel = None,
    start_time: Optional[datetime] = None,
    frequency: Optional[str] = None,
    end_time: Optional[datetime] = None,
    linke_turbidity_factor_series: LinkeTurbidityFactor = [LINKE_TURBIDITY_TIME_SERIES_DEFAULT], # REVIEW-ME + Typer Parser
    optical_air_mass_series: OpticalAirMass = [OPTICAL_AIR_MASS_TIME_SERIES_DEFAULT], # REVIEW-ME + ?
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    random_days: bool = RANDOM_DAY_SERIES_FLAG_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
) -> np.array:
    """Calculate the direct normal irradiance (SID) [W*m-2]

    The direct normal irradiance represents the amount of solar radiation
    received per unit area by a surface that is perpendicular (normal) to the
    rays that come in a straight line from the direction of the sun at its
    current position in the sky.

    This function implements the algorithm described by Hofierka [1]_.

    References
    ----------
    .. [1] Hofierka, J. (2002). Some title of the paper. Journal Name, vol(issue), pages.
    """
    with progress:
        extraterrestrial_normal_irradiance_series = (
            calculate_extraterrestrial_normal_irradiance_time_series(
                timestamps=timestamps,
                solar_constant=solar_constant,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                random_days=random_days,
            )
        )
        corrected_linke_turbidity_factor_series = correct_linke_turbidity_factor_time_series(
            linke_turbidity_factor_series,
            verbose=verbose,
        )
        rayleigh_optical_thickness_series = calculate_rayleigh_optical_thickness_time_series(
            optical_air_mass_series,
            verbose=verbose,
        )

        # Calculate
        direct_normal_irradiance_series = (
            extraterrestrial_normal_irradiance_series
            * np.exp(
                corrected_linke_turbidity_factor_series.value
                * optical_air_mass_series.value
                * rayleigh_optical_thickness_series.value
            )
        )
        # Warning
        LOWER_PHYSICALLY_POSSIBLE_LIMIT = -4
        UPPER_PHYSICALLY_POSSIBLE_LIMIT = 2000  # Update-Me
        # See : https://bsrn.awi.de/fileadmin/user_upload/bsrn.awi.de/Publications/BSRN_recommended_QC_tests_V2.pdf
        out_of_range_indices = np.where(
            (direct_normal_irradiance_series < LOWER_PHYSICALLY_POSSIBLE_LIMIT)
            | (direct_normal_irradiance_series > UPPER_PHYSICALLY_POSSIBLE_LIMIT)
        )
        if out_of_range_indices[0].size > 0:
            print()
            print(
                    f"{WARNING_OUT_OF_RANGE_VALUES} in `direct_normal_irradiance_series` : {out_of_range_indices[0]}!"
            )
            print()

    # Building the output dictionary=========================================

    if verbose > 0:
        results = {
            'Title': 'Direct',
            DIRECT_NORMAL_IRRADIANCE_COLUMN_NAME: direct_normal_irradiance_series,
        }
    
    if verbose > 1:
        extended_results = {
            EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME: extraterrestrial_normal_irradiance_series,
            LINKE_TURBIDITY_ADJUSTED_COLUMN_NAME: corrected_linke_turbidity_factor_series.value,
            LINKE_TURBIDITY_COLUMN_NAME: linke_turbidity_factor_series.value,
            RAYLEIGH_OPTICAL_THICKNESS_COLUMN_NAME: rayleigh_optical_thickness_series.value,
            OPTICAL_AIR_MASS_COLUMN_NAME: optical_air_mass_series.value,
        }
        results = results | extended_results

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    if verbose > 0:
        return results

    return direct_normal_irradiance_series


def calculate_direct_horizontal_irradiance_time_series(
    longitude: float,
    latitude: float,
    elevation: float,
    timestamps: BaseTimestampSeriesModel = None,
    start_time: Optional[datetime] = None,  # reuse callback inside function?
    frequency: Optional[str] = None,  # reuse callback inside function?
    end_time: Optional[datetime] = None,  # reuse callback inside function?
    timezone: Optional[str] = None,#Annotated[Optional[ZoneInfo], typer_option_timezone] = None,
    solar_time_model: SolarTimeModels = SOLAR_TIME_ALGORITHM_DEFAULT,
    time_offset_global: float = 0,
    hour_offset: float = 0,
    solar_position_model: SolarPositionModels = SOLAR_POSITION_ALGORITHM_DEFAULT,
    linke_turbidity_factor_series: LinkeTurbidityFactor = None, # [LINKE_TURBIDITY_TIME_SERIES_DEFAULT], # REVIEW-ME + Typer Parser
    apply_atmospheric_refraction: Optional[bool] = True,
    refracted_solar_zenith: Optional[float] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: str = 'minutes',
    angle_units: str = RADIANS,
    angle_output_units: str = RADIANS,
    rounding_places: Optional[int] = ROUNDING_PLACES_DEFAULT,
    statistics: bool = False,
    csv: Path = None,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    index: bool = False,
) -> np.ndarray:
    """Calculate the direct horizontal irradiance (SID) [W*m-2]

    This function implements the algorithm described by Hofierka [1]_.

    References
    ----------
    .. [1] Hofierka, J. (2002). Some title of the paper. Journal Name, vol(issue), pages.
    """
    solar_time_model = validate_model(SolarTimeModels, solar_time_model)  # can be only one of!
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
        verbose=verbose,
    )
    
    # expects solar altitude in degrees! ----------------------------------vvv
    refracted_solar_altitude_series = calculate_refracted_solar_altitude_time_series(
        solar_altitude_series=solar_altitude_series,   # expects altitude in degrees!
        verbose=verbose,
    )
    optical_air_mass_series = calculate_optical_air_mass_time_series(
        elevation=elevation,
        refracted_solar_altitude_series=refracted_solar_altitude_series,
        verbose=verbose,
    )
    # ^^^ --------------------------------- expects solar altitude in degrees!
    direct_normal_irradiance_series = calculate_direct_normal_irradiance_time_series(
        timestamps=timestamps,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        optical_air_mass_series=optical_air_mass_series,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        verbose=0,
    )

    # Mask conditions -------------------------------------------------------
    mask_solar_altitude_positive = solar_altitude_series.radians > 0
    mask_not_in_shade = np.full_like(solar_altitude_series.radians, True)  # Stub, replace with actual condition
    mask = np.logical_and.reduce((mask_solar_altitude_positive, mask_not_in_shade))

    # Initialize the direct irradiance series to zeros
    direct_horizontal_irradiance_series = np.zeros_like(solar_altitude_series.radians)
    if np.any(mask):
        # direct_horizontal_irradiance_series = direct_normal_irradiance_series * np.sin(solar_altitude_series_array)
        direct_horizontal_irradiance_series[mask] = (
            direct_normal_irradiance_series * np.sin(solar_altitude_series.radians)
        )[mask]

    # Building the output dictionary=========================================

    if verbose > 0:
        results = {
            'Title': 'Direct',
            DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME: direct_horizontal_irradiance_series,
        }

    if verbose > 1:
        extended_results = {
            DIRECT_NORMAL_IRRADIANCE_COLUMN_NAME: direct_normal_irradiance_series,
            LINKE_TURBIDITY_COLUMN_NAME: linke_turbidity_factor_series.value,
            OPTICAL_AIR_MASS_COLUMN_NAME: optical_air_mass_series.value,
            REFRACTED_SOLAR_ALTITUDE_COLUMN_NAME: refracted_solar_altitude_series.value if apply_atmospheric_refraction else np.full_like(refracted_solar_altitude_series.value, np.nan),#else np.array(["-"]),
            ALTITUDE_COLUMN_NAME: getattr(solar_altitude_series, angle_output_units),
        }
        results = results | extended_results
        results['Title'] += ' & relevant components'

    if verbose > 2:
        more_extended_results = {
            SOLAR_CONSTANT_COLUMN_NAME: solar_constant,
            PERIGEE_OFFSET_COLUMN_NAME: perigee_offset,
            ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME: eccentricity_correction_factor,
        }
        results = results | more_extended_results               # FIXME: Only the first raw is printed because of this line. But verbosity is 0 by choice

    if verbose > 3:
        even_more_extended_results = {
            IRRADIANCE_SOURCE_COLUMN_NAME: IRRADIANCE_ALGORITHM_HOFIERKA_2002,
            POSITION_ALGORITHM_COLUMN_NAME: solar_position_model.value,
            TIME_ALGORITHM_COLUMN_NAME: solar_time_model.value,
            # "Shade": in_shade,
        }
        results = results | even_more_extended_results

    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    if verbose > 0:
        return results

    return direct_horizontal_irradiance_series


def calculate_direct_inclined_irradiance_time_series_pvgis(
    longitude: float,
    latitude: float,
    elevation: float,
    timestamps: BaseTimestampSeriesModel = None,
    start_time: Optional[datetime] = None,
    frequency: Optional[str] = None,
    end_time: Optional[datetime] = None,
    convert_longitude_360: bool = False,
    timezone: Optional[str] = None,
    random_time_series: bool = False,
    direct_horizontal_component: Optional[Path] = None,
    mask_and_scale: bool = False,
    neighbor_lookup: MethodsForInexactMatches = None,
    tolerance: Optional[float] = TOLERANCE_DEFAULT,
    in_memory: bool = False,
    surface_tilt: Optional[float] = SURFACE_TILT_DEFAULT,
    surface_orientation: Optional[float] = SURFACE_ORIENTATION_DEFAULT,
    linke_turbidity_factor_series: LinkeTurbidityFactor = None,  # Changed this to np.ndarray
    apply_atmospheric_refraction: Optional[bool] = True,
    refracted_solar_zenith: Optional[float] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    apply_angular_loss_factor: Optional[bool] = True,
    solar_position_model: SolarPositionModels = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: SolarIncidenceModels = SOLAR_INCIDENCE_ALGORITHM_DEFAULT,
    solar_time_model: SolarTimeModels = SOLAR_TIME_ALGORITHM_DEFAULT,
    time_offset_global: float = 0,
    hour_offset: float = 0,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: str = 'minutes',
    angle_units: str = RADIANS,
    angle_output_units: str = RADIANS,
    rounding_places: Optional[int] = ROUNDING_PLACES_DEFAULT,
    statistics: bool = False,
    csv: Path = None,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    index: bool = False,
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
    References
    ----------
    .. [1] Hofierka, J. (2002). Some title of the paper. Journal Name, vol(issue), pages.
    """
    solar_incidence_series = model_solar_incidence_time_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        random_time_series=random_time_series,
        solar_incidence_model=solar_incidence_model,
        surface_tilt=surface_tilt,
        surface_orientation=surface_orientation,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
        verbose=0,
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
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
        verbose=0,
    )

    # ========================================================================
    # Essentially, perform calculations for when:
    # - solar altitude > 0
    # - not in shade
    # - solar incidence > 0
    #
    # To add : ---------------------------------------------------------------
    mask_solar_altitude_positive = solar_altitude_series.radians > 0
    mask_solar_incidence_positive = solar_incidence_series.radians > 0
    mask_not_in_shade = np.full_like(
        solar_altitude_series.radians, True
    )  # Stub, replace with actual condition
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
        print(f'i [bold]Modelling[/bold] [bold magenta]direct horizontal irradiance[/bold magenta]...')
        direct_horizontal_irradiance_series = calculate_direct_horizontal_irradiance_time_series(
            longitude=longitude,  # required by some of the solar time algorithms
            latitude=latitude,
            elevation=elevation,
            timestamps=timestamps,
            start_time=start_time,
            frequency=frequency,
            end_time=end_time,
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
            rounding_places=rounding_places,
            verbose=0,  # no verbosity here by choice!
        )
    else:  # read from a time series dataset
        print(f'i [bold]Reading[/bold] [magenta]direct horizontal irradiance[/magenta] from [bold]external dataset[/bold]...')
        direct_horizontal_irradiance_series = select_time_series(
            time_series=direct_horizontal_component,
            # longitude=longitude_for_selection,
            # latitude=latitude_for_selection,
            longitude=convert_float_to_degrees_if_requested(longitude, DEGREES),
            latitude=convert_float_to_degrees_if_requested(latitude, DEGREES),
            timestamps=timestamps,
            start_time=start_time,
            end_time=end_time,
            # convert_longitude_360=convert_longitude_360,
            neighbor_lookup=neighbor_lookup,
            tolerance=tolerance,
            mask_and_scale=mask_and_scale,
            in_memory=in_memory,
            verbose=0,  # no verbosity here by choice!
        ).to_numpy()

    try:
        compare_temporal_resolution(timestamps, direct_horizontal_irradiance_series)
        direct_inclined_irradiance_series = (
            direct_horizontal_irradiance_series
            * np.sin(solar_incidence_series.radians)
            / np.sin(solar_altitude_series.radians)
        )

    except ZeroDivisionError:
        logger.error(f"Error: Division by zero in calculating the direct inclined irradiance!")
        print("Is the solar altitude angle zero?")
        # should this return something? Like in r.sun's simpler's approach?
        raise ValueError

    if apply_angular_loss_factor:

        try:
            angular_loss_factor_series = (
                calculate_angular_loss_factor_for_direct_irradiance_time_series(
                    solar_incidence_series=solar_incidence_series.radians,
                    verbose=verbose,
                )
            )
            direct_inclined_irradiance_series = (
                direct_horizontal_irradiance_series * angular_loss_factor_series
            )

        except ZeroDivisionError as e:
            logger.error(f"Which Error? {e}")
            raise ValueError

    if np.any(direct_inclined_irradiance_series < 0):
        print("[red]Warning: Negative values found in `direct_inclined_irradiance_series`![/red]")

    if verbose > 0:
        results = {
            DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME: direct_inclined_irradiance_series,
        }
        title = 'Direct'

    if verbose > 1:
        extended_results = {
            LOSS_COLUMN_NAME: 1 - angular_loss_factor_series if apply_angular_loss_factor else ['-'],
            SURFACE_TILT_COLUMN_NAME: convert_float_to_degrees_if_requested(surface_tilt, angle_output_units),
            SURFACE_ORIENTATION_COLUMN_NAME: convert_float_to_degrees_if_requested(surface_orientation, angle_output_units),
        }
        results = results | extended_results

    if verbose > 2:
        more_extended_results = {
            DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME: direct_horizontal_irradiance_series,
            INCIDENCE_COLUMN_NAME: getattr(solar_incidence_series, angle_output_units),
            ALTITUDE_COLUMN_NAME: getattr(solar_altitude_series, angle_output_units),
        }
        results = results | more_extended_results
        title += ' & relevant components'

    if verbose > 3:
        even_more_extended_results = {
            'Irradiance source': 'External data' if direct_horizontal_component else IRRADIANCE_ALGORITHM_HOFIERKA_2002,
            INCIDENCE_ALGORITHM_COLUMN_NAME: solar_incidence_model.value,
            POSITION_ALGORITHM_COLUMN_NAME: solar_position_model.value,
            TIME_ALGORITHM_COLUMN_NAME: solar_time_model.value,
            # "Shade": in_shade,
        }
        results = results | even_more_extended_results

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    if verbose > 0:
        return results

    return direct_inclined_irradiance_series
