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
import numpy as np
from datetime import datetime
from ..constants import AOI_CONSTANTS
from ..geometry.solar_declination import calculate_solar_declination
from ..geometry.solar_time import SolarTimeModels
from ..geometry.solar_time import model_solar_time
from ..utilities.conversions import convert_to_radians
from ..utilities.conversions import convert_dictionary_to_table
from ..utilities.timestamp import attach_timezone
from ..utilities.timestamp import ctx_convert_to_timezone
from ..utilities.timestamp import now_datetime
from .angular_loss_factor import calculate_angular_loss_factor
from .extraterrestrial_irradiance import calculate_extraterrestrial_irradiance


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


# some correction for the given elevation (Hofierka, 2002)
adjust_elevation = lambda elevation: math.exp(-elevation / 8434.5)

# ensure value ranges in [-pi, pi]
range_in_minus_plus_pi = lambda radians: (radians + math.pi) % (2 * math.pi) - math.pi
corrected_linke_turbidity_factor = lambda tlk: -0.8662 * tlk


def calculate_refracted_solar_altitude(
        solar_altitude: float,
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
            * (0.1594 + 1.123 * solar_altitude + 0.065656 * math.pow(solar_altitude, 2))
            / (1 + 28.9344 * solar_altitude + 277.3971 * math.pow(solar_altitude, 2))
            )
    refracted_solar_altitude = solar_altitude + atmospheric_refraction
    return refracted_solar_altitude


def calculate_optical_air_mass(
        elevation: float,
        refracted_solar_altitude: float, 
        ):
    """
    This function implements the algorithm described by Hofierka :cite:`p:hofierka2002`.
    """
    optical_air_mass = adjust_elevation(elevation) / (
            math.sin(refracted_solar_altitude)
            + 0.50572
            * math.pow((refracted_solar_altitude + 6.07995), -1.6364)
            )
    return optical_air_mass


def rayleigh_optical_thickness(
        optical_air_mass: float,
        ):
    """
    δ R(m) = 1/(6.6296 + 1.7513m - 0.1202m2 + 0.0065m3 - 0.00013m4)
    This function implements the algorithm described by Hofierka
    :cite:`p:hofierka2002`.
    """
    if optical_air_mass <= 20:
        rayleigh_optical_thickness = 1 / (
        6.6296 + 1.7513 * optical_air_mass
        - 0.1202 * pow(optical_air_mass, 2)
        + 0.0065 * pow(optical_air_mass, 3)
        - 0.00013* pow(optical_air_mass, 4)
        )

    if optical_air_mass > 20:
        rayleigh_optical_thickness = 1 / (10.4 + 0.718 * optical_air_mass)

    return rayleigh_optical_thickness


