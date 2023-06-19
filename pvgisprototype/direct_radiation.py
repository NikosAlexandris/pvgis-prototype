"""
Direct irradiance

The _direct_ or _beam_ irradiance is one of the main components of solar irradiance.
It comes perpendicular from the Sun and is not scattered before it irradiates a surface.

During a cloudy day the sunlight will be partially absorbed and scattered by
different air molecules. The latter part is defined as the _diffuse_
irradiance. The remaining part is the _beam_ irradiance.
"""


AOI_CONSTANTS = [ -0.074, 0.155]

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


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"Estimate the direct normal radiance",
)


class IncidenceAngle(BaseModel):
    angle: Union[float, str] = Field(..., description="Angle of incidence")

    @validator('angle')
    def validate_angle(cls, value):
        if isinstance(value, float):
            return value
        elif isinstance(value, str):
            if value.lower() == "auto":
                solar_altitude = 0.5  # Placeholder value, replace with actual solar altitude
                return calculate_angle_of_incidence_auto(solar_altitude)
            else:
                raise ValueError("Invalid angle value. Must be 'auto' or a float.")
        else:
            raise ValueError("Invalid angle value. Must be 'auto' or a float.")

    class Config:
        allow_mutation = False


def parse_incidence_angle(angle: str):
    return IncidenceAngle(angle=angle).angle


def calculate_angle_of_incidence_auto(solar_altitude: float) -> float:
    # 
    # if winter:
    #     optimum_tilt_angle = latitude + 15
    # if summer:
    #     optimum_tilt_angle = latitude - 15
    return  AOI_CONSTANTS[1] * 25  # Fake it.


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
    angular_loss_factor = 1 - math.exp( -solar_altitude / incidence_angle )
    normalisation_term =  1 / ( 1 - math.exp( -1 / incidence_angle))
    adjusted_direct_radiation = direct_radiation * angular_loss_factor / normalisation_term

    typer.echo(adjusted_direct_radiation)
    return(adjusted_direct_radiation)


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
