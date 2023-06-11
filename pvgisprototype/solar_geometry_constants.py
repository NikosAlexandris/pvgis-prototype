import logging

from pydantic import BaseModel
from pvgisprototype.data_structures import SolarGeometryDayConstants
from pvgisprototype.data_structures import GridGeometry
from pvgisprototype.constants import EPS

from math import acos, pi, fabs
from typing import Optional
import numpy as np


# from :
# function : com_par_const()
def calculate_solar_geometry_constants(
        longitude: Annotated[float, typer.Argument(
            help='Longitude in decimal degrees, west is negative',
            min=-180, max=180)],  #lon
        latitude: Annotated[float, typer.Argument(
            help='Latitude in decimal degrees, south is negative',
            min=-90, max=90)],  # lat
        local_solar_time: float,
        cosine_of_declination: float,
        sine_of_declination: float,
        grid_geometry: GridGeometry,
        time_offset: float = 0,
        EPS: float = 1e-5,  # Assume a default value for EPS
) -> SolarGeometryDayConstants:
    """
    Compute solar geometry constants for the day.

    Parameters
    ----------
    local_solar_time : float
        Longitude time.
    cosine_of_declination : float
        Cosine of the solar declination.
    sine_of_declination : float
        Sine of the solar declination.
    grid_geometry : GridGeometry
        Grid geometry constants.

    Returns
    -------
    SolarGeometryDayConstants
        Sun geometry constants for the day.
    """
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
