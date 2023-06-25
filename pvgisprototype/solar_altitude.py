import typer
from typing import Annotated
from typing import Optional
from enum import Enum
from datetime import datetime
import math
import numpy as np


# from .data_structures import SolarGeometryDayConstants
# from .data_structures import SolarGeometryDayVariables


from .time import now_datetime
from .time import convert_to_timezone
from .time import attach_timezone
from .conversions import convert_to_radians
from .conversions import convert_to_degrees_if_requested
from .solar_declination import calculate_solar_declination
from .solar_time import calculate_solar_time_ephem

# app = typer.Typer(
#     add_completion=False,
#     add_help_option=True,
#     help=f"Calculate solar altitude for a location and time",
# )

# @app.callback('altitude', no_args_is_help=True, help='Calculate solar altitude')
def calculate_solar_altitude(
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
            callback=convert_to_timezone)] = None,
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
    solar_geometry_day_constants : SolarGeometryDayConstants
        The input solar geometry constants.
    """
    solar_declination = calculate_solar_declination(
            timestamp,
            output_units=output_units,
            )
    C31 = math.cos(latitude) * math.cos(solar_declination)
    C33 = math.sin(latitude) * math.sin(solar_declination)

    # solar_time = calculate_solar_time(year, hour_of_year)
    # hour_angle = np.radians(15) * (solar_time - 12)
    # hour_angle = (solar_time - 12)
    
    # timestamp = hour_of_year_to_datetime(year, hour_of_year)
    hour_angle = calculate_solar_time_ephem(
            timestamp=timestamp,
            latitude=latitude,
            longitude=longitude,
    )
    
    sine_solar_altitude = C31 * math.cos(hour_angle) + C33
    solar_altitude = np.arcsin(sine_solar_altitude) 
    solar_altitude = convert_to_degrees_if_requested(
            solar_altitude,
            output_units,
            )

    return solar_altitude
