from datetime import datetime
from typing import Optional
from typing import NamedTuple
from .decorators import validate_with_pydantic
from .noaa_models import CalculateFractionalYearNOAAInput
from math import pi
from ...api.utilities.conversions import convert_to_degrees_if_requested
from pvgisprototype.api.named_tuples import generate


@validate_with_pydantic(CalculateFractionalYearNOAAInput)
def calculate_fractional_year_noaa(
        timestamp: datetime,
        angle_output_units: str = "radians",  # Returned, not used!
        ) -> NamedTuple:
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

    fractional_year = generate('fractional_year', (fractional_year, angle_output_units))

    # fractional_year = convert_to_degrees_if_requested(fractional_year, angle_output_units)
    # if angle_output_units == 'degrees':
    #     if not 0 <= fractional_year < 360:
    #         raise ValueError('Fractional year (in degrees) must be in the range [0, 360]')
            
    return fractional_year
