from pvgisprototype.data_structures import SolarGeometryDayConstants
from pvgisprototype.data_structures import SolarGeometryDayVariables

from pvgisprototype.constants import EPS
from pvgisprototype.constants import HOUR_ANGLE
from pvgisprototype.solar_declination import calculate_solar_declination

from math import fabs
from math import cos
from math import sin
import typer
import math
from math import acos
from math import radians

from pydantic import BaseModel
from typing_extensions import Annotated
from typing import Optional
import numpy as np
from numba import njit
import datetime

import logging


# UNDEF = -9999  # Example value
UNDEF = float('nan')
double_numpi = 2 * np.pi
half_numpi = 0.5 * np.pi


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"Calculate solar geometry variables for a given latitude",
)


def parse_solar_geometry_constants_class(dict):
    return SolarGeometryDayConstants(dict)


def get_day_from_hour_of_year(year: int, hour_of_year: int):
    """Get day of year from hour of year."""
    start_of_year = np.datetime64(f'{year}-01-01')
    date_and_time = start_of_year + np.timedelta64(hour_of_year, 'h')
    date_and_time = date_and_time.astype(datetime.datetime)
    day_of_year = int(date_and_time.strftime('%j'))
    # month = int(date_and_time.strftime('%m'))  # Month
    # day_of_month = int(date_and_time.strftime('%d')) 
    # hour_of_day = int(date_and_time.strftime('%H'))
    
    return day_of_year


def convert_to_degrees_if_requested(angle: float, output_units: str) -> float:
    """Convert angle from radians to degrees if requested."""

    return np.degrees(angle) if output_units == 'degrees' else angle


def calculate_solar_time(
        year: int,
        hour_of_year: int,
        days_in_a_year: float = 365.25,
        perigee_offset = 0.048869,
        eccentricity = 0.01672,
        hour_offset: float = 0,
):
    """Calculate the solar time.

    1. Map the day of the year onto the circumference of a circle, essentially
    converting the day of the year into radians.

    2. Approximate empirically the equation of time, which accounts for the
    elliptical shape of Earth's orbit and the tilt of its axis.

    3. Calculate the solar time by adding the current hour of the year, the
    time offset from the equation of time, and the hour offset (likely a
    longitude-based correction).
    """
    day_of_year = get_day_from_hour_of_year(year, hour_of_year)
    day_of_year_in_radians = double_numpi * day_of_year / days_in_a_year  
    time_offset = -0.128 * np.sin(day_of_year_in_radians - perigee_offset) - eccentricity * np.sin(2 * day_of_year_in_radians + 0.34383)
    solar_time = hour_of_year % 24 + time_offset + hour_offset

    return solar_time


# REDESIGN-ME -----------------------------------------------------------------
# from: rsun_base.cpp
# function : com_par()
@app.callback(invoke_without_command=True)
def calculate_solar_geometry_variables(
        # solar_geometry_day_constants: SolarGeometryDayConstants,
        solar_geometry_day_constants: Annotated[SolarGeometryDayConstants, typer.Argument(parser=parse_solar_geometry_constants_class)],
        year: int,
        hour_of_year: int,
        days_in_a_year: float = 365.25,
        perigee_offset = 0.048869,
        eccentricity = 0.01672,
        hour_offset: float = 0,
        output_units: Annotated[str, typer.Option(
            '-o',
            '--output-units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar geometry variables (degrees or radians)")] = 'radians',
        ) -> SolarGeometryDayVariables:
    """Compute various solar geometry variables.

    Parameters
    ----------
    solar_geometry_day_constants : SolarGeometryDayConstants
        The input solar geometry constants.
    """
    # print(len(solar_geometry_day_constants.dict().values()))
    # print(solar_geometry_day_constants.dict().values())
    # Unpack constants
    (
        latitude,
        solar_declination,
        cosine_of_solar_declination,
        sine_of_solar_declination,
        lum_C11,
        lum_C13,
        lum_C22,
        lum_C31,
        lum_C33,
        sunrise_time,
        sunset_time,
    ) = solar_geometry_day_constants.dict().values()

    solar_time = calculate_solar_time(
            year,
            hour_of_year,
            days_in_a_year,
            perigee_offset,
            eccentricity,
            hour_offset
    )
    # approximate sun position in the sky (`solar_time`), convert to angle
        # solar noon : 0 degrees, solar midnight : 180 degrees
        # `solar_time - 12` : center the solar time around solar noon (i.e., 12:00).
    time_angle = (solar_time - 12) * HOUR_ANGLE

    # the sine of solar altitude == height above the horizon.
    # lum_C31, lum_C33 : coefficients to calculate height aboe horizon?
    sine_solar_altitude = lum_C31 * np.cos(time_angle) + lum_C33

    if np.abs(lum_C31) < EPS:
        if np.abs(sine_solar_altitude) >= EPS:
            if sine_solar_altitude > 0:
                sunrise_time = 0
                sunset_time = 24
            else:
                logging.warning('The Sun is above the area during the whole day')
                solar_altitude = 0.
                solar_azimuth = UNDEF
                return SolarGeometryDayVariables(solar_altitude=0., solar_azimuth=UNDEF)
        else:
            logging.warning('The Sun is on horizon during the whole day')
            sunrise_time = 0
            sunset_time = 24

    # vertical angle of the sun
    solar_altitude = np.arcsin(sine_of_solar_altitude)

    lum_Lx = -lum_C22 * np.sin(time_angle)
    lum_Ly = lum_C11 * np.cos(time_angle) + lum_C13
    xpom = lum_Lx * lum_Lx
    ypom = lum_Ly * lum_Ly
    pom = np.sqrt(xpom + ypom)

    if np.abs(pom) > EPS:
        solar_azimuth = lum_Ly / pom
        solar_azimuth = np.arccos(solar_azimuth)
        if lum_Lx < 0:
            solar_azimuth = double_numpi - solar_azimuth
    else:
        solar_azimuth = UNDEF

    if solar_azimuth < half_numpi:
        sun_azimuth_angle = half_numpi - solar_azimuth
    else:
        sun_azimuth_angle = 2.5 * np.pi - solar_azimuth

    input_angle = sun_azimuth_angle + half_numpi
    input_angle = input_angle if input_angle >= double_numpi else input_angle - double_numpi
    tan_of_solar_altitude = np.tan(solar_altitude)

    solar_altitude = convert_to_degrees_if_requested(solar_altitude, output_units)
    sine_of_solar_altitude = convert_to_degrees_if_requested(sine_of_solar_altitude, output_units)
    tan_of_solar_altitude = convert_to_degrees_if_requested(tan_of_solar_altitude, output_units)
    solar_azimuth = convert_to_degrees_if_requested(solar_azimuth, output_units)
    sun_azimuth_angle = convert_to_degrees_if_requested(sun_azimuth_angle, output_units)

    return SolarGeometryDayVariables(
        # is_shadow=is_shadow,
        # z_orig=z_orig,
        # z_max=z_max,
        # zp=zp,
        solar_altitude=solar_altitude,
        sine_of_solar_altitude=sine_of_solar_altitude,
        tan_of_solar_altitude=tan_of_solar_altitude,
        solar_azimuth=solar_azimuth,
        sun_azimuth_angle=sun_azimuth_angle,
        # step_sine_angle=step_sine_angle,
        # step_cosine_angle=step_cosine_angle
    )
