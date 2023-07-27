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
from typing import NamedTuple
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

from pvgisprototype.api.input_models import SolarTimeInput
from pvgisprototype.api.decorators import validate_with_pydantic


@validate_with_pydantic(SolarTimeInput)
def model_solar_time(
        input: SolarTimeInput
    )-> NamedTuple:
    """Calculates the sola time and returns the calculated value and the units.

    Parameters
    ----------
    input : SolarTimeInput
        _description_

    Returns
    -------
    SolarTime
        _description_
    """

    # if local and timestamp is not None and timezone is not None:
    #     timestamp = timezone.localize(timestamp)

    # debug(locals())
    if input.model.value == SolarTimeModels.eot:

        solar_time = calculate_solar_time_eot(
                input.longitude,
                input.latitude,
                input.timestamp,
                input.timezone,
                input.days_in_a_year,
                input.perigee_offset,
                input.eccentricity,
                input.time_offset_global,
                input.hour_offset,
                )

    if input.model.value == SolarTimeModels.ephem:

        solar_time = calculate_solar_time_ephem(
            input.longitude,
            input.latitude,
            input.timestamp,
            input.timezone,
            )

    if input.model.value == SolarTimeModels.pvgis:

        solar_time = calculate_solar_time_pvgis(
            input.longitude,
            input.latitude,
            input.timestamp,
            input.timezone,
            )

    if input.model.value == SolarTimeModels.noaa:

        solar_time = calculate_local_solar_time_noaa(
            input.longitude,
            input.latitude,
            input.timestamp,
            input.timezone,
            input.refracted_solar_zenith,
            input.apply_atmospheric_refraction,
            input.time_output_units,
            input.angle_units,
            input.angle_output_units,
            # verbose,
            )

    if input.model.value == SolarTimeModels.skyfield:

        # --------------------------------------------------- expects degrees!
        longitude = convert_to_degrees_if_requested(input.longitude, 'degrees')
        latitude = convert_to_degrees_if_requested(input.latitude, 'degrees')
        # expects degrees ! --------------------------------------------------

        solar_time = calculate_solar_time_skyfield(
            longitude,
            latitude,
            input.timestamp,
            input.timezone,
            )

    return solar_time


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
    """Calculates the solar time using all models and returns the results in a table.

    Parameters
    ----------

    
    Returns
    -------
    _type_
        _description_
    """
    results = []
    for model in models:
        if model != SolarTimeModels.all:  # ignore 'all' in the enumeration
            solar_time = model_solar_time(
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
                'Solar time': solar_time.value,
                'Units': solar_time.unit,  # Don't trust me -- Redesign Me!
            })

    # debug(locals())
    return results
