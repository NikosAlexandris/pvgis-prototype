import logging
import typer
from pvgisprototype.data_structures import SolarGeometryDayConstants
from math import fabs
from math import cos
from math import sin
from math import acos
from math import radians
import numpy as np


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"Calculate solar geometry constants for a given latitude",
)


# from : rsun_base.cpp
# function : com_par_const()
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

    lum_C11 = sine_of_latitude * cosine_of_solar_declination
    lum_C13 = -cosine_of_latitude * sine_of_solar_declination
    lum_C22 = cosine_of_solar_declination
    lum_C31 = cosine_of_latitude * cosine_of_solar_declination
    lum_C33 = sine_of_latitude * sine_of_solar_declination

    sunrise_time = sunset_time = None

    if fabs(lum_C31) >= EPS:
        total_time_offset = time_offset + local_solar_time

        pom = -lum_C33 / lum_C31
        if fabs(pom) <= 1:
            pom = acos(pom)
            pom = (pom * 180) / np.pi
            sunrise_time = (90 - pom) / 15 + 6
            sunset_time = (pom - 90) / 15 + 18
        else:
            if pom < 0:
                logging.warning('The sun is above the surface during the whole day')
                sunrise_time = 0
                sunset_time = 24
            else:
                logging.warning('The sun is below the surface during the whole day')
                if fabs(pom) - 1 <= EPS:
                    sunrise_time = 12
                    sunset_time = 12

    return SolarGeometryDayConstants(
        latitude=latitude,
        solar_declination=solar_declination,
        cosine_of_solar_declination=cosine_of_solar_declination,
        sine_of_solar_declination=sine_of_solar_declination,
        lum_C11=lum_C11,
        lum_C13=lum_C13,
        lum_C22=lum_C22,
        lum_C31=lum_C31,
        lum_C33=lum_C33,
        sunrise_time=sunrise_time,
        sunset_time=sunset_time,
    )
