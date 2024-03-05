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
from pvgisprototype.algorithms.caching import custom_hashkey
from pandas import DatetimeIndex


@validate_with_pydantic(CalculateEquationOfTimeNOAAInput)
def calculate_equation_of_time_noaa(
    timestamp: datetime,
) -> EquationOfTime:
    """Calculate the equation of time in minutes."""
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


@cached(cache={}, key=custom_hashkey)
@validate_with_pydantic(CalculateEquationOfTimeTimeSeriesNOAAInput) 
def calculate_equation_of_time_time_series_noaa(
    timestamps: DatetimeIndex,
) -> EquationOfTime:
    """Calculate the equation of time in minutes for a time series."""
    fractional_year_series = calculate_fractional_year_time_series_noaa(
        timestamps=timestamps,
        angle_output_units=RADIANS
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

    from pvgisprototype.validation.hashing import generate_hash
    equation_of_time_series_hash = generate_hash(equation_of_time_series)
    print(
        "EquationOfTime : calculate_equation_of_time_time_series_noaa() |",
        f"Data Type : [bold]{equation_of_time_series.dtype}[/bold] |",
        f"Output Hash : [code]{equation_of_time_series_hash}[/code]",
    )
    
    return EquationOfTime(
        value=equation_of_time_series,
        unit=MINUTES,
        position_algorithm='NOAA',
        timing_algorithm='NOAA',
    )
