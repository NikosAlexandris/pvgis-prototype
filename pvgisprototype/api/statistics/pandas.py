import numpy
import pandas
from pandas import DatetimeIndex

from pvgisprototype.api.utilities.conversions import round_float_values

from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
)

def calculate_sum_and_percentage(
    series,
    reference_series,
    rounding_places=None,
    dtype=DATA_TYPE_DEFAULT,
    array_backend=ARRAY_BACKEND_DEFAULT,
):
    """Calculate sum of a series and its percentage relative to a reference series.

    Notes
    -----

    Uses .item() to convert NumPy numerics to standard Python types.
    """
    total = numpy.nansum(series).item()
    if isinstance(total, numpy.ndarray):
        total = total.astype(dtype).item()

    percentage = (total / reference_series * 100) if reference_series != 0 else 0

    if isinstance(percentage, numpy.ndarray):
        percentage.astype(dtype)

    if rounding_places is not None:
        total = round_float_values(total, rounding_places)
        percentage = round_float_values(percentage, rounding_places)

    return total, percentage


def calculate_statistics(
    series,
    timestamps,
    frequency,
    reference_series,
    rounding_places=None,
    dtype=DATA_TYPE_DEFAULT,
    array_backend=ARRAY_BACKEND_DEFAULT,
):
    """Calculate the sum, mean, standard deviation of a series based on a
    specified frequency and its percentage relative to a reference series.
    """
    if frequency == "Single":
        total = series.item()  # total is the single value in the series
        mean = total  # For a single value, the mean is the value itself
        std_dev = 0  # Standard deviation is 0 for a single value
        percentage = (total / reference_series * 100) if reference_series != 0 else 0

        if rounding_places is not None:
            total = round_float_values(total, rounding_places)
            percentage = round_float_values(percentage, rounding_places)

        return total, mean, std_dev, percentage

    pandas_series = pandas.Series(series, timestamps)
    resampled = pandas_series.resample(frequency)
    total = resampled.sum().sum().item()  # convert to Python float
    # if isinstance(total, numpy.ndarray):
    #     total = total.astype(dtype)
    percentage = (total / reference_series * 100) if reference_series != 0 else 0
    # if isinstance(percentage, numpy.ndarray):
    #     percentage.astype(dtype)
    if rounding_places is not None:
        total = round_float_values(total, rounding_places)
        percentage = round_float_values(percentage, rounding_places)
    mean = resampled.mean().mean().item()  # convert to Python float
    std_dev = resampled.std().mean()  # Mean of standard deviations over the period

    return total, mean, std_dev, percentage


def calculate_mean_of_series_per_time_unit(
    series: numpy.ndarray,
    timestamps: DatetimeIndex,
    frequency: str,
):
    """ """
    # from devtools import debug

    # debug(locals())
    if frequency == "Single" or len(timestamps) == 1:
        return series.mean().item()  # Direct mean for a single value

    pandas_series = pandas.Series(series, index=timestamps)
    # print(pandas_series)
    mean = pandas_series.resample(frequency).sum().mean().item()  # convert to float

    # print(mean)
    return mean
