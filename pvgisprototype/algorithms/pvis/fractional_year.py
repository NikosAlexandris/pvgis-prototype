from devtools import debug
from pvgisprototype.log import log_data_fingerprint
from pvgisprototype.log import log_function_call
from pandas import DatetimeIndex
from pvgisprototype.api.utilities.timestamp import get_days_in_year
from pvgisprototype.api.utilities.timestamp import get_days_in_years
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateFractionalYearPVISInputModel
from datetime import date, datetime
from pvgisprototype import FractionalYear
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import FRACTIONAL_YEAR_MINIMUM
from pvgisprototype.constants import FRACTIONAL_YEAR_MAXIMUM
from math import pi
from math import isclose
from cachetools import cached
from pvgisprototype.caching import custom_hashkey
from pandas import DatetimeIndex
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.validation.arrays import create_array
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
import numpy


@validate_with_pydantic(CalculateFractionalYearPVISInputModel)
def calculate_fractional_year_pvis(
    timestamp: datetime,
) -> FractionalYear:
    """Calculate fractional year in radians

    Notes
    -----
    In PVGIS' C source code, this is called `day_angle`

    NOAA's corresponding equation:

        fractional_year = (
            2
            * pi
            / 365
            * (timestamp.timetuple().tm_yday - 1 + float(timestamp.hour - 12) / 24)
        )
    """
    day_of_year = timestamp.timetuple().tm_yday
    days_in_year = get_days_in_year(timestamp.year)
    fractional_year = 2 * pi * day_of_year / days_in_year

    if not ((isclose(FRACTIONAL_YEAR_MINIMUM, fractional_year) or FRACTIONAL_YEAR_MINIMUM < fractional_year) and 
            (isclose(FRACTIONAL_YEAR_MAXIMUM, fractional_year) or fractional_year < FRACTIONAL_YEAR_MAXIMUM)):
        raise ValueError(f'Calculated fractional year {fractional_year} is out of the expected range [{FRACTIONAL_YEAR_MINIMUM}, {FRACTIONAL_YEAR_MAXIMUM}] radians')

    print(f'{fractional_year=}')
    fractional_year = FractionalYear(value=fractional_year, unit=RADIANS)
            
    return fractional_year


# @validate_with_pydantic(CalculateFractionalYearPVISInputModel)
@log_function_call
@cached(cache={}, key=custom_hashkey)
def calculate_fractional_year_series_pvis(
    timestamps: DatetimeIndex,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> FractionalYear:
    """Calculate fractional year in radians

    Notes
    -----
    In PVGIS' C source code, this is called `day_angle`

    NOAA's corresponding equation:

        fractional_year = (
            2
            * pi
            / 365
            * (timestamp.timetuple().tm_yday - 1 + float(timestamp.hour - 12) / 24)
        )
    """
    days_of_year = timestamps.dayofyear
    days_in_years = get_days_in_years(timestamps.year) 
    array_parameters = {
        "shape": timestamps.shape,
        "dtype": dtype,
        "init_method": "zeros",
        "backend": array_backend,
    }  # Borrow shape from timestamps
    fractional_year_series = create_array(**array_parameters)
    fractional_year_series = numpy.array(
        2 * pi * days_of_year / days_in_years,
        dtype=dtype,
    )
    print(f'{fractional_year_series=}')

    # if not ((isclose(FRACTIONAL_YEAR_MINIMUM, fractional_year) or FRACTIONAL_YEAR_MINIMUM < fractional_year) and 
    #         (isclose(FRACTIONAL_YEAR_MAXIMUM, fractional_year) or fractional_year < FRACTIONAL_YEAR_MAXIMUM)):
    #     raise ValueError(f'Calculated fractional year {fractional_year} is out of the expected range [{FRACTIONAL_YEAR_MINIMUM}, {FRACTIONAL_YEAR_MAXIMUM}] radians')

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
            data=fractional_year_series,
            log_level=log,
            hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )
            
    return FractionalYear(
        value=fractional_year_series,
        unit=RADIANS,
        position_algorithm='PVIS',
        timing_algorithm='PVIS',
    )
