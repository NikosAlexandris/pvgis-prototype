import typer
from datetime import datetime
from math import pi
from math import sin
from math import asin
from ..utilities.conversions import convert_to_degrees_if_requested

from pvgisprototype.api.input_models import SolarDeclinationInput
from pvgisprototype.api.decorators import validate_with_pydantic


# @validate_with_pydantic(SolarDeclinationInput)
def calculate_solar_declination(input: SolarDeclinationInput) -> float:
    """Approximate the sun's declination for a given day of the year.

    The solar declination is the angle between the Sun's rays and the
    equatorial plane of Earth. It varies throughout the year due to the tilt of
    the Earth's axis and is an important parameter in determining the seasons
    and the amount of solar radiation received at different latitudes.

    The function calculates the `proportion` of the way through the year (in
    radians), which is given by `(2 * pi * day_of_year) / 365.25`.
    The `0.3978`, `1.4`, and `0.0355` are constants in the approximation
    formula, with the `0.0489` being an adjustment factor for the slight
    eccentricity of Earth's orbit.
  
    Parameters
    ----------
    day_of_year: int
        The day of the year (ranging from 1 to 365 or 366 in a leap year).

    Returns
    -------
    solar_declination: float
        The solar declination in radians for the given day of the year.

    Notes
    -----

    The equation used here is a simple approximation and bases upon a direct
    translation from PVGIS' rsun3 source code:

      - from file: rsun_base.cpp
      - function: com_declin(no_of_day)

    For more accurate calculations of solar position, comprehensive models like
    the Solar Position Algorithm (SPA) are typically used.
    """
    year = input.timestamp.year
    start_of_year = datetime(year=year, month=1, day=1)
    day_of_year = input.timestamp.timetuple().tm_yday
    day_angle = 2 * pi * day_of_year / input.days_in_a_year
    declination = asin(
            0.3978 * sin(
                day_angle - 1.4 + input.orbital_eccentricity * sin(
                    day_angle - input.perigee_offset
                    )
                )
            )
    declination = convert_to_degrees_if_requested(declination, input.angle_output_units)

    return declination
