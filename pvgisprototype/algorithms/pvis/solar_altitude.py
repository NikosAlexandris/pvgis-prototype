from devtools import debug
from datetime import datetime
from zoneinfo import ZoneInfo
from math import cos
from math import sin
from math import asin
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarAltitudePVISInputModel
from pvgisprototype import Latitude
from pvgisprototype import Longitude
from pvgisprototype.api.geometry.models import SolarTimeModels
from pvgisprototype import SolarAltitude
from pvgisprototype.api.geometry.declination import calculate_solar_declination_pvis
from pvgisprototype.api.geometry.time import model_solar_time
from pvgisprototype.algorithms.pvis.solar_hour_angle import calculate_solar_hour_angle_pvis
from pvgisprototype.constants import RADIANS
from math import isfinite


@validate_with_pydantic(CalculateSolarAltitudePVISInputModel)
def calculate_solar_altitude_pvis(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo,
    perigee_offset: float,
    eccentricity_correction_factor: float,
    time_offset_global: int,
    solar_time_model: SolarTimeModels,
    verbose: int = 0,
) -> SolarAltitude:
    """Compute various solar geometry variables.
    Parameters
    ----------
    longitude : float
        The longitude in degrees. This value will be converted to radians. 
        It should be in the range [-180, 180].

    latitude : float
        The latitude in degrees. This value will be converted to radians. 
        It should be in the range [-90, 90].
    
    timestamp : datetime, optional
        The timestamp for which to calculate the solar altitude. 
        If not provided, the current UTC time will be used.
    
    timezone : str, optional
        The timezone to use for the calculation. 
        If not provided, the system's local timezone will be used.
    
    angle_output_units : str, default 'radians'
        The units to use for the output solar geometry variables. 
        This should be either 'degrees' or 'radians'.

    Returns
    -------
    float
        The calculated solar altitude.
    """
    solar_declination = calculate_solar_declination_pvis(
        timestamp=timestamp,
        timezone=timezone,
        eccentricity_correction_factor=eccentricity_correction_factor,
        perigee_offset=perigee_offset,
    )
    C31 = cos(latitude.radians) * cos(solar_declination.radians)
    C33 = sin(latitude.radians) * sin(solar_declination.radians)
    C31 = cos(latitude.radians) * cos(solar_declination.radians)
    C33 = sin(latitude.radians) * sin(solar_declination.radians)
    solar_time = model_solar_time(
        longitude=longitude,
        latitude=latitude,
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        solar_time_model=solar_time_model,  # returns datetime.time object
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_offset_global=time_offset_global,
    )
    hour_angle = calculate_solar_hour_angle_pvis(
            solar_time=solar_time,
    )
    sine_solar_altitude = C31 * cos(hour_angle.radians) + C33
    solar_altitude = asin(sine_solar_altitude)
    solar_altitude = SolarAltitude(
        value=solar_altitude,
        unit=RADIANS,
        position_algorithm='PVIS',
        timing_algorithm=solar_time_model.value,
    )
    if (
        not isfinite(solar_altitude.degrees)
        or not solar_altitude.min_degrees <= solar_altitude.degrees <= solar_altitude.max_degrees
    ):
        raise ValueError(
            f"The calculated solar altitude angle {solar_altitude.degrees} is out of the expected range\
            [{solar_altitude.min_degrees}, {solar_altitude.max_degrees}] radians"
        )

    if verbose == 3:
        debug(locals())

    return solar_altitude
