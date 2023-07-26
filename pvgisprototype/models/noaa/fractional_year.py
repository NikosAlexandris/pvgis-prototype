from datetime import datetime
from typing import Optional
from .decorators import validate_with_pydantic
from .noaa_models import CalculateFractionalYearNOAAInput
from math import pi
from ...api.utilities.conversions import convert_to_degrees_if_requested


@validate_with_pydantic(CalculateFractionalYearNOAAInput)
def calculate_fractional_year_noaa(
        timestamp: datetime,
        angle_output_units: str = "radians",  # Returned, not used!
        ) -> float:
    """Calculate fractional year in radians """
    fractional_year = (
        2
        * pi
        / 365
        * (timestamp.timetuple().tm_yday - 1 + float(timestamp.hour - 12) / 24)
    )

    # slightly less than 0 ?
    if -pi/365 <= fractional_year < 0:  # for example, consider values > -1e-6 as close enough to 0
        fractional_year = 0

    if not 0 <= fractional_year < 2 * pi:
        raise ValueError(f'The calculated fractional year {fractional_year} is outside the expected range [0, 2*pi] radians')

    return fractional_year, angle_output_units
