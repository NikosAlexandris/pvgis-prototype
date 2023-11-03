from devtools import debug
from datetime import datetime
from zoneinfo import ZoneInfo
from math import sin
from math import cos
from math import isfinite
from pvgisprototype import SolarAzimuth
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype.constants import RADIANS


def calculate_solar_azimuth_jenco(
):
    """ """
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo,
    apply_atmospheric_refraction: bool,
    refracted_solar_zenith: RefractedSolarZenith,
    perigee_offset: float,
    eccentricity_correction_factor: float,
    time_offset_global: int,
    hour_offset: int,
    solar_time_model: SolarTimeModels.pvis,
) -> SolarAzimuth:
    """Compute various solar geometry variables.

    Returns
    -------
    solar_azimuth: float


    Returns
    -------
    solar_azimuth: float
    """
    solar_declination = calculate_solar_declination_pvis(
        timestamp=timestamp,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
    )
    C11 = sin(latitude.radians) * cos(solar_declination.radians)
    C13 = cos(latitude.radians) * sin(solar_declination.radians)
    C22 = cos(solar_declination.radians)
    solar_time = model_solar_time(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        model=SolarTimeModels.pvis,  # use same timing algorithm as for the declination
        refracted_solar_zenith=refracted_solar_zenith,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
    )
    hour_angle = calculate_hour_angle(solar_time=solar_time)
    tangent_solar_azimuth = (C22 * sin(hour_angle.radians)) / (
        C11 * cos(hour_angle.radians) - C13
    )
    solar_azimuth = atan(tangent_solar_azimuth)

    solar_azimuth = SolarAzimuth(
        value=solar_azimuth,
        unit=RADIANS,
        position_algorithm='Jenco',
        timing_algorithm='Jenco',
    ) # zero_direction ='East'

    if (
        not isfinite(solar_azimuth.degrees)
        or not solar_azimuth.min_degrees <= solar_azimuth.degrees <= solar_azimuth.max_degrees
    ):
        raise ValueError(
            f"The calculated solar azimuth angle {solar_azimuth.degrees} is out of the expected range\
            [{solar_azimuth.min_degrees}, {solar_azimuth.max_degrees}] degrees"
        )

    return solar_azimuth
