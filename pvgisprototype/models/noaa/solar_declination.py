from .noaa_models import CalculateSolarDeclinationNOAAInput
from typing import Optional
from typing import NamedTuple
from datetime import datetime
from ...api.utilities.conversions import convert_to_degrees_if_requested
from .decorators import validate_with_pydantic
from .fractional_year import calculate_fractional_year_noaa 
from math import sin
from math import cos
from pvgisprototype.api.named_tuples import generate


# @cache_result
@validate_with_pydantic(CalculateSolarDeclinationNOAAInput)
def calculate_solar_declination_noaa(
        timestamp: datetime,
        angle_output_units: Optional[str] = 'radians'
) -> NamedTuple:
        """Calculate the solar declination in radians"""
        fractional_year = calculate_fractional_year_noaa(
                timestamp,
                angle_output_units = angle_units,
                )
        declination = (
        0.006918
        - 0.399912 * cos(fractional_year.value)
        + 0.070257 * sin(fractional_year.value)
        - 0.006758 * cos(2 * fractional_year.value)
        + 0.000907 * sin(2 * fractional_year.value)
        - 0.002697 * cos(3 * fractional_year.value)
        + 0.00148 * sin(3 * fractional_year.value)
        )

        declination = generate(
                'solar_declination',
                (declination, angle_output_units),
        )
        return declination

