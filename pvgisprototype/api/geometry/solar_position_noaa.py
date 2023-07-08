"""
The General Solar Position Calculations
provided by the NOAA Global Monitoring Division

See also: https://unpkg.com/solar-calculator@0.1.0/index.js
"""
import logging
from datetime import datetime
from datetime import timedelta
from datetime import time
from math import sin
from math import cos
from math import tan
from math import acos
from math import radians
from math import degrees
from math import pi
from math import isfinite
from pydantic import BaseModel
from pydantic import Field
from pydantic import validator
from typing import Annotated
from typing import Callable
from typing import Optional
from typing import Tuple
from typing import Union
from ..utilities.conversions import convert_to_degrees_if_requested
from ..utilities.conversions import convert_to_radians_if_requested
from .decorators import validate_with_pydantic
from .models import Longitude
from .models import Latitude
from .models import CalculateFractionalYearNOAAInput
from .models import CalculateEquationOfTimeNOAAInput
from .models import CalculateSolarDeclinationNOAAInput
from .models import CalculateTimeOffsetNOAAInput
from .models import CalculateTrueSolarTimeNOAAInput
from .models import CalculateSolarHourAngleNOAAInput
from .models import AdjustSolarZenithForAtmosphericRefractionNOAAInput
from .models import CalculateSolarZenithNOAAInput
from .models import CalculateSolarAltitudeNOAAInput
from .models import CalculateSolarAzimuthNOAAInput
from .models import CalculateEventHourAngleNOAAInput
from .models import CalculateEventTimeNOAAInput
from .models import CalculateLocalSolarTimeNOAAInput
from .models import CalculateSolarPositionNOAA
from zoneinfo import ZoneInfo


radians_to_time_minutes = lambda value_in_radians: (1440 / (2 * pi)) * value_in_radians
degrees_to_time_minuts = lambda value_in_degrees: 4 * value_in_degrees




@validate_with_pydantic(CalculateFractionalYearNOAAInput)
def calculate_fractional_year_noaa(
        timestamp: datetime,
        angle_output_units: Optional[str] = "radians",
        ) -> float:
    """Calculate fractional year in radians """
    fractional_year = (
        2
        * pi
        / 365
        * (timestamp.timetuple().tm_yday - 1 + float(timestamp.hour - 12) / 24)
    )

    if not 0 <= fractional_year < 2 * pi:
        raise ValueError('Fractional year (in radians) must be in the range [0, 2*pi]')

    fractional_year = convert_to_degrees_if_requested(fractional_year, angle_output_units)
    if angle_output_units == 'degrees':
        if not 0 <= fractional_year < 360:
            raise ValueError('Fractional year (in degrees) must be in the range [0, 360]')
    return fractional_year, angle_output_units


@validate_with_pydantic(CalculateEquationOfTimeNOAAInput)
def calculate_equation_of_time_noaa(
    timestamp: datetime,
    time_output_units: str = 'minutes',
    angle_units: str = 'radians',
) -> float:
    """Calculate the equation of time in minutes"""
    fractional_year, _units = calculate_fractional_year_noaa(
        timestamp, angle_units
    )
    equation_of_time = 229.18 * (
        0.000075
        + 0.001868 * cos(fractional_year)
        - 0.032077 * sin(fractional_year)
        - 0.014615 * cos(2 * fractional_year)
        - 0.040849 * sin(2 * fractional_year)
    )

    # Validate
    if not -20 <= equation_of_time <= 20:
        raise ValueError("The equation of time must be within the range [-20, 20] minutes")

    return equation_of_time, time_output_units


@validate_with_pydantic(CalculateSolarDeclinationNOAAInput)
def calculate_solar_declination_noaa(
        timestamp: datetime,
        angle_units: Optional[str] = 'radians',
        angle_output_units: Optional[str] = 'radians'
) -> float:
    """Calculate the solar declination in radians"""
    # debug(locals())
    fractional_year, _units = calculate_fractional_year_noaa(
            timestamp,
            angle_output_units = angle_units,
            )
    declination = (
        0.006918
        - 0.399912 * cos(fractional_year)
        + 0.070257 * sin(fractional_year)
        - 0.006758 * cos(2 * fractional_year)
        + 0.000907 * sin(2 * fractional_year)
        - 0.002697 * cos(3 * fractional_year)
        + 0.00148 * sin(3 * fractional_year)
    )
    declination = convert_to_degrees_if_requested(declination, angle_output_units)
    return declination, angle_output_units


