from devtools import debug
import logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('error.log'),  # Save log to a file
        logging.StreamHandler()  # Print log to the console
    ]
)
import typer
from typing import Annotated
from typing import Optional
from typing import List
from datetime import datetime
from datetime import time as datetime_time
from datetime import timedelta
from zoneinfo import ZoneInfo


import numpy as np
from math import pi
from math import sin
from math import cos
from math import tan 
from math import acos
from math import radians
from ..constants import HOUR_ANGLE
from ..constants import UNDEF
from ..constants import double_numpi
from ..constants import half_numpi
from ..utilities.conversions import convert_to_radians
from ..utilities.conversions import convert_to_degrees_if_requested
from ..utilities.timestamp import now_utc_datetimezone
from ..utilities.timestamp import ctx_convert_to_timezone
from ..utilities.timestamp import attach_timezone
from ..utilities.timestamp import convert_hours_to_seconds
from ..utilities.image_offset_prototype import get_image_offset
from ...models.noaa.solar_position import calculate_local_solar_time_noaa
from ...models.skyfield.solar_time import calculate_solar_time_skyfield
from ...models.milne1921.solar_time import calculate_solar_time_eot
from ...models.pyephem.solar_time import calculate_solar_time_ephem
from ...models.pvgis.solar_time import calculate_solar_time_pvgis
from .time_models import SolarTimeModels


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"Calculate solar time for a location and moment in time",
)


def model_solar_time(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Specify timezone (e.g., "Europe/Athens"). Use "local" to use the system\'s time zone',
            callback=ctx_convert_to_timezone)] = None,
        model: Annotated[SolarTimeModels, typer.Option(
            '-m',
            '--model',
            help="Model to calculate solar position",
            show_default=True,
            show_choices=True,
            case_sensitive=False)] = SolarTimeModels.skyfield,
        refracted_solar_zenith: float = 1.5853349194640094,  # radians
        apply_atmospheric_refraction: Annotated[Optional[bool], typer.Option(
            '-a',
            '--atmospheric-refraction',
            help='Apply atmospheric refraction functions',
            )] = True,
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
        ):
    """
    """
    # if local and timestamp is not None and timezone is not None:
    #     timestamp = timezone.localize(timestamp)

    # debug(locals())
    if model.value == SolarTimeModels.eot:

        solar_time, units = calculate_solar_time_eot(
                longitude,
                latitude,
                timestamp,
                timezone,
                days_in_a_year,
                perigee_offset,
                eccentricity,
                time_offset_global,
                hour_offset,
                )

    if model.value == SolarTimeModels.ephem:

        solar_time, units = calculate_solar_time_ephem(
            longitude,
            latitude,
            timestamp,
            timezone,
            )

    if model.value == SolarTimeModels.pvgis:

        solar_time, units = calculate_solar_time_pvgis(
            longitude,
            latitude,
            timestamp,
            timezone,
            )

    if model.value == SolarTimeModels.noaa:

        solar_time, units = calculate_local_solar_time_noaa(
            longitude,
            latitude,
            timestamp,
            timezone,
            refracted_solar_zenith,
            apply_atmospheric_refraction,
            time_output_units,
            angle_units,
            angle_output_units,
            # verbose,
            )

    if model.value == SolarTimeModels.skyfield:

        solar_time, units = calculate_solar_time_skyfield(
            longitude,
            latitude,
            timestamp,
            timezone,
            )

    return (solar_time, units)


# @app.callback(invoke_without_command=True, no_args_is_help=True, context_settings={"ignore_unknown_options": True})
# @app.command('solar-time')
def calculate_solar_time(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone)],
        timezone: Annotated[Optional[ZoneInfo], typer.Option(
            help='Specify timezone (e.g., "Europe/Athens"). Use "local" to use the system\'s time zone',
            callback=ctx_convert_to_timezone)] = None,
        models: Annotated[List[SolarTimeModels], typer.Option(
            '-m',
            '--model',
            help="Model to calculate solar position",
            show_default=True,
            show_choices=True,
            case_sensitive=False)] = [SolarTimeModels.skyfield],
        refracted_solar_zenith: float = 1.5853349194640094,  # radians
        apply_atmospheric_refraction: Annotated[Optional[bool], typer.Option(
            '-a',
            '--atmospheric-refraction',
            help='Apply atmospheric refraction functions',
            )] = True,
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
):
    """
    Calculates the solar time using all models and returns the results in a table.
    """
    # debug(locals())
    results = []
    for model in models:
        if model != SolarTimeModels.all:  # ignore 'all' in the enumeration
            solar_time, units = model_solar_time(
                    longitude,
                    latitude,
                    timestamp,
                    timezone,
                    model,
                    refracted_solar_zenith,
                    apply_atmospheric_refraction,
                    time_output_units,
                    angle_units,
                    angle_output_units,
                    days_in_a_year,
                    perigee_offset,
                    eccentricity,
                    time_offset_global,
                    hour_offset,
                    )
            results.append({
                'Model': model.value,
                'Solar time': solar_time,
                'Units': units,  # Don't trust me -- Redesign Me!
            })

    # debug(locals())
    return results
