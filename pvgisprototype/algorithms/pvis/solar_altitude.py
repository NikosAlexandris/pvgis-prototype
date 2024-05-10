from devtools import debug
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from cachetools import cached
from pvgisprototype.caching import custom_hashkey
from datetime import datetime
from pandas import DatetimeIndex
from zoneinfo import ZoneInfo
from math import cos
from math import sin
from math import asin
from pvgisprototype.algorithms.pvis.solar_declination import calculate_solar_declination_time_series_pvis
from pvgisprototype.algorithms.noaa.solar_hour_angle import calculate_solar_hour_angle_time_series_noaa
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarAltitudePVISInputModel
from pvgisprototype import Latitude
from pvgisprototype import Longitude
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype import SolarAltitude
from pvgisprototype.api.position.declination import calculate_solar_declination_pvis
from pvgisprototype.api.position.solar_time import model_solar_time
from pvgisprototype.algorithms.pvis.solar_hour_angle import calculate_solar_hour_angle_pvis
from pvgisprototype.constants import RADIANS
from math import isfinite
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT, DATA_TYPE_DEFAULT, LOG_LEVEL_DEFAULT, RADIANS, VERBOSE_LEVEL_DEFAULT
import numpy


@validate_with_pydantic(CalculateSolarAltitudePVISInputModel)
def calculate_solar_altitude_pvis(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo,
    perigee_offset: float,
    eccentricity_correction_factor: float,
    time_offset_global: int,
    solar_time_model: SolarTimeModel,
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
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
    )
    C31 = cos(latitude.radians) * cos(solar_declination.radians)
    C33 = sin(latitude.radians) * sin(solar_declination.radians)
    solar_time = model_solar_time(
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


@log_function_call
@cached(cache={}, key=custom_hashkey)
# @validate_with_pydantic(CalculateSolarAltitudePVISInputModel)
def calculate_solar_altitude_time_series_pvis(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    perigee_offset: float,
    eccentricity_correction_factor: float,
    # time_offset_global: int,
    # solar_time_model: SolarTimeModel,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> SolarAltitude:
    """Calculate the solar altitude angle.

    Calculate the solar altitude angle based on the equation 

    sine_solar_altitude = (
        sin(latitude.radians)
        * np.sin(solar_declination_series.radians)
        + cos(latitude.radians)
        * np.cos(solar_declination_series.radians)
        * np.cos(solar_hour_angle_series.radians)

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

    Notes
    -----

    NOAA's equation is practically the same, though it targets the cosine
    function of the solar zenith angle which it the complementary of the solar
    altitude angle.

    cosine_solar_zenith = (
        sin(latitude.radians)
        * np.sin(solar_declination_series.radians)
        + cos(latitude.radians)
        * np.cos(solar_declination_series.radians)
        * np.cos(solar_hour_angle_series.radians)

    """
    solar_declination_series = calculate_solar_declination_time_series_pvis(
        timestamps=timestamps,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
    )
    C31 = cos(latitude.radians) * numpy.cos(solar_declination_series.radians)
    C33 = sin(latitude.radians) * numpy.sin(solar_declination_series.radians)
    solar_hour_angle_series = calculate_solar_hour_angle_time_series_noaa(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    solar_altitude_series = numpy.arcsin(
        C31 * numpy.cos(solar_hour_angle_series.radians) + C33
    )

    # The hour angle of the time of sunrise/sunset over a horizontal surface
    # Thr,s can be calculated then as:
    # cos(event_hour_angle_horizontal) = -C33 / C31

    # if (
    #     not isfinite(solar_altitude.degrees)
    #     or not solar_altitude.min_degrees <= solar_altitude.degrees <= solar_altitude.max_degrees
    # ):
    #     raise ValueError(
    #         f"The calculated solar altitude angle {solar_altitude.degrees} is out of the expected range\
    #         [{solar_altitude.min_degrees}, {solar_altitude.max_degrees}] radians"
    #     )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
            data=solar_altitude_series,
            log_level=log,
            hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return SolarAltitude(
        value=solar_altitude_series,
        unit=RADIANS,
        position_algorithm='PVIS',
        timing_algorithm=solar_hour_angle_series.timing_algorithm,
    )
