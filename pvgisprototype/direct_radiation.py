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
def calculate_direct_radiation_for_a_tilted_surface(
        direct_radiation_coefficient: Annotated[float, typer.Argument(
            help='Direct normal radiation coefficient',
            min=0, max=1)],  # bh = sunRadVar->cbh;
        sun_height: Annotated[float, typer.Argument(
            help='Direct normal radiation coefficient',
            min=0, max=1)],  # sh, s0
        sine_of_sun_height: Annotated[float, typer.Argument(
            help='Sine of solar altitude',
            min=0, max=1)],  # sunVarGeom->sinSolarAltitude;
        aoi_constant_index: Annotated[int, typer.Argument(
            help='AOI constant -- What is this?')],  #
        radiations,
    ):
    """
    Calculate the direct radiation based on given parameters.

    Args:
        direct_radiation_coefficient (list): Direct horizontal radiation
        sun_height (float): Solar height ?
        sine_of_sun_height (float): Sine of solar altitude.
        aoi_constant_index (int): Index 0 or 1 for .. and .. respectively.

    Returns:
        float: Direct radiation value.

    Notes
    -----

    After directly translating the original C code in to a Python-alike
    pseudocode:

        - `direct_radiation_coefficient` : from `solar_radiation_variables['direct_radiation_coefficient']`
        - `sine_of_sun_height` : from `sun_geometry['sine_of_sun_height']`
    """
    direct_radiation = direct_radiation_coefficient * sun_height / sine_of_sun_height

    angular_loss = calculate_angular_loss(aoi_constant_index)
    aoi = AOI_CONSTANTS[aoi_constant_index]  # aoi = angle of incidence ?
    if angular_loss:
        direct_radiation *= ( 1 - math.exp( -sun_height / aoi ) ) * angular_loss
    
    typer.echo(direct_radiation)
    return direct_radiation
