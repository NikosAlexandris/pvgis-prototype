from devtools import debug
from datetime import datetime
# from datetime import date
# from typing import Optional
from typing import Union
from typing import Sequence
from pvgisprototype.api.utilities.timestamp import get_days_in_year
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.algorithms.noaa.function_models import CalculateFractionalYearNOAAInput
from pvgisprototype.algorithms.noaa.function_models import CalculateFractionalYearTimeSeriesNOAAInput
# from pvgisprototype.api.utilities.conversions import convert_to_degrees_if_requested
from pvgisprototype import FractionalYear
from math import pi
import numpy as np





@validate_with_pydantic(CalculateFractionalYearNOAAInput)
def calculate_fractional_year_noaa(
        timestamp: datetime,
        # angle_output_units: str = "radians",
    ) -> FractionalYear:
    """Calculate fractional year in radians """
    fractional_year = (
        2
        * pi
        / get_days_in_year(timestamp.year)
        * (timestamp.timetuple().tm_yday - 1 + float(timestamp.hour - 12) / 24)
    )

    # slightly less than 0 ?
    if -pi/365 <= fractional_year < 0:  # for example, consider values > -1e-6 as close enough to 0
        fractional_year = 0

    if not 0 <= fractional_year < 2 * pi:
        raise ValueError(f'The calculated fractional year {fractional_year} is outside the expected range [0, 2*pi] radians')

    fractional_year = FractionalYear(value=fractional_year, unit='radians')

    # fractional_year = convert_to_degrees_if_requested(fractional_year, angle_output_units)
    
    if not 0 <= fractional_year.degrees < 360:
            raise ValueError('Fractional year (in degrees) must be in the range [0, 360]')
            
    return fractional_year


@validate_with_pydantic(CalculateFractionalYearTimeSeriesNOAAInput)
def calculate_fractional_year_time_series_noaa(
        timestamps: Union[datetime, Sequence[datetime]],
        angle_output_units: str = "radians"
    ):
    """ """
    is_scalar_input = isinstance(timestamps, datetime)
    timestamps = np.atleast_1d(np.array(timestamps, dtype=datetime))
    days_in_year_series = np.array([get_days_in_year(ts.year) for ts in timestamps])
    days_of_year_series = np.array([ts.timetuple().tm_yday for ts in timestamps])
    hours = np.array([ts.hour for ts in timestamps])
    fractional_year_series = 2 * np.pi / days_in_year_series * (days_of_year_series - 1 + (hours - 12) / 24)
    fractional_year_series[fractional_year_series < 0] = 0
    if not np.all((0 <= fractional_year_series) & (fractional_year_series < 2 * np.pi)):
        raise ValueError(f'The calculated fractional years are outside the expected range [0, {2*pi}] radians')

    if is_scalar_input:
        return FractionalYear(value=fractional_year_series[0], unit='radians')
    else:
        return np.array([FractionalYear(value=value, unit='radians') for value in fractional_year_series], dtype=object)
