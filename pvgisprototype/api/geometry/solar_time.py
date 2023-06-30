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
from enum import Enum
from datetime import datetime
from datetime import time as datetime_time
from datetime import timedelta
import pytz
from tzlocal import get_localzone
import ephem

from skyfield import almanac
from skyfield.api import Topos
from skyfield.api import load
from skyfield.api import N
from skyfield.api import W
from skyfield.api import E
from skyfield.api import wgs84
from skyfield.api import load

import numpy as np
from math import pi
from math import sin
from math import cos
from math import tan 
from math import acos
from ..constants import HOUR_ANGLE
from ..constants import UNDEF
from ..constants import double_numpi
from ..constants import half_numpi
from ..utilities.conversions import convert_to_radians
from ..utilities.conversions import convert_to_degrees_if_requested
from ..utilities.timestamp import now_datetime
from ..utilities.timestamp import ctx_convert_to_timezone
from ..utilities.timestamp import attach_timezone
from ..utilities.timestamp import convert_hours_to_seconds
from ..utilities.image_offset import get_image_offset


class SolarTimeModels(str, Enum):
    eot = 'eot'
    ephem = 'ephem'
    noaa = 'NOAA'
    pvgis = 'PVGIS'
    skyfield = 'Skyfield'


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"Calculate solar time for a location and moment in time",
)


def calculate_solar_time_skyfield(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_datetime)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Timezone',
            callback=ctx_convert_to_timezone)] = None,
        verbose: bool = False,
        ):
    """
    Returns
    -------
    (decimal_hours, units): float, str
    """
    # Handle Me during input validation? -------------------------------------
    try:
        timestamp = timezone.localize(timestamp)
    except Exception:
        logging.warning(f'tzinfo {timezone} already set for timestamp = {timestamp}')
    # Handle Me during input validation? -------------------------------------

    midnight = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
    next_midnight = midnight + timedelta(days=1)
    timescale = load.timescale()
    midnight_time = timescale.from_datetime(midnight)
    next_midnight_time = timescale.from_datetime(next_midnight)

    ephemeris = load('de421.bsp')
    sun = ephemeris['Sun']
    location = wgs84.latlon(latitude * N, longitude * W)
    f = almanac.meridian_transits(ephemeris, sun, location)
    times, events = almanac.find_discrete(midnight_time, next_midnight_time, f)
    
    times = times[events == 1]  # select transits instead of antitransits
    if not times:
        raise ValueError("No solar noon found in the given time range")

    solar_noon = times[0]
    solar_noon_string = str(solar_noon.astimezone(timezone))[:19]
    solar_noon_datetime = solar_noon.utc_datetime().replace(tzinfo=pytz.UTC)
    local_solar_time = timestamp - solar_noon_datetime.astimezone(timezone)
    decimal_hours = local_solar_time.total_seconds() / 3600

    if verbose:
        typer.echo(f'Solar noon: {solar_noon_string}')
        typer.echo(f'Local solar time: {local_solar_time}')

    return decimal_hours, 'decimal hours'


def calculate_solar_time_ephem(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_datetime)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Timezone',
            callback=ctx_convert_to_timezone)] = None,
        verbose: bool = False,
        ):
    """Calculate the solar time using PyEphem

    The position of the Sun in the sky changes slightly day to day due to the
    Earth's elliptical orbit and axis tilt around the Sun. In consequence, the
    length of each solar day varies slightly.

    The mean solar time (as "opposed" to the apparent solar time which is
    measured with a sundial), averages out these variations to create a "mean"
    or average solar day of 24 hours long. This is the basis of our standard
    time system, although further adjusted to create the time zones.

    A key concept in solar time is the solar noon, the moment when the Sun
    reaches its highest point in the sky each day. In apparent solar time,
    solar noon is the moment the Sun crosses the local meridian (an imaginary
    line that runs from North to South overhead).

    Solar time can vary significantly from standard clock time, depending on
    the time of year and the observer's longitude within their time zone. For
    example, at the eastern edge of a time zone, the Sun may reach its highest
    point (solar noon) significantly earlier than noon according to standard
    clock time.

    Returns
    -------

    (solar_time, units): float, str

    Notes
    -----

    hour_angle: float

        The hour angle is the time since the Sun was at the local meridian
        measured in radians.

        The hour angle is the time elapsed since an astronomical object (in
        this case, the Sun) passed the observer's local meridian, an imaginary
        line in the sky that goes from north to south and passes directly
        overhead. In astronomical terms, the hour angle is the difference
        between the local sidereal time and the right ascension of the object.

        - The local meridian is an imaginary line in the sky that runs from the
          north to the south and passes directly over the observer's location.

        - Solar noon (or local solar noon) is the moment when the Sun is at its
          highest point in the sky, directly overhead or on the local meridian,
          for a specific location on Earth. The exact time of solar noon
          depends on the observer's longitude because different places on Earth
          reach this point at different times as the Earth rotates.

        - Local solar time is exactly 12:00 (noon) when the sun crosses the
          local meridian. Effectively, the Sun is in its highest point in the
          sky (noon) when the _sidereal time_ equals its time of right
          ascension.

        - The local sidereal time is a measure of the position of the observer
          relative to the stars (hence, 'sidereal', which means 'related to the
          stars').

        - The right ascension of an object is its position along the celestial
          equator (an imaginary line in the sky above the Earth's equator).

        - Subtracting the Sun's right ascension (`sun.ra`) from the local
        sidereal time (`observer.sidereal_time()`) gives the time elapsed since
        the Sun was at the observer's local meridian.
    """
    observer = ephem.Observer()
    observer.date = timestamp
    observer.lon = longitude
    observer.lat = latitude
    sidereal_time = observer.sidereal_time()

    sun = ephem.Sun()  # a Sun object
    sun.compute(observer)  # sun position for observer's location and time
    sun_right_ascension = sun.ra

    hour_angle = sidereal_time - sun_right_ascension

    # norm -> normalise to 24h
    solar_time = ephem.hours(hour_angle + ephem.hours('12:00')).norm

    if verbose:
        typer.echo(f'Local sidereal time: {sidereal_time}')
        typer.echo(f'Sun right ascension: {sun.ra}')
        typer.echo(f'Hour angle: {hour_angle}')
        typer.echo(f'Sun transit: {ephem.localtime(observer.date)}')
        typer.echo(f'Mean solar time: {solar_time}')
    return solar_time, 'decimal hours'  # norm for 24h


