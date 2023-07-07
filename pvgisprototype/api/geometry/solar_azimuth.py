import typer
from typing import Annotated
from typing import Optional
from enum import Enum
from datetime import datetime
import math
import numpy as np

from ..utilities.timestamp import now_datetime
from ..utilities.timestamp import ctx_convert_to_timezone
from ..utilities.timestamp import attach_timezone
from ..utilities.conversions import convert_to_radians
from ..utilities.conversions import convert_to_degrees_if_requested

from .solar_declination import calculate_solar_declination
from .solar_time import calculate_solar_time_ephem
from .solar_time import model_solar_time
from .solar_time import calculate_hour_angle

# from .data_structures import SolarGeometryDayConstants
# from .data_structures import SolarGeometryDayVariables

# app = typer.Typer(
#     add_completion=False,
#     add_help_option=True,
#     help=f"Calculate solar azimuth for a location and time",
# )

# Clean-Up --------------------------------------------------------------------
# @app.callback(invoke_without_command=True)
# @app.callback('azimuth', no_args_is_help=True, help='Calculate solar azimuth')
def calculate_solar_azimuth(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        latitude: Annotated[Optional[float], typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_datetime)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Timezone',
            callback=ctx_convert_to_timezone)] = None,
        days_in_a_year: float = 365.25,
        perigee_offset: float = 0.048869,
        eccentricity: float = 0.01672,
        hour_offset: float = 0,
        output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar geometry variables (degrees or radians)")] = 'radians',
        ) -> float:
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

    # solar_time = calculate_solar_time(year, hour_of_year)
    # hour_angle = np.radians(15) * (solar_time - 12)
    # hour_angle = (solar_time - 12)
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
