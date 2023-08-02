from devtools import debug
import typer
from typing import Optional
from datetime import datetime
from zoneinfo import ZoneInfo
from math import pi
from math import sin
from math import asin
from ..utilities.conversions import convert_to_degrees_if_requested

from pvgisprototype.api.input_models import SolarDeclinationInput
from pvgisprototype.api.decorators import validate_with_pydantic


def calculate_fractional_year_pvis(
        timestamp: datetime,
        days_in_a_year: float,
        angle_output_units: Optional[str] = "radians",
        ) -> float:
    """Calculate fractional year in radians

    Notes
    -----
    In PVGIS' source code, this is called `day_angle`"""
    year = timestamp.year
    start_of_year = datetime(year=year, month=1, day=1)
    day_of_year = timestamp.timetuple().tm_yday
    fractional_year = 2 * pi * day_of_year / days_in_a_year

    # NOAA's corresponding equation
    # fractional_year = (
    #     2
    #     * pi
    #     / 365
    #     * (timestamp.timetuple().tm_yday - 1 + float(timestamp.hour - 12) / 24)
    # )

    if not 0 <= fractional_year < 2 * pi:
        raise ValueError('Fractional year (in radians) must be in the range [0, 2*pi]')
    # fractional_year = convert_to_degrees_if_requested(fractional_year, angle_output_units)
            
    return fractional_year, angle_output_units


@validate_with_pydantic(SolarDeclinationInput, expand_args=True)
def calculate_solar_declination(
        timestamp: datetime,
        timezone: ZoneInfo,
        days_in_a_year: float,
        eccentricity: float,
        perigee_offset: float,
        angle_output_units: str,
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
    fractional_year, _ = calculate_fractional_year_pvis(
            timestamp=timestamp,
            days_in_a_year=days_in_a_year,
            angle_output_units=angle_output_units,
            )
    declination = asin(
            0.3978 * sin(
                fractional_year - 1.4 + eccentricity * sin(
                    fractional_year - perigee_offset
                    )
                )
            )
    # declination = convert_to_degrees_if_requested(declination, input.angle_output_units)

    return declination
