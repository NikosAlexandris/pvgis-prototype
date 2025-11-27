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
from devtools import debug
from pandas import DatetimeIndex, Timestamp
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT, DATA_TYPE_DEFAULT, DEBUG_AFTER_THIS_VERBOSITY_LEVEL, HASH_AFTER_THIS_VERBOSITY_LEVEL, LOG_LEVEL_DEFAULT, RADIANS, TIMEZONE_UTC, VERBOSE_LEVEL_DEFAULT
from functools import partial
from math import isfinite, radians, sin
import numpy
from pvgisprototype import SolarDeclination
from pvgisprototype.api.datetime.helpers import get_days_in_years
from pvgisprototype.constants import DEGREES
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.validation.functions import (
    CalculateSolarDeclinationHargreavesInputModel,
    validate_with_pydantic,
)
from pvgisprototype.api.position.models import SolarDeclinationModel
from pvgisprototype.validation.values import identify_values_out_of_range_x


# @validate_with_pydantic(CalculateSolarDeclinationHargreavesInputModel)
@log_function_call
@custom_cached
def calculate_solar_declination_series_hargreaves(
    timestamps: DatetimeIndex,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> SolarDeclination:
    """
    Approximate the solar declination for a series of timestamps 
    using the Hargreaves formula, with days-in-year from each timestamp's year.

                      ⎛360   ⎛                    ⎛360            ⎞⎞⎞
     δ = 23.45° ⋅ sin ⎜─── ⋅ ⎜284 + n + 0.4 ⋅ sin ⎜─── ⋅ (n - 100)⎟⎟⎟
                      ⎝365   ⎝                    ⎝365            ⎠⎠⎠

     Notes
     -----

     - 365.25: The number 365.25 represents the average number of days in a
     year. This value is used to scale the orbital position of the Earth.

     - 284: The number 284 represents a constant term added to the day of the
     year. It adjusts the calculation to align with the Earth's position
     during the winter solstice, which usually occurs around December 21st
     (approximately 284 days into the year).

     - 0.4: The number 0.4 is a constant that determines the amplitude of the
     seasonal variation. It is multiplied by the second sine term to
     modulate the seasonal change in the solar declination.

     - 100: The number 100 represents an offset to the day of the year. It is
     subtracted from the original day of the year before calculating the
     second sine term. This offset helps adjust the timing of the seasonal
     variation and is usually chosen to align with the summer solstice,
     which typically occurs around June 21st.
    """
    if not isinstance(timestamps, DatetimeIndex):
        raise TypeError("timestamps must be a pandas.DatetimeIndex")

    days_in_years = get_days_in_years(timestamps.year)
    days_of_year = timestamps.dayofyear

    inner_angle = numpy.array(360.0 / days_in_years * (days_of_year - 100.0))
    solar_declination_series = numpy.sin(
        numpy.radians(
            360.0
            / days_in_years
            * (284.0 + days_of_year + 0.4 * numpy.sin(numpy.radians(inner_angle)))
        )
    ).to_numpy().astype(dtype)

    out_of_range, out_of_range_index = identify_values_out_of_range_x(
        series=solar_declination_series,
        shape=timestamps.shape,
        data_model=SolarDeclination(unit=RADIANS),
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
        out_of_range=out_of_range,
        out_of_range_index=out_of_range_index,
        algorithm=SolarDeclinationModel.hargreaves,
    )
