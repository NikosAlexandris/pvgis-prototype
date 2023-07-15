from devtools import debug
import logging
from functools import partial
from math import acos
from math import cos
from math import fabs
from math import radians
from math import sin
from pydantic import BaseModel
from typing import Annotated
from typing_extensions import Annotated
from typing import Optional
import datetime
import numpy as np
import typer
from ...api.constants import EPS
from ...api.constants import HOUR_ANGLE
from ...api.constants import UNDEF
from ...api.constants import double_numpi
from ...api.constants import half_numpi
from ...api.data_structures import SolarGeometryDayConstants
from ...api.data_structures import SolarGeometryDayVariables
from ...api.utilities.conversions import convert_to_degrees_if_requested
from ...api.utilities.conversions import convert_to_radians
from ...api.utilities.timestamp import attach_timezone
from ...api.utilities.timestamp import convert_to_timezone
from ...api.utilities.timestamp import ctx_convert_to_timezone
from ...api.utilities.timestamp import get_day_from_hour_of_year
from ...api.utilities.timestamp import now_utc_datetimezone
from .solar_time import calculate_solar_time_pvgis


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"Calculate solar geometry parameters for a day in a year",
)


# from : rsun_base.cpp
# function : com_par_const()
def calculate_solar_geometry_pvgis_constants(
        longitude: float,
        latitude: float,
        local_solar_time: float,
        solar_declination: float,
        time_offset: float = 0,
        EPS: float = 1e-5
        ) -> SolarGeometryDayConstants:
    """Calculate solar geometry constants for a given latitude based on PVGIS' C code

    Returns
    -------
    
    SolarGeometryDayConstants: class
        An object with various solar geometry "constants"

    Notes
    -----

    - IMPORTANT: In the original C source code there is :

        `latitude = -deg2rad*fixedData.latitude;`

        likely due to `decl = -decl` line in `com_declin()` function.

        Why? This has been "fixed" in this function here.-
    """
    longitude = radians(longitude)
    latitude = radians(latitude)
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
        longitude=longitude,
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


def parse_solar_geometry_constants_class(dict):
    return SolarGeometryDayConstants(dict)


# REDESIGN-ME -----------------------------------------------------------------
# from: rsun_base.cpp
# function : com_par()
@app.callback(invoke_without_command=True)
def calculate_solar_geometry_pvgis_variables(
        # solar_geometry_day_constants: SolarGeometryDayConstants,
        solar_geometry_day_constants: Annotated[SolarGeometryDayConstants, typer.Argument(parser=parse_solar_geometry_constants_class)],
        timestamp: Annotated[Optional[datetime.datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Specify timezone (e.g., "Europe/Athens"). Use "local" to use the system\'s time zone',
            callback=convert_to_timezone)] = None,
        days_in_a_year: Annotated[float, typer.Option(
            help='Days in a year')] = 365.25,
        perigee_offset: Annotated[float, typer.Option(
            help='Perigee offset')] = 0.048869,
        eccentricity: Annotated[float, typer.Option(
            help='Eccentricity')] = 0.01672,
        hour_offset: Annotated[float, typer.Option(
            help='Hour offset')] = 0,
        output_units: Annotated[str, typer.Option(
            '-o',
            '--output-units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar geometry variables (degrees or radians)")] = 'radians',
        ) -> SolarGeometryDayVariables:
    """Calculate solar geometry variables based on PVGIS' C code

    Parameters
    ----------
    solar_geometry_day_constants : SolarGeometryDayConstants
        The input solar geometry constants.
    """

    year = timestamp.year
    start_of_year = datetime.datetime(year=year, month=1, day=1)
    hour_of_year = int((timestamp - start_of_year).total_seconds() / 3600)

    # Unpack constants
    (
        longitude,
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

    solar_time, _units = calculate_solar_time_pvgis(
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
    solar_altitude = np.arcsin(sine_solar_altitude)

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
    tan_solar_altitude = np.tan(solar_altitude)

    solar_altitude = convert_to_degrees_if_requested(solar_altitude, output_units)
    sine_solar_altitude = convert_to_degrees_if_requested(sine_solar_altitude, output_units)
    tan_solar_altitude = convert_to_degrees_if_requested(tan_solar_altitude, output_units)
    solar_azimuth = convert_to_degrees_if_requested(solar_azimuth, output_units)
    sun_azimuth_angle = convert_to_degrees_if_requested(sun_azimuth_angle, output_units)

    return SolarGeometryDayVariables(
        # is_shadow=is_shadow,
        # z_orig=z_orig,
        # z_max=z_max,
        # zp=zp,
        solar_altitude=solar_altitude,
        sine_solar_altitude=sine_solar_altitude,
        tan_solar_altitude=tan_solar_altitude,
        solar_azimuth=solar_azimuth,
        sun_azimuth_angle=sun_azimuth_angle,
        # step_sine_angle=step_sine_angle,
        # step_cosine_angle=step_cosine_angle
    )


def parse_solar_geometry_constants_class(dict):
    return SolarGeometryDayConstants(dict)


def calculate_solar_position_pvgis(
        solar_geometry_day_constants: Annotated[SolarGeometryDayConstants, typer.Argument(parser=parse_solar_geometry_constants_class)],
        timestamp: Annotated[Optional[datetime.datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Specify timezone (e.g., "Europe/Athens"). Use "local" to use the system\'s time zone',
            callback=ctx_convert_to_timezone)] = None,
        days_in_a_year: Annotated[float, typer.Option(
            help='Days in a year')] = 365.25,
        perigee_offset: Annotated[float, typer.Option(
            help='Perigee offset')] = 0.048869,
        eccentricity: Annotated[float, typer.Option(
            help='Eccentricity')] = 0.01672,
        hour_offset: Annotated[float, typer.Option(
            help='Hour offset')] = 0,
        output_units: Annotated[str, typer.Option(
            '-o',
            '--output-units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar geometry variables (degrees or radians)")] = 'radians',
        ) -> SolarGeometryDayVariables:
    """Calculate solar altitude, azimuth and sun azimuth angles based on PVGIS'
    implementation in C.

    Note, purposefully an attempt to transfer 1:1 the implementation in C into
    Python.

    Parameters
    ----------

    Returns
    -------

    solar_altitude: float

    solar_azimuth: float

    sun_azimuth: float
    """
    # Unpack constants
    (
        longitude,
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

    solar_time, _units = calculate_solar_time_pvgis(
            longitude,
            latitude,
            timestamp,
            timezone,
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
            if sine_solar_altitude < 0:
                logging.warning('The Sun is above the area during the whole day')

                return UNDEF

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
        sun_azimuth = half_numpi - solar_azimuth
    else:
        sun_azimuth = 2.5 * np.pi - solar_azimuth

    solar_altitude = convert_to_degrees_if_requested(np.arcsin(sine_solar_altitude), output_units)
    solar_azimuth = convert_to_degrees_if_requested(solar_azimuth, output_units)
    sun_azimuth = convert_to_degrees_if_requested(sun_azimuth, output_units)

    return solar_altitude, solar_azimuth, sun_azimuth
