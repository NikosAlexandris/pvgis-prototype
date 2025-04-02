from numpy import ndarray
from pandas import DatetimeIndex

from pvgisprototype.constants import LOG_LEVEL_DEFAULT, VERBOSE_LEVEL_DEFAULT
from pvgisprototype.log import log_function_call


@log_function_call
def compare_temporal_resolution(
    timestamps: DatetimeIndex = None,
    array: ndarray = None,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
):
    """
    Check if the frequency of `timestamps` matches the temporal resolution of the `array`.

    Parameters
    ----------
    timestamps:
        An array of generated timestamps.
    array:
        An array of data corresponding to some time series.

    Raises
    ------
        ValueError: If the lengths of the timestamps and data_series don't match.
    """
    if timestamps.size != array.size:
        raise ValueError(
            f"The frequency of `timestamps` ({timestamps.size}) does not match the temporal resolution of the `array` ({array.size}). Please ensure they have the same temporal resolution."
        )