@validate_with_pydantic(CalculateTimeOffsetNOAAInput)
def calculate_time_offset_noaa(
        longitude: float, 
        timestamp: datetime, 
        time_output_units: str = 'minutes',  # redesign me!
        angle_units: str = 'radians',
    ) -> float:
    """Calculate the time offset for NOAA's solar position calculations
    measured in minutes.

    The time offset (in minutes) incorporates the Equation of Time and accounts
    for the variation of the Local Solar Time (LST) within a given time zone
    due to the longitude variations within the time zone.

    Parameters
    ----------
    timestamp: datetime
        The timestamp to calculate offset for
    longitude: float
        The longitude for calculation
    equation_of_time: float
        The equation of time value for calculation

    Returns
    -------
    float: The time offset

    Notes
    -----

    The reference equation here is:

        `time_offset = eqtime + 4*longitude – 60*timezone`

        (source: https://gml.noaa.gov/grad/solcalc/solareqns.PDF)

        where (variable name and units):
            - time_offset, minutes
            - longitude, degrees
            - timezone, hours
            - eqtime, minutes

    A cleaner (?) reference:

        `TC = 4 * (Longitude - LSTM) + EoT`

        where:
            - TC       : Time Correction Factor, minutes
            - Longitude: Geographical Longitude, degrees
            - LSTM     : Local Standard Time Meridian, degrees * hours

                where:
                - `LSTM = 15 degrees * ΔTUTC`
            
                    where:
                    - ΔTUTC = LT - UTC, hours

                        where:
                        - LT : Local Time
                        - UTC: Universal Coordinated Time
                        - difference of LT from UTC in hours

            - The factor of 4 minutes comes from the fact that the Earth
              rotates 1° every 4 minutes.

            Examples:
                Mount Olympus is UTC + 2, hence LSTM = 15 * 2 = 30 deg. East
    """

    longitude_in_minutes = radians_to_time_minutes(longitude)  # time
    timezone_offset_minutes = timestamp.utcoffset().total_seconds() / 60  # minutes
    equation_of_time, _units = calculate_equation_of_time_noaa(timestamp,
                                                               time_output_units,
                                                               angle_units,
                                                               )  # minutes
    time_offset = longitude_in_minutes - timezone_offset_minutes + equation_of_time

    # Validate output
    if not -720 <= time_offset <= 720:
        raise ValueError("The time offset must range within [-720, 720] minutes ?")

    return time_offset, time_output_units

@validate_with_pydantic(CalculateTrueSolarTimeNOAAInput)
def calculate_true_solar_time_noaa(
        longitude: float,
        timestamp: datetime, 
        timezone: Optional[ZoneInfo],
        time_output_units: str = 'minutes',
        angle_units: str = 'radians',
    ) -> float:
    """Calculate the true solar time.

    Parameters
    ----------
    timestamp: datetime, optional
        The timestamp to calculate offset for
    timezone: str, optional
        The timezone for calculation
    time_offset: float
        The time offset for calculation

    Returns
    -------
    float: The true solar time
    """
    if timezone != timestamp.tzinfo:
        try:
            timestamp = timestamp.astimezone(timezone)
        except pytz.UnknownTimeZoneError as e:
            logging.warning(f'Unknown timezone: {e}')
            raise
    
    time_offset, _units = calculate_time_offset_noaa(
            longitude,
            timestamp,
            time_output_units,
            angle_units,
            )  # in minutes
    true_solar_time = (
        timestamp.hour * 60 + timestamp.minute + timestamp.second / 60 + time_offset
    )

    if time_output_units == 'minutes':
        if not 0 <= true_solar_time <= 1440:
            raise ValueError("The true solar time must range within [0, 1440] minutes")

    return true_solar_time, time_output_units


