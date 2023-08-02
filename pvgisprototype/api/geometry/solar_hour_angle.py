import typer
from typing import Annotated
from typing import Optional
from ..utilities.timestamp import convert_hours_to_seconds
from ..utilities.conversions import convert_to_degrees_if_requested
from datetime import time
from math import radians
from math import acos
from math import tan

from pvgisprototype.api.data_classes import HourAngle
from pvgisprototype.api.data_classes import HourAngleSunrise
from pvgisprototype.api.data_classes import Latitude

from pvgisprototype.api.input_models import HourAngleInput
from pvgisprototype.api.input_models import HourAngleSunriseInput

from pvgisprototype.api.decorators import validate_with_pydantic
from ..utilities.timestamp import timestamp_to_decimal_hours


@validate_with_pydantic(HourAngleInput, expand_args=True)
def calculate_hour_angle(
            solar_time: time,
            angle_output_units: str = 'radians',
        ) -> HourAngle:
    """Calculate the hour angle ω'

    ω = (ST / 3600 - 12) * 15 * pi / 180

    Parameters
    ----------

    solar_time : float
        The solar time (ST) is a calculation of the passage of time based on the
        position of the Sun in the sky. It is expected to be decimal hours in a
        24 hour format and measured internally in seconds. 
    
    output_units: str, optional
        Angle output units (degrees or radians).

    Returns
    -------

    Tuple(float, str)
        Tuple containg (hour_angle, units). Hour angle is the angle (ω) at any
        instant through which the earth has to turn to bring the meridian of the
        observer directly in line with the sun's rays measured in radian.

    Notes
    -----

    In PVGIS :
        hour_angle = (solar_time / 3600 - 12) * 15 * 0.0175

        which means:
        - solar time is expected in seconds
        - conversion to radians `* 0.0175` replaced by `pi / 180`

    In this function:
    """
    # `solar_time` here received in seconds!
    # hour_angle = (solar_time / 3600 - 12) * 15 * 0.0175
    solar_time_decimal_hours = timestamp_to_decimal_hours(solar_time)
    hour_angle = radians(15) * (solar_time_decimal_hours - 12)

    hour_angle = HourAngle(value=hour_angle, unit='radians')
    hour_angle = convert_to_degrees_if_requested(hour_angle, angle_output_units)
    return hour_angle


@validate_with_pydantic(HourAngleSunriseInput, expand_args=True)
def calculate_hour_angle_sunrise(
        latitude: Latitude,
        surface_tilt: float = 0,
        solar_declination: float = 0,
        angle_output_units: str = 'radians',
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

    Tuple(float, str)
        Tuple containg (hour_angle, units). Hour angle (ω) is the angle at any
        instant through which the earth has to turn to bring the meridian of the
        observer directly in line with the sun's rays measured in radian.
    """
    hour_angle_sunrise = acos(
            -tan(
                latitude.value - surface_tilt.value
                )
            *tan(solar_declination.value)
            )
    hour_angle_sunrise = HourAngleSunrise(value=hour_angle_sunrise, unit='radians')
    hour_angle_sunrise = convert_to_degrees_if_requested(
        hour_angle_sunrise,
        angle_output_units,
        )
    return hour_angle_sunrise


if __name__ == "__main__":
    typer.run(main)
