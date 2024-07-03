from datetime import datetime, timedelta
from math import pi
import ephem
from log import logger

from pvgisprototype import Latitude, Longitude
from pvgisprototype.validation.functions import (
    CalculateSolarTimeEphemInputModel,
    validate_with_pydantic,
)


@validate_with_pydantic(CalculateSolarTimeEphemInputModel)
def calculate_solar_time_ephem(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: str = None,
    verbose: int = 0,
) -> datetime:
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
    # Handle Me during input validation? -------------------------------------
    if timezone != timestamp.tzinfo:
        try:
            timestamp = timestamp.astimezone(timezone)
        except Exception as e:
            logger.warning(f"Error setting tzinfo for timestamp = {timestamp}: {e}")
    # Handle Me during input validation? -------------------------------------

    observer = ephem.Observer()
    observer.date = timestamp
    observer.lon = longitude.degrees
    observer.lat = latitude.degrees
    sidereal_time = observer.sidereal_time()

    sun = ephem.Sun()  # a Sun object
    sun.compute(observer)  # sun position for observer's location and time
    # sun_right_ascension = sun.ra

    # hour_angle = sidereal_time - sun_right_ascension
    hour_angle = sun.ha

    # ------------------------------------------------------------------------
    # Calculate the start of a new (solar) day at 0:00 hrs : `base_date`
    reference_date = round(observer.date)
    if reference_date > observer.date:
        base_date = reference_date - 1.5
    else:
        base_date = reference_date - 0.5

    # mean solar time = UTC + longitude | solar time = mean solar time + equation of time
    mean_solar_time = ephem.date(observer.date + (observer.lon / pi * 12) * ephem.hour)
    hour, minute, second = mean_solar_time.tuple()[3:]
    # mean_solar_time_decimal_hours = (
    #     hour + minute / 60 + second / 3600
    # )  # to decimal hours

    # solar time = hour angle + 12 hrs
    solar_time_alternative = ephem.date(
        base_date + (hour_angle + ephem.hours("12:00")) / (2 * pi)
    )
    hour, minute, second = solar_time_alternative.tuple()[3:]
    # solar_time_alternative_decimal_hours = hour + minute / 60 + second / 3600
    # ------------------------------------------------------------------------

    # norm -> normalise to 24h
    solar_time_hours = ephem.hours(hour_angle + ephem.hours("12:00")).norm
    solar_time_decimal_hours = (
        solar_time_hours * 24 / pi / 2
    )  # convert to decimal hours
    solar_time_datetime = timestamp + timedelta(
        hours=solar_time_decimal_hours
    )  # FIXME: solar_time_hours or solar_time_decimal_hours ?

    if verbose:
        logger.info(f"Local sidereal time: {sidereal_time}")
        logger.info(f"Sun right ascension: {sun.ra}")
        logger.info(f"Hour angle: {hour_angle}")
        logger.info(f"Sun transit: {ephem.localtime(observer.date)}")
        logger.info(f"Mean solar time: {mean_solar_time}")

    return solar_time_datetime