@validate_with_pydantic(CalculateSolarHourAngleNOAAInput)
def calculate_solar_hour_angle_noaa(
        longitude: float,
        timestamp: datetime, 
        timezone: Optional[str], 
        time_output_units: Optional[str] = 'minutes',
        angle_output_units: Optional[str] = 'radians',

        ) -> float:
    """Calculate the solar hour angle in radians.

    The solar hour angle calculation converts the local solar time (LST) into
    the number of degrees which the sun moves across the sky. In other words,
    it reflects the Earth's rotation and indicates the time of the day relative
    to the position of the Sun. It bases on the longitude and timestamp and by
    definition, the solar hour angle is :

      - 0° at solar noon
      - negative in the morning
      - positive in the afternoon.

    Since the Earth rotates 15° per hour, each hour away from solar noon
    corresponds to an angular motion of the sun in the sky of 15°.
    Practically, the calculation converts a timestamp into a solar time.

    Parameters
    ----------
    timestamp: datetime, optional
        The timestamp to calculate offset for

    timezone: str, optional
        The timezone for calculation
    
    longitude: float
        The longitude for calculation

    Returns:
    float: The solar hour angle

    Notes
    -----

    In the "original" equation, the solar hour angle is measured in degrees.

        `hour_angle = true_solar_time / 4 - 180`
        
        which is the same as

        `hour_angle = true_solar_time * 0.25 - 180`

    In the present implementation, we calculate the solar hour angle directly
    to radians. A circle is 360 degrees, dividing by 1440 minutes in a day
    equals to 0.25.
    """
    true_solar_time, _units = calculate_true_solar_time_noaa(
        longitude, timestamp, timezone, time_output_units
    )  # in minutes

    solar_hour_angle = (true_solar_time - 720) * (pi / 720)

    # Validate
    if angle_output_units == 'radians' and not -pi <= solar_hour_angle <= pi:
        raise ValueError("The hour angle in radians must be within the range [-π, π]")

    elif angle_output_units == 'degrees' and not -180 <= solar_hour_angle <= 180:
        raise ValueError("The hour angle in degrees must be within the range [-180, 180] degrees")

    return solar_hour_angle, angle_output_units


def atmospheric_refraction_for_high_solar_altitude(
    solar_altitude: float,
) -> float:
    """
    Calculate the atmospheric refraction adjustment for high solar_altitudes.

    Parameters:
    tangent_solar_altitude (float): The tangent of the solar altitude angle

    Returns:
    float: The correction factor
    """
    tangent_solar_altitude = tan(solar_altitude)  # in radians
    adjustment_in_degrees = (
        58.1 / tangent_solar_altitude
        - 0.07 / (tangent_solar_altitude**3)
        + 0.000086 / (tangent_solar_altitude**5)
    ) / 3600  # 1 degree / 3600 seconds

    return radians(adjustment_in_degrees)


def atmospheric_refraction_for_near_horizon(solar_altitude: float) -> float:
    """
    Calculate the atmospheric refraction adjusment for near horizon.

    Parameters:
    solar_altitude (float): The solar solar_altitude angle

    Returns:
    float: The adjustment factor
    """
    solar_altitude = degrees(solar_altitude)
    adjustment_in_degrees = (
        1735
        + solar_altitude
        * (
            -518.2
            + solar_altitude
            * (103.4 + solar_altitude * (-12.79 + solar_altitude * 0.711))
        )
    ) / 3600  # 1 degree / 3600 seconds

    return radians(adjustment_in_degrees)


def atmospheric_refraction_for_below_horizon(solar_altitude: float) -> float:
    """
    Calculate the atmospheric refraction adjustment for below horizon.

    Parameters:
    tangent_solar_altitude (float): The tangent of the solar altitude angle

    Returns:
    float: The correction factor
    """
    tangent_solar_altitude = tan(solar_altitude)  # in radians
    adjustment_in_degrees = (
        -20.774 / tangent_solar_altitude
    ) / 3600  # 1 degree / 3600 seconds

    return radians(adjustment_in_degrees)

