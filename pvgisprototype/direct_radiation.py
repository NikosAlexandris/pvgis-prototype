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


AOI_CONSTANTS = [ -0.074, 0.155]


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"Estimate the direct normal radiance",
)


def calculate_angle_of_incidence_auto(solar_altitude: float) -> float:
    # 
    # if winter:
    #     optimum_tilt_angle = latitude + 15
    # if summer:
    #     optimum_tilt_angle = latitude - 15
    return AOI_CONSTANTS[1]  # Fake it.


class IncidenceAngle(BaseModel):
    angle: Union[float, str] = Field(..., description="Angle of incidence")

    @validator('angle')
    def validate_angle(cls, value):
        if isinstance(value, float):
            # Ensuring the value is within 0 and 90
            if 0 <= value <= 90:
                return value
            else:
                raise ValueError("Angle value must be between 0 and 90.")
        elif isinstance(value, str):
            if value.lower() == "auto":
                solar_altitude = 0.5  # Placeholder value, replace with actual solar altitude
                return calculate_angle_of_incidence_auto(solar_altitude)
            else:
                try:
                    value = float(value)
                    if 0 <= value <= 90:
                        return value
                    else:
                        raise ValueError("Angle value must be between 0 and 90.")
                except ValueError:
                    raise ValueError("Invalid angle value. Must be 'auto', a float, or a string representation of a float.")
        else:
            raise ValueError("Invalid angle value. Must be 'auto', a float, or a string representation of a float.")


def parse_incidence_angle(angle: Union[str, float]) -> float:
    if isinstance(angle, str) and angle.lower() == "auto":
        solar_altitude = 0.5  # Placeholder value, replace with actual solar altitude
        return calculate_angle_of_incidence_auto(solar_altitude)
    else:
        try:
            angle = float(angle)
            if not 0 <= angle <= 90:
                raise ValueError
        except ValueError:
            raise ValueError("Invalid angle value. Must be 'auto', a float, or a string representation of a float between 0 and 90.")
        return angle


@app.command('angular-loss')
def apply_angular_loss(
        direct_radiation: float,
        solar_altitude: float,
        incidence_angle: float,
    ):
    """Apply losses to the direct normal radiation due to the angle of incidence

    The adjustment factor represents the fraction of the original
    `direct_radiation` that is retained after accounting for the loss of
    radiation due to the angle of incidence or the orientation of the surface
    with respect to the sun.

    Parameters
    ----------

    direct_radiation (float): The direct normal radiation in watts per square meter (W/m²).
    incidence_angle (float): In degrees (°).
    solar_altitude (float): solar altitude angle in degrees (°).
    expected_result (float): in watts per square meter (W/m²).

    Returns
    -------
    adjusted_direct_radiation

    Notes
    -----

    The adjustment involves:

    1. computes the fraction of radiation that is not lost due to
    the `solar_altitude` angle divided by the `incidence_angle` ranging between
    0 (complete loss) and 1 (no loss):

        `( 1 - exp( -solar_altitude / incidence_angle ) )`

        - The exponential function `exp`, raises the mathematical constant `e`
          (approximately 2.71828) to the power of the given argument.

        - The negative exponential term of the fraction `solar_altitude /
          incidence_angle` calculates the exponential decay or attenuation
          factor based on the ratio of `solar_altitude` to the `incidence_angle`. 
    
    2. rescales the adjusted value to bring it within a suitable range,
    by multiplying it by the reciprocal of the exponential term with the
    reciprocal of the `incidence_angle`:

        `1 / ( 1 - exp( - 1 / incidence_angle) )`

    ensuring no excessive amplification or diminishing the effect
    (over-amplification or under-amplification).
    """
    try:
        angular_loss_factor = 1 - math.exp( -solar_altitude / incidence_angle )
        normalisation_term =  1 / ( 1 - math.exp( -1 / incidence_angle))
        return direct_radiation * angular_loss_factor / normalisation_term

    except ZeroDivisionError as e:
        logging.error(f"Zero Division Error: {e}")
        typer.echo("No angular losses when the incidence angle is 0.")
        return direct_radiation


def calculate_refracted_solar_altitude(
        solar_altitude: float,
        ):
    """
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
# from: rsun_base.c
# function name: brad_angle_irradiance
@app.command('direct', no_args_is_help=True)
def calculate_direct_radiation_for_tilted_surface(
        direct_horizontal_radiation_coefficient: Annotated[float, typer.Argument(
            help='Direct normal radiation coefficient',
            min=-9000, max=1000)],  # bh = sunRadVar->cbh;
        solar_altitude: Annotated[float, typer.Argument(
            help='Direct normal radiation coefficient',
            min=0, max=90)],  # sh, s0
        sine_of_solar_altitude: Annotated[float, typer.Argument(
            help='Sine of solar altitude',
            min=0, max=1)],  # sunVarGeom->sinSolarAltitude;
         # incidence_angle: Annotated[Union[IncidenceAngle, float], typer.Option(
         incidence_angle: Annotated[IncidenceAngle, typer.Option(
             parser=parse_incidence_angle,
             help='Angle of incidence',
             case_sensitive=False)] = IncidenceAngle(angle='auto'),
    ):
    """Calculate the direct radiation based on given parameters.

    Calculate the angle of incidence irradiance and modify it based on certain
    conditions.

    Parameters
    ----------
        direct_horizontal_radiation_coefficient (list): Direct horizontal radiation coefficient. Likely a reference to the clear-sky beam horizontal radiation?
        solar_altitude (float): Solar altitude angle.
        sine_of_solar_altitude (float): Sine of solar altitude angle.
        incidence_angle_index (int): Index 0 or 1 for .. and .. respectively.
        sun_geometry: Sun geometry variables for a specific day ?
        sun_radiation_variables: Solar radiation variables.

    Returns
    -------
        float: Direct radiation value.

    Notes
    -----

    This function is the product of:

        1. direct translation of the original C code function(s) in to
        Python-like pseudocode
    
        2. refactoring, trial and error

    - `direct_radiation_coefficient` : from `solar_radiation_variables['direct_radiation_coefficient']`
    - `sine_of_solar_altitude` : from `sun_geometry['sine_of_solar_altitude']`
    """
    # the direct radiation value to adjust
    direct_radiation = direct_horizontal_radiation_coefficient * solar_altitude / sine_of_solar_altitude
    adjusted_direct_radiation = apply_angular_loss(
            direct_radiation,
            solar_altitude,
            incidence_angle
            )

    typer.echo(adjusted_direct_radiation)
    return adjusted_direct_radiation
