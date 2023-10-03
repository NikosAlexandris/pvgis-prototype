from devtools import debug
"""
_Direct_ or _beam_ irradiance is one of the main components of solar
irradiance. It comes perpendicular from the Sun and is not scattered before it
irradiates a surface.

During a cloudy day the sunlight will be partially absorbed and scattered by
different air molecules. The latter part is defined as the _diffuse_
irradiance. The remaining part is the _direct_ irradiance.
"""

import logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('error.log'),  # Save log to a file
        logging.StreamHandler()  # Print log to the console
    ]
)
from functools import partial
from pydantic import BaseModel
from pydantic import Field
from pydantic import validator
import typer
from typing import Annotated
from typing import Optional
from typing import Union
from enum import Enum
from rich import print
from rich.console import Console
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_advanced_options
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_geometry
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_atmospheric_properties
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_earth_orbit
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_efficiency
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_geometry_surface
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_output
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_series_irradiance
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_solar_time
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_toolbox
import math
from math import sin
from math import cos
from math import exp
from math import atan
import numpy as np
from datetime import datetime
from pvgisprototype.constants import AOI_CONSTANTS
from pvgisprototype.api.geometry.solar_declination import model_solar_declination
from pvgisprototype.api.geometry.solar_altitude import model_solar_altitude
from pvgisprototype.api.geometry.solar_time import model_solar_time
from pvgisprototype.api.geometry.solar_hour_angle import calculate_hour_angle
from pvgisprototype.algorithms.jenco.solar_incidence import calculate_relative_longitude
from pvgisprototype.api.utilities.conversions import convert_to_radians
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.api.utilities.conversions import convert_to_degrees_if_requested
from pvgisprototype.api.utilities.conversions import convert_float_to_radians_if_requested
from pvgisprototype.api.utilities.conversions import convert_to_radians_if_requested
from pvgisprototype.api.utilities.conversions import convert_dictionary_to_table
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.api.utilities.timestamp import ctx_convert_to_timezone
# from pvgisprototype.api.utilities.timestamp import timestamp_to_decimal_hours
from pvgisprototype.api.utilities.timestamp import ctx_attach_requested_timezone
from pvgisprototype.api.utilities.timestamp import parse_timestamp
from .loss import calculate_angular_loss_factor_for_direct_irradiance
from .extraterrestrial import calculate_extraterrestrial_normal_irradiance
from pvgisprototype.validation.functions import AdjustElevationInputModel
from pvgisprototype.validation.functions import CalculateOpticalAirMassInputModel
from pvgisprototype.validation.functions import validate_with_pydantic
from pydantic import BaseModel
from pydantic import Field
from pydantic import validator
from math import radians
from math import degrees
from pathlib import Path
from pvgisprototype.cli.series import select_time_series
from pvgisprototype.cli.typer_parameters import OrderCommands
from pvgisprototype.cli.typer_parameters import typer_argument_longitude
from pvgisprototype.cli.typer_parameters import typer_argument_latitude
from pvgisprototype.cli.typer_parameters import typer_argument_elevation
from pvgisprototype import Elevation
from pvgisprototype.cli.typer_parameters import typer_argument_refracted_solar_altitude
from pvgisprototype import RefractedSolarAltitude
from pvgisprototype.cli.typer_parameters import typer_argument_timestamp
from pvgisprototype.cli.typer_parameters import typer_option_timezone
from pvgisprototype.cli.typer_parameters import typer_argument_surface_tilt
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_argument_surface_orientation
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_argument_linke_turbidity_factor
from pvgisprototype.constants import LINKE_TURBIDITY_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_linke_turbidity_factor
from pvgisprototype import OpticalAirMass
from pvgisprototype.cli.typer_parameters import typer_option_optical_air_mass
from pvgisprototype.constants import OPTICAL_AIR_MASS_DEFAULT
from pvgisprototype.constants import OPTICAL_AIR_MASS_UNIT
from pvgisprototype import RayleighThickness
from pvgisprototype.constants import RAYLEIGH_OPTICAL_THICKNESS_UNIT
from pvgisprototype.cli.typer_parameters import typer_option_apply_atmospheric_refraction
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_refracted_solar_zenith
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_argument_solar_altitude
from pvgisprototype.cli.typer_parameters import typer_option_direct_horizontal_irradiance
from pvgisprototype.api.irradiance.models import DirectIrradianceComponents
from pvgisprototype.cli.typer_parameters import typer_option_apply_angular_loss_factor
from pvgisprototype.cli.typer_parameters import typer_option_solar_incidence_model
from pvgisprototype.api.geometry.models import SolarIncidenceModels
from pvgisprototype.cli.typer_parameters import typer_option_solar_declination_model
from pvgisprototype.api.geometry.models import SolarDeclinationModels
from pvgisprototype.cli.typer_parameters import typer_option_solar_position_model
from pvgisprototype.api.geometry.models import SolarPositionModels
from pvgisprototype.cli.typer_parameters import typer_option_solar_time_model
from pvgisprototype.api.geometry.models import SolarTimeModels
from pvgisprototype.cli.typer_parameters import typer_option_global_time_offset
from pvgisprototype.constants import TIME_OFFSET_GLOBAL_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_hour_offset
from pvgisprototype.constants import HOUR_OFFSET_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_solar_constant
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.cli.typer_parameters import typer_option_days_in_a_year
from pvgisprototype.constants import DAYS_IN_A_YEAR
from pvgisprototype.cli.typer_parameters import typer_option_perigee_offset
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.cli.typer_parameters import typer_option_eccentricity_correction_factor
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.cli.typer_parameters import typer_option_time_output_units
from pvgisprototype.constants import TIME_OUTPUT_UNITS_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_angle_units
from pvgisprototype.cli.typer_parameters import typer_option_angle_output_units
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_rounding_places
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_verbose
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_mask_and_scale
from pvgisprototype.constants import MASK_AND_SCALE_FLAG_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_inexact_matches_method
from pvgisprototype.api.irradiance.models import MethodsForInexactMatches
from pvgisprototype.cli.typer_parameters import typer_option_tolerance
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_in_memory
from pvgisprototype.constants import IN_MEMORY_FLAG_DEFAULT


