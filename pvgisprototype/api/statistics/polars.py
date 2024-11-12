from pvgisprototype.log import log_function_call, logger
from pandas import DatetimeIndex
from pvgisprototype.api.utilities.conversions import round_float_values
import polars
import numpy
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
)

FREQUENCY_PANDAS_TO_POLARS = {
    "YE": "1y",
    "ME": "1mo",
    "W": "1w",
    "D": "1d",
    "3h": "3h",
    "h": "1h",
    "min": "1m",
    "8min": "8m",
}


@log_function_call
def calculate_sum_and_percentage(
    series,
    reference_series,
    rounding_places=None,
    dtype=DATA_TYPE_DEFAULT,
    array_backend=ARRAY_BACKEND_DEFAULT,
):
    """Calculate sum of a series and its percentage relative to a reference series.

    Parameters
    ----------
    series : array-like
        The input series to sum over.
    reference_series : float or int
        Reference value for calculating percentage.
    rounding_places : int, optional
        Number of decimal places for rounding the result.
    dtype : str, optional
        Data type for the calculations, default is "float32".
    
    Returns
    -------
    tuple
        The total sum and percentage relative to the reference.
    """
    total = numpy.nansum(series, dtype=dtype)
    percentage = (total / reference_series * 100) if reference_series != 0 else 0

    if rounding_places is not None:
        total = round_float_values(total, rounding_places)
        percentage = round_float_values(percentage, rounding_places)

    return total, percentage


@log_function_call
def get_season(month):
    """
    Map each timestamp to a season
    """
    if month in [12, 1, 2]:  # December-January-February
        return "DJF"
    elif month in [3, 4, 5]:  # March-April-May
        return "MAM"
    elif month in [6, 7, 8]:  # June-July-August
        return "JJA"
    elif month in [9, 10, 11]:  # September-October-November
        return "SON"


