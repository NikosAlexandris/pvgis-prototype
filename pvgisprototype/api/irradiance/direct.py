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
from ..constants import AOI_CONSTANTS
from pvgisprototype.api.geometry.solar_declination import model_solar_declination
from pvgisprototype.api.geometry.solar_altitude import model_solar_altitude
from ..geometry.models import SolarDeclinationModels
from ..geometry.models import SolarIncidenceModels
from ..geometry.models import SolarTimeModels
from ..geometry.solar_time import model_solar_time
from ..utilities.conversions import convert_to_radians
from ..utilities.conversions import convert_float_to_degrees_if_requested
from ..utilities.conversions import convert_to_degrees_if_requested
from ..utilities.conversions import convert_float_to_radians_if_requested
from ..utilities.conversions import convert_to_radians_if_requested
from ..utilities.conversions import convert_dictionary_to_table
from ..utilities.timestamp import now_utc_datetimezone
from ..utilities.timestamp import ctx_convert_to_timezone
from ..utilities.timestamp import timestamp_to_decimal_hours
from ..utilities.timestamp import ctx_attach_requested_timezone
from ..utilities.timestamp import parse_timestamp
from .loss import calculate_angular_loss_factor_for_direct_irradiance
from .extraterrestrial import calculate_extraterrestrial_normal_irradiance

from pvgisprototype.api.function_models import CalculateOpticalAirMassInputModel
from pvgisprototype.api.decorators import validate_with_pydantic

from pydantic import BaseModel
from pydantic import Field
from pydantic import validator
from math import radians
from math import degrees
from pathlib import Path
from .constants import SOLAR_CONSTANT

# from pvgisprototype.api.series.utilities import select_coordinates
from pvgisprototype.cli.series import select_time_series
from pvgisprototype.cli.typer_parameters import OrderCommands
from pvgisprototype.cli.typer_parameters import typer_argument_longitude
from pvgisprototype.cli.typer_parameters import typer_argument_latitude
from pvgisprototype.cli.typer_parameters import typer_argument_elevation
from pvgisprototype.cli.typer_parameters import typer_argument_refracted_solar_altitude
from pvgisprototype.cli.typer_parameters import typer_option_refracted_solar_zenith
from pvgisprototype.cli.typer_parameters import typer_argument_timestamp
from pvgisprototype.cli.typer_parameters import typer_option_timezone
from pvgisprototype.cli.typer_parameters import typer_argument_surface_tilt
from pvgisprototype.cli.typer_parameters import typer_argument_surface_orientation
from pvgisprototype.cli.typer_parameters import typer_argument_linke_turbidity_factor
from pvgisprototype.cli.typer_parameters import typer_option_linke_turbidity_factor
from pvgisprototype.cli.typer_parameters import typer_option_optical_air_mass
from pvgisprototype.cli.typer_parameters import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer_parameters import typer_option_refracted_solar_zenith
from pvgisprototype.cli.typer_parameters import typer_argument_solar_altitude
from pvgisprototype.cli.typer_parameters import typer_option_albedo
from pvgisprototype.cli.typer_parameters import typer_option_direct_horizontal_component
from pvgisprototype.cli.typer_parameters import typer_option_apply_angular_loss_factor
from pvgisprototype.cli.typer_parameters import typer_option_solar_incidence_model
from pvgisprototype.cli.typer_parameters import typer_option_solar_declination_model
from pvgisprototype.cli.typer_parameters import typer_option_solar_time_model
from pvgisprototype.cli.typer_parameters import typer_option_global_time_offset
from pvgisprototype.cli.typer_parameters import typer_option_hour_offset
# from pvgisprototype.cli.typer_parameters import typer_argument_solar_constant
from pvgisprototype.cli.typer_parameters import typer_option_solar_constant
from pvgisprototype.cli.typer_parameters import typer_option_days_in_a_year
from pvgisprototype.cli.typer_parameters import typer_option_perigee_offset
from pvgisprototype.cli.typer_parameters import typer_option_eccentricity_correction_factor
from pvgisprototype.cli.typer_parameters import typer_option_time_output_units
from pvgisprototype.cli.typer_parameters import typer_option_angle_units
from pvgisprototype.cli.typer_parameters import typer_option_angle_output_units
from pvgisprototype.cli.typer_parameters import typer_option_rounding_places
from pvgisprototype.cli.typer_parameters import typer_option_verbose
from pvgisprototype.cli.typer_parameters import typer_option_mask_and_scale
from pvgisprototype.cli.typer_parameters import typer_option_inexact_matches_method
from pvgisprototype.cli.typer_parameters import typer_option_tolerance
from pvgisprototype.cli.typer_parameters import typer_option_in_memory


