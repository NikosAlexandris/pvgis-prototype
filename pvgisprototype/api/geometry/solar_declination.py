from devtools import debug
import typer
from typing import Annotated
from typing import Optional
import math
import numpy as np
from functools import partial
from datetime import datetime
from datetime import timezone
from datetime import timedelta
from ..utilities.timestamp import now_utc_datetimezone
from ..utilities.timestamp import convert_to_timezone
from ..utilities.timestamp import attach_timezone


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"Approximate the solar declination for a day in the year",
)


def convert_to_degrees_if_requested(angle: float, output_units: str) -> float:
    """Convert angle from radians to degrees if requested."""
    x = np.degrees(angle) if output_units == 'degrees' else angle
    return x


def convert_to_radians_if_requested(angle: float, output_units: str) -> float:
    """Convert angle from degrees to radians if requested."""
    return np.radians(angle) if output_units == 'radians' else angle


@app.callback(invoke_without_command=True, no_args_is_help=True)
def calculate_solar_declination(
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Timezone',
            callback=convert_to_timezone)] = None,
        days_in_a_year: float = 365.25,
        orbital_eccentricity: float = 0.03344,
        perigee_offset: float = 0.048869,
        output_units: Annotated[str, typer.Option(
            '-o',
            '--output-units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar declination (degrees or radians)")] = 'radians',
        random_time: Annotated[bool, typer.Option(
            '-r',
            '--random-time',
            help="Generate a random date, time and timezone to demonstrate calculation")] = False,
        ) -> float:
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
    year = timestamp.year
    start_of_year = datetime(year=year, month=1, day=1)
    day_of_year = timestamp.timetuple().tm_yday
    day_angle = 2 * math.pi * day_of_year / days_in_a_year
    declination = math.asin(
            0.3978 * math.sin(
                day_angle - 1.4 + orbital_eccentricity * math.sin(
                    day_angle - perigee_offset
                    )
                )
            )
    declination = convert_to_degrees_if_requested(declination, output_units)

    return declination