@log_function_call
def calculate_statistics(
    series,
    timestamps,
    frequency,
    reference_series,
    rounding_places=None,
    dtype=DATA_TYPE_DEFAULT,
    array_backend=ARRAY_BACKEND_DEFAULT,
):
    """Calculate the descriptive statistics for a series based on a specified
    frequency and its percentage relative to a reference series.

    Calculate the sum, mean and standard deviation of a series based on a
    frequency and its percentage relative to a reference series.

    Parameters
    ----------
    series : np.ndarray
        The input series.
    timestamps : np.ndarray
        The timestamps associated with the series.
    frequency : str
        The frequency of the series (e.g., "S" for seasonal).
    reference_series : np.ndarray
        The reference series.
    rounding_places : Optional[int], optional
        The number of decimal places to round the results to. Defaults to None.
    dtype : str, optional
        The data type of the results. Defaults to np.float64.
    array_backend : str, optional
        The array backend to use. Defaults to "numpy".

    Returns
    -------
    tuple
        A tuple containing the sum, mean, standard deviation, and percentage of
        the series relative to the reference series.

    See Also
    --------
    numpy.sum, numpy.mean, numpy.std

    Notes
    -----
    This function uses Polars DataFrames for efficient grouping and aggregation.

    Examples
    --------
    Calculate statistics for a seasonal series:

    >>> from numpy import array
    >>> from pandas import date_range
    >>> series = array([1, 2, 3, 4, 5, 6, 7, 8, 9])
    >>> timestamps = date_range(start='2022-01-01', end='2022-01-02', freq='3h')
    >>> frequency = "D"
    >>> reference_series = array([4])
    >>> calculate_statistics(series, timestamps, frequency, reference_series)
    (45.0, 6.75, 2.4494898319244385, 1125.0)

    Raises
    ------
    ValueError
        If series or reference_series is None.
    """

    logger.info("Calculate statistics")
    # Ensure initial inputs are in the specified dtype
    logger.info(
            f"The input series {series} of shape {series.shape} is of type {type(series)} while the requested type is {dtype}.",
            alt=f"The input series {series} of shape {series.shape} is of type {type(series)} while the requested type is {dtype}."
            )
    series = numpy.asarray(series, dtype=dtype) if series.dtype != dtype else series
    reference_series = (
        numpy.asarray(reference_series, dtype=dtype)
        if not isinstance(reference_series, numpy.generic)
        or reference_series.dtype != dtype
        else reference_series
    )

    if frequency == "Single":
        logger.info(
            f"The requested frequency is {frequency}.",
            alt=f"The requested frequency is [code]{frequency}[/code]."
        )
        total = series.sum()
        mean = total
        std_dev = numpy.array(
            0, dtype=dtype
        )  # zero standard deviation for single values
        percentage = (total / reference_series * 100) if reference_series != 0 else 0

        if rounding_places is not None:
            total = round(total, rounding_places)
            percentage = round(percentage, rounding_places)

        return total, mean, std_dev, percentage

    # Convert timestamps and series to Polars DataFrame
    data = polars.DataFrame(
        {
            "timestamps": polars.Series(timestamps),
            "values": polars.Series(series, dtype=getattr(polars, dtype.capitalize())),
        }
    )

    # Seasonal grouping
    if frequency == "S":
        logger.info(
            f"The requested frequency is {frequency} meaning seasonal.",
            alt=f"The requested frequency is {frequency} meaning [italic]seasonal[/italic].",
        )

        # Add a season column based on month
        data = data.with_columns(
            polars.col("timestamps").dt.month().apply(get_season).alias("season")
        )

        # Group by season
        resampled = data.group_by("season").agg(
            [
                polars.col("values").sum().alias("total"),
                polars.col("values").mean().alias("mean"),
                polars.col("values").std().alias("std_dev"),
            ]
        )

    # Non-seasonal grouping
    else:
        # Convert Pandas to Polars frequency strings
        polars_frequency = FREQUENCY_PANDAS_TO_POLARS.get(frequency, frequency)
        logger.info(
                f"The requested frequency is {frequency} (Polars : {polars_frequency}).",
            alt=f"The requested frequency is [code]{frequency}[/code] (Polars : {polars_frequency})."
        )

        # Group by frequency and compute aggregations
        resampled = data.group_by_dynamic("timestamps", every=polars_frequency).agg(
            [
                polars.col("values").sum().alias("total"),
                polars.col("values").mean().alias("mean"),
                polars.col("values").std().alias("std_dev"),
            ]
        )

    # Calculate sum, mean, std_dev over all resampled intervals _and_ cast to dtype
    total = numpy.array(resampled["total"].sum(), dtype=dtype).item()
    mean = numpy.array(resampled["mean"].mean(), dtype=dtype).item()
    std_dev = numpy.array(resampled["std_dev"].mean(), dtype=dtype).item()
    percentage = (
        numpy.array((total / reference_series * 100), dtype=dtype).item()
        if reference_series != 0
        else numpy.array(0, dtype=dtype).item()
    )

    # Apply rounding if needed
    if rounding_places is not None:
        logger.info(
                f"Rounding values total : {total}, mean : {mean}, std_dev : {std_dev} and percentage : {percentage}",
                alt=f"Rounding values total : {total}, mean : {mean}, std_dev : {std_dev} and percentage : {percentage}"
                )
        total = round_float_values(total, rounding_places)
        mean = round_float_values(mean, rounding_places)
        std_dev = round_float_values(std_dev, rounding_places)
        percentage = round_float_values(percentage, rounding_places)

    # return numpy.array(total, dtype=dtype), numpy.array(mean, dtype=dtype), numpy.array(std_dev, dtype=dtype), numpy.array(percentage, dtype=dtype)
    return total, mean, std_dev, percentage


def calculate_mean_of_series_per_time_unit(
    series: numpy.ndarray,
    timestamps: DatetimeIndex,
    frequency: str,
):
    """Calculate the mean of a series resampled to a specified time frequency using Polars."""
    logger.info(
        f"The series input {series} is of type {type(series)}.",
        alt=f"The series input {series} is of type {type(series)}.",
    )
    # Handle the case for a single timestamp or "Single" frequency
    if frequency == "Single" or len(timestamps) == 1:
        logger.info(
            f"The requested frequency is {frequency} or the input DatetimeIndex is a single timestamp.",
            alt=f"The requested frequency is [code]{frequency}[/code] or the DatetimeIndex is a single timestamp."
        )
        return series.mean().item()  # Direct mean for a single value

    # Create a Polars DataFrame with series values and timestamps
    data = polars.DataFrame(
        {"timestamps": polars.Series(timestamps), "values": polars.Series(series)}
    )

    # Convert Pandas to Polars frequency strings
    polars_frequency = FREQUENCY_PANDAS_TO_POLARS.get(frequency, frequency)

    # Resample data using Polars' dynamic grouping
    resampled_sum = data.group_by_dynamic("timestamps", every=polars_frequency).agg(
        polars.col("values").sum()
    )  # Sum within each time unit

    # Compute the mean of the summed values
    return resampled_sum["values"].mean()
