from pvgisprototype.api.decorators import validate_with_pydantic
from pvgisprototype.models.noaa.function_models import CalculateEquationOfTimeNOAAInput
from datetime import datetime
from .fractional_year import calculate_fractional_year_noaa 
from math import sin
from math import cos

from pvgisprototype.api.models import EquationOfTime


# @cache_result
@validate_with_pydantic(CalculateEquationOfTimeNOAAInput)
def calculate_equation_of_time_noaa(
    timestamp: datetime,
    time_output_units: str = 'minutes',
    angle_units: str = 'radians',
) -> EquationOfTime:
    """Calculate the equation of time in minutes"""
    fractional_year = calculate_fractional_year_noaa(
        timestamp=timestamp,
        angle_output_units='radians'
    )
    if not fractional_year.unit == angle_units:
        raise ValueError("The fractional year value must be in radians")

    equation_of_time = 229.18 * (
        0.000075
        + 0.001868 * cos(fractional_year.value)
        - 0.032077 * sin(fractional_year.value)
        - 0.014615 * cos(2 * fractional_year.value)
        - 0.040849 * sin(2 * fractional_year.value)
    )

    if not -20 <= equation_of_time <= 20:
        raise ValueError("The equation of time must be within the range [-20, 20] minutes")

    return EquationOfTime(value=equation_of_time, unit='minutes')
