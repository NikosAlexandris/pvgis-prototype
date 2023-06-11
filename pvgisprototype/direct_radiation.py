"""
Direct irradiance

The _direct_ or _beam_ irradiance is one of the main components of solar irradiance.
It comes perpendicular from the Sun and is not scattered before it irradiates a surface.

During a cloudy day the sunlight will be partially absorbed and scattered by
different air molecules. The latter part is defined as the _diffuse_
irradiance. The remaining part is the _beam_ irradiance.
"""


AOI_CONSTANTS = [ -0.074, 0.155]


import typer
from typing_extensions import Annotated
from typing import Optional
from rich import print

import numpy as np
import math


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"Estimate the direct normal radiance",
)


@app.command('angular-loss')
def calculate_angular_loss(
        index: int,
    ):
    """
    """
    typer.echo(1 / ( 1 - math.exp( - 1 / AOI_CONSTANTS[index])))
    return 1 / ( 1 - math.exp( - 1 / AOI_CONSTANTS[index]))


# from: rsun_base.c
# function name: brad_angle_irradiance
@app.command('direct')
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
