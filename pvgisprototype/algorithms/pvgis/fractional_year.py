from devtools import debug
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateFractionalYearPVISInputModel
from pvgisprototype import FractionalYear
from pvgisprototype.cli.typer_parameters import DAYS_IN_A_YEAR
from datetime import datetime
from datetime import date
from datetime import timedelta
from math import pi
from math import isclose


FRACTIONAL_YEAR_MINIMUM = 0
FRACTIONAL_YEAR_MAXIMUM = 2 * pi


# @validate_with_pydantic(CalculateFractionalYearPVGISInputModel, expand_args=True)
def calculate_fractional_year_pvgis(
    timestamp: datetime,
    angle_units: str = 'radians',
    angle_output_units: str = 'radians',
) -> FractionalYear:
    """Calculate fractional year in radians using 365.25 days in a year

    Notes
    -----
    - In PVGIS' C source code, this is called `day_angle`
    - NOAA's corresponding equation uses 365 days in a year
    """
    year = timestamp.year
    start_of_year = datetime(year=year, month=1, day=1)
    day_of_year = timestamp.timetuple().tm_yday
    fractional_year = 2 * pi * day_of_year / 365.25

    if not ((isclose(FRACTIONAL_YEAR_MINIMUM, fractional_year) or FRACTIONAL_YEAR_MINIMUM < fractional_year) and 
            (isclose(FRACTIONAL_YEAR_MAXIMUM, fractional_year) or fractional_year < FRACTIONAL_YEAR_MAXIMUM)):
        raise ValueError(f'Calculated fractional year {fractional_year} is out of the expected range [{FRACTIONAL_YEAR_MINIMUM}, {FRACTIONAL_YEAR_MAXIMUM}] radians')

    fractional_year = FractionalYear(value=fractional_year, unit='radians')
    # fractional_year = convert_to_degrees_if_requested(fractional_year, angle_output_units)
            
    return fractional_year
