"""
Important sun and solar surface geometry parameters in calculating the amount of solar radiation that reaches a particular location on the Earth's surface
"""

import typer
from typing import Annotated
from typing import Optional
from typing import List
from rich.console import Console
from rich.table import Table
from rich import box

from datetime import datetime
from zoneinfo import ZoneInfo
import math
import numpy as np

from ..api.utilities.timestamp import attach_timezone
from ..api.utilities.timestamp import ctx_attach_requested_timezone
from ..api.utilities.timestamp import ctx_convert_to_timezone
from ..api.utilities.timestamp import now_utc_datetimezone
from ..api.utilities.timestamp import random_datetimezone
from ..api.utilities.conversions import convert_to_radians
from ..api.utilities.conversions import convert_to_degrees_if_requested
from ..api.geometry.time_models import SolarTimeModels
from ..api.geometry.solar_time import calculate_solar_time
from ..api.geometry.solar_hour_angle import calculate_hour_angle


console = Console()
app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f":timer_clock:  Calculate the solar time for a location and moment",
)


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


@app.command('fractional-year', no_args_is_help=True, help='⦩ Calculate the fractional year')
def fractional_year():
    """
    """
    pass


@app.command('eot', no_args_is_help=True, help='⦩ Calculate the equation of time')
def equation_of_time(
        ):
    """
    """
    pass


@app.command('offset', no_args_is_help=True, help='⦩ Calculate the time offset')
def offset(
        ):
    """
    """
    pass


# @app.callback(invoke_without_command=True, no_args_is_help=True, context_settings={"ignore_unknown_options": True})
@app.command(
    'solar',
    no_args_is_help=True,
    help='⦩ Calculate the solar time'
)
def solar_time(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone,
            callback=ctx_attach_requested_timezone,
            )],
        timezone: Annotated[Optional[str], typer.Option(
            help='Specify timezone (e.g., "Europe/Athens"). Use "local" to use the system\'s time zone',
            callback=ctx_convert_to_timezone)] = None,
        model: Annotated[List[SolarTimeModels], typer.Option(
            '-m',
            '--model',
            help="Model to calculate solar time",
            show_default=True,
            show_choices=True,
            case_sensitive=False)] = [SolarTimeModels.skyfield],
        refracted_solar_zenith: float = 1.5853349194640094,  # radians
        apply_atmospheric_refraction: Annotated[Optional[bool], typer.Option(
            '-a',
            '--atmospheric-refraction',
            help='Apply atmospheric refraction functions',
            )] = True,
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
        time_output_units: Annotated[str, typer.Option(
            '-u',
            '--output-units',
            show_default=True,
            case_sensitive=False,
            help="Time units for output and internal calculations (seconds, minutes or hours) - :warning: [bold red]Keep fingers away![/bold red]")] = 'minutes',
        angle_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Angular units for internal calculations (degrees or radians) - :warning: [bold red]Keep fingers away![/bold red]")] = 'radians',
        angle_output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Angular units for solar position calculations output (degrees or radians)")] = 'radians',
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
    # Convert the input timestamp to UTC, for _all_ internal calculations
    utc_zoneinfo = ZoneInfo("UTC")
    if timestamp.tzinfo != utc_zoneinfo:

        # Note the input timestamp and timezone
        user_requested_timestamp = timestamp
        user_requested_timezone = timezone

        timestamp = timestamp.astimezone(utc_zoneinfo)
        timezone = utc_zoneinfo
        typer.echo(f'The requested timestamp - zone {user_requested_timestamp} {user_requested_timezone} has been converted to {timestamp} for all internal calculations!')
    
    # Why does the callback function `_parse_model` not work? 
    if SolarTimeModels.all in model:
        model = [model for model in SolarTimeModels if model != SolarTimeModels.all]

    solar_time  = calculate_solar_time(
            longitude,
            latitude,
            timestamp,
            timezone,
            model,
            refracted_solar_zenith,
            apply_atmospheric_refraction,
            time_output_units,
            angle_output_units,
            days_in_a_year,
            perigee_offset,
            orbital_eccentricity,
            time_offset_global,
            hour_offset,
            )
    solar_time_table = Table('Model', 'Solar time', 'Units',
                                 box=box.SIMPLE_HEAD)
    for model_result in solar_time:
        # typer.echo(f'Solar time: {solar_time} {units} ({timezone})')
        model_name = model_result.get('Model', '')
        solar_time = model_result.get('Solar time', '')
        units = model_result.get('Units', '')
        solar_time_table.add_row(
                model_name,
                str(solar_time),
                str(units),
        )
    console.print(solar_time_table)


@app.command('local', no_args_is_help=True, help='⦩ Calculate the local time')
def local(
        ):
    """
    """
    pass


@app.command('correction', no_args_is_help=True, help='⦩ Calculate the time correction')
def correction(
        ):
    """
    """
    pass


if __name__ == "__main__":
    app()
