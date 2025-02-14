import numpy as np
from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import FractionalYear
from pvgisprototype.algorithms.noaa.function_models import (
    CalculateFractionalYearTimeSeriesNOAAInput,
)
from pvgisprototype.api.datetime.helpers import get_days_in_years
from pvgisprototype.api.position.models import SolarPositionModel
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
    VALIDATE_OUTPUT_DEFAULT
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.core.arrays import create_array
from pvgisprototype.validation.functions import validate_with_pydantic


@log_function_call
@custom_cached
@validate_with_pydantic(CalculateFractionalYearTimeSeriesNOAAInput)
def calculate_fractional_year_series_noaa(
    timestamps: DatetimeIndex,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT
) -> FractionalYear:
    """Calculate the fractional year for a time series.

    Parameters
    ----------
    timestamps : DatetimeIndex
        A Pandas DatetimeIndex representing the timestamps.

    dtype : str, optional
        The data type for the calculations (the default is 'float32').

    array_backend : str, optional
        The backend used for calculations (the default is 'NUMPY').

    verbose: int
        Verbosity level

    log: int
        Log level

    Returns
    -------
    FractionalYear
        A FractionalYear object containing the calculated fractional year
        series.

    Raises
    ------
    ValueError
        If any calculated fractional year value is outside the expected range.

    Examples
    --------
    >>> timestamps = pd.date_range(start='2020-01-01', end='2020-12-31', freq='D')
    >>> fractional_year_series = calculate_fractional_year_series_noaa(timestamps)
    >>> print(fractional_year_series)

    Notes
    -----
    The function calculates the fractional year considering leap years and
    converts the timestamps into fractional values considering their position
    within the year.

    See also
    --------
    The default data type (`dtype`) and backend (`array_backend`) for arrays
    are set in `constants.py` via the global variables `DATA_TYPE_DEFAULT` and
    `ARRAY_BACKEND_DEFAULT`.

    """
    days_of_year = timestamps.dayofyear
    hours = timestamps.hour
    days_in_years = get_days_in_years(timestamps.year)
    array_parameters = {
        "shape": timestamps.shape,
        "dtype": dtype,
        "init_method": "zeros",
        "backend": array_backend,
    }  # Borrow shape from timestamps
    fractional_year_series = create_array(**array_parameters)
    fractional_year_series = np.array(
        2 * np.pi / days_in_years * (days_of_year - 1 + (hours - 12) / 24),
        dtype=dtype,
    )
    # Is this "restriction" correct ?
    fractional_year_series[fractional_year_series < 0] = 0
    
    if validate_output:
        if not np.all(
            (FractionalYear().min_radians <= fractional_year_series)
            & (fractional_year_series <= FractionalYear().max_radians)
        ):
            index_of_out_of_range_values = np.where(
                (fractional_year_series < FractionalYear().min_radians)
                | (fractional_year_series > FractionalYear().max_radians)
            )
            out_of_range_values = fractional_year_series[index_of_out_of_range_values]
            # Report values in "human readable" degrees
            raise ValueError(
                f"{WARNING_OUT_OF_RANGE_VALUES} "
                f"[{FractionalYear().min_radians}, {FractionalYear().max_radians}] radians"
                f" in [code]fractional_year_series[/code] : {out_of_range_values}"
            )

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
        position_algorithm=SolarPositionModel.noaa,
    )