app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"Estimate the direct solar radiation",
)
console = Console()


class DirectIrradianceComponents(str, Enum):
    normal = 'normal'
    on_horizontal_surface = 'horizontal'
    on_inclined_surface = 'inclined'


class MethodsForInexactMatches(str, Enum):
    none = None # only exact matches
    pad = 'pad' # ffill: propagate last valid index value forward
    backfill = 'backfill' # bfill: propagate next valid index value backward
    nearest = 'nearest' # use nearest valid index value

# Forbid using --solar-time-model all wherever it does not make sense?
# def validate_solar_time_model(value: SolarTimeModels) -> SolarTimeModels:
#     if value == SolarTimeModels.all:
#         raise typer.BadParameter("The 'all' option is not allowed.")
#     return value


# @validate_with_pydantic(Elevation)
def adjust_elevation(
    elevation: Annotated[float, typer_argument_elevation],
):
    """Some correction for the given solar altitude 

    [1]_

    Notes
    -----

    .. [1] Hofierka, 2002
    """
    # debug(locals())
    return exp(-elevation.value / 8434.5)


# ensure value ranges in [-pi, pi]
range_in_minus_plus_pi = lambda radians: (radians + pi) % (2 * pi) - pi


def correct_linke_turbidity_factor(
    linke_turbidity_factor: Annotated[Optional[float], typer_argument_linke_turbidity_factor] = 2,
):
    """Calculate the air mass 2 Linke atmospheric turbidity factor"""
    # debug(locals())
    return -0.8662 * linke_turbidity_factor


