from numpy.typing import NDArray
from sparklines import sparklines
from pandas import DatetimeIndex, Timestamp, Series


def convert_series_to_sparkline(
    series: NDArray,
    timestamps: DatetimeIndex | Timestamp,
    frequency: str,
):
    """ """
    pandas_series = Series(series, timestamps)
    if (
        frequency == "Single"
        or (isinstance(timestamps, DatetimeIndex) and timestamps.size == 1)
        or isinstance(timestamps, Timestamp)
    ):
        return "▁"  # Return a flat line for a single value
    
    yearly_sum_series = pandas_series.resample(frequency).sum()
    sparkline = sparklines(yearly_sum_series)[0]
    
    return sparkline
