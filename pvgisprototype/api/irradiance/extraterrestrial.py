from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from devtools import debug
from typing import Optional
from typing import Union
from datetime import datetime
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RANDOM_DAY_SERIES_FLAG_DEFAULT
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import EXTRATERRESTRIAL_NORMAL_IRRADIANCE
from pvgisprototype.constants import EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DAY_OF_YEAR_COLUMN_NAME
from pvgisprototype.constants import DISTANCE_CORRECTION_COLUMN_NAME
from pvgisprototype.validation.pvis_data_classes import BaseTimestampSeriesModel
import numpy as np
from pandas import DatetimeIndex
from cachetools import cached
from pvgisprototype.algorithms.caching import custom_hashkey


def get_days_per_year(years):
    return 365 + ((years % 4 == 0) & ((years % 100 != 0) | (years % 400 == 0))).astype(int)


@log_function_call
@cached(cache={}, key=custom_hashkey)
def calculate_extraterrestrial_normal_irradiance_time_series(
    timestamps: DatetimeIndex = None,
    start_time: Optional[datetime] = None,
    frequency: Optional[str] = None,
    end_time: Optional[datetime] = None,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    random_days: bool = RANDOM_DAY_SERIES_FLAG_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
) -> Union[np.ndarray, dict]:
    """
    Calculate the normal extraterrestrial irradiance over a period of time
    """
    years_in_timestamps = timestamps.year
    years, indices = np.unique(years_in_timestamps, return_inverse=True)
    days_per_year = get_days_per_year(years).astype(dtype)
    days_in_years = days_per_year[indices]

    if random_days:
        day_of_year_series = np.random.randint(1, days_in_years + 1)
        day_of_year_series = np.random.randint(1, days_in_years.max() + 1, size=timestamps.size).astype(dtype)

    else:
        day_of_year_series = timestamps.dayofyear.to_numpy().astype(dtype)

    position_of_earth_series = 2 * np.pi * day_of_year_series / days_in_years
    distance_correction_factor_series = 1 + eccentricity_correction_factor * np.cos(position_of_earth_series - perigee_offset)
    extraterrestrial_normal_irradiance_series = solar_constant * distance_correction_factor_series

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    if verbose > 0:
        results = {
            'Title': EXTRATERRESTRIAL_NORMAL_IRRADIANCE,  # + Units : W / m*m REVIEWME
            EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME: extraterrestrial_normal_irradiance_series
        }

    if verbose > 1:
        extended_results = {
            DAY_OF_YEAR_COLUMN_NAME: day_of_year_series,
            DISTANCE_CORRECTION_COLUMN_NAME: distance_correction_factor_series,
        }
        results = results | extended_results

    if verbose > 0:
        return results

    log_data_fingerprint(
        data=extraterrestrial_normal_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return extraterrestrial_normal_irradiance_series
