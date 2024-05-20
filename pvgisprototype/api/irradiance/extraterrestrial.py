from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from devtools import debug
from typing import Optional
from typing import Union
from datetime import datetime
from pvgisprototype import Irradiance
from pvgisprototype.validation.hashing import generate_hash
from pvgisprototype.constants import IRRADIANCE_UNITS
from pvgisprototype.constants import FINGERPRINT_COLUMN_NAME
from pvgisprototype.constants import DAY_ANGLE_SERIES
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RANDOM_TIMESTAMPS_FLAG_DEFAULT
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import TITLE_KEY_NAME
from pvgisprototype.constants import EXTRATERRESTRIAL_NORMAL_IRRADIANCE
from pvgisprototype.constants import EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DAY_OF_YEAR_COLUMN_NAME
from pvgisprototype.constants import DISTANCE_CORRECTION_COLUMN_NAME
from pvgisprototype.validation.pvis_data_classes import BaseTimestampSeriesModel
import numpy as np
from pandas import DatetimeIndex
from cachetools import cached
from pvgisprototype.caching import custom_hashkey


def get_days_per_year(years):
    return 365 + ((years % 4 == 0) & ((years % 100 != 0) | (years % 400 == 0))).astype(int)


@log_function_call
@cached(cache={}, key=custom_hashkey)
def calculate_extraterrestrial_normal_irradiance_time_series(
    timestamps: DatetimeIndex,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
    fingerprint: bool = False,
) -> Union[np.ndarray, dict]:
    """
    Calculate the normal extraterrestrial irradiance over a period of time

    Notes
    -----
    Symbol in ... `G0`

    """
    years_in_timestamps = timestamps.year
    years, indices = np.unique(years_in_timestamps, return_inverse=True)
    days_per_year = get_days_per_year(years).astype(dtype)
    days_in_years = days_per_year[indices]
    day_of_year_series = timestamps.dayofyear.to_numpy().astype(dtype)
    # day angle == fractional year, hence : use model_fractional_year_series()
    day_angle_series = 2 * np.pi * day_of_year_series / days_in_years
    distance_correction_factor_series = 1 + eccentricity_correction_factor * np.cos(day_angle_series - perigee_offset)
    extraterrestrial_normal_irradiance_series = solar_constant * distance_correction_factor_series

    components_container = {
        'main': lambda: {
            TITLE_KEY_NAME: EXTRATERRESTRIAL_NORMAL_IRRADIANCE,
            EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME: extraterrestrial_normal_irradiance_series,
        },

        'extended': lambda: {
            DAY_OF_YEAR_COLUMN_NAME: day_of_year_series,
            DAY_ANGLE_SERIES: day_angle_series,
            DISTANCE_CORRECTION_COLUMN_NAME: distance_correction_factor_series,
        } if verbose > 1 else {},

        'fingerprint': lambda: {
            FINGERPRINT_COLUMN_NAME: generate_hash(extraterrestrial_normal_irradiance_series),
        } if fingerprint else {},
    }

    components = {}
    for key, component in components_container.items():
        components.update(component())

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=extraterrestrial_normal_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return Irradiance(
            value=extraterrestrial_normal_irradiance_series,
            unit=IRRADIANCE_UNITS,
            position_algorithm="",
            timing_algorithm="",
            elevation=None,
            surface_orientation=None,
            surface_tilt=None,
            components=components,
            )