app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"Estimate the direct solar radiation",
)
console = Console()


# Forbid using --solar-time-model all wherever it does not make sense?
# def validate_solar_time_model(value: SolarTimeModels) -> SolarTimeModels:
#     if value == SolarTimeModels.all:
#         raise typer.BadParameter("The 'all' option is not allowed.")
#     return value


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
    adjusted_elevation = exp(-elevation.value / 8434.5)
    return Elevation(value=adjusted_elevation, unit="meters")


@app.command(
    'correct-linke-turbidity',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_atmospheric_properties,
)
def correct_linke_turbidity_factor(
    linke_turbidity_factor: Annotated[Optional[float], typer_argument_linke_turbidity_factor] = LINKE_TURBIDITY_DEFAULT
):
    """Calculate the air mass 2 Linke atmospheric turbidity factor

    Notes
    -----
    The term -0.8662 * TLK is the air mass 2 Linke atmospheric turbidity factor
    [dimensionless] corrected by Kasten [1]_.

    In PVGIS C source code the relevant code fragment is :

	elevationCorr = exp(-sunVarGeom->z_orig / 8434.5);
	temp1 = 0.1594 + locSolarAltitude * (1.123 + 0.065656 * locSolarAltitude);
	temp2 = 1. + locSolarAltitude * (28.9344 + 277.3971 * locSolarAltitude);
	drefract = 0.061359 * temp1 / temp2;    /* in radians */
	h0refract = locSolarAltitude + drefract;
	opticalAirMass = elevationCorr / (sin(h0refract) + 0.50572 * pow(h0refract * rad2deg + 6.07995, -1.6364));
	airMass2Linke = 0.8662 * sunRadVar->linke;
    """
    corrected_linke_turbidity_factor = -0.8662 * linke_turbidity_factor
    return corrected_linke_turbidity_factor