def calculate_solar_time_noaa(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_datetime)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Timezone',
            callback=ctx_convert_to_timezone)] = None,
        verbose: bool = False,
        ):
    """
    General Solar Position Calculations - NOAA Global Monitoring Division

    Returns
    -------

    (solar_time, units): float, str
    """
    # Handle Me during input validation? -------------------------------------
    try:
        timestamp = timezone.localize(timestamp)
    except Exception:
        logging.warning(f'tzinfo already set for timestamp = {timestamp}')
    # Handle Me during input validation? -------------------------------------

    # utc_offset_hours = timestamp.utcoffset().total_seconds() / 3600

    # Calculate the fractional year, in radians
    gamma = 2 * pi / 365 * (timestamp.timetuple().tm_yday - 1 + float(timestamp.hour - 12) / 24)

    # equation of time in minutes
    equation_of_time = 229.18 * (
                    0.000075 \
                    + 0.001868 * cos(gamma) \
                    - 0.032077 * sin(gamma) \
                    - 0.014615 * cos(2 * gamma) \
                    - 0.040849 * sin(2 * gamma)
                    )

    # solar declination in radians
    declination = 0.006918 - 0.399912 * cos(gamma) + 0.070257 * sin(gamma) \
           - 0.006758 * cos(2 * gamma) + 0.000907 * sin(2 * gamma) \
           - 0.002697 * cos(3 * gamma) + 0.00148 * sin(3 * gamma)
    
    # time offset in minutes ?
    timezone_offset = timestamp.utcoffset().total_seconds() / 3600
    time_offset = equation_of_time + 4 * longitude - 60 * timezone_offset

    # the true solar time in minutes
    true_solar_time = timestamp.hour * 60 + timestamp.minute + timestamp.second / 60 + time_offset
    
    # the solar hour angle (in degrees)
    hour_angle = true_solar_time / 4 - 180
    
    # # Calculate the solar zenith angle (in radians)
    # cos_phi = sin(latitude) * sin(declination) + cos(latitude) * cos(decl) * cos(radians(h))
    # phi = acos(cos_phi)
    
    # # Calculate the solar azimuth (in radians)
    # cos_theta = (-sin(latitude_rad) * cos(phi) - sin(decl)) / (cos(latitude_rad) * sin(phi))
    # theta = pi - acos(cos_theta)
    
    # hour angle at sunrise/sunset (in degrees)
    hour_angle_ss = np.degrees(acos(cos(np.radians(90.833)) / (cos(latitude) * cos(declination)) - tan(latitude) * tan(declination)))
    
    # the UTC time of sunrise and sunset (in minutes)
    sunrise = 720 - 4 * (longitude + hour_angle_ss) - equation_of_time
    sunset = 720 - 4 * (longitude - hour_angle_ss) - equation_of_time
    
    # Calculate solar noon in minutes
    solar_noon = 720 - 4 * longitude - equation_of_time
    
    # Convert minutes to datetime objects
    # sunrise_time = datetime.combine(timestamp.date(), datetime_time(0)) + timedelta(minutes=sunrise)
    # sunset_time = datetime.combine(timestamp.date(), datetime_time(0)) + timedelta(minutes=sunset)
    solar_noon_time = datetime.combine(timestamp.date(), datetime_time(0)) + timedelta(minutes=solar_noon)
    solar_noon_time = solar_noon_time.replace(tzinfo=pytz.UTC)
    solar_noon_time = solar_noon_time.astimezone(timezone)

    local_solar_time = timestamp - solar_noon_time
    decimal_hours = local_solar_time.total_seconds() / 3600

    # return sunrise_time, sunset_time, solar_noon_time
    # return solar_noon_time
    if verbose:
        typer.echo(f'Local solar time: {local_solar_time}')
    return decimal_hours, 'decimal hours?'


