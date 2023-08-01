# import typer
from typing import Annotated
from typing import Optional
from enum import Enum
from datetime import datetime
from zoneinfo import ZoneInfo
from math import cos
from math import sin
from math import asin
import numpy as np

# from .data_structures import SolarGeometryDayConstants
# from .data_structures import SolarGeometryDayVariables

from pvgisprototype.models.noaa.noaa_models import Longitude_in_Radians
from pvgisprototype.models.noaa.noaa_models import Latitude_in_Radians
from ..utilities.timestamp import now_utc_datetimezone
from ..utilities.timestamp import ctx_convert_to_timezone
from ..utilities.timestamp import attach_timezone
from ..utilities.timestamp import convert_hours_to_seconds
from ..utilities.timestamp import timestamp_to_decimal_hours
from ..utilities.conversions import convert_to_radians
from ..utilities.conversions import convert_to_degrees_if_requested
from .solar_declination import calculate_solar_declination
from .time_models import SolarTimeModels
from .solar_time import model_solar_time
from .solar_hour_angle import calculate_hour_angle

from pvgisprototype.api.input_models import SolarAltitudeInput
from pvgisprototype.api.input_models import SolarDeclinationInput
from pvgisprototype.api.decorators import validate_with_pydantic


# app = typer.Typer(
#     add_completion=False,
#     add_help_option=True,
#     help=f"Calculate solar altitude for a location and time",
# )


@validate_with_pydantic(SolarAltitudeInput, expand_args=True)
def calculate_solar_altitude(
        longitude: Longitude_in_Radians,
        latitude: Latitude_in_Radians,
        timestamp: datetime,
        timezone: ZoneInfo,
        days_in_a_year: float,
        perigee_offset: float,
        eccentricity: float,
        time_offset_global: int,
        hour_offset: int,
        solar_time_model: SolarTimeModels,
        angle_output_units: str,
        ) -> float:
    """Compute various solar geometry variables.
    Parameters
    ----------
    longitude : float
        The longitude in degrees. This value will be converted to radians. 
        It should be in the range [-180, 180].

    latitude : float
        The latitude in degrees. This value will be converted to radians. 
        It should be in the range [-90, 90].
    
    timestamp : datetime, optional
        The timestamp for which to calculate the solar altitude. 
        If not provided, the current UTC time will be used.
    
    timezone : str, optional
        The timezone to use for the calculation. 
        If not provided, the system's local timezone will be used.
    
    output_units : str, default 'radians'
        The units to use for the output solar geometry variables. 
        This should be either 'degrees' or 'radians'.

    Returns
    -------
    float
        The calculated solar altitude.
    """
    solar_declination = calculate_solar_declination(
        SolarDeclinationInput(
            timestamp=timestamp,
            timezone=timezone,
            days_in_a_year=days_in_a_year,
            eccentricity=eccentricity,
            perigee_offset=perigee_offset,
            angle_output_units=angle_output_units,
        )
    )
    C31 = cos(latitude) * cos(solar_declination)
    C33 = sin(latitude) * sin(solar_declination)
    solar_time = model_solar_time(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            model=solar_time_model,  # returns datetime.time object
            days_in_a_year=days_in_a_year,
            perigee_offset=perigee_offset,
            eccentricity=eccentricity,
            time_offset_global=time_offset_global,
            hour_offset=hour_offset
            )
    # year = timestamp.year
    # start_of_year = datetime(year=year, month=1, day=1, tzinfo=timestamp.tzinfo)
    # hour_of_year = int((timestamp - start_of_year).total_seconds() / 3600)
    # # -------------------------------------------------------------------------
    # solar_time = model_solar_time(
    # )
    solar_time_decimal_hours = timestamp_to_decimal_hours(solar_time)
    hour_angle, hour_angle_units = calculate_hour_angle(
            solar_time,
            angle_output_units,
    )
    sine_solar_altitude = C31 * cos(hour_angle) + C33
    solar_altitude = asin(sine_solar_altitude)

    return solar_altitude, angle_output_units