@app.command(
    'refracted-solar-altitude',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_geometry,
)
def calculate_refracted_solar_altitude(
    solar_altitude: Annotated[float, typer_argument_solar_altitude],
    angle_output_units: Annotated[str, typer_option_angle_output_units] = ANGLE_OUTPUT_UNITS_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """Adjust the solar altitude angle for atmospheric refraction

                       ⎛                                  2⎞
            0.061359 ⋅ ⎜0.1594 + 1.123 ⋅ h  + 0.065656 ⋅ h ⎟
      ref              ⎝                  0               0⎠
    ∆h    = ────────────────────────────────────────────────
      0                                            2        
                    1 + 28.9344 ⋅ h  + 277.3971 ⋅ h         
                                   0               0        
                                                            
     ref          ref                                       
    h    = h  + ∆h                                          
     0      0     0                                         

    This function implements the algorithm described by Hofierka :cite:`p:hofierka2002`.

    Notes
    -----

    In PVGIS C source code the relevant code fragment is :

	elevationCorr = exp(-sunVarGeom->z_orig / 8434.5);
	temp1 = 0.1594 + locSolarAltitude * (1.123 + 0.065656 * locSolarAltitude);
	temp2 = 1. + locSolarAltitude * (28.9344 + 277.3971 * locSolarAltitude);
	drefract = 0.061359 * temp1 / temp2;    /* in radians */
	h0refract = locSolarAltitude + drefract;
    """
    if solar_altitude.unit != "degrees":
        raise ValueError(f"The atmospheric refraction equation expects the solar altitude angle in `degrees`!")

    atmospheric_refraction = (
        0.061359
        * (
            0.1594
            + 1.123 * solar_altitude.radians
            + 0.065656 * pow(solar_altitude.radians, 2)
        )
        / (
            1
            + 28.9344 * solar_altitude.radians
            + 277.3971 * pow(solar_altitude.radians, 2)
        )
    )
    refracted_solar_altitude = RefractedSolarAltitude(
        value=solar_altitude.radians + atmospheric_refraction,
        unit=solar_altitude.unit,
    )
    refracted_solar_altitude = convert_to_radians_if_requested(
        refracted_solar_altitude,
        angle_output_units,
    )

    if verbose == 3:
        debug(locals())
    return refracted_solar_altitude


@app.command(
    'optical-air-mass',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_atmospheric_properties,
)
@validate_with_pydantic(CalculateOpticalAirMassInputModel)
def calculate_optical_air_mass(
    elevation: Annotated[float, typer_argument_elevation],
    refracted_solar_altitude: Annotated[float, typer_argument_refracted_solar_altitude],
) -> OpticalAirMass:
    """Approximate the relative optical air mass.

    This function implements the algorithm described by Minzer et al. [1]_ 
    and Hofierka [2]_.

    Parameters
    ----------
    elevation: float
        The elevation in meters

    refracted_solar_altitude: float
        Refracted solar altitude angle in degrees

    Returns
    -------
    tuple
        Unitless relative optical air mass m(γ) at solar altitude γ

    Notes
    -----

    UPDATE-Me
    The m(γ) table has been computed from the air density profile of the ARDC
    Model Atmosphere, 1959, with 

        - ρ0 = 1.22500 kg/m3
        - Δ0 = 2.76 X 10-4
        - R = 6.371229 X 106

    ...
    m, and a function f(γ) for approximating m(γ) was found for 
    in degrees.
    ...
    UPDATE-Me

    The ARDC Model Atmosphere was developed in 1959 and is widely used in 
    atmospheric research. More details about this model and its applications 
    can be found in the original publication [1]_.

    References
    ----------
    .. [1] Minzer, A., Champion, K. S. W., & Pond, H. L. (1959). 
           The ARDC Model Atmosphere. Air Force Surveys in Geophysics, 115. AFCRL.

    .. [2] Hofierka, 2002
    """
    adjusted_elevation = adjust_elevation(elevation.value)
    optical_air_mass = adjusted_elevation.value / (
        sin(refracted_solar_altitude.radians)
        + 0.50572
        * math.pow((refracted_solar_altitude.radians + 6.07995), -1.6364)
    )
    optical_air_mass = OpticalAirMass(
        value=optical_air_mass,
        unit=OPTICAL_AIR_MASS_UNIT,
    )

    return optical_air_mass


def calculate_rayleigh_optical_thickness(
    optical_air_mass: Annotated[float, typer_option_optical_air_mass] = OPTICAL_AIR_MASS_DEFAULT,
) -> RayleighThickness:
    """
    δ R(m) = 1/(6.6296 + 1.7513m - 0.1202m2 + 0.0065m3 - 0.00013m4)
    This function implements the algorithm described by Hofierka, 2002 [1]_

    Returns
    -------
    rayleigh_optical_thickness: float
        Unitless rayleigh optical thickness

    .. [1] Hofierka, 2002
    """
    if optical_air_mass.value <= 20:
        rayleigh_optical_thickness = 1 / (
        6.6296 + 1.7513 * optical_air_mass.value
        - 0.1202 * math.pow(optical_air_mass.value, 2)
        + 0.0065 * math.pow(optical_air_mass.value, 3)
        - 0.00013* math.pow(optical_air_mass.value, 4)
        )

    if optical_air_mass.value > 20:
        rayleigh_optical_thickness = 1 / (10.4 + 0.718 * optical_air_mass.value)
    rayleigh_optical_thickness = RayleighThickness(
        value=rayleigh_optical_thickness,
        unit=RAYLEIGH_OPTICAL_THICKNESS_UNIT,
    )
    return rayleigh_optical_thickness


@app.command('normal', no_args_is_help=True)
def calculate_direct_normal_irradiance(
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    linke_turbidity_factor: Annotated[Optional[float], typer_option_linke_turbidity_factor] = LINKE_TURBIDITY_DEFAULT,
    optical_air_mass: Annotated[float, typer_option_optical_air_mass] = OPTICAL_AIR_MASS_DEFAULT,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = DAYS_IN_A_YEAR,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """Calculate the direct normal irradiance attenuated by the cloudless atmosphere

    This function implements the algorithm described by Hofierka
    :cite:`p:Hofierka2002`.

    Parameters
    ----------
    extraterrestial_irradiance: float

    linke_turbidity_factor: float
        The Linke turbidity factor (TL, for an air mass equal to 2) is a very
        convenient approximation to model the atmospheric absorption and
        scattering of the solar radiation under clear skies. It describes the
        optical thickness of the atmosphere due to both the absorption by the
        water vapor and the absorption and scattering by the aerosol particles
        relative to a dry and clean atmosphere. It summarizes the turbidity of
        the atmosphere, and hence the attenuation of the direct beam solar
        radiation (WMO, 1981; Kasten, 1996). The larger the TL, the larger the
        attenuation of the radiation by the clear sky atmosphere. It is equal
        to the ratio of total optical depth to the Rayleigh optical depth.

    optical_air_mass: float

    References
    ----------

    @article{Kasten1996,
        doi = {10.1016/0038-092x(95)00114-7},
        year = 1996,
        publisher = {Elsevier {BV}},
        volume = {56},
        number = {3},
        pages = {239--244},
        author = {F. Kasten},
        title = {The linke turbidity factor based on improved values of the integral Rayleigh optical thickness},
        journal = {Solar Energy}
    }
    """
    extraterrestial_normal_irradiance = calculate_extraterrestrial_normal_irradiance(
        # day_of_year=timestamp.timetuple().tm_yday,  # make `day_of_year` optional ?
        timestamp=timestamp,
        solar_constant=solar_constant,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
    )
    corrected_linke_turbidity_factor = correct_linke_turbidity_factor(linke_turbidity_factor)
    rayleigh_optical_thickness = calculate_rayleigh_optical_thickness(optical_air_mass)
    direct_normal_irradiance = (
        extraterrestial_normal_irradiance
        * exp(
            corrected_linke_turbidity_factor
            * optical_air_mass.value
            * rayleigh_optical_thickness.value
        )
    )
    if verbose > 1:
        print(f'Direct normal irradiance = Extraterrestial normal irradiance * exp( Corrected Linke turbidity factor * Optical air mass * Rayleigh Optical Thickness )')
    if verbose > 0:
        print(f'Direct normal irradiance: {direct_normal_irradiance}')  # B0c
    if verbose == 3:
        debug(locals())
    return direct_normal_irradiance  # B0c


@app.command('horizontal', no_args_is_help=True)
def calculate_direct_horizontal_irradiance(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    solar_position_model: Annotated[SolarPositionModels, typer_option_solar_position_model] = SolarPositionModels.noaa,
    linke_turbidity_factor: Annotated[Optional[float], typer_option_linke_turbidity_factor] = LINKE_TURBIDITY_DEFAULT,
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    solar_time_model: Annotated[SolarTimeModels, typer_option_solar_time_model] = SolarTimeModels.milne,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = TIME_OFFSET_GLOBAL_DEFAULT,
    hour_offset: Annotated[float, typer_option_hour_offset] = HOUR_OFFSET_DEFAULT,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = DAYS_IN_A_YEAR,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: Annotated[str, typer_option_time_output_units] = TIME_OUTPUT_UNITS_DEFAULT,
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = ANGLE_OUTPUT_UNITS_DEFAULT,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """Calculate the direct irradiatiance incident on a horizontal surface

    Parameters
    ----------

    Returns
    -------

    Notes
    -----
    This function implements the algorithm described by Hofierka [1]_

        `Bhc = B0c sin(h0)`
    """
    solar_altitude = model_solar_altitude(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        model=solar_position_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        solar_time_model=solar_time_model,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        # time_output_units=time_output_units,
        # angle_units=angle_units,
        # angle_output_units=angle_output_units,
    )
    # The refraction equation expects the solar altitude angle in degrees! ---
    expected_solar_altitude_units = 'degrees'
    solar_altitude_in_degrees = convert_to_degrees_if_requested(
            solar_altitude,
            expected_solar_altitude_units,  # Here!
            )
    # refracted_solar_altitude, refracted_solar_altitude_units = calculate_refracted_solar_altitude(
    refracted_solar_altitude = calculate_refracted_solar_altitude(
            solar_altitude=solar_altitude_in_degrees,
            angle_output_units='radians',  # Here in radians!
            ) 
    optical_air_mass = calculate_optical_air_mass(
            elevation=elevation,
            refracted_solar_altitude=refracted_solar_altitude,
            )
    # --------------------------------------expects solar altitude in degrees!
    direct_normal_irradiance = calculate_direct_normal_irradiance(
            optical_air_mass=optical_air_mass,
            linke_turbidity_factor=linke_turbidity_factor,
            timestamp=timestamp,
            solar_constant=solar_constant,
            days_in_a_year=days_in_a_year,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            verbose=verbose,
            )
    direct_horizontal_irradiance = direct_normal_irradiance * sin(solar_altitude.radians)

    # table_with_inputs = convert_dictionary_to_table(locals())
    # console.print(table_with_inputs)
    if verbose > 0:
        print(f'Direct horizontal irradiance: {direct_horizontal_irradiance}')  # B0c
    if verbose == 3:
        debug(locals())
    return direct_horizontal_irradiance


@app.command('inclined', no_args_is_help=True)
def calculate_direct_inclined_irradiance_pvgis(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    direct_horizontal_component: Annotated[Optional[Path], typer_option_direct_horizontal_irradiance] = None,
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = MASK_AND_SCALE_FLAG_DEFAULT,
    inexact_matches_method: Annotated[MethodsForInexactMatches, typer_option_inexact_matches_method] = MethodsForInexactMatches.nearest,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = TOLERANCE_DEFAULT,
    in_memory: Annotated[bool, typer_option_in_memory] = IN_MEMORY_FLAG_DEFAULT,
    surface_tilt: Annotated[Optional[float], typer_argument_surface_tilt] = SURFACE_TILT_DEFAULT,
    surface_orientation: Annotated[Optional[float], typer_argument_surface_orientation] = SURFACE_ORIENTATION_DEFAULT,
    linke_turbidity_factor: Annotated[Optional[float], typer_option_linke_turbidity_factor] = LINKE_TURBIDITY_DEFAULT,
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    solar_declination_model: Annotated[SolarDeclinationModels, typer_option_solar_declination_model] = SolarDeclinationModels.pvlib,
    solar_position_model: Annotated[SolarPositionModels, typer_option_solar_position_model] = SolarPositionModels.noaa,
    solar_incidence_model: Annotated[SolarIncidenceModels, typer_option_solar_incidence_model] = SolarIncidenceModels.jenco,
    solar_time_model: Annotated[SolarTimeModels, typer_option_solar_time_model] = SolarTimeModels.milne,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = TIME_OFFSET_GLOBAL_DEFAULT,
    hour_offset: Annotated[float, typer_option_hour_offset] = HOUR_OFFSET_DEFAULT,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = DAYS_IN_A_YEAR,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: Annotated[str, typer_option_time_output_units] = TIME_OUTPUT_UNITS_DEFAULT,
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = ANGLE_OUTPUT_UNITS_DEFAULT,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """Calculate the direct irradiance incident on a tilted surface [W*m-2] 

    This function implements the algorithm described by Hofierka
    :cite:`p:hofierka2002`.

    Notes
    -----

    The following equations require the sine of the relative latitude. Both the
    equation by Hofierka (2002) and the implementation in PVGIS derive the same
    quantity though using different trigonometric functions!


    Hofierka, 2002

    sine_relative_latitude = -cos(latitude) 
                             * sin(surface_tilt)
                             * cos(surface_orientation)
                             + sin(latitude)
                             * cos (surface_tilt)
    which is equal to

    sine_relative_latitude = -cos(latitude)
                             * cos(half_pi - surface_tilt)
                             * sin(half_pi + surface_orientation)
                             + sin(latitude)
                             * sin(half_pi - surface_tilt)
    Additional Notes
    ----------------

              B   ⋅ sin ⎛δ   ⎞                    
               hc       ⎝ exp⎠         ⎛ W ⎞
        B   = ────────────────     in  ⎜───⎟
         ic       sin ⎛h ⎞             ⎜ -2⎟           
                      ⎝ 0⎠             ⎝m  ⎠           
    """
    solar_altitude = model_solar_altitude(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        solar_time_model=solar_time_model,
        refracted_solar_zenith=refracted_solar_zenith,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        # time_output_units=time_output_units,
        # angle_units=angle_units,
        # angle_output_units=angle_output_units,
    )
    sine_solar_altitude = sin(solar_altitude.radians)

    # make it a function -----------------------------------------------------
    #

    solar_declination = model_solar_declination(
        timestamp=timestamp,
        timezone=timezone,
        model=solar_declination_model,
        days_in_a_year=days_in_a_year,
        eccentricity_correction_factor=eccentricity_correction_factor,
        perigee_offset=perigee_offset,
        # angle_output_units=angle_output_units,
    )
    sine_relative_latitude = -cos(latitude) * sin(surface_tilt) * cos(
        surface_orientation
    ) + sin(latitude) * cos(surface_tilt)
    relative_latitude = math.asin(sine_relative_latitude)
    # calculate C3x geometry parameters for inclined surface
    C31_inclined = math.cos(relative_latitude) * math.cos(solar_declination.radians)
    C33_inclined = sine_relative_latitude * math.sin(solar_declination.radians)

    # Left-over comment from ? -----------------------------------------------
    # cos(hour_angle - relative_longitude) = C33_inclined / C31_inclined
    # ------------------------------------------------------------------------

    solar_time = model_solar_time(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        model=solar_time_model,
        refracted_solar_zenith=refracted_solar_zenith,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        # time_output_units=time_output_units,
        # angle_units=angle_units,
        # angle_output_units=angle_output_units,
    )
    hour_angle = calculate_hour_angle(
        solar_time=solar_time,
        # angle_output_units=angle_output_units,
    )
    relative_longitude = calculate_relative_longitude(
        latitude,
        surface_tilt,
        surface_orientation,
        # angle_output_units=angle_output_units,
    )
    sine_solar_incidence_angle = (
        C31_inclined * math.cos(hour_angle.radians - relative_longitude.radians) + C33_inclined
    )

    #
    # ----------------------------------------------------- make it a function

    if not direct_horizontal_component:
        direct_horizontal_irradiance = calculate_direct_horizontal_irradiance(
                longitude=longitude,  # required by some of the solar time algorithms
                latitude=latitude,
                elevation=elevation,
                timestamp=timestamp,
                timezone=timezone,
                linke_turbidity_factor=linke_turbidity_factor,
                )
    else:  # read from a time series dataset
        # time = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        longitude_for_selection = convert_float_to_degrees_if_requested(longitude, 'degrees')
        latitude_for_selection = convert_float_to_degrees_if_requested(latitude, 'degrees')
        direct_horizontal_irradiance = select_time_series(
            time_series=direct_horizontal_component,
            longitude=longitude_for_selection,
            latitude=latitude_for_selection,
            timestamps=[timestamp],  # preserve input, feed it as needed!
            mask_and_scale=mask_and_scale,
            inexact_matches_method=inexact_matches_method,
            tolerance=tolerance,
            verbose=verbose,
        )
        print(f'Direct horizontal irradiance from time series: {direct_horizontal_irradiance}')

    try:
        modified_direct_horizontal_irradiance = (
            direct_horizontal_irradiance
            * sine_solar_incidence_angle
            / sine_solar_altitude
        )
        if verbose == 3:
            debug(locals())
    except ZeroDivisionError:
        logging.error(f"Error: Division by zero in calculating the direct inclined irradiance!")
        print("Is the solar altitude angle zero?")
        # should this return something? Like in r.sun's simpler's approach?
        raise ValueError

    # "Simpler" way to calculate the inclined solar declination?
    if solar_incidence_model == 'PVGIS':

        # In the old C source code, the following runs if:
        # --------------------------------- Review & Add ?
            # 1. surface is NOT shaded
            # 3. solar declination > 0
        # --------------------------------- Review & Add ?

        try:
            angular_loss_factor = calculate_angular_loss_factor_for_direct_irradiance(
                    sine_solar_incidence_angle,
                    angle_of_incidence_constant = 0.155,
                    )
            direct_inclined_irradiance = modified_direct_horizontal_irradiance * angular_loss_factor
            print(f'Direct inclined irradiance: {direct_inclined_irradiance} (based on {PVGIS})')  # B0c

            return direct_inclined_irradiance

        # Else, the following runs:
        # --------------------------------- Review & Add ?
            # 1. surface is shaded
            # 3. solar declination = 0
        # --------------------------------- Review & Add ?
        except ZeroDivisionError as e:
            logging.error(f"Which Error? {e}")
            raise ValueError

    if verbose > 0:
        print(f'Direct inclined irradiance: {modified_direct_horizontal_irradiance} (based on {solar_incidence_model})')  # B0c
    if verbose == 3:
        debug(locals())
    return modified_direct_horizontal_irradiance


# from: rsun_base.c
# function name: brad_angle_irradiance
# @app.command('direct', no_args_is_help=True)
def calculate_direct_irradiance(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    # solar_altitude: Annotated[float, typer.Argument(
    #     help='Solar altitude in degrees °',
    #     min=0, max=90)],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    component: Annotated[DirectIrradianceComponents, typer.Option(
        '-c',
        '--component',
        show_default=True,
        show_choices=True,
        case_sensitive=False,
        help="Direct irradiance component to calculate")] = 'inclined',
    direct_horizontal_component: Annotated[Optional[Path], typer_option_direct_horizontal_irradiance] = None,
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = MASK_AND_SCALE_FLAG_DEFAULT,
    inexact_matches_method: Annotated[MethodsForInexactMatches, typer_option_inexact_matches_method] = MethodsForInexactMatches.nearest,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = TOLERANCE_DEFAULT,
    in_memory: Annotated[bool, typer_option_in_memory] = IN_MEMORY_FLAG_DEFAULT,
    surface_tilt: Annotated[Optional[float], typer_argument_surface_tilt] = SURFACE_TILT_DEFAULT,
    surface_orientation: Annotated[Optional[float], typer_argument_surface_orientation] = SURFACE_ORIENTATION_DEFAULT,
    linke_turbidity_factor: Annotated[Optional[float], typer_option_linke_turbidity_factor] = LINKE_TURBIDITY_DEFAULT,
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    solar_incidence_model: Annotated[SolarIncidenceModels, typer_option_solar_incidence_model] = SolarIncidenceModels.jenco,
    solar_time_model: Annotated[SolarTimeModels, typer_option_solar_time_model] = SolarTimeModels.milne,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = TIME_OFFSET_GLOBAL_DEFAULT,
    hour_offset: Annotated[float, typer_option_hour_offset] = HOUR_OFFSET_DEFAULT,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = DAYS_IN_A_YEAR,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: Annotated[str, typer_option_time_output_units] = TIME_OUTPUT_UNITS_DEFAULT,
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = ANGLE_OUTPUT_UNITS_DEFAULT,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    ):
    """Calculate the direct irradiatiance incident on a solar surface.

    This function implements the algorithm described by Hofierka
    :cite:`p:hofierka2002`.

    Parameters
    ----------
    direct_horizontal_radiation_coefficient: list
        Direct horizontal radiation coefficient. Likely a reference to the clear-sky beam horizontal radiation?
    solar_altitude: float
        Solar altitude angle.
    sun_geometry:
        Sun geometry variables for a specific day ?
    sun_radiation_variables:
        Solar radiation variables.

    Returns
    -------
    direct_irradiance: float
        The direct radiant flux incident on a surface per unit area in W/m².

    """
    pass
    # year = timestamp.year
    # start_of_year = datetime(year=year, month=1, day=1, tzinfo=timezone.utc)
    # hour_of_year = int((timestamp - start_of_year).total_seconds() / 3600)
    # day_of_year = timestamp.timetuple().tm_yday
    # day_of_year_in_radians = double_numpi * day_of_year / days_in_a_year  
    # if surface_tilt == 0:
    #     print(f'Direct horizontal irradiance: {direct_horizontal_irradiance}')
    #     direct_horizontal_irradiance = calculate_direct_horizontal_irradiance()
    #     return direct_horizontal_irradiance  # Bhc

    # if surface_tilt != 0:
    #     direct_inclined_irradiance = calculate_direct_inclined_irradiance()
    #     print(f'Direct inclined irradiance : {direct_inclined_irradiance}')
    #     return direct_inclined_irradiance  # Bic
