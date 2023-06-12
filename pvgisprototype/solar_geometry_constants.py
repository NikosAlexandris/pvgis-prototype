import logging
from pvgisprototype.data_structures import SolarGeometryDayConstants

from math import fabs
from math import cos
from math import sin
from math import acos
from math import radians

from pydantic import BaseModel
import typer
from typing import Optional
import numpy as np


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"Estimate the direct normal radiance",
)



@app.callback(invoke_without_command=True, no_args_is_help=True)
def calculate_solar_geometry_constants(
        latitude: float,
        local_solar_time: float,
        solar_declination: float,
        time_offset: float = 0,
        EPS: float = 1e-5
        ) -> SolarGeometryDayConstants:
    """Calculate solar geometry constants for a given latitude and return a SolarGeometryDayConstants object with the calculated values.
    """
    # as per the original source code :
    # `latitude = -deg2rad*fixedData.latitude;`
    # that is, convert to radians & invert sign : why?
    latitude = - radians(latitude)
    sine_of_latitude = sin(latitude) 
    cosine_of_latitude = cos(latitude)

    sine_of_solar_declination = np.sin(solar_declination)
    cosine_of_solar_declination = np.cos(solar_declination)

    solar_geometry_day_constants = SolarGeometryDayConstants(
            cosine_of_declination=cosine_of_declination,
            sine_of_declination=sine_of_declination,
    )
    solar_geometry_day_constants.lum_C11 = grid_geometry.sine_of_latitude * solar_geometry_day_constants.cosine_of_declination
    solar_geometry_day_constants.lum_C13 = -grid_geometry.cosine_of_latitude * solar_geometry_day_constants.sine_of_declination
    solar_geometry_day_constants.lum_C22 = solar_geometry_day_constants.cosine_of_declination
    solar_geometry_day_constants.lum_C31 = grid_geometry.cosine_of_latitude * solar_geometry_day_constants.cosine_of_declination
    solar_geometry_day_constants.lum_C33 = grid_geometry.sine_of_latitude * solar_geometry_day_constants.sine_of_declination

    if fabs(solar_geometry_day_constants.lum_C31) >= EPS:
        total_time_offset = time_offset + local_solar_time

        pom = -solar_geometry_day_constants.lum_C33 / solar_geometry_day_constants.lum_C31
        if fabs(pom) <= 1:
            pom = acos(pom)
            pom = (pom * 180) / pi
            solar_geometry_day_constants.sunrise_time = (90 - pom) / 15 + 6
            solar_geometry_day_constants.sunset_time = (pom - 90) / 15 + 18
        else:
            if pom < 0:
                logging.warning('The sun is above the surface during the whole day')
                solar_geometry_day_constants.sunrise_time = 0
                solar_geometry_day_constants.sunset_time = 24
            else:
                logging.warning('The sun is below the surface during the whole day')
                if fabs(pom) - 1 <= EPS:
                    solar_geometry_day_constants.sunrise_time = 12
                    solar_geometry_day_constants.sunset_time = 12

    return solar_geometry_day_constants
