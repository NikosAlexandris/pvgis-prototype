from devtools import debug
from datetime import datetime
from typing import Union
from typing import Sequence
from pvgisprototype.api.utilities.timestamp import get_days_in_year
from pvgisprototype.api.utilities.timestamp import get_days_in_years_series
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.algorithms.noaa.function_models import CalculateFractionalYearNOAAInput
from pvgisprototype.algorithms.noaa.function_models import CalculateFractionalYearTimeSeriesNOAAInput
from pvgisprototype import FractionalYear
from pvgisprototype.constants import RADIANS
from math import pi
import numpy as np
from rich import print
from cachetools import cached
from pvgisprototype.algorithms.caching import custom_hashkey
from pandas import DatetimeIndex


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


@cached(cache={}, key=custom_hashkey)
@validate_with_pydantic(CalculateFractionalYearTimeSeriesNOAAInput)
def calculate_fractional_year_time_series_noaa(
        timestamps: Union[datetime, DatetimeIndex],
    ) -> FractionalYear:
    """
    Calculate the fractional year series for a given series of timestamps.

    Parameters
    ----------
    timestamps : DatetimeIndex
        A Pandas DatetimeIndex representing the timestamps.

    backend : str, optional
        The backend used for calculations (the default is 'numpy').
    
    dtype : str, optional
        The data type for the calculations (the default is 'float64').

    Returns
    -------
    FractionalYear
        A FractionalYear object containing the calculated fractional year series.

    Raises
    ------
    ValueError
        If any calculated fractional year value is outside the expected range.

    Examples
    --------
    >>> timestamps = pd.date_range(start='2020-01-01', end='2020-12-31', freq='D')
    >>> fractional_year_series = calculate_fractional_year_time_series_noaa(timestamps)
    >>> print(fractional_year_series)

    Notes
    -----
    The function calculates the fractional year considering leap years and converts
    the timestamps into fractional values considering their position within the year.
    This is used in various solar energy calculations and models.
    """
    days_of_year_series = timestamps.dayofyear
    hours = timestamps.hour
    days_in_year_series = get_days_in_years_series(timestamps.year) 
    fractional_year_series = np.array(
        2 * np.pi / days_in_year_series * (days_of_year_series - 1 + (hours - 12) / 24),
        dtype=np.float32,
    )
    fractional_year_series[fractional_year_series < 0] = 0
    
    if not np.all((0 <= fractional_year_series) & (fractional_year_series < 2 * np.pi)):
        raise ValueError(f'The calculated fractional years are outside the expected range [0, {2*pi}] radians')

    from pvgisprototype.validation.hashing import generate_hash
    fractional_year_series_hash = generate_hash(fractional_year_series)
    print(
        "FY : calculate_fractional_year_time_series_noaa() |",
        f"Data Type : [bold]{fractional_year_series.dtype}[/bold] |",
        f"Output Hash : [code]{fractional_year_series_hash}[/code]",
    )

    fractional_year_series = FractionalYear(
        value=fractional_year_series,
        unit=RADIANS,
        position_algorithm='NOAA',
        timing_algorithm='NOAA',
    )
    if not np.all(
        (fractional_year_series.min_degrees <= fractional_year_series.degrees)
        & (fractional_year_series.degrees <= fractional_year_series.max_degrees)
    ):
        wrong_values_index = np.where(
            fractional_year_series.min_degrees
            <= np.all(fractional_year_series.degrees)
            <= fractional_year_series.max_degrees
        )
        wrong_values = fractional_year_series.degrees[wrong_values_index]
        raise ValueError(
            f"The calculated fractional year `{wrong_values}` is out of the expected range [{fractional_year_series.min_degrees}, {fractional_year_series.max_degrees}] degrees!')"
        )

    return fractional_year_series