def calculate_solar_time_eot(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians, min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians, min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_datetime)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Timezone',
            callback=ctx_convert_to_timezone)] = None,
        days_in_a_year: Annotated[float, typer.Option(
            help='Days in a year')] = 365.25,
        perigee_offset: Annotated[float, typer.Option(
            help='Perigee offset')] = 0.048869,
        eccentricity: Annotated[float, typer.Option(
            help='Eccentricity')] = 0.01672,
        time_offset_global: Annotated[float, typer.Option(
            help='Global time offset')] = 0,
        hour_offset: Annotated[float, typer.Option(
            help='Hour offset')] = 0,
):
    """Calculate the solar time.

    Convert this one to use Milne's_ equation of time?

    1. Map the day of the year onto the circumference of a circle, essentially
    converting the day of the year into radians.

    2. Approximate empirically the equation of time, which accounts for the
    elliptical shape of Earth's orbit and the tilt of its axis.

    3. Calculate the solar time by adding the current hour of the year, the
    time offset from the equation of time, and the hour offset (likely a
    longitude-based correction).

    Notes
    -----
    _Milne

    @article{Milne1921,
        doi = {10.2307/3604631},
        year = 1921,
        publisher = {Cambridge University Press ({CUP})},
        volume = {10},
        number = {155},
        pages = {372--375},
        author = {R. M. Milne},
        title = {593. Note on the Equation of Time},
        journal = {The Mathematical Gazette}
    }
    """
    year = timestamp.year
    start_of_year = datetime(year=year, month=1, day=1, tzinfo=timestamp.tzinfo)
    hour_of_year = int((timestamp - start_of_year).total_seconds() / 3600)
    day_of_year = timestamp.timetuple().tm_yday
    day_of_year_in_radians = double_numpi * day_of_year / days_in_a_year  
    time_offset = - 0.128 * np.sin(day_of_year_in_radians - perigee_offset) - eccentricity * np.sin(2 * day_of_year_in_radians + 0.34383)

    # set `image_offset` for `hour_offset`
    image_offset = get_image_offset(longitude, latitude)

    # set `hour_offset` for `solar_time`
    hour_offset = time_offset_global + longitude / 15 + image_offset

    solar_time = hour_of_year % 24 + time_offset + hour_offset
    
    return solar_time, 'decimal hours?'


def calculate_solar_time_pvgis(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        latitude: Annotated[Optional[float], typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            callback=attach_timezone)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Timezone',
            callback=ctx_convert_to_timezone)] = None,
        days_in_a_year: float = 365.25,
        perigee_offset: float = 0.048869,
        eccentricity: float = 0.165,  # from the C code
        time_slot_offset_global: float = 0,
) -> float:
    """Calculate the solar time.

    1. Map the day of the year onto the circumference of a circle, essentially
    converting the day of the year into radians.

    2. Approximate empirically the equation of time, which accounts for the
    elliptical shape of Earth's orbit and the tilt of its axis.

    3. Calculate the solar time by adding the current hour of the year, the
    time offset from the equation of time, and the hour offset (likely a
    longitude-based correction).

    Returns
    -------
    solar_time: float
        The solar time in decimal hours
    """
    year = timestamp.year
    start_of_year = datetime(year=year, month=1, day=1, tzinfo=timestamp.tzinfo)
    day_of_year = timestamp.timetuple().tm_yday
    day_of_year_in_radians = double_numpi * day_of_year / days_in_a_year  
    hour_of_year = int((timestamp - start_of_year).total_seconds() / 3600)
    hour_of_day = hour_of_year % 24  # integer

    # approximation like the Equation of Time?!
    time_offset = - 0.128 \
                  * np.sin(day_of_year_in_radians - perigee_offset) \
                  - eccentricity \
                  * np.sin(2 * day_of_year_in_radians + 0.34383)

    # Complicated implementation borrowed from SPECMAGIC!
    image_offset = get_image_offset(longitude, latitude)  # for `hour_offset`

    # adding longitude to UTC produces mean solar time!
    hour_offset = time_slot_offset_global + longitude / 15 + image_offset  # for `solar_time`
    solar_time = hour_of_day + time_offset + hour_offset
    
    return solar_time, 'decimal hours?'


