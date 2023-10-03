from devtools import debug
from datetime import datetime
from zoneinfo import ZoneInfo
from math import cos
from math import sin
from math import asin
from typing import Optional

from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarAltitudePVISInputModel
from pvgisprototype import Latitude
from pvgisprototype import Longitude
from pvgisprototype import RefractedSolarZenith
from pvgisprototype.api.geometry.models import SolarTimeModels
from pvgisprototype import SolarAltitude
from pvgisprototype.api.geometry.solar_declination import calculate_solar_declination_pvis
from pvgisprototype.api.geometry.solar_time import model_solar_time
from pvgisprototype.api.geometry.solar_hour_angle import calculate_hour_angle
# from pvgisprototype.api.utilities.conversions import convert_to_degrees_if_requested


@validate_with_pydantic(CalculateSolarAltitudePVISInputModel)
def calculate_solar_altitude_pvis(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo,
    apply_atmospheric_refraction: bool,
    refracted_solar_zenith: RefractedSolarZenith,
    days_in_a_year: float,
    perigee_offset: float,
    eccentricity_correction_factor: float,
    time_offset_global: int,
    hour_offset: int,
    solar_time_model: SolarTimeModels,
    # time_output_units: str,
    # angle_units: str,
    # angle_output_units: str,
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
        days_in_a_year=days_in_a_year,
        eccentricity_correction_factor=eccentricity_correction_factor,
        perigee_offset=perigee_offset,
        # angle_output_units=angle_output_units,
    )
    C31 = cos(latitude.radians) * cos(solar_declination.radians)
    C33 = sin(latitude.radians) * sin(solar_declination.radians)
    solar_time = model_solar_time(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        solar_time_model=solar_time_model,  # returns datetime.time object
        refracted_solar_zenith=refracted_solar_zenith,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        # time_output_units=time_output_units,
        # angle_units=angle_units,
        # angle_output_units=angle_output_units,
    )
    hour_angle = calculate_hour_angle(
            solar_time=solar_time,
            # angle_output_units='radians',
    )
    sine_solar_altitude = C31 * cos(hour_angle.radians) + C33
    solar_altitude = asin(sine_solar_altitude)
    solar_altitude = SolarAltitude(value=solar_altitude, unit='radians')
    # solar_altitude = convert_to_degrees_if_requested(solar_altitude, angle_output_units)

    if verbose == 3:
        debug(locals())
    return solar_altitude
