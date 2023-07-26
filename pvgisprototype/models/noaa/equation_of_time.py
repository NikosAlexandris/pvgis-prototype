from .noaa_models import CalculateEquationOfTimeNOAAInput
from .decorators import validate_with_pydantic
from datetime import datetime
from .fractional_year import calculate_fractional_year_noaa 
from math import sin
from math import cos
from typing import NamedTuple
from pvgisprototype.api.named_tuples import generate


# @cache_result
@validate_with_pydantic(CalculateEquationOfTimeNOAAInput)
def calculate_equation_of_time_noaa(
    timestamp: datetime,
    time_output_units: str = 'minutes',
    angle_units: str = 'radians',
) -> NamedTuple:
    """Calculate the equation of time in minutes"""
    fractional_year, _units = calculate_fractional_year_noaa(
        timestamp, angle_units
    )
    equation_of_time = 229.18 * (
        0.000075
        + 0.001868 * cos(fractional_year)
        - 0.032077 * sin(fractional_year)
        - 0.014615 * cos(2 * fractional_year)
        - 0.040849 * sin(2 * fractional_year)
    )

    if not -20 <= equation_of_time <= 20:
        raise ValueError("The equation of time must be within the range [-20, 20] minutes")

    equation_of_time = generate(
        'equation_of_time'.upper(),
        (equation_of_time, time_output_units),
        )
    return equation_of_time
