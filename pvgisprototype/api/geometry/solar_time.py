import logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('error.log'),  # Save log to a file
        logging.StreamHandler()  # Print log to the console
    ]
)
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
from pvgisprototype.models.noaa.noaa_models import Longitude_in_Radians
from pvgisprototype.models.noaa.noaa_models import Latitude_in_Radians


def model_solar_time(
        longitude: Longitude_in_Radians,
        latitude: Latitude_in_Radians,
        timestamp: datetime,
        timezone: ZoneInfo,
        model: SolarTimeModels,
        refracted_solar_zenith: float,
        apply_atmospheric_refraction: Optional[bool],
        days_in_a_year: float,
        perigee_offset: float,
        eccentricity: float,
        time_offset_global: int,
        hour_offset: int,
        time_output_units: str,
        angle_units: str,
        angle_output_units: str,
        ):
    """
    """
    # if local and timestamp is not None and timezone is not None:
    #     timestamp = timezone.localize(timestamp)

    if model.value == SolarTimeModels.eot:

        solar_time = calculate_solar_time_eot(
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

        solar_time, solar_time_units = calculate_local_solar_time_noaa(
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

    # return (solar_time, units)
    return solar_time


def calculate_solar_time(
        longitude: Longitude_in_Radians,
        latitude: Latitude_in_Radians,
        timestamp: datetime,
        timezone: ZoneInfo,
        models: List[SolarTimeModels] = [SolarTimeModels.skyfield],
        refracted_solar_zenith: float = 1.5853349194640094,  # radians
        apply_atmospheric_refraction: Optional[bool] = True,
        days_in_a_year: float = 365.25,
        perigee_offset: float = 0.048869,
        eccentricity: float = 0.01672,
        time_offset_global: int = 0,
        hour_offset: int = 0,
        time_output_units: str = 'minutes',
        angle_units: str = 'radians',
        angle_output_units: str = 'radians'
):
    """
    Calculates the solar time using all models and returns the results in a table.
    """
    # # debug(locals())
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
                'Solar time': solar_time,
                'Units': 'something',  # Don't trust me -- Redesign Me!
            })

    # debug(locals())
    return results
