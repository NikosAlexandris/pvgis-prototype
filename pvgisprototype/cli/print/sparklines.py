from numpy.typing import NDArray
from sparklines import sparklines
from pandas import DatetimeIndex, Series


def convert_series_to_sparkline(
    series: NDArray,
    timestamps: DatetimeIndex,
    frequency: str,
):
    """ """
    pandas_series = Series(series, timestamps)
    yearly_sum_series = pandas_series.resample(frequency).sum()
    sparkline = sparklines(yearly_sum_series)[0]

    return sparkline
