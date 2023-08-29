from devtools import debug
from typing import Annotated
from typing import Optional
from enum import Enum
from datetime import datetime
from zoneinfo import ZoneInfo
from math import pi
from math import sin
from math import cos
from math import acos
from pvgisprototype.api.decorators import validate_with_pydantic
from pvgisprototype.api.function_models import CalculateSolarAzimuthPVISInputModel
from pvgisprototype.api.data_classes import Longitude
from pvgisprototype.api.data_classes import Latitude
from pvgisprototype.api.geometry.models import SolarTimeModels
from pvgisprototype.api.data_classes import SolarAzimuth
from pvgisprototype.api.geometry.solar_declination import calculate_solar_declination_pvis
from pvgisprototype.api.geometry.solar_time import model_solar_time
from pvgisprototype.api.geometry.solar_hour_angle import calculate_hour_angle
from pvgisprototype.api.utilities.timestamp import timestamp_to_decimal_hours
from pvgisprototype.api.utilities.conversions import convert_to_degrees_if_requested


def convert_east_to_north_radians_convention(azimuth_east_radians):
    return (azimuth_east_radians + 3 * pi / 2) % (2 * pi)


@validate_with_pydantic(CalculateSolarAzimuthPVISInputModel, expand_args=True)
def calculate_solar_azimuth_pvis(
    longitude: Longitude,
    latitude: Latitude,
    # longitude: Longitude_in_Radians,
    # latitude: Latitude_in_Radians,
    timestamp: datetime,
    timezone: ZoneInfo,
    apply_atmospheric_refraction: bool,
    refracted_solar_zenith: float,
    days_in_a_year: float,
    perigee_offset: float,
    eccentricity_correction_factor: float,
    time_offset_global: int,
    hour_offset: int,
    solar_time_model: SolarTimeModels,
    time_output_units: str,
    angle_units: str,
    angle_output_units: str,
) -> SolarAzimuth:
    """Compute various solar geometry variables.

    Returns
    -------
    solar_azimuth: float


    Returns
    -------
    solar_azimuth: float

    Notes
    -----
    According to ... solar azimuth is measured from East!
    Conflicht with Jenvco 1992?
    """
    solar_declination = calculate_solar_declination_pvis(
        timestamp=timestamp,
        angle_output_units=angle_output_units,
    )
    C11 = sin(latitude.value) * cos(solar_declination.value)
    C13 = -cos(latitude.value) * sin(solar_declination.value)
    C22 = cos(solar_declination.value)
    C31 = cos(latitude.value) * cos(solar_declination.value)
    C33 = sin(latitude.value) * sin(solar_declination.value)
    solar_time = model_solar_time(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        model=solar_time_model,  # returns datetime.time object
        refracted_solar_zenith=refracted_solar_zenith,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
    )
    hour_angle = calculate_hour_angle(
        solar_time=solar_time,
        angle_output_units=angle_output_units,
    )
    cosine_solar_azimuth = (C11 * cos(hour_angle.value + C13)) / pow(
        pow((C22 * sin(hour_angle.value)), 2)
        + pow((C11 * cos(hour_angle.value) + C13), 2),
        0.5,
    )
    solar_azimuth = acos(cosine_solar_azimuth)
    # -------------------------- convert east to north zero degrees convention
    # PVGIS' follows Hofierka (2002) who states : azimuth is measured from East
    # solar_azimuth = convert_east_to_north_radians_convention(solar_azimuth)
    # convert east to north zero degrees convention --------------------------

    solar_azimuth = SolarAzimuth(value=solar_azimuth, unit="radians") # zero_direction='East'
    solar_azimuth = convert_to_degrees_if_requested(solar_azimuth, angle_output_units)

    return solar_azimuth
