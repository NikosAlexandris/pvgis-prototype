#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
from datetime import datetime, time
from functools import wraps
import numpy as np
from rich import print
from pandas import Index


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(
            f"'{func.__name__}' executed in {elapsed_time:.6f} seconds (or {elapsed_time:.2f} seconds)."
        )
        return result

    return wrapper


# Time


def get_day_from_hour_of_year(year: int, hour_of_year: int):
    """Get day of year from hour of year."""
    start_of_year = np.datetime64(f"{year}-01-01")
    date_and_time = start_of_year + np.timedelta64(hour_of_year, "h")
    date_and_time = date_and_time.astype(datetime.datetime)
    day_of_year = int(date_and_time.strftime("%j"))
    # month = int(date_and_time.strftime('%m'))  # Month
    # day_of_month = int(date_and_time.strftime('%d'))
    # hour_of_day = int(date_and_time.strftime('%H'))

    return day_of_year


# Time series


def get_days_in_year(year):
    """Calculate the number of days in a given year, accounting for leap years.

    Parameters
    ----------
    year : int
        The year for which to calculate the number of days.

    Returns
    -------
    int
        The number of days in the given year.

    Examples
    --------
    >>> get_days_in_year(2020)
    366

    >>> get_days_in_year(2021)
    365
    """
    start_date = datetime(year, 1, 1)  # First day of the year
    end_date = datetime(year + 1, 1, 1)  # First day of the next year
    return (end_date - start_date).days


def get_days_in_years(years):
    """Calculate the number of days in a given year, accounting for leap years.

    Parameters
    ----------
    years : DatetimeIndex
        The years series for which to calculate the number of days.

    Returns
    -------
    DatetimeIndex :
        The number of days series for the given years series

    Examples
    --------
    >>> get_days_in_years_series(pd.DatetimeIndex(['2000-12-22 21:12:12', '2001-11-11 11:11:11']))
    Index([366, 365], dtype='int64')
    """

    years = years.to_numpy().astype(int)
    is_leap_year = (years % 4 == 0) & ((years % 100 != 0) | (years % 400 == 0)) # Vectorized calculation for leap years
    days_in_year = np.where(is_leap_year, 366, 365)

    return Index(days_in_year, dtype='int32')
