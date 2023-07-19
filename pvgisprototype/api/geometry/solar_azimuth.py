from devtools import debug
import typer
from typing import Annotated
from typing import Optional
from enum import Enum
from datetime import datetime
import math

from pvgisprototype.api.input_models import SolarAzimuthInput
from pvgisprototype.api.decorators import validate_with_pydantic
from .solar_declination import calculate_solar_declination
from .solar_time import model_solar_time
from .solar_hour_angle import calculate_hour_angle


@validate_with_pydantic(SolarAzimuthInput)
def calculate_solar_azimuth(input: SolarAzimuthInput) -> float:
    """Compute various solar geometry variables.

    Parameters
    ----------

    Returns
    -------
    solar_azimuth: float
    """
    solar_declination = calculate_solar_declination(
            timestamp=timestamp,
            output_units=output_units,
            )
    C11 = math.sin(latitude) * math.cos(solar_declination)
    C13 = -math.cos(latitude) * math.sin(solar_declination)
    C22 = math.cos(solar_declination)
    C31 = math.cos(latitude) * math.cos(solar_declination)
    C33 = math.sin(latitude) * math.sin(solar_declination)
    solar_time, _units = model_solar_time(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            )
    hour_angle, _units = calculate_hour_angle(
            solar_time,
            output_units,
    )
    cosine_solar_azimuth = (C11 * math.cos(hour_angle + C13)) / pow(
    pow((C22 * math.sin(hour_angle)), 2) + pow((C11 * math.cos(hour_angle) + C13), 2), 0.5
)
    solar_azimuth = math.acos(cosine_solar_azimuth)
    solar_azimuth = convert_to_degrees_if_requested(solar_azimuth, output_units)

    return solar_azimuth, output_units
