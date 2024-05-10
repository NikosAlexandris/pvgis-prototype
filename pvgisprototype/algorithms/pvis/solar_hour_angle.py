from devtools import debug
from math import isfinite
from datetime import datetime

import numpy
from pvgisprototype import SolarHourAngle
from pvgisprototype import HourAngleSunrise
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pandas import DatetimeIndex
from zoneinfo import ZoneInfo
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarHourAnglePVISInputModel
from pvgisprototype.validation.functions import CalculateEventHourAnglePVISInputModel
from pvgisprototype.api.utilities.timestamp import timestamp_to_minutes
from math import pi
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT


@validate_with_pydantic(CalculateSolarHourAnglePVISInputModel)
def calculate_solar_hour_angle_pvis(
    solar_time:datetime,
)-> SolarHourAngle:
    """Calculate the hour angle ω'

    ω = (ST / 3600 - 12) * 15 * pi / 180

    Parameters
    ----------

    solar_time: float
        The solar time (ST) is a calculation of the passage of time based on the
        position of the Sun in the sky. It is expected to be decimal hours in a
        24 hour format and measured internally in seconds. 

    Returns
    --------

    hour_angle: float
        The solar hour angle (ω) is the angle at any instant through which the
        earth has to turn to bring the meridian of the observer directly in
        line with the sun's rays measured in radian.

    Notes
    -----
    If not mistaken, in PVGIS' C source code, the conversion function is:

        hour_angle = (solar_time / 3600 - 12) * 15 * 0.0175

        where the solar time was given in seconds.
    """
    true_solar_time_minutes = timestamp_to_minutes(solar_time)
    hour_angle = (true_solar_time_minutes / 60 - 12) * 15 * pi / 180
    hour_angle = SolarHourAngle(
        value=hour_angle,
        unit=RADIANS,
        position_algorithm='PVIS',
        timing_algorithm='PVIS',
    )
    if (
        not isfinite(hour_angle.degrees)
        or not hour_angle.min_degrees <= hour_angle.degrees <= hour_angle.max_degrees
    ):
        raise ValueError(
            f"The calculated solar hour angle {hour_angle.degrees} is out of the expected range\
            [{hour_angle.min_degrees}, {hour_angle.max_degrees}] degrees"
        )
    return hour_angle


def calculate_solar_hour_angle_time_series_pvis(
    longitude: Longitude,
    timestamps: DatetimeIndex, 
    timezone: ZoneInfo,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
)-> SolarHourAngle:
    """Calculate the hour angle ω'

    ω = (ST / 3600 - 12) * 15 * pi / 180

    Parameters
    ----------

    solar_time: float
        The solar time (ST) is a calculation of the passage of time based on the
        position of the Sun in the sky. It is expected to be decimal hours in a
        24 hour format and measured internally in seconds. 

    Returns
    --------

    hour_angle: float
        The solar hour angle (ω) is the angle at any instant through which the
        earth has to turn to bring the meridian of the observer directly in
        line with the sun's rays measured in radian.

    Notes
    -----
    If not mistaken, in PVGIS' C source code, the conversion function is:

        hour_angle = (solar_time / 3600 - 12) * 15 * 0.0175

        where the solar time was given in seconds.
    """
    from pvgisprototype.algorithms.noaa.solar_time import calculate_true_solar_time_time_series_noaa
    true_solar_time_series = calculate_true_solar_time_time_series_noaa(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    solar_hour_angle_series = (true_solar_time_series.minutes - 720.) * (numpy.pi / 720.)
    # if (
    #     not isfinite(hour_angle.degrees)
    #     or not hour_angle.min_degrees <= hour_angle.degrees <= hour_angle.max_degrees
    # ):
    #     raise ValueError(
    #         f"The calculated solar hour angle {hour_angle.degrees} is out of the expected range\
    #         [{hour_angle.min_degrees}, {hour_angle.max_degrees}] degrees"
    #     )
    return SolarHourAngle(
        value=solar_hour_angle_series,
        unit=RADIANS,
        position_algorithm='PVIS',
        timing_algorithm='PVIS',
    )


@validate_with_pydantic(CalculateEventHourAnglePVISInputModel)
def calculate_event_hour_angle_pvis(  # rename to: calculate_event_hour_angle
        latitude: Latitude,
        surface_tilt: float = 0,
        solar_declination: float = 0,
    ) -> HourAngleSunrise:
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
    hour_angle_sunrise: float
        Hour angle (ω) is the angle at any instant through which the earth has
        to turn to bring the meridian of the observer directly in line with the
        sun's rays measured in radian.
    """
    hour_angle_sunrise_value = acos(
            -tan(
                latitude - surface_tilt
                )
            *tan(solar_declination)
            )
    hour_angle_sunrise = HourAngleSunrise(
        value=hour_angle_sunrise_value,
        unit=RADIANS,
    )

    return hour_angle_sunrise


if __name__ == "__main__":
    typer.run(main)
