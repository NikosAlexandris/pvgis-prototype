from devtools import debug
from typing import Optional
from typing import Union
from datetime import datetime
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RANDOM_DAY_SERIES_FLAG_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import EXTRATERRESTRIAL_NORMAL_IRRADIANCE
from pvgisprototype.constants import EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DAY_OF_YEAR_COLUMN_NAME
from pvgisprototype.constants import DISTANCE_CORRECTION_COLUMN_NAME
from pvgisprototype.validation.pvis_data_classes import BaseTimestampSeriesModel
import numpy as np


def get_days_per_year(years):
    return 365 + ((years % 4 == 0) & ((years % 100 != 0) | (years % 400 == 0))).astype(int)

from pandas import DatetimeIndex
from cachetools.keys import hashkey
def custom_hashkey(*args, **kwargs):
    args = tuple(str(arg) if isinstance(arg, DatetimeIndex) else arg for arg in args)
    kwargs = {k: str(v) if isinstance(v, DatetimeIndex) else v for k, v in kwargs.items()}
    return hashkey(*args, **kwargs)

from cachetools import cached
@cached(cache={}, key=custom_hashkey)
def calculate_extraterrestrial_normal_irradiance_time_series(
    timestamps: BaseTimestampSeriesModel = None,  # DatetimeIndex ?
    start_time: Optional[datetime] = None,
    frequency: Optional[str] = None,
    end_time: Optional[datetime] = None,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    random_days: bool = RANDOM_DAY_SERIES_FLAG_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
) -> Union[np.ndarray, dict]:
    """
    Calculate the normal extraterrestrial irradiance over a period of time
    """
    timestamps = np.array(timestamps)
    years_in_timestamps = timestamps.astype('datetime64[Y]').astype(int) + 1970
    years, indices = np.unique(years_in_timestamps, return_inverse=True)
    days_per_year = get_days_per_year(years)
    days_in_years = days_per_year[indices]

    if random_days:
        day_of_year_series = np.random.randint(1, days_in_years + 1)
    else:
        start_of_years = np.datetime64('1970-01-01').astype('datetime64[D]').astype(int) + 365 * (years - 1970) + (years // 4 - 1970 // 4)
        start_of_timestamp_years = start_of_years[indices]
        day_of_year_series = (timestamps.astype('datetime64[D]').astype(int) - start_of_timestamp_years) + 1

    position_of_earth_series = 2 * np.pi * day_of_year_series / days_in_years
    distance_correction_factor_series = 1 + eccentricity_correction_factor * np.cos(position_of_earth_series - perigee_offset)
    extraterrestrial_normal_irradiance_series = solar_constant * distance_correction_factor_series

    if verbose == 7:
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

    return extraterrestrial_normal_irradiance_series
