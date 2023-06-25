from devtools import debug
import logging
import typer
from typing import Annotated
from typing import Optional

from pvgisprototype.data_structures import SolarGeometryDayConstants
from pvgisprototype.data_structures import SolarGeometryDayVariables
from .solar_declination import calculate_solar_declination
from .constants import HOUR_ANGLE
from .constants import EPS
from .constants import HOUR_ANGLE
from .constants import UNDEF
from .constants import double_numpi
from .constants import half_numpi
from .conversions import convert_to_radians
from .conversions import convert_to_degrees_if_requested
from .time import now_datetime
from .time import convert_to_timezone
from .time import attach_timezone
import numpy as np
from functools import partial
import datetime
import math

from .solar_time import calculate_solar_time
from .solar_time import calculate_solar_time_ephem
from .solar_time import calculate_solar_time_pvgis


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"Calculate solar geometry parameters for a day in a year",
)


def parse_solar_geometry_constants_class(dict):
    return SolarGeometryDayConstants(dict)


def calculate_solar_position_pvgis(
        solar_geometry_day_constants: Annotated[SolarGeometryDayConstants, typer.Argument(parser=parse_solar_geometry_constants_class)],
        timestamp: Annotated[Optional[datetime.datetime], typer.Argument(
            help='Timestamp',
            callback=attach_timezone)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Timezone',
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

    solar_time = calculate_solar_time(
            longitude,
            latitude,
            timestamp,
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


def calculate_solar_geometry_constants(
        latitude: Annotated[float, typer.Argument(
            help='Latitude in decimal degrees, south is negative',
            min=-90, max=90)],
        local_solar_time: float,
        cosine_of_declination: float,
        sine_of_declination: float,
        time_offset: float = 0,
        EPS: float = 1e-5,
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

    Returns
    -------
    SolarGeometryDayConstants
        Solar geometry constants for the day.
    """
    solar_geometry_constants = calculate_solar_geometry_constants(
            latitude,
            local_solar_time,
            cosine_of_declination,
            sine_of_declination,
            )

    typer.echo(solar_geometry_constants)
    return solar_geometry_constants


def calculate_solar_geometry_variables(
        solar_geometry_day_constants: SolarGeometryDayConstants,
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
    """Compute solar geometry variables for a given year and hour of year

    Parameters
    ----------
    solar_geometry_day_constants : SolarGeometryDayConstants
        The input solar geometry constants.
    """
    solar_geometry_constants = calculate_solar_geometry_constants(
            latitude,
            local_solar_time,
            cosine_of_declination,
            sine_of_declination,
            )
    solar_geometry_variables = calculate_solar_geometry_variables(
            solar_geometry_day_constants,
            year,
            hour_of_year,
            )

    typer.echo(solar_geometry_variables)
    return solar_geometry_variables
