"""
Direct irradiance

The _direct_ or _beam_ irradiance is one of the main components of solar irradiance.
It comes perpendicular from the Sun and is not scattered before it irradiates a surface.

During a cloudy day the sunlight will be partially absorbed and scattered by
different air molecules. The latter part is defined as the _diffuse_
irradiance. The remaining part is the _beam_ irradiance.
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
from pydantic import BaseModel
from pydantic import Field
from pydantic import validator
import typer
from rich import print
from typing import Union
from typing_extensions import Annotated
from typing import Optional
from enum import Enum
import numpy as np
import math
from .extraterrestrial_irradiance import calculate_extraterrestrial_irradiance
from .angular_loss_factor import calculate_angular_loss_factor


AOI_CONSTANTS = [ -0.074, 0.155]


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"Estimate the direct normal radiance",
)


# some correction for the given elevation (Hofierka, 2002)
adjust_elevation = lambda elevation: math.exp(-elevation / 8434.5)
# ensure value ranges in [-pi, pi]
range_in_minus_plus_pi = lambda radians: (radians + math.pi) % (2 * math.pi) - math.pi
corrected_linke_turbidity_factor = lambda tlk: -0.8662 * tlk


def calculate_refracted_solar_altitude(
        solar_altitude: float,
        ):
    """
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
        latitude: Annotated[Optional[float], typer.Argument(min=-90, max=90)],
        elevation: float,
        year: int,
        day_of_year: float,
        hour_of_year: int,
        linke_turbidity_factor: float,
        ):
    """Calculate the direct irradiatiance incident on a horizontal solar surface.

    This function implements the algorithm described by Hofierka
    :cite:`p:hofierka2002`.
    """
    solar_declination = calculate_solar_declination(day_of_year)
    C31 = math.cos(latitude) * math.cos(solar_declination)
    C33 = math.sin(latitude) * math.sin(solar_declination)
    solar_time = calculate_solar_time(year, hour_of_year)
    hour_angle = np.radians(15) * (solar_time - 12)
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

    typer.echo(f'Direct horizontal irradiance: {direct_horizontal_irradiance}')  # B0c
    return direct_horizontal_irradiance


@app.command('inclined', no_args_is_help=True)
def calculate_direct_inclined_irradiance(
        latitude: Annotated[Optional[float], typer.Argument(min=-90, max=90)],
        elevation: float,
        year: int,
        day_of_year: float,
        hour_of_year: int,
        surface_tilt: Annotated[Optional[float], typer.Argument(min=-90, max=90)],
        surface_orientation: float,
        direct_horizontal_radiation: Annotated[float, typer.Argument(
            help='Direct normal radiation in W/m²',
            min=-9000, max=1000)],  # `sh` which comes from `s0`
        direct_horizontal_radiation_coefficient: Annotated[float, typer.Argument(
            help='Direct normal radiation coefficient (dimensionless)',
            min=0, max=1)],  # bh = sunRadVar->cbh;
        solar_altitude: Annotated[float, typer.Argument(
            help='Solar altitude in degrees °',
            min=0, max=90)],
        # incidence_angle: Annotated[Union[IncidenceAngle, float], typer.Option(
        linke_turbidity_factor: float,
        incidence_angle: Annotated[IncidenceAngle, typer.Option(
             '--incidence-angle',
             show_default=True,
             parser=parse_incidence_angle,
             help='Angle of incidence in degrees °',
             case_sensitive=False)] = 'auto',
        ):
    """Calculate the direct irradiatiance incident on a tilted solar surface.

    This function implements the algorithm described by Hofierka
    :cite:`p:hofierka2002`.
    """
    # Hofierka, 2002 ------------------------------------------------------
    # tangent_relative_longitude = - sin(surface_tilt)
    #                              * sin(surface_orientation) /
    #                                sin(latitude) 
    #                              * sin(surface_tilt) 
    #                              * cos(surface_orientation) 
    #                              + cos(latitude) 
    #                              * cos(surface_tilt)
    tangent_relative_longitude = -math.sin(surface_tilt) * math.sin(surface_orientation) / math.sin(
        latitude
    ) * math.sin(surface_tilt) * math.cos(surface_orientation) + math.cos(latitude) * math.cos(surface_tilt)
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
    # Following is equal to above.
    # # Huld ?
    # sine_relative_latitude = -cos(latitude)
    #                          * cos(half_pi - surface_tilt)
    #                          * sin(half_pi + surface_orientation)
    #                          + sin(latitude)
    #                          * sin(half_pi - surface_tilt)
    relative_latitude = math.asin(sine_relative_latitude)
    math.cosine_relative_latitude = math.cos(relative_latitude)

    from .solar_declination import calculate_solar_declination
    solar_declination_horizontal = calculate_solar_declination(day_of_year)
    C31_inclined = math.cos(relative_latitude) * math.cos(solar_declination_horizontal)
    C33_inclined = math.sin(relative_latitude) * math.sin(solar_declination_horizontal)

    from .solar_geometry_variables import calculate_solar_time
    solar_time = calculate_solar_time(year, hour_of_year)
    hour_angle = 0.261799 * (solar_time - 12)
    solar_declination_inclined = C31_inclined * math.cos (hour_angle - relative_longitude) + C33_inclined

    direct_horizontal_irradiance = calculate_direct_horizontal_irradiance(
            latitude=latitude,
            elevation=elevation,
            year=year,
            day_of_year=day_of_year,
            hour_of_year=hour_of_year,
            solar_altitude=solar_altitude,
            linke_turbidity_factor=linke_turbidity_factor,
            )
    direct_inclined_irradiance = direct_horizontal_irradiance * math.sin(solar_declination_inclined) / math.sin(solar_altitude)
    return direct_inclined_irradiance


