from devtools import debug
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.algorithms.noaa.function_models import CalculateSolarHourAngleNOAAInput
from pvgisprototype import Longitude
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo
from pvgisprototype import SolarHourAngle
from .solar_time import calculate_true_solar_time_noaa
from math import pi
from pvgisprototype.algorithms.noaa.function_models import CalculateSolarHourAngleTimeSeriesNOAAInput
from typing import Union
from typing import Sequence
from pvgisprototype.api.utilities.timestamp import timestamp_to_minutes
import numpy as np


@validate_with_pydantic(CalculateSolarHourAngleNOAAInput)
def calculate_solar_hour_angle_noaa(
    longitude: Longitude,
    timestamp: datetime, 
    timezone: Optional[ZoneInfo] = None, 
    time_output_units: str = 'minutes',
    angle_output_units: str = 'radians',
    verbose: int = 0,
) -> SolarHourAngle:
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

    Returns
    -------
    float: The solar hour angle

    Notes
    -----

    In the "original" equation, the solar hour angle is measured in degrees.

        `hour_angle = true_solar_time / 4 - 180`
        
        which is the same as

        `hour_angle = true_solar_time * 0.25 - 180`

    In the present implementation, we calculate the solar hour angle directly
    to radians. A circle is 360 degrees, dividing by 1440 minutes in a day,
    each minute equals to 0.25 radians.
    """
    true_solar_time = calculate_true_solar_time_noaa(
        longitude=longitude,
        timestamp=timestamp,
        timezone=timezone,
        time_output_units='minutes',                    # NOTE gounaol: Should not be None
    )  # in minutes

    true_solar_time_minutes = timestamp_to_minutes(true_solar_time)
    solar_hour_angle = (true_solar_time_minutes - 720) * (pi / 720)

    # Important ! ------------------------------------------------------------
    # If (hourangle < -180) Then hourangle = hourangle + 360
    if solar_hour_angle < -pi:
        solar_hour_angle += 2 * pi
    # ------------------------------------------------------------------------

    if angle_output_units == 'radians' and not -pi <= solar_hour_angle <= pi:
        raise ValueError(f'The calculated hour angle {solar_hour_angle} is out of the expected range [{-pi}, {pi}] radians')

    # elif angle_output_units == 'degrees' and not -180 <= solar_hour_angle <= 180:
    #     raise ValueError("The hour angle in degrees must be within the range [-180, 180] degrees")

    solar_hour_angle = SolarHourAngle(
        value=solar_hour_angle,
        unit=angle_output_units,
    )

    if verbose == 3:
        debug(locals())
    return solar_hour_angle


@validate_with_pydantic(CalculateSolarHourAngleTimeSeriesNOAAInput)
def calculate_solar_hour_angle_time_series_noaa(
    longitude: Longitude,
    timestamps: Sequence[datetime], 
    timezone: Optional[str] = None, 
    time_output_units: Optional[str] = 'minutes',
    angle_output_units: Optional[str] = 'radians',
    verbose: int = 0,
):
    """Calculate the solar hour angle in radians for a time series."""
    solar_hour_angle_series = []
    
    for timestamp in timestamps:
        true_solar_time = calculate_true_solar_time_noaa(
            longitude=longitude,
            timestamp=timestamp,
            timezone=timezone,
            time_output_units=time_output_units,
        )  # in minutes

        true_solar_time_minutes = timestamp_to_minutes(true_solar_time)
        solar_hour_angle = (true_solar_time_minutes - 720) * (pi / 720)

        if angle_output_units == 'radians' and not -pi <= solar_hour_angle <= pi:
            raise ValueError("The hour angle in radians must range within [-π, π]")

        solar_hour_angle_obj = SolarHourAngle(
            value=solar_hour_angle,
            unit='radians',
        )

        solar_hour_angle_series.append(solar_hour_angle_obj)

    if verbose == 3:
        debug(locals())
    return np.array(solar_hour_angle_series, dtype=object)
