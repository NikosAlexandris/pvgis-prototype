import typer
from typing import Annotated
from typing import Optional
from typing import Tuple
from ..utilities.timestamp import convert_hours_to_seconds
from ..utilities.conversions import convert_to_degrees_if_requested
from math import pi
from math import acos
from math import tan

from pvgisprototype.api.input_models import HourAngleInput
from pvgisprototype.api.input_models import HourAngleSunriseInput


def calculate_hour_angle(
        input: HourAngleInput,
        ) -> Tuple[float, str]:
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
    """
    # `solar_time` here received in seconds!
    # hour_angle = (solar_time / 3600 - 12) * 15 * 0.0175
    hour_angle = (input.solar_time / 3600 - 12) * 15 * pi / 180
    hour_angle = convert_to_degrees_if_requested(
            hour_angle,
            input.angle_output_units,
            )
    return (
        hour_angle,
        input.angle_output_units,
        )



def calculate_hour_angle_sunrise(
        input: HourAngleSunriseInput,
        ) -> Tuple[float, str]:
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
    hour_angle = acos(
            -tan(
                input.latitude - input.surface_tilt
                )
            *tan(input.solar_declination)
            )
    hour_angle = convert_to_degrees_if_requested(
            hour_angle,
            input.angle_output_units,
            )
    return (
        hour_angle,
        input.angle_output_units,
        )


if __name__ == "__main__":
    typer.run(main)