@validate_with_pydantic(AdjustSolarZenithForAtmosphericRefractionNOAAInput)
def adjust_solar_zenith_for_atmospheric_refraction(
        solar_zenith: float,
        angle_output_units: str = 'radians',
        ) -> float:
    """Adjust solar zenith for atmospheric refraction

    The effects of the atmosphere vary with atmospheric pressure, humidity, and
    other variables. Therefore, the solar position calculations presented here
    are approximate. Errors in sunrise and sunset times can be expected to
    increase the further away you are from the equator, because the sun rises
    and sets at a very shallow angle. Small variations in the atmosphere can
    have a larger effect.

    Parameters
    ----------
    solar_zenith: float
        The solar zenith angle in degrees

    Returns
    -------
    float: The corrected solar zenith angle
    """
    atmospheric_refraction_functions: Dict[str, Callable[[float], float]] = {
        'high_solar_altitude': atmospheric_refraction_for_high_solar_altitude,
        'near_horizon': atmospheric_refraction_for_near_horizon,
        'below_horizon': atmospheric_refraction_for_below_horizon
    }

    solar_altitude = radians(90) - solar_zenith  # in radians
    if solar_altitude <= radians(85):

        if solar_altitude > radians(5):
            function: Callable = atmospheric_refraction_functions['high_solar_altitude']
        
        elif solar_altitude > radians(-0.575):
            function = atmospheric_refraction_functions['near_horizon']
        
        else:
            function = atmospheric_refraction_functions['below_horizon']
        
        # solar zenith = 0 degrees + refraction correction.
        atmospheric_refraction_adjustment_radians = function(solar_altitude)  # in radians
        solar_zenith -= atmospheric_refraction_adjustment_radians  # in radians
        # solar_zenith += function(solar_altitude)  # in radians

    solar_zenith = convert_to_degrees_if_requested(solar_zenith, angle_output_units)

    # Reasonably increase the upper limit for the solar zenith
    # beyond π/2 radians to account for atmospheric refraction.
    # i.e. at 90.833 degrees or about π/2 + 0.0146 radians
    # which is the solar zenith angle when the center of the sun is at the horizon,
    # considering both its apparent size and atmospheric refraction.
    if not isfinite(solar_zenith) or not 0 <= solar_zenith <= pi:
        # raise ValueError('The `solar_zenith` should be a finite number ranging in [0, π/2 + 0.0146] radians')
        raise ValueError(f'The `solar_zenith` should be a finite number ranging in [0, {pi}] radians')

    return solar_zenith, angle_output_units

@validate_with_pydantic(CalculateSolarZenithNOAAInput)
def calculate_solar_zenith_noaa(
        latitude: float,
        timestamp: datetime,
        solar_hour_angle: float,
        apply_atmospheric_refraction: bool = False,
        # time_output_units: str = 'minutes',
        angle_units: str = 'radians',
        angle_output_units: str = 'radians',
        ):
    """Calculate the solar zenith angle (φ) in radians
    """
    solar_declination, _units = calculate_solar_declination_noaa(
            timestamp,
            angle_units,
            angle_output_units,
            )
    cosine_solar_zenith = sin(latitude) * sin(solar_declination) + cos(latitude) * cos(
        solar_declination
    ) * cos(solar_hour_angle)
    # debug(locals())
    solar_zenith = acos(cosine_solar_zenith)
    if apply_atmospheric_refraction:
        solar_zenith, _units = adjust_solar_zenith_for_atmospheric_refraction(
                solar_zenith,
                angle_output_units,
                )  # in radians
    solar_zenith = convert_to_degrees_if_requested(
            solar_zenith,
            angle_output_units,
            )

    # if not isfinite(solar_zenith) or not 0 <= solar_zenith <= pi/2 + 0.0146:
    #     raise ValueError('The `solar_zenith` should be a finite number ranging in [0, π + 0.0146] radians')
    if not isfinite(solar_zenith) or not 0 <= solar_zenith <= pi:
        raise ValueError('The `solar_zenith` should be a finite number ranging in [0, π] radians')

    return solar_zenith, angle_output_units


