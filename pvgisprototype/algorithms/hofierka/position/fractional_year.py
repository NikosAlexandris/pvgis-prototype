from math import pi

import numpy
from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import FractionalYear
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
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.core.arrays import create_array


# @validate_with_pydantic(CalculateFractionalYearPVISInputModel)
@log_function_call
@custom_cached
def calculate_day_angle_series_hofierka(
    timestamps: DatetimeIndex,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> FractionalYear:
    """Calculate the day angle for a time series.

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

    Notes
    -----
    The day angle [0]_ is the same quantity called Fractional Year in NOAA's
    solar geometry equations, i.e. the function
    calculate_fractional_year_time_series_noaa().

    In PVGIS' C source code, this is called `day_angle`

    NOAA's corresponding equation:

        fractional_year = (
            2
            * pi
            / 365
            * (timestamp.timetuple().tm_yday - 1 + float(timestamp.hour - 12) / 24)
        )

    References
    ----------
    .. [0] Hofierka, 2002

    NOAA's corresponding equation:

        day_angle = (
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
    day_angle_series = create_array(**array_parameters)
    day_angle_series = numpy.array(
        2 * pi * days_of_year / days_in_years,
        dtype=dtype,
    )

    if not numpy.all(
        (FractionalYear().min_radians <= day_angle_series)
        & (day_angle_series <= FractionalYear().max_radians)
    ):
        index_of_out_of_range_values = numpy.where(
            (day_angle_series < FractionalYear().min_radians)
            | (day_angle_series > FractionalYear().max_radians)
        )
        out_of_range_values = day_angle_series[index_of_out_of_range_values]
        # Report values in "human readable" degrees
        raise ValueError(
            f"{WARNING_OUT_OF_RANGE_VALUES} "
            f"[{FractionalYear().min_radians}, {FractionalYear().max_radians}] radians"
            f" in [code]day_angle_series[/code] : {out_of_range_values}"
        )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=day_angle_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return FractionalYear(
        value=day_angle_series,
        unit=RADIANS,
        position_algorithm=SolarPositionModel.hofierka,
    )
