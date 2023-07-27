from devtools import debug
import typer
from typing import Annotated
from typing import Optional
from typing import NamedTuple
from enum import Enum
from datetime import datetime
from math import sin
from math import cos
from math import acos

from pvgisprototype.api.input_models import SolarAzimuthInput
from pvgisprototype.api.named_tuples import generate

from pvgisprototype.api.decorators import validate_with_pydantic
from .solar_declination import calculate_solar_declination
from .solar_time import model_solar_time
from .solar_hour_angle import calculate_hour_angle
from ..utilities.timestamp import timestamp_to_decimal_hours
from ..utilities.conversions import convert_to_degrees_if_requested


@validate_with_pydantic(SolarAzimuthInput)
def calculate_solar_azimuth(input: SolarAzimuthInput) -> NamedTuple:
    """Compute various solar geometry variables.

    Parameters
    ----------

    Returns
    -------
    solar_azimuth: float
    """
    solar_declination = calculate_solar_declination(
            timestamp=input.timestamp,
            angle_output_units=input.output_units,
            )
    C11 = sin(input.latitude) * cos(solar_declination.value)
    C13 = -cos(input.latitude) * sin(solar_declination.value)
    C22 = cos(solar_declination.value)
    C31 = cos(input.latitude) * cos(solar_declination.value)
    C33 = sin(input.latitude) * sin(solar_declination.value)
    solar_time = model_solar_time(
            longitude=input.longitude,
            latitude=input.latitude,
            timestamp=input.timestamp,
            timezone=input.timezone,
            )
    solar_time_decimal_hours = timestamp_to_decimal_hours(solar_time.value)
    hour_angle = calculate_hour_angle(
            solar_time.value,
            input.output_units,
    )
    cosine_solar_azimuth = (C11 * cos(hour_angle.value + C13)) / pow(
    pow((C22 * sin(hour_angle.value)), 2) + pow((C11 * cos(hour_angle.value) + C13), 2), 0.5
)
    solar_azimuth = acos(cosine_solar_azimuth)
    solar_azimuth = generate(
        'solar_azimuth'.upper(),
        (solar_azimuth, input.output_units),
    )
    solar_azimuth = convert_to_degrees_if_requested(solar_azimuth, input.output_units)

    return solar_azimuth
