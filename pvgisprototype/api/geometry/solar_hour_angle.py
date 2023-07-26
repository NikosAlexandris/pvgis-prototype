import typer
from typing import Annotated
from typing import Optional
from ..utilities.timestamp import convert_hours_to_seconds
from ..utilities.conversions import convert_to_degrees_if_requested
from math import pi


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f":timer_clock:  Calculate the hour angle time for a location and moment",
)


def calculate_hour_angle(
        solar_time: time,
        output_units: str = 'radians',
        ):
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

    Notes
    -----

    In PVGIS :
        hour_angle = (solar_time / 3600 - 12) * 15 * 0.0175

        which means:
        - solar time is expected in seconds
        - conversion to radians `* 0.0175` replaced by `pi / 180`

    In this function:
    """
    hour_angle = (solar_time / 3600 - 12) * 15 * pi / 180
    return hour_angle, output_units


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
