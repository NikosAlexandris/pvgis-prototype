import typer
from typing import Annotated
from typing import Optional
from typing import NamedTuple
from ...utilities.timestamp import convert_hours_to_seconds
from pvgisprototype.api.named_tuples import generate


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
        )-> NamedTuple:
    """Calculate the hour angle ω'

    ω = (ST / 3600 - 12) * 15 * pi / 180

    Parameters
    ----------

    hour_angle: float
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
    # hour_angle = (solar_time / 3600 - 12) * 15 * 0.0175
    hour_angle = (solar_time / 3600 - 12) * 15 * pi / 180
    hour_angle = generate('hour_angle', (hour_angle, output_units))
    # hour_angle = convert_to_degrees_if_requested(
    #         hour_angle,
    #         output_units,
    #         )
    return hour_angle


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
        ) -> NamedTuple:
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
    hour_angle_sunrise = generate(
        'hour_angle_sunrise',
        (hour_angle_sunrise_value, output_units),
    )
    hour_angle_sunrise = convert_to_degrees_if_requested(
            hour_angle_sunrise,
            output_units,
            )
    return hour_angle_sunrise


if __name__ == "__main__":
    typer.run(main)