def calculate_refracted_solar_altitude(
    solar_altitude: Annotated[float, typer_argument_solar_altitude],
    angle_input_units: Annotated[str, typer_option_angle_units] = 'degrees',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = 'radians',
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
    """
    if angle_input_units != "degrees":
        raise ValueError(f"Only `degrees` are supported for `angle_input_units`.")

    atmospheric_refraction = (
        0.061359
        * (
            0.1594
            + 1.123 * solar_altitude.value
            + 0.065656 * pow(solar_altitude.value, 2)
        )
        / (1 + 28.9344 * solar_altitude.value + 277.3971 * pow(solar_altitude.value, 2))
    )
    refracted_solar_altitude = solar_altitude.value + atmospheric_refraction
    refracted_solar_altitude = convert_float_to_radians_if_requested(
        refracted_solar_altitude, angle_output_units
    )

    # debug(locals())
    return refracted_solar_altitude


def calculate_refracted_solar_altitude_time_series(
    solar_altitudes: np.ndarray,
    angle_input_units: str = 'degrees',
    angle_output_units: str = 'radians',
):
    """Adjust the solar altitude angle for atmospheric refraction for a time series of solar altitudes.
    
    This function is vectorized to handle arrays of solar altitudes.
    """
    if angle_input_units != "degrees":
        raise ValueError("Only degrees are supported for angle_input_units.")

    # Vectorized calculation of atmospheric refraction
    atmospheric_refraction = (
        0.061359
        * (
            0.1594
            + 1.123 * solar_altitude_series
            + 0.065656 * np.power(solar_altitude_series, 2)
        )
        / (
            1
            + 28.9344 * solar_altitude_series
            + 277.3971 * np.power(solar_altitude_series, 2)
        )
    )
    refracted_solar_altitude_series = solar_altitude_series + atmospheric_refraction
    refracted_solar_altitude_series = convert_to_radians_if_requested(
        refracted_solar_altitude_series, angle_output_units
    )

    return refracted_solar_altitude_series


@validate_with_pydantic(CalculateOpticalAirMassInputModel, expand_args=True)
def calculate_optical_air_mass(
    elevation: Annotated[float, typer_argument_elevation],
    refracted_solar_altitude: Annotated[float, typer_argument_refracted_solar_altitude],
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
) -> float:
    """Approximate the relative optical air mass.

    This function implements the algorithm described by Minzer et al. [1]_ 
    and Hofierka [2]_.

    Parameters
    ----------
    elevation: float
        The elevation in meters

    refracted_solar_altitude: float
        Refracted solar altitude angle in degrees

    angle_units: str, default='degrees'
        The expected units for the refracted solar altitude is 'degrees'.

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
    # debug(locals())
    optical_air_mass = adjust_elevation(elevation) / (
            sin(refracted_solar_altitude.value)
            + 0.50572
            * math.pow((refracted_solar_altitude.value + 6.07995), -1.6364)
            )

    # debug(locals())
    return optical_air_mass


def calculate_optical_air_mass_time_series(
    elevations: np.ndarray,
    refracted_solar_altitude_series: np.ndarray,
    angle_units: str = 'radians',
) -> np.ndarray:
    """Vectorized function to approximate the relative optical air mass for a time series."""
    optical_air_masse_series = adjust_elevation(elevations) / (
        np.sin(refracted_solar_altitude_series)
        + 0.50572
        * np.power((refracted_solar_altitude_series + 6.07995), -1.6364)
    )
    
    return optical_air_masse_series


def rayleigh_optical_thickness(
    optical_air_mass: Annotated[float, typer_option_optical_air_mass] = 2,
):
    """
    δ R(m) = 1/(6.6296 + 1.7513m - 0.1202m2 + 0.0065m3 - 0.00013m4)
    This function implements the algorithm described by Hofierka, 2002 [1]_

    Returns
    -------
    rayleigh_optical_thickness: float
        Unitless rayleigh optical thickness

    .. [1] Hofierka, 2002
    """
    if optical_air_mass <= 20:
        rayleigh_optical_thickness = 1 / (
        6.6296 + 1.7513 * optical_air_mass
        - 0.1202 * math.pow(optical_air_mass, 2)
        + 0.0065 * math.pow(optical_air_mass, 3)
        - 0.00013* math.pow(optical_air_mass, 4)
        )

    if optical_air_mass > 20:
        rayleigh_optical_thickness = 1 / (10.4 + 0.718 * optical_air_mass)

    # debug(locals())
    return rayleigh_optical_thickness


@app.command('normal', no_args_is_help=True)
def calculate_direct_normal_irradiance(
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    linke_turbidity_factor: Annotated[Optional[float], typer_option_linke_turbidity_factor] = 2,
    optical_air_mass: Annotated[float, typer_option_optical_air_mass] = 2,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = 365,  # 365.25,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = 0.048869,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = 0.03344,
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
    direct_normal_irradiance = extraterrestial_normal_irradiance * exp(
            correct_linke_turbidity_factor(linke_turbidity_factor)
            * optical_air_mass
            * rayleigh_optical_thickness(optical_air_mass)
            )
    typer.echo(f'Direct normal irradiance: {direct_normal_irradiance}')  # B0c

    return direct_normal_irradiance  # B0c


@app.command('horizontal', no_args_is_help=True)
def calculate_direct_horizontal_irradiance(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    linke_turbidity_factor: Annotated[Optional[float], typer_option_linke_turbidity_factor] = 2,
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = True,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = 1.5853349194640094,  # radians
    solar_time_model: Annotated[SolarTimeModels, typer_option_solar_time_model] = SolarTimeModels.skyfield,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = 0,
    hour_offset: Annotated[float, typer_option_hour_offset] = 0,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = 365,  # 365.25,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = 0.048869,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = 0.03344,
    time_output_units: Annotated[str, typer_option_time_output_units] = 'minutes',
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = 'radians',
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = 5,
    verbose: Annotated[Optional[bool], typer_option_verbose]= False,
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
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        solar_time_model=solar_time_model,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
        )
    # expects solar altitude in degrees! -------------------------------------
    expected_solar_altitude_units = 'degrees'
    solar_altitude_in_degrees = convert_to_degrees_if_requested(
            solar_altitude,
            expected_solar_altitude_units,  # Here!
            )
    # refracted_solar_altitude, refracted_solar_altitude_units = calculate_refracted_solar_altitude(
    refracted_solar_altitude = calculate_refracted_solar_altitude(
            solar_altitude=solar_altitude_in_degrees,
            angle_input_units=expected_solar_altitude_units,
            angle_output_units='radians',  # Here in radians!
            )
    optical_air_mass = calculate_optical_air_mass(
            elevation=elevation,
            refracted_solar_altitude=refracted_solar_altitude,
            angle_units=expected_solar_altitude_units,  # and Here!
            )
    # --------------------------------------expects solar altitude in degrees!
    direct_normal_irradiance = calculate_direct_normal_irradiance(
            optical_air_mass=optical_air_mass,
            linke_turbidity_factor=linke_turbidity_factor,
            # day_of_year=day_of_year,  # day_of_year = timestamp.timetuple().tm_yday
            # day_of_year=timestamp.timetuple().tm_yday,
            timestamp=timestamp,
            solar_constant=solar_constant,
            days_in_a_year=days_in_a_year,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            )
    direct_horizontal_irradiance = direct_normal_irradiance * sin(solar_altitude.value)

    # table_with_inputs = convert_dictionary_to_table(locals())
    # console.print(table_with_inputs)
    typer.echo(f'Direct horizontal irradiance: {direct_horizontal_irradiance}')  # B0c
    return direct_horizontal_irradiance


@app.command('inclined', no_args_is_help=True)
def calculate_direct_inclined_irradiance_pvgis(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    direct_horizontal_component: Annotated[Optional[Path], typer_option_direct_horizontal_component] = None,
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = False,
    inexact_matches_method: Annotated[MethodsForInexactMatches, typer_option_inexact_matches_method] = MethodsForInexactMatches.nearest,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = 0.1, # Customize default if needed
    in_memory: Annotated[bool, typer_option_in_memory] = False,
    surface_tilt: Annotated[Optional[float], typer_argument_surface_tilt] = 45,
    surface_orientation: Annotated[Optional[float], typer_argument_surface_orientation] = 180,
    linke_turbidity_factor: Annotated[Optional[float], typer_option_linke_turbidity_factor] = 2,
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = True,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = 1.5853349194640094,  # radians
    solar_declination_model: Annotated[SolarDeclinationModels, typer_option_solar_declination_model] = SolarDeclinationModels.pvis,
    solar_incidence_model: Annotated[SolarIncidenceModels, typer_option_solar_incidence_model] = SolarIncidenceModels.jenco,
    solar_time_model: Annotated[SolarTimeModels, typer_option_solar_time_model] = SolarTimeModels.skyfield,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = 0,
    hour_offset: Annotated[float, typer_option_hour_offset] = 0,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = 365.25,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = 0.048869,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = 0.03344,
    time_output_units: Annotated[str, typer_option_time_output_units] = 'minutes',
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = 'radians',
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = 5,
    verbose: Annotated[Optional[bool], typer_option_verbose]= False,
):
    """Calculate the direct irradiance incident on a tilted surface [W*m-2] 

    This function implements the algorithm described by Hofierka
    :cite:`p:hofierka2002`.
    """
    # Notes
    # -----
    #           B   ⋅ sin ⎛δ   ⎞                    
    #            hc       ⎝ exp⎠         ⎛ W ⎞
    #     B   = ────────────────     in  ⎜───⎟
    #      ic       sin ⎛h ⎞             ⎜ -2⎟           
    #                   ⎝ 0⎠             ⎝m  ⎠           
    year = timestamp.year
    start_of_year = datetime(year=year, month=1, day=1,
                             tzinfo=timestamp.tzinfo)
    day_of_year = timestamp.timetuple().tm_yday
    hour_of_year = int((timestamp - start_of_year).total_seconds() / 3600)

    # day_of_year_in_radians = double_numpi * day_of_year / days_in_a_year  

    # Hofierka, 2002 ------------------------------------------------------
    # tangent_relative_longitude = - sin(surface_tilt)
    #                              * sin(surface_orientation) /
    #                                sin(latitude) 
    #                              * sin(surface_tilt) 
    #                              * cos(surface_orientation) 
    #                              + cos(latitude) 
    #                              * cos(surface_tilt)
    tangent_relative_longitude = -sin(surface_tilt) * sin(
        surface_orientation
    ) / sin(latitude) * sin(surface_tilt) * cos(
        surface_orientation
    ) + cos(
        latitude
    ) * cos(
        surface_tilt
    )
    # C source code -------------------------------------------------------
    # There is an error of one negative sign in either of the expressions!
    # That is so because : cos(pi/2 + x) = -sin(x)
    # tangent_relative_longitude = - cos(half_pi - surface_tilt)  # cos(pi/2 - x) = sin(x)
    #                              * cos(half_pi + surface_orientation) /  # cos(pi/2 + x) = -sin(x)
    #                                sin(latitude) 
    #                              * cos(half_pi - surface_tilt) 
    #                              * sin(half_pi + surface_orientation)  # sin(pi/2 + x) = cos(x)
    #                              + cos(latitude) 
    #                              * sin(half_pi - surface_tilt)  # sin(pi/2 - x) = cos(x)
    # --------------------------------------------------------------------

    relative_longitude = atan(tangent_relative_longitude)
    # cos(hour_angle - relative_longitude) = C33_inclined / C31_inclined

    # Hofierka, 2002
    # sine_relative_latitude = -cos(latitude) 
    #                          * sin(surface_tilt)
    #                          * cos(surface_orientation)
    #                          + sin(latitude)
    #                          * cos (surface_tilt)
    sine_relative_latitude = -cos(latitude) * sin(surface_tilt) * cos(
        surface_orientation
    ) + sin(latitude) * cos(surface_tilt)
    # Verified the following is equal to above.
    # Huld ?
    # sine_relative_latitude = -cos(latitude)
    #                          * cos(half_pi - surface_tilt)
    #                          * sin(half_pi + surface_orientation)
    #                          + sin(latitude)
    #                          * sin(half_pi - surface_tilt)
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
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
    )
    sine_solar_altitude = sin(solar_altitude.value)

    # make it a function -----------------------------------------------------
    #

    # calculate solar declination + C3x geometry parameters
    solar_declination = model_solar_declination(
            timestamp=timestamp,
            timezone=timezone,
            model=solar_declination_model,
            days_in_a_year=days_in_a_year,
            eccentricity_correction_factor=eccentricity_correction_factor,
            perigee_offset=perigee_offset,
            angle_output_units=angle_output_units,
            )
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
            time_output_units=time_output_units,
            angle_units=angle_units,
            angle_output_units=angle_output_units,
    )
    solar_time_decimal_hours = timestamp_to_decimal_hours(solar_time)
    hour_angle = np.radians(15) * (solar_time_decimal_hours - 12)

    # calculate C3x geometry parameters for inclined surface
    relative_latitude = math.asin(sine_relative_latitude)
    C31_inclined = math.cos(relative_latitude) * math.cos(solar_declination.value)
    C33_inclined = math.sin(relative_latitude) * math.sin(solar_declination.value)

    # calculate solar incidence angle
    sine_solar_incidence_angle = C31_inclined * math.cos (hour_angle - relative_longitude) + C33_inclined

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
        time = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        longitude_for_selection = convert_float_to_degrees_if_requested(longitude, 'degrees')
        latitude_for_selection = convert_float_to_degrees_if_requested(latitude, 'degrees')
        direct_horizontal_irradiance = select_time_series(
                time_series=direct_horizontal_component,
                longitude=longitude_for_selection,
                latitude=latitude_for_selection,
                time=time,
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
    except ZeroDivisionError:
        logging.error(f"Error: Division by zero in calculating the direct inclined irradiance!")
        typer.echo("Is the solar altitude angle zero?")
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
            typer.echo(f'Direct inclined irradiance: {direct_inclined_irradiance} (based on {PVGIS})')  # B0c

            return direct_inclined_irradiance

        # Else, the following runs:
        # --------------------------------- Review & Add ?
            # 1. surface is shaded
            # 3. solar declination = 0
        # --------------------------------- Review & Add ?
        except ZeroDivisionError as e:
            logging.error(f"Which Error? {e}")
            raise ValueError

    typer.echo(f'Direct inclined irradiance: {modified_direct_horizontal_irradiance} (based on {solar_incidence_model})')  # B0c

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
    direct_horizontal_component: Annotated[Optional[Path], typer_option_direct_horizontal_component] = None,
    # direct_horizontal_radiation: Annotated[float, typer.Argument(
    #     help='Direct normal radiation in W/m²',
    #     min=-9000, max=1000)],  # `sh` which comes from `s0`
    # direct_horizontal_radiation_coefficient: Annotated[float, typer.Argument(
    #     help='Direct normal radiation coefficient (dimensionless)',
    #     min=0, max=1)],  # bh = sunRadVar->cbh;
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = False,
    inexact_matches_method: Annotated[MethodsForInexactMatches, typer_option_inexact_matches_method] = MethodsForInexactMatches.nearest,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = 0.1, # Customize default if needed
    in_memory: Annotated[bool, typer_option_in_memory] = False,
    surface_tilt: Annotated[Optional[float], typer_argument_surface_tilt] = 45,
    surface_orientation: Annotated[Optional[float], typer_argument_surface_orientation] = 180,
    linke_turbidity_factor: Annotated[Optional[float], typer_option_linke_turbidity_factor] = 2,
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = True,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = 1.5853349194640094,  # radians
    solar_incidence_model: Annotated[SolarIncidenceModels, typer_option_solar_incidence_model] = SolarIncidenceModels.jenco,
    solar_time_model: Annotated[SolarTimeModels, typer_option_solar_time_model] = SolarTimeModels.skyfield,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = 0,
    hour_offset: Annotated[float, typer_option_hour_offset] = 0,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = 365.25,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = 0.048869,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = 0.03344,
    time_output_units: Annotated[str, typer_option_time_output_units] = 'minutes',
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = 'radians',
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = 5,
    verbose: Annotated[Optional[bool], typer_option_verbose]= False,
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
    #     typer.echo(f'Direct horizontal irradiance: {direct_horizontal_irradiance}')
    #     direct_horizontal_irradiance = calculate_direct_horizontal_irradiance()
    #     return direct_horizontal_irradiance  # Bhc

    # if surface_tilt != 0:
    #     direct_inclined_irradiance = calculate_direct_inclined_irradiance()
    #     typer.echo(f'Direct inclined irradiance : {direct_inclined_irradiance}')
    #     return direct_inclined_irradiance  # Bic