class DirectIrradianceComponents(str, Enum):
    normal = 'normal'
    on_horizontal_surface = 'horizontal'
    on_inclined_surface = 'inclined'


# from: rsun_base.c
# function name: brad_angle_irradiance
@app.command('direct', no_args_is_help=True)
def calculate_direct_irradiance(
        latitude: Annotated[Optional[float], typer.Argument(min=-90, max=90)],
        year: int,
        day_of_year: float,
        hour_of_year: float,
        # direct_horizontal_radiation: Annotated[float, typer.Argument(
        #     help='Direct normal radiation in W/m²',
        #     min=-9000, max=1000)],  # `sh` which comes from `s0`
        # direct_horizontal_radiation_coefficient: Annotated[float, typer.Argument(
        #     help='Direct normal radiation coefficient (dimensionless)',
        #     min=0, max=1)],  # bh = sunRadVar->cbh;
        solar_altitude: Annotated[float, typer.Argument(
            help='Solar altitude in degrees °',
            min=0, max=90)],
        # incidence_angle: Annotated[Union[IncidenceAngle, float], typer.Option(
        incidence_angle: Annotated[IncidenceAngle, typer.Option(
             '--incidence-angle',
             show_default=True,
             parser=parse_incidence_angle,
             help='Angle of incidence in degrees °',
             case_sensitive=False)] = 'auto',
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
    incidence_angle_index: int
        Index 0 or 1 for .. and .. respectively.
    sun_geometry:
        Sun geometry variables for a specific day ?
    sun_radiation_variables:
        Solar radiation variables.

    Returns
    -------
    direct_irradiance: float
        The direct radiant flux incident on a surface per unit area in W/m².

    """
    # # convert to radians!
    # sine_of_solar_altitude = np.sin(np.radians(solar_altitude))
    # try:
    #     # how to name this factor?
    #     some_factor = direct_horizontal_radiation_coefficient / sine_of_solar_altitude
    # except ZeroDivisionError as e:
    #     logging.error(f"Zero Division Error: {e}")
    #     typer.echo("Likely the solar altitude angle is zero.")
    #     some_factor = 0

    # modified_direct_irradiance = direct_horizontal_radiation * some_factor
    # direct_irradiance = apply_angular_loss(
    #         modified_direct_irradiance,
    #         solar_altitude,
    #         incidence_angle
    #         )

    if surface_tilt == 0:
        typer.echo(direct_horizontal_irradiance)
        direct_horizontal_irradiance = calculate_direct_horizontal_irradiance()
        return direct_horizontal_irradiance  # Bhc

    if surface_tilt != 0:
        direct_inclined_irradiance = calculate_direct_inclined_irradiance()
        typer.echo(direct_inclined_irradiance)
        return direct_inclined_irradiance  # Bic
