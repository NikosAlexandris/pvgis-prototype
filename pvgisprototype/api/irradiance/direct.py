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
import math
from math import sin
from math import cos
from math import exp
from math import atan
import numpy as np
from datetime import datetime
from ..constants import AOI_CONSTANTS
from ..geometry.solar_declination import calculate_solar_declination
from ..geometry.time_models import SolarTimeModels
from ..geometry.solar_time import model_solar_time
from ..utilities.conversions import convert_to_radians
from ..utilities.conversions import convert_to_degrees_if_requested
from ..utilities.conversions import convert_dictionary_to_table
from ..utilities.timestamp import attach_timezone
from ..utilities.timestamp import now_utc_datetimezone
from ..utilities.timestamp import ctx_convert_to_timezone
from ..utilities.timestamp import timestamp_to_decimal_hours
from .loss import calculate_angular_loss_factor
from .extraterrestrial import calculate_extraterrestrial_irradiance

from .input_models import OpticalAirMassInputModel
from .input_models import Elevation
from .input_models import IrradianceInputModel
from pvgisprototype.api.decorators import validate_with_pydantic

from pydantic import BaseModel
from pydantic import Field
from pydantic import validator
from math import radians
from math import degrees


console = Console()
app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"Estimate the direct solar radiation",
)


class DirectIrradianceComponents(str, Enum):
    normal = 'normal'
    on_horizontal_surface = 'horizontal'
    on_inclined_surface = 'inclined'


class SolarIncidenceAngleMethod(str, Enum):
    jenco = 'Jenco'
    simple = 'PVGIS'


# Forbid using --solar-time-model all wherever it does not make sense?
# def validate_solar_time_model(value: SolarTimeModels) -> SolarTimeModels:
#     if value == SolarTimeModels.all:
#         raise typer.BadParameter("The 'all' option is not allowed.")
#     return value


@validate_with_pydantic(Elevation, expand_args=True)
def adjust_elevation(elevation: float):
    """Some correction for the given solar altitude 

    [1]_

    Notes
    -----

    .. [1] Hofierka, 2002
    """
    # debug(locals())
    return exp(-elevation / 8434.5)


# ensure value ranges in [-pi, pi]
range_in_minus_plus_pi = lambda radians: (radians + pi) % (2 * pi) - pi

def correct_linke_turbidity_factor(linke_turbidity_factor):
    """Calculate the air mass 2 Linke atmospheric turbidity factor"""
    # debug(locals())
    return -0.8662 * linke_turbidity_factor


def calculate_refracted_solar_altitude(
        solar_altitude: float,
        angle_units: str = 'degrees',
        angle_output_units: str = 'degrees',
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
    atmospheric_refraction = (
            0.061359
            * (0.1594 + 1.123 * solar_altitude + 0.065656 * pow(solar_altitude, 2))
            / (1 + 28.9344 * solar_altitude + 277.3971 * pow(solar_altitude, 2))
            )
    refracted_solar_altitude = solar_altitude + atmospheric_refraction

    # debug(locals())
    return refracted_solar_altitude, angle_output_units


@validate_with_pydantic(OpticalAirMassInputModel, expand_args=True)
def calculate_optical_air_mass(elevation, refracted_solar_altitude, angle_units) -> float:
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
            sin(refracted_solar_altitude)
            + 0.50572
            * math.pow((refracted_solar_altitude + 6.07995), -1.6364)
            )

    # debug(locals())
    return optical_air_mass


