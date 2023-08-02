from devtools import debug
import typer
from typing import Annotated
from typing import Optional
from enum import Enum
from datetime import datetime
from math import sin
from math import cos
from math import acos

from pvgisprototype.api.data_classes import SolarAzimuth
from pvgisprototype.api.data_classes import Longitude
from pvgisprototype.api.data_classes import Latitude

from pvgisprototype.api.input_models import SolarAzimuthInput

from pvgisprototype.api.decorators import validate_with_pydantic
from .solar_declination import calculate_solar_declination
from .solar_time import model_solar_time
from .solar_hour_angle import calculate_hour_angle
from ..utilities.timestamp import timestamp_to_decimal_hours
from ..utilities.conversions import convert_to_degrees_if_requested


@validate_with_pydantic(SolarAzimuthInput, expand_args=True)
def calculate_solar_azimuth(
                longitude: Longitude,
                latitude: Latitude,
                timestamp: datetime,
                timezone: str = None,
                angle_output_units: str = 'radians',
        ) -> SolarAzimuth:
        """Compute various solar geometry variables.

        Parameters
        ----------

        Returns
        -------
        solar_azimuth: float
        """
        solar_declination = calculate_solar_declination(
                timestamp=timestamp,
            angle_output_units=angle_output_units,
            angle_output_units=angle_output_units,
                )
        C11 = sin(latitude) * cos(solar_declination.value)
        C13 = -cos(latitude) * sin(solar_declination.value)
        C22 = cos(solar_declination.value)
        C31 = cos(latitude) * cos(solar_declination.value)
        C33 = sin(latitude) * sin(solar_declination.value)
        solar_time = model_solar_time(
                longitude=longitude,
                latitude=latitude,
                timestamp=timestamp,
                timezone=timezone,
                )
        solar_time_decimal_hours = timestamp_to_decimal_hours(solar_time.value)
        hour_angle = calculate_hour_angle(
                solar_time=solar_time.value,
        )
        cosine_solar_azimuth = (C11 * cos(hour_angle.value + C13)) / pow(
        pow((C22 * sin(hour_angle.value)), 2) + pow((C11 * cos(hour_angle.value) + C13), 2), 0.5
        )
        solar_azimuth = acos(cosine_solar_azimuth)

        solar_azimuth = SolarAzimuth(value=solar_azimuth, unit='radians')
        solar_azimuth = convert_to_degrees_if_requested(solar_azimuth, angle_output_units)

        return solar_azimuth