def calculate_solar_time(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians, min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians, min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp', default_factory=now_datetime)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Specify timezone (e.g., "Europe/Athens"). Use \'local\' to use the system\'s time zone',
            callback=ctx_convert_to_timezone)] = None,
        model: Annotated[SolarTimeModels, typer.Option(
            '-m',
            '--model',
            help="Model to calculate solar position",
            show_default=True,
            show_choices=True,
            case_sensitive=False)] = SolarTimeModels.skyfield,
        days_in_a_year: Annotated[float, typer.Option(
            help='Days in a year')] = 365.25,
        perigee_offset: Annotated[float, typer.Option(
            help='Perigee offset')] = 0.048869,
        eccentricity: Annotated[float, typer.Option(
            help='Eccentricity')] = 0.01672,
        time_offset_global: Annotated[float, typer.Option(
            help='Global time offset')] = 0,
        hour_offset: Annotated[float, typer.Option(
            help='Hour offset')] = 0,
        ):
    """
    """
    # if local and timestamp is not None and timezone is not None:
    #     timestamp = timezone.localize(timestamp)

    if model.value == SolarTimeModels.skyfield:

        solar_time, units = calculate_solar_time_skyfield(
            longitude,
            latitude,
            timestamp,
            timezone,
            )

    if model.value == SolarTimeModels.ephem:

        solar_time, units = calculate_solar_time_ephem(
            longitude,
            latitude,
            timestamp,
            timezone,
            )

    if model.value == SolarTimeModels.noaa:

        solar_time, units = calculate_solar_time_noaa(
            longitude,
            latitude,
            timestamp,
            timezone,
            )

    if model.value == SolarTimeModels.eot:

        solar_time, units = calculate_solar_time_eot(
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

    if model.value == SolarTimeModels.pvgis:

        solar_time, units = calculate_solar_time_pvgis(
            longitude,
            latitude,
            timestamp,
            timezone,
            )

    return solar_time, units


def calculate_hour_angle(
        solar_time: Annotated[float, typer.Argument(
            help='The solar time in decimal hours on a 24 hour base',
            callback=convert_hours_to_seconds)],
        output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar geometry variables (degrees or radians)")] = 'radians',
        ):
    """Calculate the hour angle 'ω = (ST / 3600 - 12) * 15 * 0.0175'
    
    Parameters
    ----------

    solar_time: float
        The solar time (ST) is a calculation of the passage of time based on the
        position of the Sun in the sky. It is expected to be decimal hours in a
        24 hour format and measured internally in seconds. 

    Returns
    --------

    hour_angle: float
        Hour angle is the angle (ω) at any instant through which the earth has
        to turn to bring the meridian of the observer directly in line with the
        sun's rays measured in radian.
    """
    # `solar_time` here received in seconds!
    hour_angle = (solar_time / 3600 - 12) * 15 * 0.0175
    hour_angle = convert_to_degrees_if_requested(
            hour_angle,
            output_units,
            )
    return hour_angle


@app.callback()
def calculate_hour_angle_sunrise(
        latitude: Annotated[Optional[float], typer.Argument(
            min=-90, max=90)],
        surface_tilt: Annotated[Optional[float], typer.Argument(
            min=0, max=90)] = 0,
        solar_declination: Annotated[Optional[float], typer.Argument(
            min=-90, max=90)] = 180,
        output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar geometry variables (degrees or radians)")] = 'radians',
        ) -> float:
    """Calculate the hour angle (ω) at sunrise and sunset

    Hour angle = acos(-tan(Latitude Angle-Tilt Angle)*tan(Declination Angle))

    The hour angle (ω) at sunrise and sunset measures the angular distance
    between the sun at the local solar time and the sun at solar noon.

    ω = acos(-tan(Φ-β)*tan(δ))

    Parameters
    ----------

    latitude: float
        Latitude (Φ) is the angle between the sun's rays and its projection on the
        horizontal surface measured in radians

    surface_tilt: float
        Surface tilt (or slope) (β) is the angle between the inclined surface
        (slope) and the horizontal plane.

    solar_declination: float
        Solar declination (δ) is the angle between the equator and a line drawn
        from the centre of the Earth to the centre of the sun measured in
        radians.

    Returns
    -------
    hour_angle: float
        Hour angle (ω) is the angle at any instant through which the earth has
        to turn to bring the meridian of the observer directly in line with the
        sun's rays measured in radian.
    """
    hour_angle = acos(
            -tan(
                latitude - surface_tilt
                )
            *tan(solar_declination)
            )
    hour_angle = convert_to_degrees_if_requested(
            hour_angle,
            output_units,
            )
    return hour_angle


if __name__ == "__main__":
    typer.run(main)
