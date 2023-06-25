import typer
from typing import Annotated
from typing import Optional
from enum import Enum
# from datetime import datetime
from datetime import datetime
import pytz
from tzlocal import get_localzone
import ephem
import numpy as np
from .constants import HOUR_ANGLE
from .constants import UNDEF
from .constants import double_numpi
from .constants import half_numpi
from .conversions import convert_to_radians
from .conversions import convert_to_degrees_if_requested
from .timestamp import now_datetime
from .timestamp import convert_to_timezone
from .timestamp import attach_timezone
from .timestamp import convert_hours_to_seconds
from .image_offset import get_image_offset
from math import cos
from math import tan 
from math import acos


class SolarTimeModels(str, Enum):
    eot = 'eot'
    ephem = 'ephem'
    pvgis = 'pvgis'


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"Calculate solar time for a location and moment in time",
)


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
            callback=convert_to_timezone)] = None,
        ):
    """
    """
    observer = ephem.Observer()
    observer.date = timestamp
    observer.lon = longitude
    observer.lat = latitude
    sun=ephem.Sun()
    sun.compute(observer)
    hour_angle = observer.sidereal_time() - sun.ra

    return hour_angle


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
            callback=convert_to_timezone)] = None,
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
    start_of_year = datetime(year=year, month=1, day=1,
                                      tzinfo=timestamp.tzinfo)
    
    hour_of_year = int((timestamp - start_of_year).total_seconds() / 3600)
    day_of_year = timestamp.timetuple().tm_yday
    day_of_year_in_radians = double_numpi * day_of_year / days_in_a_year  
    
    time_offset = - 0.128 * np.sin(day_of_year_in_radians - perigee_offset) - eccentricity * np.sin(2 * day_of_year_in_radians + 0.34383)

    # set `image_offset` for `hour_offset`
    image_offset = get_image_offset(longitude, latitude)

    # set `hour_offset` for `solar_time`
    hour_offset = time_offset_global + longitude / 15 + image_offset

    solar_time = hour_of_year % 24 + time_offset + hour_offset
    
    return solar_time


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
            callback=convert_to_timezone)] = None,
        days_in_a_year: float = 365.25,
        perigee_offset: float = 0.048869,
        eccentricity: float = 0.0165,  # from the C code
        time_slot_offset_global: float = 0,
):
    """Calculate the solar time.

    1. Map the day of the year onto the circumference of a circle, essentially
    converting the day of the year into radians.

    2. Approximate empirically the equation of time, which accounts for the
    elliptical shape of Earth's orbit and the tilt of its axis.

    3. Calculate the solar time by adding the current hour of the year, the
    time offset from the equation of time, and the hour offset (likely a
    longitude-based correction).
    """
    year = timestamp.year
    start_of_year = datetime(year=year, month=1, day=1,
                                      tzinfo=timestamp.tzinfo)
    
    day_of_year = timestamp.timetuple().tm_yday
    day_of_year_in_radians = double_numpi * day_of_year / days_in_a_year  
    hour_of_year = int((timestamp - start_of_year).total_seconds() / 3600)

    # set `time_offset` for `solar_time`
    time_offset = - 0.128 * np.sin(day_of_year_in_radians - perigee_offset) - eccentricity * np.sin(2 * day_of_year_in_radians + 0.34383)
    
    # set `image_offset` for `hour_offset`
    image_offset = get_image_offset(longitude, latitude)

    # set `hour_offset` for `solar_time`
    hour_offset = time_slot_offset_global + longitude / 15 + image_offset

    solar_time = hour_of_year % 24 + time_offset + hour_offset
    
    return solar_time


def calculate_solar_time(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians, min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians, min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_datetime)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Specify timezone (e.g., "Europe/Athens"). Use "local" to use the system\'s time zone',
            callback=convert_to_timezone)] = None,
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
        model: Annotated[SolarTimeModels, typer.Option(
            '-m',
            '--model',
            show_default=True,
            show_choices=True,
            case_sensitive=False,
            help="Model to calculate solar position")] = SolarTimeModels.ephem,
        ):
    """
    """
    # if local and timestamp is not None and timezone is not None:
    #     timestamp = timezone.localize(timestamp)

    if model.value == SolarTimeModels.ephem:

        solar_time = calculate_solar_time_ephem(
            longitude,
            latitude,
            timestamp,
            timezone,
            )

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

    if model.value == SolarTimeModels.pvgis:

        solar_time = calculate_solar_time_pvgis(
            longitude,
            latitude,
            timestamp,
            timezone,
            )

    return solar_time


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
