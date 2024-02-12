from rich import print
from devtools import debug
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarHourAngleNOAAInput
from pvgisprototype.algorithms.noaa.function_models import CalculateSolarHourAngleTimeSeriesNOAAInput
from pvgisprototype import Longitude
from datetime import datetime
from pandas import DatetimeIndex
from typing import Optional
from zoneinfo import ZoneInfo
from pvgisprototype import SolarHourAngle
from pvgisprototype.algorithms.noaa.solar_time import calculate_true_solar_time_noaa
from pvgisprototype.algorithms.noaa.solar_time import calculate_true_solar_time_time_series_noaa
from math import pi
from math import isfinite
from pvgisprototype.api.utilities.timestamp import timestamp_to_minutes
import numpy as np
from pvgisprototype.constants import RADIANS
from pandas import DatetimeIndex
from cachetools import cached
from pvgisprototype.algorithms.caching import custom_hashkey



@validate_with_pydantic(CalculateSolarHourAngleNOAAInput)
def calculate_solar_hour_angle_noaa(
    longitude: Longitude,
    timestamp: datetime, 
    timezone: Optional[ZoneInfo] = None, 
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
    )
    true_solar_time_minutes = timestamp_to_minutes(true_solar_time)
    solar_hour_angle = (true_solar_time_minutes - 720) * (pi / 720)

    # Important ! ------------------------------------------------------------
    # If (hourangle < -180) Then hourangle = hourangle + 360
    if solar_hour_angle < -pi:
        solar_hour_angle += 2 * pi
    # ------------------------------------------------------------------------

    solar_hour_angle = SolarHourAngle(
        value=solar_hour_angle,
        unit=RADIANS,
        position_algorithm='NOAA',
        timing_algorithm='NOAA',
    )
    if (
        not isfinite(solar_hour_angle.degrees)
        or not solar_hour_angle.min_degrees <= solar_hour_angle.degrees <= solar_hour_angle.max_degrees
    ):
        raise ValueError(
            f"The calculated solar hour angle {solar_hour_angle.degrees} is out of the expected range\
            [{solar_hour_angle.min_degrees}, {solar_hour_angle.max_degrees}] degrees"
        )

    if verbose == 3:
        debug(locals())

    return solar_hour_angle


@cached(cache={}, key=custom_hashkey)
@validate_with_pydantic(CalculateSolarHourAngleTimeSeriesNOAAInput)
def calculate_solar_hour_angle_time_series_noaa(
    longitude: Longitude,
    timestamps: DatetimeIndex, 
    timezone: Optional[str] = None, 
    # angle_output_units: Optional[str] = RADIANS,
    verbose: int = 0,
) -> SolarHourAngle:
    """Calculate the solar hour angle in radians for a time series."""
    true_solar_time_series = calculate_true_solar_time_time_series_noaa(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
    )
    hours = true_solar_time_series.hour
    minutes = true_solar_time_series.minute
    seconds = true_solar_time_series.second
    true_solar_time_series_in_minutes = hours * 60 + minutes + seconds / 60
    solar_hour_angle_series = (true_solar_time_series_in_minutes - 720) * (np.pi / 720)

    if not np.all((-np.pi <= solar_hour_angle_series) & (solar_hour_angle_series <= np.pi)):
            # Identify the out-of-range values for a more informative error message
            out_of_range_values = solar_hour_angle_series[~((-np.pi <= solar_hour_angle_series) & (solar_hour_angle_series <= np.pi))]
            raise ValueError(f"The solar hour angle(s) {out_of_range_values} is/are out of the expected range [-π, π] radians!")

    from pvgisprototype.validation.hashing import generate_hash
    # solar_hour_angle_series_hash = generate_hash(solar_hour_angle_series)
    print(
        'SHA : calculate_solar_hour_angle_time_series_noaa() |',
        f"Data Type : [bold]{solar_hour_angle_series.dtype}[/bold] |",
        # f"Output Hash : [code]{solar_hour_angle_series_hash}[/code]",
    )

    solar_hour_angle_series = SolarHourAngle(
        value=np.array(solar_hour_angle_series),
        unit=RADIANS,
        position_algorithm='NOAA',
        timing_algorithm='NOAA',
    )

    if verbose == 3:
        debug(locals())

    return solar_hour_angle_series
