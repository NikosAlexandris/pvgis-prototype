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
# import math
# import numpy as np

# from ..api.utilities.timestamp import attach_timezone
# from ..api.utilities.timestamp import ctx_attach_requested_timezone
# from ..api.utilities.timestamp import ctx_convert_to_timezone
# from ..api.utilities.timestamp import now_utc_datetimezone
# from ..api.utilities.timestamp import random_datetimezone
# from ..api.utilities.conversions import convert_to_radians
# from ..api.utilities.conversions import convert_to_degrees_if_requested
from ..api.geometry.models import SolarTimeModels
from ..api.geometry.solar_time import calculate_solar_time

from .typer_parameters import OrderCommands
from .typer_parameters import typer_argument_longitude
from .typer_parameters import typer_argument_latitude
from .typer_parameters import typer_argument_timestamp
from .typer_parameters import typer_option_timezone
# from .typer_parameters import typer_option_local_time
# from .typer_parameters import typer_option_random_time
# from .typer_parameters import typer_argument_solar_declination
# from .typer_parameters import typer_argument_surface_tilt
# from .typer_parameters import typer_argument_surface_orientation
# from .typer_parameters import typer_argument_hour_angle
# from .typer_parameters import typer_argument_true_solar_time
# from .typer_parameters import typer_option_solar_position_model
from .typer_parameters import typer_option_solar_time_model
from .typer_parameters import typer_option_global_time_offset
from .typer_parameters import typer_option_hour_offset
from .typer_parameters import typer_option_days_in_a_year
from .typer_parameters import typer_option_perigee_offset
from .typer_parameters import typer_option_eccentricity_correction_factor
from .typer_parameters import typer_option_apply_atmospheric_refraction
from .typer_parameters import typer_option_refracted_solar_zenith
from .typer_parameters import typer_option_time_output_units
from .typer_parameters import typer_option_angle_units
from .typer_parameters import typer_option_angle_output_units
# from .typer_parameters import typer_option_rounding_places
from .typer_parameters import typer_option_verbose
from pvgisprototype.cli.messages import NOT_IMPLEMENTED_CLI
from pvgisprototype.constants import TIME_ALGORITHM_NAME
from pvgisprototype.constants import TIME_ALGORITHM_COLUMN_NAME
from pvgisprototype.constants import SOLAR_TIME_COLUMN_NAME
from pvgisprototype.constants import SOLAR_TIME_NAME


app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f":timer_clock:  Calculate the solar time for a location and moment",
)
console = Console()


@app.command('fractional-year', no_args_is_help=True, help=f'⦩ Calculate the fractional year {NOT_IMPLEMENTED_CLI}')
def fractional_year(
):
    """
    """
    pass


@app.command('eot', no_args_is_help=True, help=f'⦩ Calculate the equation of time {NOT_IMPLEMENTED_CLI}')
def equation_of_time(
):
    """
    """
    pass


@app.command('offset', no_args_is_help=True, help=f'⦩ Calculate the time offset {NOT_IMPLEMENTED_CLI}')
def offset(
):
    """
    """
    pass


@app.command(
    'solar',
    no_args_is_help=True,
    help='⦩ Calculate the apparent solar time'
)
def solar_time(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    solar_time_model: Annotated[List[SolarTimeModels], typer_option_solar_time_model] = [SolarTimeModels.skyfield],
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = True,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = 1.5853349194640094,  # radians
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = 365.25,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = 0.048869,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = 0.03344,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = 0,
    hour_offset: Annotated[float, typer_option_hour_offset] = 0,
    time_output_units: Annotated[str, typer_option_time_output_units] = 'minutes',
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = 'radians',
    verbose: Annotated[int, typer_option_verbose]= 0,
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
    if SolarTimeModels.all in solar_time_model:
        solar_time_model = [model for model in SolarTimeModels if model != SolarTimeModels.all]

    solar_time = calculate_solar_time(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        models=solar_time_model,  # keep the CLI simple
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        # time_output_units=time_output_units,
        # angle_output_units=angle_output_units,
        verbose=verbose,
    ) 
    solar_time_table = Table(
        TIME_ALGORITHM_COLUMN_NAME, SOLAR_TIME_COLUMN_NAME, box=box.SIMPLE_HEAD  # UNITS_NAME,
    )
    for model_result in solar_time:
        # typer.echo(f'Solar time: {solar_time} {units} ({timezone})')
        model_name = model_result.get(TIME_ALGORITHM_NAME, '')
        solar_time = model_result.get(SOLAR_TIME_NAME, '')
        # units = model_result.get(UNITS_NAME, '')
        solar_time_table.add_row(
                model_name,
                str(solar_time),
                # str(units),
        )
    console.print(solar_time_table)


@app.command('local', no_args_is_help=True, help=f'⦩ Calculate the local time {NOT_IMPLEMENTED_CLI}')
def local(
):
    """
    """
    pass


@app.command('correction', no_args_is_help=True, help=f'⦩ Calculate the time correction {NOT_IMPLEMENTED_CLI}')
def correction(
        ):
    """
    """
    pass


if __name__ == "__main__":
    app()