@validate_with_pydantic(CalculateSolarAltitudeNOAAInput)
def calculate_solar_altitude_noaa(
        longitude: float,
        latitude: datetime,
        timestamp: float,
        timezone: str,
        apply_atmospheric_refraction: bool = True,
        time_output_units: str = 'minutes',
        angle_units: str = 'radians',
        angle_output_units: str = 'radians',
        ):
    """Calculate the solar zenith angle (φ) in radians
    """
    solar_hour_angle, _units = calculate_solar_hour_angle_noaa(
        longitude,
        timestamp,
        timezone,
        time_output_units,
        angle_output_units,
    )
    solar_zenith, _units = calculate_solar_zenith_noaa(
        latitude,
        timestamp,
        solar_hour_angle,
        apply_atmospheric_refraction,
        # time_output_units,
        angle_units,
        angle_output_units,
            )  # radians
    solar_altitude = pi/2 - solar_zenith
    if not isfinite(solar_altitude) or not -pi/2 <= solar_altitude <= pi/2:
        raise ValueError(f'The `solar_altitude` should be a finite number ranging in [{-pi/2}, {pi/2}] radians')

    solar_altitude = convert_to_degrees_if_requested(solar_altitude,
                                                     angle_output_units)
    return solar_altitude, angle_output_units


@validate_with_pydantic(CalculateSolarAzimuthNOAAInput)
def calculate_solar_azimuth_noaa(
        longitude: float,
        latitude: float,
        timestamp: float,
        timezone: str,
        apply_atmospheric_refraction: bool = True,
        time_output_units: str = 'minutes',
        angle_units: str = 'radians',
        angle_output_units: str = 'radians',
        ):
    """Calculate the solar azimith (θ) in radians

    Parameters
    ----------
    latitude: float
        The latitude in radians
    """
    solar_declination, _units = calculate_solar_declination_noaa(
            timestamp,
            angle_units,
            angle_output_units,
            )  # radians
    solar_hour_angle, _units = calculate_solar_hour_angle_noaa(
        longitude, timestamp, timezone, time_output_units, angle_output_units
    )  # radians
    solar_zenith, _units = calculate_solar_zenith_noaa(
        latitude,
        timestamp,
        solar_hour_angle,
        apply_atmospheric_refraction,
        # time_output_units,
        angle_units,
        angle_output_units,
            )  # radians
    cosine_pi_minus_solar_azimuth = - (sin(latitude) * cos(solar_zenith) - sin(solar_declination)) / (
        cos(latitude) * sin(solar_zenith)
    )
    cosine_pi_minus_solar_azimuth = max(-1, min(1, cosine_pi_minus_solar_azimuth))
    pi_minus_solar_azimuth = acos(cosine_pi_minus_solar_azimuth)
    solar_azimuth = pi - pi_minus_solar_azimuth 

    if not isfinite(solar_azimuth) or not 0 <= solar_azimuth <= 2*pi:
        raise ValueError('The `solar_azimuth` should be a finite number ranging in [0, 2π] radians')

    solar_azimuth = convert_to_degrees_if_requested(solar_azimuth, angle_output_units)

    return solar_azimuth, angle_output_units

@validate_with_pydantic(CalculateEventHourAngleNOAAInput)
def calculate_event_hour_angle_noaa(
        latitude: Latitude,
        timestamp: datetime,
        event: str,
        refracted_solar_zenith: float = 1.5853349194640094,  # radians
        angle_units: str = 'radians',
        angle_output_units: str = 'radians',
        ):
    """
    """
    solar_declination, _units = calculate_solar_declination_noaa(
            timestamp,
            angle_units,
            angle_output_units,
            )  # radians
    cosine_event_hour_angle = cos(refracted_solar_zenith) / (
        cos(latitude) * cos(solar_declination)
    ) - tan(latitude) * tan(solar_declination)
    event_hour_angle = acos(cosine_event_hour_angle)  # radians

    # ------------------------------------------------------------------------
    if angle_output_units == 'degrees':  # is this ever needed?
        event_hour_angle = convert_to_degrees_if_requested(
                event_hour_angle,
                angle_output_units,
                )
    # ------------------------------------------------------------------------

    return event_hour_angle, angle_output_units