def rayleigh_optical_thickness(
        optical_air_mass: float,
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
# def calculate_direct_normal_irradiance(irradiance_input: IrradianceInputModel
def calculate_direct_normal_irradiance(
        linke_turbidity_factor: Annotated[float, typer.Argument(
            help='A measure of atmospheric turbidity',
            min=0, max=8)],
        optical_air_mass: float,
        extraterrestial_irradiance: Annotated[float, typer.Argument(
            help='The average solar radiation at the top of the atmosphere ~1360.8 W/m^2 (Kopp, 2011)',
            min=1360)] = 1360.8,
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
    # direct_normal_irradiance = extraterrestial_irradiance * exp(
    #         corrected_linke_turbidity_factor(irradiance_input.linke_turbidity_factor)
    #         * irradiance_input.optical_air_mass
    #         * rayleigh_optical_thickness(irradiance_input.optical_air_mass)
    #         )
    direct_normal_irradiance = extraterrestial_irradiance * exp(
            correct_linke_turbidity_factor(linke_turbidity_factor)
            * optical_air_mass
            * rayleigh_optical_thickness(optical_air_mass)
            )

    # debug(locals())
    typer.echo(f'Direct normal irradiance: {direct_normal_irradiance}')  # B0c
    return direct_normal_irradiance  # B0c


@app.command('horizontal', no_args_is_help=True)
def calculate_direct_horizontal_irradiance(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians, min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians, min=-90, max=90)],
        elevation: float,
        linke_turbidity_factor: float,
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Timezone',
            callback=ctx_convert_to_timezone)] = None,
        days_in_a_year: Annotated[float, typer.Option(
            help='Days in a year')] = 365.25,
        perigee_offset: Annotated[float, typer.Option(
            help='Perigee offset')] = 0.048869,
        eccentricity: Annotated[float, typer.Option(
            help='Eccentricity')] = 0.01672,
        time_offset_global: Annotated[float, typer.Option(
            help='Global time offset')] = 0,
        hour_offset: Annotated[float, typer.Option(
            help='Hour offset')] = 0,
        solar_time_model: Annotated[SolarTimeModels, typer.Option(
            help="Model to calculate solar position",
            show_default=True,
            show_choices=True,
            case_sensitive=False,
            rich_help_panel=rich_help_panel_solar_time)] = SolarTimeModels.skyfield,
        angle_output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Angular units for the calculated solar azimuth output (degrees or radians)")] = 'radians',
        ):
    """Calculate the direct irradiatiance incident on a horizontal surface

    This function implements the algorithm described by Hofierka
    :cite:`p:hofierka2002`.
    """
    # if timestamp.tzinfo is None:
    #     timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)

    day_of_year = timestamp.timetuple().tm_yday
    solar_declination = calculate_solar_declination(
            timestamp=timestamp,
            timezone=timezone,
            days_in_a_year=days_in_a_year,
            orbital_eccentricity=eccentricity,
            perigee_offset=perigee_offset,
            angle_output_units=angle_output_units,
            )
    C31 = cos(latitude) * cos(solar_declination)
    C33 = sin(latitude) * sin(solar_declination)


    sine_solar_altitude = C31 * math.cos(hour_angle) + C33
    solar_altitude = math.asin(sine_solar_altitude)
    solar_altitude_angle_units = 'degrees'
    # debug(locals())
    solar_altitude_in_degrees = convert_to_degrees_if_requested(solar_altitude,
                                                                solar_altitude_angle_units,
                                                                )
    # expects solar altitude in degrees!
    refracted_solar_altitude, refracted_solar_altitude_units = calculate_refracted_solar_altitude(
            solar_altitude=solar_altitude_in_degrees,
            angle_units=solar_altitude_angle_units,
            )
    optical_air_mass = calculate_optical_air_mass(
            elevation=elevation,
            refracted_solar_altitude=refracted_solar_altitude,
            angle_units=solar_altitude_angle_units,
            )
    # debug(locals())

    extraterrestial_irradiance = calculate_extraterrestrial_irradiance(day_of_year)
    direct_normal_irradiance = calculate_direct_normal_irradiance(
            linke_turbidity_factor=linke_turbidity_factor,
            optical_air_mass=optical_air_mass,
            extraterrestial_irradiance=extraterrestial_irradiance,
            )
    # debug(locals())
    direct_horizontal_irradiance = direct_normal_irradiance * sine_solar_altitude

    table_with_inputs = convert_dictionary_to_table(locals())
    console.print(table_with_inputs)
    typer.echo(f'Direct horizontal irradiance: {direct_horizontal_irradiance}')  # B0c
    return direct_horizontal_irradiance


