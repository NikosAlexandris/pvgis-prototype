#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
from pandas import Timestamp
from math import isfinite
from typing import Tuple

from skyfield.api import load, wgs84

from pvgisprototype import (
    Latitude,
    Longitude,
    SolarAltitude,
    SolarAzimuth,
    SolarDeclination,
    SolarHourAngle,
)
from pvgisprototype.algorithms.skyfield.function_models import (
    CalculateSolarPositionSkyfieldInputModel,
)
from pvgisprototype.constants import RADIANS
from pvgisprototype.validation.functions import (
    CalculateSolarAltitudeAzimuthSkyfieldInputModel,
    SolarHourAngleSkyfieldInput,
    validate_with_pydantic,
)


@validate_with_pydantic(CalculateSolarPositionSkyfieldInputModel)
def calculate_solar_position_skyfield(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: Timestamp,
):
    """Calculate sun position above the local horizon using Skyfield.

    Returns
    -------
    solar_altitude:
        Altitude measures the angle above or below the horizon. The
        zenith is at +90°, an object on the horizon’s great circle is at 0°,
        and the nadir beneath your feet is at −90°.

    solar_azimuth:
        Azimuth measures the angle around the sky from the north pole: 0° means
        exactly north, 90° is east, 180° is south, and 270° is west.

    Notes
    -----

    For the implementation, see also:
    https://techoverflow.net/2022/06/19/how-to-compute-position-of-sun-in-the-sky-in-python-using-skyfield/

    Factors influencing the accuracy of the calculation using Skyfield:

    - Skyfield considers:

        - The slight shift in position caused by light speed
        - The very very slight shift in position caused by earth’s gravity

    - Skyfield does not consider:

        - Atmospheric distortions shifting the sun’s position
        - The extent of the sun’s disk causing the sun to emanate not from a
          point but apparently from an area

    Notes
    -----

    To consider:

    - https://rhodesmill.org/skyfield/almanac.html#elevated-vantage-points
    - The `Time` class in Skyfield (i.e. `timescale()`) only uses UTC for input
      and output
    - https://rhodesmill.org/skyfield/time.html#utc-and-your-timezone
    - https://rhodesmill.org/skyfield/time.html#utc-and-leap-seconds
    """
    # # Handle Me during input validation? -------------------------------------
    # try:
    #     timestamp = timezone.localize(timestamp)
    # except Exception:
    #     logging.warning(f'tzinfo already set for timestamp = {timestamp}')
    # # Handle Me during input validation? -------------------------------------
    planets = load("de421.bsp")
    sun = planets["Sun"]
    earth = planets["Earth"]
    location = wgs84.latlon(latitude.degrees, longitude.degrees)
    timescale = load.timescale()
    requested_timestamp = timescale.from_datetime(timestamp)
    # sun position seen from observer location
    # sun position seen from observer location
    solar_position = (earth + location).at(requested_timestamp).observe(sun).apparent()

    return solar_position


@validate_with_pydantic(CalculateSolarAltitudeAzimuthSkyfieldInputModel)
def calculate_solar_altitude_azimuth_skyfield(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: Timestamp,
) -> Tuple[SolarAltitude, SolarAzimuth]:
    """Calculate sun position"""
    solar_position = calculate_solar_position_skyfield(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
    )
    solar_altitude, solar_azimuth, distance_to_sun = solar_position.altaz()
    solar_altitude = SolarAltitude(
        value=solar_altitude.radians,
        unit=RADIANS,
        solar_positioning_algorithm="Skyfield",
        solar_timing_algorithm="Skyfield",
    )
    solar_azimuth = SolarAzimuth(
        value=solar_azimuth.radians,
        unit=RADIANS,
        solar_positioning_algorithm="Skyfield",
        solar_timing_algorithm="Skyfield",
    )

    if (
        not isfinite(solar_azimuth.degrees)
        or not solar_azimuth.min_degrees
        <= solar_azimuth.degrees
        <= solar_azimuth.max_degrees
    ):
        raise ValueError(
            f"The calculated solar azimuth angle {solar_azimuth.degrees} is out of the expected range\
            [{solar_azimuth.min_degrees}, {solar_azimuth.max_degrees}] degrees"
        )

    if (
        not isfinite(solar_altitude.degrees)
        or not solar_altitude.min_degrees
        <= solar_altitude.degrees
        <= solar_altitude.max_degrees
    ):
        raise ValueError(
            f"The calculated solar altitude angle {solar_altitude.degrees} is out of the expected range\
            [{solar_altitude.min_degrees}, {solar_altitude.max_degrees}] degrees"
        )

    return solar_altitude, solar_azimuth  # , distance_to_sun


@validate_with_pydantic(SolarHourAngleSkyfieldInput)
def calculate_solar_hour_angle_declination_skyfield(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: Timestamp,
    timezone: str = None,
) -> Tuple[SolarHourAngle, SolarDeclination]:
    """Calculate the hour angle ω'

    Parameters
    ----------


    Returns
    --------

    hour_angle: float
        Hour angle is the angle (ω) at any instant through which the earth has
        to turn to bring the meridian of the observer directly in line with the
        sun's rays measured in radian.
    """
    solar_position = calculate_solar_position_skyfield(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
    )
    hour_angle, solar_declination, distance_to_sun = solar_position.hadec()

    hour_angle = SolarHourAngle(
        value=hour_angle.radians,
        unit=RADIANS,
        solar_positioning_algorithm="Skyfield",
        solar_timing_algorithm="Skyfield",
    )
    solar_declination = SolarDeclination(
        value=solar_declination.radians,
        unit=RADIANS,
        solar_positioning_algorithm="Skyfield",
        solar_timing_algorithm="Skyfield",
    )
    if (
        not isfinite(hour_angle.degrees)
        or not hour_angle.min_degrees <= hour_angle.degrees <= hour_angle.max_degrees
    ):
        raise ValueError(
            f"The calculated solar hour angle {hour_angle.degrees} is out of the expected range\
            [{hour_angle.min_degrees}, {hour_angle.max_degrees}] degrees"
        )
    if (
        not isfinite(solar_declination.degrees)
        or not solar_declination.min_degrees
        <= solar_declination.degrees
        <= solar_declination.max_degrees
    ):
        raise ValueError(
            f"The calculated solar declination angle {solar_declination.degrees} is out of the expected range\
            [{solar_declination.min_degrees}, {solar_declination.max_degrees}] degrees"
        )
    return hour_angle, solar_declination
