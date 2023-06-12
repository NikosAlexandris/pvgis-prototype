import typer
from typing_extensions import Annotated
import math


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"Approximate the solar declination for a day in the year",
)


# from: rsun_base.cpp
# function: com_declin(no_of_day)
@app.callback(invoke_without_command=True, no_args_is_help=True)
def calculate_solar_declination(
        day_of_year: int,
        days_in_a_year: float = 365.25,
        orbital_eccentricity: float = 0.03344,
        perigee_offset: float = 0.048869,
        output_units: Annotated[str, typer.Option(
            '-o',
            '--output-units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar declination (degrees or radians)")] = 'radians',
        ) -> float:
    """Approximate the sun's declination for a given day of the year.

    The solar declination is the angle between the Sun's rays and the
    equatorial plane of Earth. It varies throughout the year due to the tilt of
    the Earth's axis and is an important parameter in determining the seasons
    and the amount of solar radiation received at different latitudes.

    Parameters
    ----------
    day_of_year: int
        The day of the year (ranging from 1 to 365 or 366 in a leap year).

    Returns
    -------
    float
        The solar declination for the given day of the year.

    Notes
    -----

    - The function calculates the `proportion` of the way through the year (in
      radians), which is given by `(2 * pi * day_of_year) / 365.25`.

    - The `0.3978`, `1.4`, and `0.0355` are constants in the approximation
      formula, with the `0.0489` being an adjustment factor for the slight
      eccentricity of Earth's orbit.
  
    - Finally, the declination is negated (`declination = - declination`). This
      might be due to the coordinate system in use, where a negative
      declination means the sun is in the Southern Hemisphere. This would
      depend on the broader context of the program.

    - Please note that the formula used here is a simple approximation, and
      might not provide highly precise results. For more accurate calculations
      of solar position, comprehensive models like the Solar Position Algorithm
      (SPA) are typically used.
    """
    some_term = 2 * math.pi * day_of_year / days_in_a_year
    declination = math.asin(0.3978 * math.sin(some_term - 1.4 + orbital_eccentricity * math.sin(some_term - perigee_offset)))
    declination = - declination  # why? in the C source code: decl = - decl;
    if output_units == 'degrees':
        declination = math.degrees(declination)

    return declination


