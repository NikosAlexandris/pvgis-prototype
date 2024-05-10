from devtools import debug
from rich import print
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateEquationOfTimeNOAAInput
from pvgisprototype.algorithms.noaa.function_models import CalculateEquationOfTimeTimeSeriesNOAAInput
from datetime import datetime
from pvgisprototype import EquationOfTime
from pvgisprototype import FractionalYear
from pvgisprototype.algorithms.noaa.fractional_year import calculate_fractional_year_noaa 
from math import sin
from math import cos
from typing import Union
from typing import Sequence
import numpy as np
from pvgisprototype.algorithms.noaa.fractional_year import calculate_fractional_year_time_series_noaa 
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import MINUTES
from cachetools import cached
from pvgisprototype.caching import custom_hashkey
from pandas import DatetimeIndex
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint


@validate_with_pydantic(CalculateEquationOfTimeNOAAInput)
def calculate_equation_of_time_noaa(
    timestamp: datetime,
) -> EquationOfTime:
    """Calculate the Equation of Time in minutes.

    The Equation of Time is the difference between solar apparent and mean time.

    """
    fractional_year = calculate_fractional_year_noaa(
        timestamp=timestamp,
    )
    equation_of_time_minutes = 229.18 * (
        0.000075
        + 0.001868 * cos(fractional_year.radians)
        - 0.032077 * sin(fractional_year.radians)
        - 0.014615 * cos(2 * fractional_year.radians)
        - 0.040849 * sin(2 * fractional_year.radians)
    )
    equation_of_time = EquationOfTime(value=equation_of_time_minutes, unit='minutes')

    if not equation_of_time.min_minutes <= equation_of_time.minutes <= equation_of_time.max_minutes:
        raise ValueError("The calculated equation of time is out of the expected range [{EQUATIONOFTIME_MINIMUM}, {EQUATIONOFTIME_MAXIMUM}] {EQUATIONOFTIME_UNITS}")

    return equation_of_time


@log_function_call
@cached(cache={}, key=custom_hashkey)
@validate_with_pydantic(CalculateEquationOfTimeTimeSeriesNOAAInput) 
def calculate_equation_of_time_time_series_noaa(
    timestamps: DatetimeIndex,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> EquationOfTime:
    """Calculate the equation of time in minutes for a time series."""
    fractional_year_series = calculate_fractional_year_time_series_noaa(
        timestamps=timestamps,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    equation_of_time_series = 229.18 * (
        0.000075
        + 0.001868 * np.cos(fractional_year_series.radians)
        - 0.032077 * np.sin(fractional_year_series.radians)
        - 0.014615 * np.cos(2 * fractional_year_series.radians)
        - 0.040849 * np.sin(2 * fractional_year_series.radians)
    )
    if not np.all(
        (EquationOfTime().min_minutes <= equation_of_time_series)
        & (equation_of_time_series <= EquationOfTime().max_minutes)
    ):
        raise ValueError(
            "The equation of time must be within the range [{EquationOfTime().min_minutes}, {EquationOfTime().max_minutes()}] minutes for all timestamps."
        )
    log_data_fingerprint(
            data=equation_of_time_series,
            log_level=log,
            hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )
    
    return EquationOfTime(
        value=equation_of_time_series,
        unit=MINUTES,
        position_algorithm='NOAA',
        timing_algorithm='NOAA',
    )
