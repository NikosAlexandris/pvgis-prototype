from .noaa_models import CalculateSolarHourAngleNOAAInput
from .decorators import validate_with_pydantic
from datetime import datetime
from typing import Optional
from .noaa_models import Longitude_in_Radians
from .solar_time import calculate_true_solar_time_noaa
from math import pi
from typing import NamedTuple
from pvgisprototype.api.named_tuples import generate
from pvgisprototype.api.utilities.timestamp import timestamp_to_minutes


@validate_with_pydantic(CalculateSolarHourAngleNOAAInput)
def calculate_solar_hour_angle_noaa(
        longitude: Longitude_in_Radians,
        timestamp: datetime, 
        timezone: Optional[str], 
        time_output_units: Optional[str] = 'minutes',
        angle_output_units: Optional[str] = 'radians',
        ) -> NamedTuple:
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
    true_solar_time = calculate_true_solar_time_noaa(
        longitude, timestamp, timezone, time_output_units
    )  # in minutes

    solar_hour_angle = (true_solar_time.value - 720) * (pi / 720)       # FIXME; Calculation between datetime and float

    if angle_output_units == 'radians' and not -pi <= solar_hour_angle <= pi:
        raise ValueError("The hour angle in radians must be within the range [-π, π]")

    # elif angle_output_units == 'degrees' and not -180 <= solar_hour_angle <= 180:
    #     raise ValueError("The hour angle in degrees must be within the range [-180, 180] degrees")

    solar_hour_angle = generate(
        'solar_hour_angle',
        (solar_hour_angle, angle_output_units)
    )
    return solar_hour_angle

