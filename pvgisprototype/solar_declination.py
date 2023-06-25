import typer
from typing import Annotated
from typing import Optional
import math
import numpy as np
from datetime import datetime
from datetime import timezone
from datetime import timedelta
from .timestamp import now_datetime
from .timestamp import convert_to_timezone
from .timestamp import attach_timezone


def convert_to_degrees_if_requested(angle: float, output_units: str) -> float:
    """Convert angle from radians to degrees if requested."""
    x = np.degrees(angle) if output_units == 'degrees' else angle
    return x


def convert_to_radians_if_requested(angle: float, output_units: str) -> float:
    """Convert angle from degrees to radians if requested."""
    return np.radians(angle) if output_units == 'radians' else angle


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"Approximate the solar declination for a day in the year",
)


# from: rsun_base.cpp
# function: com_declin(no_of_day)
@app.callback(invoke_without_command=True, no_args_is_help=True)
def calculate_solar_declination(
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_datetime)],
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
    The formula used here is a simple approximation. For more accurate
    calculations of solar position, comprehensive models like the Solar
    Position Algorithm (SPA) are typically used.
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


def calculate_solar_declination_pvgis(
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_datetime)],
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
        ) -> float:
    """Approximate the sun's declination for a given day of the year.

    This function is a 1:1 transfer of the solar declination calculation
    implemented in PVGIS' r.sun C code, in form of the function `com_declin()`
    in `rsun_base.c` (or/and `rsun_base.cpp`). It merely exists in comparing
    with the new implementation and understanding the purpose of inverting the
    sign.

    IMPORTANT: In the original C source code, there is at the end of the

    `com_declin` function:

    ```
    decl = - decl;
    ```

    which is actually : `declination = - declination`. Why? The value is
    inverted again at some other part of the program when it gets to read data.
    """
    day_of_year = timestamp.timetuple().tm_yday
    solar_declination = calculate_solar_declination(
        timestamp,
        timezone,
        days_in_a_year,
        orbital_eccentricity,
        perigee_offset,
        output_units,
        )

    return - solar_declination


def calculate_solar_declination_hargreaves(
        timestamp: datetime = partial(datetime.now, tz=timezone.utc),
        days_in_a_year: float = 365.25,
        output_units: Annotated[str, typer.Option(
            '-o',
            '--output-units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar declination (degrees or radians)")] = 'radians',
        ) -> float:
    """Approximate the solar declination based on the Hargreaves formula.

        δ = 23.45° × sin [360/365 × (284 + n + 0.4 × sin [360/365 × (n - 100)])]

        Notes
        -----

        365.25: The number 365.25 represents the average number of days in a
        year. This value is used to scale the orbital position of the Earth.

        284: The number 284 represents a constant term added to the day of the
        year. It adjusts the calculation to align with the Earth's position
        during the winter solstice, which usually occurs around December 21st
        (approximately 284 days into the year).

        0.4: The number 0.4 is a constant that determines the amplitude of the
        seasonal variation. It is multiplied by the second sine term to
        modulate the seasonal change in the solar declination.

        100: The number 100 represents an offset to the day of the year. It is
        subtracted from the original day of the year before calculating the
        second sine term. This offset helps adjust the timing of the seasonal
        variation and is usually chosen to align with the summer solstice,
        which typically occurs around June 21st.
    """
    # year = timestamp.year
    # start_of_year = datetime(year=year, month=1, day=1, tzinfo=timezone.utc)
    day_of_year = timestamp.timetuple().tm_yday
    declination = 23.45 * math.sin(math.radians(360/days_in_a_year * (284 + day_of_year + 0.4 * math.sin(math.radians(360/days_in_a_year * (day_of_year - 100))))))
    declination = convert_to_radians_if_requested(declination, output_units)

    return declination