@app.command('inclined', no_args_is_help=True)
def calculate_direct_inclined_irradiance_pvgis(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        elevation: Annotated[float, typer.Argument(
            min=0, max=8848)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Timezone',
            callback=ctx_convert_to_timezone)] = None,
        surface_tilt: Annotated[Optional[float], typer.Argument(
            min=0, max=90)] = 0,
        surface_orientation: Annotated[Optional[float], typer.Argument(
            min=0, max=360)] = 180,
        linke_turbidity_factor: Annotated[float, typer.Argument(
            help='A measure of atmospheric turbidity, equal to the ratio of total optical depth to the Rayleigh optical depth',
            min=0, max=10)] = 2,  # 2 to get going for now
        solar_incidence_angle_model: Annotated[SolarIncidenceAngleMethod, typer.Option(
            '--incidence-angle-model',
            show_default=True,
            show_choices=True,
            case_sensitive=False,
            help="Method to calculate the solar declination")] = 'jenco',
        solar_time_model: Annotated[SolarTimeModels, typer.Option(
            help="Model to calculate solar position",
            show_default=True,
            show_choices=True,
            case_sensitive=False,
            rich_help_panel=rich_help_panel_solar_time)] = SolarTimeModels.skyfield,
        days_in_a_year: Annotated[float, typer.Option(
            help='Days in a year')] = 365.25,
        perigee_offset: Annotated[float, typer.Option(
            help='Perigee offset')] = 0.048869,
        eccentricity: Annotated[float, typer.Option(
            help='Eccentricity')] = 0.01672,
        time_offset_global: Annotated[float, typer.Option(
            help='Global time offset')] = 0,
        hour_offset: Annotated[float, typer.Option(
            help='Hour offset')] = 0,
        angle_output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Angular units for the calculated solar azimuth output (degrees or radians)")] = 'radians',
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

    direct_horizontal_irradiance = calculate_direct_horizontal_irradiance(
            longitude=longitude,  # required by some of the solar time algorithms
            latitude=latitude,
            elevation=elevation,
            timestamp=timestamp,
            timezone=timezone,
            linke_turbidity_factor=linke_turbidity_factor,
            )

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

    # calculate solar declination + C3x geometry parameters
    solar_declination = calculate_solar_declination(
            timestamp=timestamp,
            timezone=timezone,
            days_in_a_year=days_in_a_year,
            orbital_eccentricity=eccentricity,
            perigee_offset=perigee_offset,
            angle_output_units=angle_output_units,
            )
    C31 = cos(latitude) * cos(solar_declination)
    C33 = sin(latitude) * sin(solar_declination)

    # calculate solar altitude
    solar_time = model_solar_time(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            model=solar_time_model,
            days_in_a_year=days_in_a_year,
            perigee_offset=perigee_offset,
            eccentricity=eccentricity,
            time_offset_global=time_offset_global,
            hour_offset=hour_offset
    )
    solar_time_decimal_hours = timestamp_to_decimal_hours(solar_time)
    hour_angle = np.radians(15) * (solar_time_decimal_hours - 12)
    sine_solar_altitude = C31 * math.cos(hour_angle) + C33
    # solar_altitude = math.asin(sine_solar_altitude)

    # calculate C3x geometry parameters for inclined surface
    relative_latitude = math.asin(sine_relative_latitude)
    C31_inclined = math.cos(relative_latitude) * math.cos(solar_declination)
    C33_inclined = math.sin(relative_latitude) * math.sin(solar_declination)

    # calculate solar incidence angle
    sine_solar_incidence_angle = C31_inclined * math.cos (hour_angle - relative_longitude) + C33_inclined

    # "Simpler" way to calculate the inclined solar declination?
    if solar_incidence_angle_model == 'simple':
        modified_direct_horizontal_irradiance = (
            direct_horizontal_irradiance
            * sine_solar_incidence_angle
            / sine_solar_altitude
        )
        # In the old C source code, the following runs if:
        # --------------------------------- Review & Add ?
            # 1. surface is NOT shaded
            # 3. solar declination > 0
        # --------------------------------- Review & Add ?

        try:
            angular_loss_factor = calculate_angular_loss_factor(
                    sine_solar_incidence_angle,
                    angle_of_incidence_constant = 0.155,
                    )
            direct_inclined_irradiance = modified_direct_horizontal_irradiance * angular_loss_factor

            # Deduplicate Me! -------------------------------------------------
            typer.echo(f'Direct inclined irradiance: {direct_inclined_irradiance}')  # B0c
            return direct_inclined_irradiance
            # Deduplicate Me! -------------------------------------------------

        # Else, the following runs:
        # --------------------------------- Review & Add ?
            # 1. surface is shaded
            # 3. solar declination = 0
        # --------------------------------- Review & Add ?
        except ZeroDivisionError as e:
            logging.error(f"Zero Division Error: {e}")
            typer.echo("Is the solar altitude angle zero?")
            # see brad_angle_irradiance() - however, why return anything?

            # Deduplicate Me! -------------------------------------------------
            typer.echo(f'Direct inclined irradiance: {direct_inclined_irradiance} (based on {simple})')  # B0c
            return modified_direct_horizontal_irradiance
            # Deduplicate Me! -------------------------------------------------

    if solar_incidence_angle_model == 'jenco':
        try:
            # split the following and deduplicate?
            # i.e. reuse modified_direct_horizontal_irradiance?
            direct_inclined_irradiance = direct_horizontal_irradiance * sine_solar_incidence_angle / sine_solar_altitude

            # Deduplicate Me! -------------------------------------------------
            typer.echo(f'Direct inclined irradiance: {direct_inclined_irradiance} (based on {solar_incidence_angle_model})')  # B0c
            return direct_inclined_irradiance
            # Deduplicate Me! -------------------------------------------------

        except ZeroDivisionError:
            logging.error(f"Error: Division by zero in calculating the direct inclined irradiance based on the solar declination algorithm by Jenco 1992.")

            typer.echo("Is the solar altitude angle zero?")
            # should this return something? Like in r.sun's simpler's approach?
            return 0


# from: rsun_base.c
# function name: brad_angle_irradiance
# @app.command('direct', no_args_is_help=True)
def calculate_direct_irradiance(
        latitude: Annotated[Optional[float], typer.Argument(min=-90, max=90)],
        # direct_horizontal_radiation: Annotated[float, typer.Argument(
        #     help='Direct normal radiation in W/m²',
        #     min=-9000, max=1000)],  # `sh` which comes from `s0`
        # direct_horizontal_radiation_coefficient: Annotated[float, typer.Argument(
        #     help='Direct normal radiation coefficient (dimensionless)',
        #     min=0, max=1)],  # bh = sunRadVar->cbh;
        solar_altitude: Annotated[float, typer.Argument(
            help='Solar altitude in degrees °',
            min=0, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Timezone',
            callback=ctx_convert_to_timezone)] = None,
        component: Annotated[DirectIrradianceComponents, typer.Option(
            '-c',
            '--component',
            show_default=True,
            show_choices=True,
            case_sensitive=False,
            help="Direct irradiance component to calculate")] = 'inclined',
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
