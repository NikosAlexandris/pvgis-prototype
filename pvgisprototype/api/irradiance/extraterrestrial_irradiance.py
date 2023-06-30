import typer
from typing_extensions import Annotated
import math
import numpy as np


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"Calculate the extraterrestial_irradiance for a day in the year",
)


@app.callback(invoke_without_command=True, no_args_is_help=True)
def calculate_extraterrestrial_irradiance(
        day_of_year: float,
        days_in_a_year: float = 365.25,
        solar_constant: Annotated[float, typer.Argument(
            help="The solar constant is a flux density measuring mean solar electromagnetic radiation (total solar irradiance) per unit area (perpendicular to the rays) arriving at the top of the Earth's atmosphere (about 1360.8 W/m2) one astronomical unit (au) away from the Sun (roughly the distance from the Sun to the Earth).",
            min=1360)] = 1360.8,
        orbital_eccentricity: float = 0.03344,
        perigee_offset: float = 0.048869,
        ) -> float:
    """Calculate the extraterrestial_irradiance for the given day of the year.

    The solar constant is the amount of solar electromagnetic radiation
    received at the outer atmosphere of Earth in a unit area perpendicular to
    the rays of the Sun, on a day when Earth is at its mean distance from the
    Sun. Its approximate value is around 1360.8 +/-0.5 W/m^2
    (:cite:`p:Kopp2011`) but varies slightly
    throughout the year due to the Earth's elliptical orbit.

    Parameters
    ----------
    day_of_year : int, float
        Number of Julian day of year counted from 1 (January 1) to 365 or 366
        (December 31).

    solar_constant: float
        1360.8 W/m^2
    
    days_in_a_year: float
        365.25

    perigee_offset: float
        0.048869 (in angular units). The earth's closest position to the sun is
        January 2 at 8:18pm or day number 2.8408. In angular units :
        2*pi * 2.8408 / 365.25 = 0.048869.

    orbital_eccentricity: float
        For Earth this is currently about 0.01672, and so the distance to the
        sun varies by +/- 0.01672 from the mean distance (1AU). Thus, the
        amplitude of the function over the year is: 2*eccentricity = 0.03344.

    Returns
    -------
    extraterrestial_irradiance: float
        The extraterrestial irradiance for the given day of the year.

    Notes
    -----

    This function came first from a direct translation from PVGIS' rsun3 source
    code:

      - from file: rsun_base.cpp
      - function: com_sol_const(int no_of_day)

    The following text considers comments from GRASS-GIS' `r.sun` module.

    The `position_of_earth` in its orbit around the Sun is calculated by
    multiplying the number of the day in the year by 2*pi (which is the full
    circumference of a circle in radians), and dividing it by 365.25 (the
    average number of days in a year, accounting for leap years). The resulting
    value is an angle in radians that represents the `position_of_earth` in its
    orbit.

    The `solar_constant` is calculated by adjusting the average (or base) value
    of 1360.8 W/m^2 based on the `position_of_earth`. The `adjustment_factor`
    `0.03344 * cos(position_of_earth - 0.048869)`, accounts for the slight
    elliptical shape of the Earth's orbit : the solar constant is a bit higher
    when the Earth is closer to the Sun (perihelion) and a bit lower when it's
    farther away (aphelion).

    The Earth is closest to the Sun (Perigee) on about January 3rd, and
    furthest from it (Apogee) about July 6th. The 1360.8 W/m^2 solar constant
    is at the average 1AU distance. However, on January 3 it gets up to around
    1412.71 W/m^2 and on July 6 it gets down to around 1321 W/m^2. This value
    is for what hits the top of the atmosphere before any energy is attenuated.
    """
    position_of_earth = 2 * math.pi * day_of_year / days_in_a_year
    distance_correction_factor = 1 + orbital_eccentricity * math.cos(position_of_earth - perigee_offset)
    extraterrestial_irradiance = solar_constant * distance_correction_factor

    typer.echo(f'Extraterrestrial irradiance: {extraterrestial_irradiance}')
    return extraterrestial_irradiance