@validate_with_pydantic(CalculateEventTimeNOAAInput)
def calculate_event_time_noaa(
        longitude: float,
        latitude: float,
        timestamp: datetime,
        timezone: str,
        event: str,
        refracted_solar_zenith: float = 1.5853349194640094,  # radians
        apply_atmospheric_refraction: bool = False,
        time_output_units: str = 'minutes',
        angle_units: str = 'radians',
        angle_output_units: str = 'radians',
        ):
    """Calculate the sunrise or sunset

    For the special case of sunrise or sunset, the zenith is set to 90.833 deg.
    (the approximate correction for atmospheric refraction at sunrise and
    sunset, and the size of the solar disk).

    Parameters
    ----------
    latitude : float
        The latitude, in radians.
    longitude : float
        The longitude, in radians.
    timestamp : datetime
        The date to calculate the event for.
    solar_declination : float
        The solar declination, in radians.
    solar_zenith : float, optional
        The solar zenith, in radians. Default is the cosine of 90.833 degrees.
    equation_of_time : float
        The equation of time, in minutes.
    event : str
        The event to calculate the hour angle for, either of 'noon', 'sunrise'
        or 'sunset'.
    output_units : str, optional
        The units for the output, either "radians" or "degrees". Default is 'radians'.

    Returns
    -------
    datetime
        The time of the event as a datetime object.

    Notes
    -----
    - All angles in radians
    - cosine(90.833) = -0.9629159426075866
    """
    equation_of_time, _ = calculate_equation_of_time_noaa(
            timestamp,
            time_output_units,
            angle_units,
            )  # minutes
    solar_declination , _ = calculate_solar_declination_noaa(
            timestamp,
            angle_units,  # for calculate_fractional_year_noaa()
            angle_output_units
            )  # radians
    solar_hour_angle, _ = calculate_solar_hour_angle_noaa(
            longitude,
            timestamp,
            timezone,
            time_output_units,
            angle_output_units,
            )  # radians
    solar_zenith, _ = calculate_solar_zenith_noaa(
            latitude,
            timestamp,
            solar_hour_angle,
            apply_atmospheric_refraction,
            # time_output_units,
            angle_units,
            angle_output_units,
            )  # radians
    event_hour_angle, _ = calculate_event_hour_angle_noaa(
            latitude,
            timestamp,
            event,
            refracted_solar_zenith,
            angle_units,
            angle_output_units,
            )
    event_hour_angle_minutes = radians_to_time_minutes(event_hour_angle)
    longitude_minutes = radians_to_time_minutes(longitude)
    event_calculations = {
        'sunrise': 720 - longitude_minutes + event_hour_angle_minutes - equation_of_time,
        'noon': 720 - longitude_minutes - equation_of_time,
        'sunset': 720 - longitude_minutes - event_hour_angle_minutes - equation_of_time
    }
    event_time = event_calculations.get(event.lower())
    event_datetime = datetime.combine(timestamp.date(), time(0)) + timedelta(minutes=event_time)
    utc_zoneinfo = ZoneInfo("UTC")
    event_datetime = event_datetime.astimezone(utc_zoneinfo)

    return event_datetime, time_output_units


@validate_with_pydantic(CalculateLocalSolarTimeNOAAInput)
def calculate_local_solar_time_noaa(
        longitude: float,
        latitude: float,
        timestamp: float,
        timezone: str,
        output_units: str = 'hours',  # for the hour angle! Remove Me?
        verbose: str = False,
    ) -> float:
    """
    Returns
    -------

    (solar_time, units): float, str
    """
    # Handle Me during input validation? -------------------------------------
    if timezone != timestamp.tzinfo:
        try:
            timestamp = timestamp.astimezone(timezone)
        except Exception as e:
            logging.warning(f'Error setting tzinfo for timestamp = {timestamp}: {e}')
    # ------------------------------------------------------------------------
    solar_noon_timestamp, units = calculate_event_time(
            longitude,
            latitude,
            timestamp,
            timezone,
            event='noon',
            output_units = 'minutes',  # THIS does not really work yet!
            )
    local_solar_time = timestamp - solar_noon_timestamp
    decimal_hours = local_solar_time.total_seconds() / 3600

    if verbose:
        typer.echo(f'Local solar time: {local_solar_time}')

    return decimal_hours, output_units
