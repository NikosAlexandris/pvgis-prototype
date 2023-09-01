from pvgisprototype.api.decorators import validate_with_pydantic
from pvgisprototype.algorithms.noaa.function_models import CalculateEquationOfTimeNOAAInput
from pvgisprototype.algorithms.noaa.function_models import CalculateEquationOfTimeTimeSeriesNOAAInput
from datetime import datetime
from pvgisprototype.api.models import EquationOfTime
from pvgisprototype.api.models import FractionalYear
from pvgisprototype.algorithms.noaa.fractional_year import calculate_fractional_year_noaa 
from math import sin
from math import cos
from typing import Union
from typing import Sequence
import numpy as np
from pvgisprototype.algorithms.noaa.fractional_year import calculate_fractional_year_time_series_noaa 

EQUATIONOFTIME_MINIMUM = -20
EQUATIONOFTIME_MAXIMUM = 20
EQUATIONOFTIME_UNITS = 'minutes'


# @cache_result
@validate_with_pydantic(CalculateEquationOfTimeNOAAInput)
def calculate_equation_of_time_noaa(
    timestamp: datetime,
    time_output_units: str = 'minutes',
) -> EquationOfTime:
    """Calculate the equation of time in minutes"""
    fractional_year = calculate_fractional_year_noaa(
        timestamp=timestamp,
        angle_output_units='radians'  # hardcoded intentionally
    )
    equation_of_time = 229.18 * (
        0.000075
        + 0.001868 * cos(fractional_year.value)
        - 0.032077 * sin(fractional_year.value)
        - 0.014615 * cos(2 * fractional_year.value)
        - 0.040849 * sin(2 * fractional_year.value)
    )
    if not EQUATIONOFTIME_MINIMUM <= equation_of_time <= EQUATIONOFTIME_MAXIMUM:
        raise ValueError("The calculated equation of time is out of the expected range [{EQUATIONOFTIME_MINIMUM}, {EQUATIONOFTIME_MAXIMUM}] {EQUATIONOFTIME_UNITS}")

    return EquationOfTime(value=equation_of_time, unit=time_output_units)


@validate_with_pydantic(CalculateEquationOfTimeTimeSeriesNOAAInput) 
def calculate_equation_of_time_time_series_noaa(
    timestamps: Union[datetime, Sequence[datetime]],
    time_output_units: str = 'minutes',
) -> Union[EquationOfTime, np.ndarray]:
    """Calculate the equation of time in minutes for a time series"""
    is_scalar_input = isinstance(timestamps, datetime)
    # timestamps = np.atleast_1d(np.array(timestamps, dtype=datetime))
    fractional_year_series = calculate_fractional_year_time_series_noaa(
        timestamps=timestamps,
        angle_output_units='radians'
    )
    fractional_year_series = np.array([item.value if isinstance(item, FractionalYear) else item for item in fractional_year_series])
    # if not isinstance(fractional_year_series, np.ndarray):
    #     fractional_year_series = np.array([fractional_year_series.value])

    equation_of_time_series = 229.18 * (
        0.000075
        + 0.001868 * np.cos(fractional_year_series)
        - 0.032077 * np.sin(fractional_year_series)
        - 0.014615 * np.cos(2 * fractional_year_series)
        - 0.040849 * np.sin(2 * fractional_year_series)
    )

    if not np.all((-20 <= equation_of_time_series) & (equation_of_time_series <= 20)):
        raise ValueError("The equation of time must be within the range [-20, 20] minutes for all timestamps.")

    if is_scalar_input:
        return EquationOfTime(value=equation_of_time_series[0], unit='minutes')
    else:
        return np.array([EquationOfTime(value=value, unit='minutes') for value in equation_of_time_series], dtype=object)
