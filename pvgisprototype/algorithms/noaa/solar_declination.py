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
import numpy as np
from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import SolarDeclination
from pvgisprototype.algorithms.noaa.fractional_year import (
    calculate_fractional_year_series_noaa,
)
from pvgisprototype.algorithms.noaa.function_models import (
    CalculateSolarDeclinationTimeSeriesNOAAInput,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    RADIANS,
    VERBOSE_LEVEL_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.values import identify_values_out_of_range_x


@log_function_call
@custom_cached
@validate_with_pydantic(CalculateSolarDeclinationTimeSeriesNOAAInput)
def calculate_solar_declination_series_noaa(
    timestamps: DatetimeIndex,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    validate_output:bool = VALIDATE_OUTPUT_DEFAULT,
) -> SolarDeclination:
    """Calculate the solar declination for a time series.

    Notes
    -----
    From NOAA's .. Excel sheet:

    sine_solar_declination
    = ASIN(
        SIN(RADIANS(R2))*SIN(RADIANS(P2))
    )

    where:

    P2 = M2-0.00569-0.00478*SIN(RADIANS(125.04-1934.136*G2))

        where:

        M2 = Geom Mean Long Sun (deg) + Geom Mean Anom Sun (deg)


    R2 = Q2 + 0.00256 * COS(RADIANS(125.04 - 1934.136*G2))

        where :

       Q2 = Mean Obliq Ecliptic (deg)

    """
    fractional_year_series = calculate_fractional_year_series_noaa(
        timestamps=timestamps,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
        validate_output=validate_output,
    )
    solar_declination_series = (
        0.006918
        - 0.399912 * np.cos(fractional_year_series.radians)
        + 0.070257 * np.sin(fractional_year_series.radians)
        - 0.006758 * np.cos(2 * fractional_year_series.radians)
        + 0.000907 * np.sin(2 * fractional_year_series.radians)
        - 0.002697 * np.cos(3 * fractional_year_series.radians)
        + 0.00148 * np.sin(3 * fractional_year_series.radians)
    )
    out_of_range = None
    out_of_range_index = None
    if validate_output:
        out_of_range, out_of_range_index = identify_values_out_of_range_x(
            series=solar_declination_series,
            shape=timestamps.shape,
            data_model=SolarDeclination(),
        )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=solar_declination_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return SolarDeclination(
        value=solar_declination_series,
        unit=RADIANS,
        out_of_range=out_of_range if out_of_range is not None else None,
        out_of_range_index=out_of_range_index if out_of_range is not None else None,
        solar_positioning_algorithm=fractional_year_series.solar_positioning_algorithm,
    )
