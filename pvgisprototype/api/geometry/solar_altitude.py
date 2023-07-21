# import typer
from typing import Annotated
from typing import Optional
from enum import Enum
from datetime import datetime
import math
import numpy as np

# from .data_structures import SolarGeometryDayConstants
# from .data_structures import SolarGeometryDayVariables


from ..utilities.timestamp import now_utc_datetimezone
from ..utilities.timestamp import ctx_convert_to_timezone
from ..utilities.timestamp import attach_timezone
from ..utilities.timestamp import convert_hours_to_seconds
from ..utilities.conversions import convert_to_radians
from ..utilities.conversions import convert_to_degrees_if_requested
from .solar_declination import calculate_solar_declination
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


@validate_with_pydantic(SolarAltitudeInput)
def calculate_solar_altitude(input: SolarAltitudeInput) -> float:
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
            timestamp=input.timestamp,
            angle_output_units=input.output_units
        )
    )
    C31 = math.cos(input.latitude) * math.cos(solar_declination)
    C33 = math.sin(input.latitude) * math.sin(solar_declination)
    solar_time, _units = model_solar_time(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            )
    
    # hour_angle = np.radians(15) * (solar_time - 12)
    # hour_angle = (solar_time - 12)
    hour_angle, _units = calculate_hour_angle(
            solar_time,
            output_units,
    )
    sine_solar_altitude = C31 * math.cos(hour_angle) + C33
    solar_altitude = np.arcsin(sine_solar_altitude) 
    solar_altitude = convert_to_degrees_if_requested(
            solar_altitude,
            output_units,
            )

    return solar_altitude, output_units
