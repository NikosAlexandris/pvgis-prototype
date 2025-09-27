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
"""
The Equation of Time based on the General Solar Position Calculations provided
by the NOAA Global Monitoring Division.

See also: https://unpkg.com/solar-calculator@0.1.0/index.js
"""

import numpy as np
from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import EquationOfTime
from pvgisprototype.algorithms.noaa.fractional_year import (
    calculate_fractional_year_series_noaa,
)
from pvgisprototype.algorithms.noaa.function_models import (
    CalculateEquationOfTimeTimeSeriesNOAAInput,
)
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    MINUTES,
    VERBOSE_LEVEL_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.validation.functions import validate_with_pydantic


@log_function_call
@custom_cached
@validate_with_pydantic(CalculateEquationOfTimeTimeSeriesNOAAInput)
def calculate_equation_of_time_series_noaa(
    timestamps: DatetimeIndex,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
) -> EquationOfTime:
    """Calculate the Equation of Time for a time series in minutes.

    The Equation of Time is the difference between the apparent solar time and
    the mean solar time.

    Returns
    -------
    equation_of_time_series : numeric
        Difference in time between solar time and mean solar time in minutes.

    """
    fractional_year_series = calculate_fractional_year_series_noaa(
        timestamps=timestamps,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
        validate_output=validate_output,
    )
    equation_of_time_series = 229.18 * (
        0.000075
        + 0.001868 * np.cos(fractional_year_series.radians)
        - 0.032077 * np.sin(fractional_year_series.radians)
        - 0.014615 * np.cos(2 * fractional_year_series.radians)
        - 0.040849 * np.sin(2 * fractional_year_series.radians)
    )
    
    if validate_output:
        if not np.all(
            (EquationOfTime().min_minutes <= equation_of_time_series)
            & (equation_of_time_series <= EquationOfTime().max_minutes)
        ):
            raise ValueError(
                "The equation of time must be within the range [{EquationOfTime().min_minutes}, {EquationOfTime().max_minutes()}] minutes for all timestamps."
            )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=equation_of_time_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return EquationOfTime(
        value=equation_of_time_series,
        unit=MINUTES,
        position_algorithm=fractional_year_series.position_algorithm,
        timing_algorithm=SolarTimeModel.noaa,
    )
