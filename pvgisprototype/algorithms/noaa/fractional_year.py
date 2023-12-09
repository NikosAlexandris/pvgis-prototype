from devtools import debug
from datetime import datetime
from typing import Union
from typing import Sequence
from pvgisprototype.api.utilities.timestamp import get_days_in_year
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.algorithms.noaa.function_models import CalculateFractionalYearNOAAInput
from pvgisprototype.algorithms.noaa.function_models import CalculateFractionalYearTimeSeriesNOAAInput
from pvgisprototype import FractionalYear
from pvgisprototype.constants import RADIANS
from math import pi
import numpy as np


@validate_with_pydantic(CalculateFractionalYearNOAAInput)
def calculate_fractional_year_noaa(
        timestamp: datetime,
    ) -> FractionalYear:
    """Calculate fractional year in radians """
    days_in_year = get_days_in_year(timestamp.year)
    fractional_year = (
        2
        * pi
        / days_in_year
        * (timestamp.timetuple().tm_yday - 1 + float(timestamp.hour - 12) / 24)
    )

    # slightly less than 0 ?
    if -pi/365 <= fractional_year < 0:  # for example, consider values > -1e-6 as close enough to 0
        fractional_year = 0
    fractional_year = FractionalYear(value=fractional_year, unit=RADIANS)

    if not 0 <= fractional_year.radians < 2 * pi:
        raise ValueError(f'The calculated fractional year {fractional_year} is outside the expected range [0, 2*pi] radians')

    return fractional_year


@validate_with_pydantic(CalculateFractionalYearTimeSeriesNOAAInput)
def calculate_fractional_year_time_series_noaa(
        timestamps: Union[datetime, Sequence[datetime]],
        backend: str = 'numpy',
        dtype: str = 'float64',
    ) -> FractionalYear:
    """ """
    timestamps = np.atleast_1d(np.array(timestamps, dtype=datetime))
    days_in_year_series = np.array(
        [get_days_in_year(ts.year) for ts in timestamps],
        dtype=dtype,
    )
    days_of_year_series = np.array(
        [ts.timetuple().tm_yday for ts in timestamps],
        dtype=dtype,
    )
    hours = np.array(
        [ts.hour for ts in timestamps],
        dtype=dtype,
    )
    fractional_year_series = (
        2 * np.pi / days_in_year_series * (days_of_year_series - 1 + (hours - 12) / 24)
    )
    fractional_year_series[fractional_year_series < 0] = 0
    
    if not np.all((0 <= fractional_year_series) & (fractional_year_series < 2 * np.pi)):
        raise ValueError(f'The calculated fractional years are outside the expected range [0, {2*pi}] radians')

    fractional_year_series = FractionalYear(
        value=fractional_year_series,
        unit=RADIANS,
        position_algorithm='NOAA',
        timing_algorithm='NOAA',
    )

    if not np.all((fractional_year_series.min_degrees <= fractional_year_series.degrees) & (fractional_year_series.degrees <= fractional_year_series.max_degrees)):
        wrong_values_index = np.where(fractional_year_series.min_degrees <= np.all(fractional_year_series.degrees) <= fractional_year_series.max_degrees)
        wrong_values = fractional_year_series.degrees[wrong_values_index]
        raise ValueError(f"The calculated fractional year `{wrong_values}` is out of the expected range [{fractional_year_series.min_degrees}, {fractional_year_series.max_degrees}] degrees!')")

    return fractional_year_series
