from devtools import debug
from datetime import datetime
from zoneinfo import ZoneInfo
from math import pi
from math import sin
from math import cos
from math import acos
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarAzimuthPVISInputModel
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype.api.geometry.models import SolarTimeModels
from pvgisprototype import SolarAzimuth
from pvgisprototype.algorithms.pvis.solar_declination import calculate_solar_declination_pvis
from pvgisprototype.algorithms.pvis.solar_hour_angle import calculate_solar_hour_angle_pvis
from pvgisprototype.api.geometry.solar_time import model_solar_time


def convert_east_to_north_radians_convention(azimuth_east_radians):
    return (azimuth_east_radians + 3 * pi / 2) % (2 * pi)


@validate_with_pydantic(CalculateSolarAzimuthPVISInputModel)
def calculate_solar_azimuth_pvis(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo,
    solar_time_model: SolarTimeModels,
) -> SolarAzimuth:
    """Compute various solar geometry variables.

    Returns
    -------
    solar_azimuth: float

    Notes
    -----
    According to ... solar azimuth is measured from East!
    Conflicht with Jenco 1992?
    """
    solar_declination = calculate_solar_declination_pvis(
        timestamp=timestamp,
    )
    C11 = sin(latitude.radians) * cos(solar_declination.radians)
    C13 = -cos(latitude.radians) * sin(solar_declination.radians)
    C22 = cos(solar_declination.radians)
    C31 = cos(latitude.radians) * cos(solar_declination.radians)
    C33 = sin(latitude.radians) * sin(solar_declination.radians)
    solar_time = model_solar_time(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        solar_time_model=solar_time_model,
    )
    hour_angle = calculate_hour_angle(
        solar_time=solar_time,
    )
    cosine_solar_azimuth = (C11 * cos(hour_angle.radians) + C13) / pow(
        pow((C22 * sin(hour_angle.radians)), 2)
        + pow((C11 * cos(hour_angle.radians) + C13), 2),
        0.5,
    )
    solar_azimuth = acos(cosine_solar_azimuth)
    # -------------------------- convert east to north zero degrees convention
    # PVGIS' follows Hofierka (2002) who states : azimuth is measured from East
    # solar_azimuth = convert_east_to_north_radians_convention(solar_azimuth)
    # convert east to north zero degrees convention --------------------------

    return SolarAzimuth(
        value=solar_azimuth,
        unit="radians",
        position_algorithm='pvis',
        timing_algorithm=solar_time_model.value,
    ) # zero_direction='East'
