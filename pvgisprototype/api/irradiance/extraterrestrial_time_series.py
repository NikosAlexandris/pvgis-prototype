from devtools import debug
from pvgisprototype.validation.parameters import BaseTimestampSeriesModel
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.constants import DAYS_IN_A_YEAR
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RANDOM_DAY_FLAG_DEFAULT
import numpy as np


def calculate_extraterrestrial_normal_irradiance_time_series(
    timestamps: BaseTimestampSeriesModel,
    solar_constant: float = SOLAR_CONSTANT,
    days_in_a_year: float = DAYS_IN_A_YEAR,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    random_days: bool = RANDOM_DAY_FLAG_DEFAULT,
    verbose: int = 0,
) -> np.ndarray:
    """ """    
    if random_days:
        day_of_year_series = np.array([random_day_of_year(int(days_in_a_year)) for _ in timestamps])

    else:
        day_of_year_series = np.array([timestamp.timetuple().tm_yday for timestamp in timestamps])
        
    position_of_earth_series = 2 * np.pi * day_of_year_series / days_in_a_year
    distance_correction_factor_series = 1 + eccentricity_correction_factor * np.cos(position_of_earth_series - perigee_offset)
    extraterrestrial_normal_irradiance_series = solar_constant * distance_correction_factor_series
    
    if verbose == 3:
        debug(locals())
    return extraterrestrial_normal_irradiance_series
