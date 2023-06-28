"""
Important sun and solar surface geometry parameters in calculating the amount of solar radiation that reaches a particular location on the Earth's surface
"""

import typer
from typing import Annotated
from typing import Optional
from rich.console import Console
from rich.table import Table
from datetime import datetime
from tzlocal import get_localzone # $ pip install tzlocal
import math
import numpy as np
from tzlocal import get_localzone # $ pip install tzlocal

from .timestamp import now_datetime
from .timestamp import convert_to_timezone
from .timestamp import attach_timezone
from .conversions import convert_to_radians
from .conversions import convert_to_degrees_if_requested
from .solar_time import SolarTimeModels
from .solar_time import calculate_solar_time
from .solar_time import calculate_hour_angle


console = Console()
app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f":timer_clock:  Calculate the solar time for a location and moment",
)


@app.callback(invoke_without_command=True, no_args_is_help=True, context_settings={"ignore_unknown_options": True})
def solar_time(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians, min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians, min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_datetime)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Timezone',
            callback=convert_to_timezone)] = None,
        days_in_a_year: Annotated[float, typer.Option(
            help='Days in a year')] = 365.25,
        perigee_offset: Annotated[float, typer.Option(
            help='Perigee offset')] = 0.048869,
        eccentricity: Annotated[float, typer.Option(
            help='Eccentricity')] = 0.01672,
        time_offset_global: Annotated[float, typer.Option(
            help='Global time offset')] = 0,
        hour_offset: Annotated[float, typer.Option(
            help='Hour offset')] = 0,
        model: Annotated[SolarTimeModels, typer.Option(
            '-m',
            '--model',
            show_default=True,
            show_choices=True,
            case_sensitive=False,
            help="Model to calculate solar time")] = SolarTimeModels.ephem,
        ):
    """Calculate the solar time.

    1. Map the day of the year onto the circumference of a circle, essentially
    converting the day of the year into radians.

    2. Approximate empirically the equation of time, which accounts for the
    elliptical shape of Earth's orbit and the tilt of its axis.

    3. Calculate the solar time by adding the current hour of the year, the
    time offset from the equation of time, and the hour offset (likely a
    longitude-based correction).
    """
    solar_time = calculate_solar_time(
            longitude,
            latitude,
            timestamp,
            timezone,
            days_in_a_year,
            perigee_offset,
            eccentricity,
            time_offset_global,
            hour_offset,
            model,
            )
    typer.echo(f'Solar time: {solar_time} ({timezone})')


# @app.callback(invoke_without_command=True, no_args_is_help=True, context_settings={"ignore_unknown_options": True})
# def hour_angle(
#         solar_time: Annotated[float, typer.Argument(
#             callback=convert_to_radians, min=-180, max=180)],
#         ):
#     """Calculate the hour angle based on the formula:
#     ω = (ST / 3600 - 12) * 15 * 0.0175
#     """
#     hour_angle = calculate_hour_angle(
#             solar_time,
#             )
#     typer.echo(f'Solar time: {hour_angle} ({timezone})')


if __name__ == "__main__":
    app()