@app.command('normal', no_args_is_help=True)
def calculate_direct_normal_irradiance(
        extraterrestial_irradiance: Annotated[float, typer.Argument(
            help="The average annual solar radiation arriving at the top of the Earth's atmosphere, about 1361 W/m2",
            min=1360)],
        linke_turbidity_factor: Annotated[float, typer.Argument(
            help='A measure of atmospheric turbidity, equal to the ratio of total optical depth to the Rayleigh optical depth',
            min=0, max=8)],
        optical_air_mass: float,
        ):
    """Calculate the direct normal irradiance attenuated by the cloudless
    atmosphere

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
        attenuation of the radiation by the clear sky atmosphere.

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
    direct_normal_irradiance = extraterrestial_irradiance * math.exp(
            corrected_linke_turbidity_factor(linke_turbidity_factor)
            * optical_air_mass
            * rayleigh_optical_thickness(optical_air_mass)
            )

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
            default_factory=now_datetime)],
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
            '-m',
            '--solar-time-model',
            help="Model to calculate solar position",
            show_default=True,
            show_choices=True,
            case_sensitive=False)] = SolarTimeModels.skyfield,
        ):
    """Calculate the direct irradiatiance incident on a horizontal surface

    This function implements the algorithm described by Hofierka
    :cite:`p:hofierka2002`.
    """
    # if timestamp.tzinfo is None:
    #     timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)

    day_of_year = timestamp.timetuple().tm_yday
    solar_declination = calculate_solar_declination(timestamp)
    C31 = math.cos(latitude) * math.cos(solar_declination)
    C33 = math.sin(latitude) * math.sin(solar_declination)

    year = timestamp.year
    start_of_year = datetime(year=year, month=1, day=1, tzinfo=timestamp.tzinfo)
    hour_of_year = int((timestamp - start_of_year).total_seconds() / 3600)
    # -------------------------------------------------------------------------
    solar_time, _units = model_solar_time(
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
    hour_angle = np.radians(15) * (solar_time - 12)
    # -------------------------------------------------------------------------

    sine_solar_altitude = C31 * math.cos(hour_angle) + C33
    solar_altitude = math.asin(sine_solar_altitude)
    refracted_solar_altitude = calculate_refracted_solar_altitude(
            solar_altitude=solar_altitude,
            )
    optical_air_mass = calculate_optical_air_mass(
            elevation=elevation,
            refracted_solar_altitude=refracted_solar_altitude,
            )

    extraterrestial_irradiance = calculate_extraterrestrial_irradiance(day_of_year)
    direct_normal_irradiance = calculate_direct_normal_irradiance(
            extraterrestial_irradiance=extraterrestial_irradiance,
            linke_turbidity_factor=linke_turbidity_factor,
            optical_air_mass=optical_air_mass,
            )
    direct_horizontal_irradiance = direct_normal_irradiance * sine_solar_altitude

    table_with_inputs = convert_dictionary_to_table(locals())
    console.print(table_with_inputs)
    typer.echo(f'Direct horizontal irradiance: {direct_horizontal_irradiance}')  # B0c
    return direct_horizontal_irradiance


@app.command('inclined', no_args_is_help=True)
def calculate_direct_inclined_irradiance(
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
            default_factory=now_datetime)],
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
            '--solar-time-model',
            help="Model to calculate solar position",
            show_default=True,
            show_choices=True,
            case_sensitive=False)] = SolarTimeModels.skyfield,
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
    tangent_relative_longitude = -math.sin(surface_tilt) * math.sin(
        surface_orientation
    ) / math.sin(latitude) * math.sin(surface_tilt) * math.cos(
        surface_orientation
    ) + math.cos(
        latitude
    ) * math.cos(
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

    relative_longitude = math.atan(tangent_relative_longitude)
    # cos(hour_angle - relative_longitude) = C33_inclined / C31_inclined

    # Hofierka, 2002
    # sine_relative_latitude = -cos(latitude) 
    #                          * sin(surface_tilt)
    #                          * cos(surface_orientation)
    #                          + sin(latitude)
    #                          * cos (surface_tilt)
    sine_relative_latitude = -math.cos(latitude) * math.sin(surface_tilt) * math.cos(
        surface_orientation
    ) + math.sin(latitude) * math.cos(surface_tilt)
    # Verified the following is equal to above.
    # Huld ?
    # sine_relative_latitude = -cos(latitude)
    #                          * cos(half_pi - surface_tilt)
    #                          * sin(half_pi + surface_orientation)
    #                          + sin(latitude)
    #                          * sin(half_pi - surface_tilt)

    # calculate solar declination + C3x geometry parameters
    solar_declination = calculate_solar_declination(timestamp)
    C31 = math.cos(latitude) * math.cos(solar_declination)
    C33 = math.sin(latitude) * math.sin(solar_declination)

    # calculate solar altitude
    solar_time, _units = model_solar_time(
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
    hour_angle = np.radians(15) * (solar_time - 12)
    sine_solar_altitude = C31 * math.cos(hour_angle) + C33
    solar_altitude = math.asin(sine_solar_altitude)

    # calculate C3x geometry parameters for inclined surface
    relative_latitude = math.asin(sine_relative_latitude)
    C31_inclined = math.cos(relative_latitude) * math.cos(solar_declination)
    C33_inclined = math.sin(relative_latitude) * math.sin(solar_declination)

    # calculate solar incidence angle
    solar_incidence_angle = C31_inclined * math.cos (hour_angle - relative_longitude) + C33_inclined

    # "Simpler" way to calculate the inclined solar declination?
    if solar_incidence_angle_model == 'simple':
        modified_direct_horizontal_irradiance = direct_horizontal_irradiance / math.sin(solar_altitude)
        # In the old C source code, the following runs if:
        # --------------------------------- Review & Add ?
            # 1. surface is NOT shaded
            # 3. solar declination > 0
        # --------------------------------- Review & Add ?
        try:
            angular_loss_factor = calculate_angular_loss_factor(
                    solar_altitude,
                    solar_declination,
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
            direct_inclined_irradiance = direct_horizontal_irradiance * math.sin(solar_incidence_angle) / math.sin(solar_altitude)

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
            default_factory=now_datetime)],
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
