from datetime import date
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateFractionalYearPVISInputModel
from pvgisprototype.api.utilities.conversions import convert_to_degrees_if_requested
from pvgisprototype.api.utilities.timestamp import get_days_in_year
from datetime import datetime
from pvgisprototype import FractionalYear
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import FRACTIONAL_YEAR_MINIMUM
from pvgisprototype.constants import FRACTIONAL_YEAR_MAXIMUM
from math import pi
from math import isclose


@validate_with_pydantic(CalculateFractionalYearPVISInputModel)
def calculate_fractional_year_pvis(
    timestamp: datetime,
    # angle_units: str = 'radians',
    # angle_output_units: str = 'radians',
) -> FractionalYear:
    """Calculate fractional year in radians

    Notes
    -----
    In PVGIS' C source code, this is called `day_angle`

    NOAA's corresponding equation:

        fractional_year = (
            2
            * pi
            / 365
            * (timestamp.timetuple().tm_yday - 1 + float(timestamp.hour - 12) / 24)
        )
    """
    year = timestamp.year
    day_of_year = timestamp.timetuple().tm_yday
    days_in_year = get_days_in_year(timestamp.year)
    fractional_year = 2 * pi * day_of_year / days_in_year

    if not ((isclose(FRACTIONAL_YEAR_MINIMUM, fractional_year) or FRACTIONAL_YEAR_MINIMUM < fractional_year) and 
            (isclose(FRACTIONAL_YEAR_MAXIMUM, fractional_year) or fractional_year < FRACTIONAL_YEAR_MAXIMUM)):
        raise ValueError(f'Calculated fractional year {fractional_year} is out of the expected range [{FRACTIONAL_YEAR_MINIMUM}, {FRACTIONAL_YEAR_MAXIMUM}] radians')

    fractional_year = FractionalYear(value=fractional_year, unit=RADIANS)
            
    return fractional_year
