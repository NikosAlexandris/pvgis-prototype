import logging
from datetime import datetime
from datetime import timedelta
from math import sin
from math import cos
from math import tan
from math import acos
from math import radians
from math import degrees
from math import pi
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
from .models import CalculateFractionalYearNOAAInput
from .models import CalculateSolarDeclinationNOAAInput
from .models import CalculateEquationOfTimeNOAAInput
from .models import CalculateTimeOffsetNOAAInput
from .models import CalculateHourAngleNOAAInput
from .models import CalculateTrueSolarTimeNOAAInput
from zoneinfo import ZoneInfo


radians_to_time_minutes = lambda value_in_radians: (1440 / (2 * pi)) * value_in_radians
degrees_to_time_minuts = lambda value_in_degrees: 4 * value_in_degrees


class SolarPositionData(BaseModel):
    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)


@validate_with_pydantic(CalculateFractionalYearNOAAInput)
def calculate_fractional_year_noaa(
        timestamp: datetime,
        output_units: Optional[str] = "radians",
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

    fractional_year = convert_to_degrees_if_requested(fractional_year, output_units)

    # Validate
    if output_units == 'degrees':
        if not 0 <= fractional_year < 360:
            raise ValueError('Fractional year (in degrees) must be in the range [0, 360]')
    return fractional_year, output_units


@validate_with_pydantic(CalculateEquationOfTimeNOAAInput)
def calculate_equation_of_time_noaa(
    timestamp: datetime,
    output_units: Optional[str] = "minutes",
) -> float:
    """Calculate the equation of time in minutes"""
    fractional_year, _units = calculate_fractional_year_noaa(timestamp)
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

    return equation_of_time, output_units


@validate_with_pydantic(CalculateSolarDeclinationNOAAInput)
def calculate_solar_declination_noaa(
        timestamp: datetime,
        output_units: Optional[str] = 'radians'
) -> float:
    """Calculate the solar declination in radians"""
    # debug(locals())
    fractional_year, _units = calculate_fractional_year_noaa(timestamp, output_units)
    declination = (
        0.006918
        - 0.399912 * cos(fractional_year)
        + 0.070257 * sin(fractional_year)
        - 0.006758 * cos(2 * fractional_year)
        + 0.000907 * sin(2 * fractional_year)
        - 0.002697 * cos(3 * fractional_year)
        + 0.00148 * sin(3 * fractional_year)
    )
    declination = convert_to_degrees_if_requested(declination, output_units)
    return declination, output_units


@validate_with_pydantic(CalculateTimeOffsetNOAAInput)
def calculate_time_offset_noaa(
        longitude: float, 
        timestamp: datetime, 
        output_units: Optional[str] = 'minutes'  # redesign me!
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
    longitude_in_minutes = radians_to_time_minutes(longitude)
    timezone_offset_minutes = timestamp.utcoffset().total_seconds() / 60  # in minutes
    equation_of_time, _units = calculate_equation_of_time_noaa(timestamp)  # in minutes
    time_offset = longitude_in_minutes - timezone_offset_minutes + equation_of_time

    # Validate output
    if not -720 <= time_offset <= 720:
        raise ValueError("The time offset must range within [-720, 720] minutes ?")

    return time_offset, output_units

@validate_with_pydantic(CalculateTrueSolarTimeNOAAInput)
def calculate_true_solar_time_noaa(
        longitude: float,
        timestamp: datetime, 
        timezone: Optional[ZoneInfo],
        output_units: Optional[str] = 'minutes',
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
    
    time_offset, _units = calculate_time_offset_noaa(longitude, timestamp)  # in minutes
    true_solar_time = timestamp.hour * 60 + timestamp.minute + timestamp.second / 60 + time_offset

    # Validate output
    if not 0 <= true_solar_time <= 1440:
        raise ValueError("The true solar time must range within [0, 1440] minutes")

    return true_solar_time, output_units


@validate_with_pydantic(CalculateHourAngleNOAAInput)
def calculate_hour_angle_noaa(
        longitude: float,
        timestamp: datetime, 
        timezone: Optional[str], 
        output_units: Optional[str] = 'radians',

        ) -> float:
    """Calculate the solar hour angle in radians.

    The Hour Angle converts the local solar time (LST) into the number of
    degrees which the sun moves across the sky. By definition, the Hour Angle
    is 0° at solar noon. Since the Earth rotates 15° per hour, each hour away
    from solar noon corresponds to an angular motion of the sun in the sky of
    15°. In the morning the hour angle is negative, in the afternoon the hour
    angle is positive.

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
    """
    true_solar_time, _units = calculate_true_solar_time_noaa(
        longitude, timestamp, timezone, output_units="minutes"
    )  # in minutes
    # hour_angle = true_solar_time / 4 - 180  # original equation in degrees!
    # Here, going directly to radians
    #  a circle is 360 degrees, divide by 1440 minutes in a day = 0.25
    hour_angle = (true_solar_time - 720) * (pi / 720)

    # Validate
    if output_units == 'radians' and not -pi <= hour_angle <= pi:
        raise ValueError("The hour angle in radians must be within the range [-π, π]")

    elif output_units == 'degrees' and not -180 <= hour_angle <= 180:
        raise ValueError("The hour angle in degrees must be within the range [-180, 180] degrees")

    return hour_angle, output_units


def atmospheric_refraction_correction_for_high_elevation(te: float) -> float:
    """
    Calculate the atmospheric refraction correction for high elevations.

    Parameters:
    te (float): The tangent of the solar elevation angle

    Returns:
    float: The correction factor
    """
    return 58.1 / te - 0.07 / (te**3) + 0.000086 / (te**5)


def atmospheric_refraction_correction_for_near_horizon(elevation: float) -> float:
    """
    Calculate the atmospheric refraction correction for near horizon.

    Parameters:
    elevation (float): The solar elevation angle

    Returns:
    float: The correction factor
    """
    return 1735 + elevation * (
        -518.2 + elevation * (103.4 + elevation * (-12.79 + elevation * 0.711))
    )


def atmospheric_refraction_correction_for_below_horizon(te: float) -> float:
    """
    Calculate the atmospheric refraction correction for below horizon.

    Parameters:
    te (float): The tangent of the solar elevation angle

    Returns:
    float: The correction factor
    """
    return -20.774 / te


def atmospheric_refraction(solar_zenith: float) -> float:
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
        'high_elevation': atmospheric_refraction_correction_for_high_elevation,
        'near_horizon': atmospheric_refraction_correction_for_near_horizon,
        'below_horizon': atmospheric_refraction_correction_for_below_horizon
    }
    solar_elevation = 90 - solar_zenith  # in degrees
    if solar_elevation <= 85:
        te = tan(radians(solar_elevation))
        if solar_elevation > 5:
            function: Callable = atmospheric_refraction_functions['high_elevation']
        elif solar_elevation > -0.575:
            function = atmospheric_refraction_functions['near_horizon']
        else:
            function = atmospheric_refraction_functions['below_horizon']
        adjusment = function(te if solar_elevation > -0.575 else solar_elevation)
        solar_zenith -= (adjusment / 3600) * radians(1)

    return solar_zenith


def calculate_solar_zenith_noaa(
        latitude: float,
        solar_declination: float,
        hour_angle: float,
        ):
    """Calculate the solar zenith angle (φ) in radians
    """
    cosine_solar_zenith = sin(latitude) * sin(solar_declination) + cos(latitude) * cos(
        solar_declination
    ) * cos(radians(hour_angle))
    solar_zenith = acos(cosine_solar_zenith)
    solar_zenith = atmospheric_refraction(solar_zenith)

    return solar_zenith


def calculate_solar_azimuth_noaa(
        latitude: float,
        solar_declination: float,
        solar_zenith: float = -0.9629159426075866,  # cosine of 90.833
        ):
    """Calculate the solar azimith (θ) in radians

    Parameters
    ----------
    latitude: float
        The latitude in radians
    """
    cosine_solar_azimuth = (-sin(latitude) * cos(solar_zenith) - sin(solar_declination)) / (
        cos(latitude) * sin(solar_zenith)
    )
    return pi - acos(cosine_solar_azimuth)


def calculate_event_time(
        longitude: float,
        latitude: float,
        timestamp: float,
        timezone: str,
        solar_declination: float,
        equation_of_time: float,
        event: str,
        solar_zenith: float = -0.9629159426075866,  # cosine of 90.833
        output_units: str = 'radians',
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
    expression = (cos(solar_zenith) / (cos(latitude) * cos(solar_declination))) - tan(
        latitude
    ) * tan(solar_declination)
    hour_angle = acos(expression)
    hour_angle = convert_to_degrees_if_requested(hour_angle, output_units)

    event_calculations = {
        'noon': 720 - 4 * longitude - equation_of_time,
        'sunrise': 720 - 4 * (longitude + hour_angle) - equation_of_time,
        'sunset': 720 - 4 * (longitude - hour_angle) - equation_of_time
    }
    event_time = event_calculations.get(event.lower())
    event_datetime = datetime.combine(timestamp.date(), time(0)) + timedelta(
        minutes=event_time
    )
    # Review the following !
    event_datetime = event_datetime.replace(tzinfo=pytz.UTC)
    event_datetime = event_datetime.astimezone(pytz.timezone(timezone))

    return event_datetime


def calculate_local_solar_time_noaa(
        longitude: float,
        latitude: float,
        timestamp: float,
        timezone: str,
        solar_declination: float,
        equation_of_time: float,
        solar_zenith: float = -0.9629159426075866,  # cosine of 90.833
        event: str = 'noon',
        output_units: str = 'radians'  # for the hour angle! Remove Me?
    ) -> float:
    """
    """
    # Handle Me during input validation? -------------------------------------
    if timezone != timestamp.tzinfo:
        try:
            timestamp = timestamp.astimezone(timezone)
        except Exception as e:
            logging.warning(f'Error setting tzinfo for timestamp = {timestamp}: {e}')
    # ------------------------------------------------------------------------
    solar_noon_timestamp = calculate_event_time(
            longitude,
            latitude,
            timestamp,
            timezone,
            solar_zenith,
            solar_declination,
            equation_of_time,
            event,  # = 'noon'
            output_units,
            )
    local_solar_time = timestamp - solar_noon_timestamp
    decimal_hours = local_solar_time.total_seconds() / 3600

    if verbose:
        typer.echo(f'Local solar time: {local_solar_time}')

    debug(locals())
    return decimal_hours, 'decimal hours'

