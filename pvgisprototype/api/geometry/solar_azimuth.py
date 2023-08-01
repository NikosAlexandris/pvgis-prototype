from devtools import debug
import typer
from typing import Annotated
from typing import Optional
from enum import Enum
from datetime import datetime
from zoneinfo import ZoneInfo
from math import sin
from math import cos
from math import acos

from pvgisprototype.api.input_models import SolarAzimuthInput
from pvgisprototype.api.decorators import validate_with_pydantic
from .solar_declination import calculate_solar_declination
from .time_models import SolarTimeModels
from .solar_time import model_solar_time
from .solar_hour_angle import calculate_hour_angle
from ..utilities.timestamp import timestamp_to_decimal_hours
from ..utilities.conversions import convert_to_degrees_if_requested
from pvgisprototype.models.noaa.noaa_models import Longitude_in_Radians
from pvgisprototype.models.noaa.noaa_models import Latitude_in_Radians


@validate_with_pydantic(SolarAzimuthInput, expand_args=True)
def calculate_solar_azimuth(
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

    Returns
    -------
    solar_azimuth: float

    Notes
    -----

    According to ... solar azimuth is measured from East!
    Conflicht with Jenvco 1992?

    """
    solar_declination = calculate_solar_declination(
            timestamp=timestamp,
            angle_output_units=angle_output_units,
            )
    C11 = sin(latitude) * cos(solar_declination)
    C13 = -cos(latitude) * sin(solar_declination)
    C22 = cos(solar_declination)
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

    # solar time is a datetime.time object!
    solar_time_decimal_hours = timestamp_to_decimal_hours(solar_time)
    hour_angle, hour_angle_units = calculate_hour_angle(
            solar_time,
            angle_output_units,
    )
    cosine_solar_azimuth = (C11 * cos(hour_angle + C13)) / pow(
        pow((C22 * sin(hour_angle)), 2)
        + pow((C11 * cos(hour_angle) + C13), 2),
        0.5)
    solar_azimuth = acos(cosine_solar_azimuth)
    # solar_azimuth = convert_to_degrees_if_requested(solar_azimuth, output_units)

    return solar_azimuth, angle_output_units
