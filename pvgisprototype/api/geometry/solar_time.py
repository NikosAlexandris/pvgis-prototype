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

from pvgisprototype.api.data_classes import SolarTime
from pvgisprototype.api.data_classes import Longitude
from pvgisprototype.api.data_classes import Latitude

from pvgisprototype.api.input_models import SolarTimeInput
from pvgisprototype.api.decorators import validate_with_pydantic


@validate_with_pydantic(SolarTimeInput, expand_args=True)
def model_solar_time(
        longitude: Longitude,
        latitude: Latitude,
        timestamp: datetime,
        timezone: str = None,
        model: SolarTimeModels = SolarTimeModels.skyfield,
        refracted_solar_zenith: float = 1.5853349194640094,  # radians
        apply_atmospheric_refraction: bool = True,
        time_output_units: str = 'minutes',
        angle_output_units: str = 'radians',
        days_in_a_year: float = 365.25,
        perigee_offset: float = 0.048869,
        orbital_eccentricity: float = 0.03344,
        time_offset_global: float = 0,
        hour_offset: float = 0,
    )-> SolarTime:
    """Calculates the solar time and returns the calculated value and the units.

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
    if model.value == SolarTimeModels.eot:

        solar_time = calculate_solar_time_eot(
                longitude,
                latitude,
                timestamp,
                timezone,
                days_in_a_year,
                perigee_offset,
                orbital_eccentricity,
                time_offset_global,
                hour_offset,
                )

    if model.value == SolarTimeModels.ephem:

        solar_time = calculate_solar_time_ephem(
            longitude,
            latitude,
            timestamp,
            timezone,
            )

    if model.value == SolarTimeModels.pvgis:

        solar_time = calculate_solar_time_pvgis(
            longitude,
            latitude,
            timestamp,
            timezone,
            )

    if model.value == SolarTimeModels.noaa:

        solar_time = calculate_local_solar_time_noaa(
            longitude,
            latitude,
            timestamp,
            timezone,
            refracted_solar_zenith,
            apply_atmospheric_refraction,
            time_output_units,
            angle_output_units,
            # verbose,
            )

    if model.value == SolarTimeModels.skyfield:

        # --------------------------------------------------- expects degrees!
        longitude = convert_to_degrees_if_requested(longitude, 'degrees')
        latitude = convert_to_degrees_if_requested(latitude, 'degrees')
        # expects degrees ! --------------------------------------------------

        solar_time = calculate_solar_time_skyfield(
            longitude,
            latitude,
            timestamp,
            timezone,
            )

    return solar_time


def calculate_solar_time(
        longitude: Longitude,
        latitude: Latitude,
        timestamp: datetime,
        # : Annotated[Optional[datetime], typer.Argument(
            # help='Timestamp',
            # default_factory=now_utc_datetimezone)],
        timezone: str = None,
        # : Annotated[Optional[ZoneInfo], typer.Option(
            # help='Specify timezone (e.g., "Europe/Athens"). Use "local" to use the system\'s time zone',
            # callback=ctx_convert_to_timezone)] = None,
        models: List[SolarTimeModels] = [SolarTimeModels.skyfield],
        refracted_solar_zenith: float = 1.5853349194640094,  # radians
        apply_atmospheric_refraction: bool = True,
        time_output_units: str = 'minutes',
        angle_output_units: str = 'radians',
        days_in_a_year: float = 365.25,
        perigee_offset: float = 0.048869,
        orbital_eccentricity: float = 0.03344,
        time_offset_global: float = 0,
        hour_offset: float = 0,
) -> List:
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
                longitude=longitude,
                latitude=latitude,
                timestamp=timestamp,
                timezone=timezone,
                model=model,
                refracted_solar_zenith=refracted_solar_zenith,
                apply_atmospheric_refraction=apply_atmospheric_refraction,
                time_output_units=time_output_units,
                angle_output_units=angle_output_units,
                days_in_a_year=days_in_a_year,
                perigee_offset=perigee_offset,
                orbital_eccentricity=orbital_eccentricity,
                time_offset_global=time_offset_global,
                hour_offset=hour_offset,
            )
            results.append({
                'Model': model.value,
                'Solar time': solar_time.value,
                'Units': solar_time.unit,  # Don't trust me -- Redesign Me!
            })

    # debug(locals())
    return results
